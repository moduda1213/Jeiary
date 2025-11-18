from fastapi import APIRouter, Depends, status, Request, Response
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated
from loguru import logger

from app.dependencies import AuthServiceDep, CurrentUserDep
from app.schemas.user import UserResponse, UserCreate
from app.schemas.auth import AuthLogin
from app.core.limiter import limiter
from app.core.exceptions import CredentialException
from app.config import settings


router = APIRouter(
    prefix="/auth",
    tags=["Auth"],
)

@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="회원가입",
    description="새로운 사용자를 생성하고, 생성된 사용자 정보를 반환합니다."
)
async def register(
    request: Request, 
    user_data: UserCreate, 
    service: AuthServiceDep,
) -> UserResponse:
    """
    새로운 사용자를 등록합니다.

    **email**: 사용자의 이메일 주소 (고유)
    **password**: 비밀번호(8자 이상, 영문/숫자 포함)
    """
    logger.info(f"요청 URL : {str(request.url.path)}?email={user_data.email} -> 새로운 사용자 등록 엔드포인트 진입")
    new_user = await service.register(user_create=user_data)
    return new_user

@router.post(
    "/login",
    summary="로그인 (Access/Refresh Token 발급)",
    description="사용자 이메일(username)과 비밀번호로 로그인하여 토큰을 발급받습니다."
)
@limiter.limit("5/minute")
async def login(
    request: Request, 
    response: Response,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()], 
    service: AuthServiceDep,
) -> dict:
    """
    사용자 이메일과 비밀번호로 로그인합니다.
    
    성공 시 **httpOnly 쿠키**에 토큰을 설정하고 성공 메시지를 반환합니다.
    """
    logger.info(f"요청 URL : {str(request.url.path)}?username={form_data.username} -> 로그인 엔드포인트 진입")
    
    # 서비스 계층은 AuthLogin 스키마를 사용하므로 변환 과정이 필요
    auth_data = AuthLogin(email=form_data.username, password=form_data.password)
    token_response = await service.login(form_data=auth_data)
    
    '''
    response.set_cookie(
        key = "",
        value = "",
        httponly = True,  # True : JavaScript에서 쿠키에 접근하는 것을 막아 보안을 강화
        secure = True,    # True : HTTPS를 사용하는 운영 환경에서는 쿠키가 암호화된 연결을 통해서만 전송
        samesite = "lax",      # CSRF 공격을 일부 방지하는 표준적인 설정
        max_age = "seconds" # 초 단위로 설정
    )
    '''
    response.set_cookie(
        key = "access_token",
        value = token_response.access_token,
        httponly = True,
        secure = settings.ENVIRONMENT != "development",
        samesite = "lax",
        max_age = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60 # 초 단위로 설정
    )
    
    response.set_cookie(
        key = "refresh_token",
        value = token_response.refresh_token,
        httponly = True,
        secure = settings.ENVIRONMENT != "development",
        samesite = "lax",
        max_age = settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60 # 초 단위로 설정
    )
    
    return {"message": "Login successful"}

@router.post(
    "/refresh",
    summary="Access Token 갱신(쿠키 방식)",
    description="쿠키의 Refresh Token을 사용하여 새로운 Access Token을 발급하고 쿠키로 설정합니다."
)
async def refresh_access_token(
    request: Request,
    response: Response,
    service: AuthServiceDep,
) -> dict:
    """
    쿠키의 Refresh Token을 사용하여 새로운 Access Token을 발급하고 쿠키를 갱신합니다.
    """
    logger.info(f"요청 URL : {str(request.url.path)} -> 새로운 Access Token 갱신 엔드포인트 진입")
    
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise CredentialException(detail="Refresh Token이 존재하지 않습니다.")
    
    new_token_response = await service.refresh_access_token(
        refresh_token = refresh_token
    )
    
    response.set_cookie(
        key = "access_token",
        value = new_token_response.access_token,
        httponly = True,
        secure = settings.ENVIRONMENT != "development",
        samesite = "lax",
        max_age = settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60 # 초 단위로 설정
    )
    
    return {"message": "Access token refreshed successfully"}

@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="로그아웃 (쿠키 방식)",
    description="Refresh Token을 무효화하고 클라이언트의 토큰 쿠키를 삭제합니다."
)
async def logout(
    request: Request,
    response: Response,
    service: AuthServiceDep,
) -> None:
    """
    클라이언트의 Refresh Token을 받아 DB에서 무효화 처리하고,
    브라우저의 토큰 쿠키를 삭제합니다.
    """
    logger.info(f"요청 URL : {str(request.url)} -> 로그아웃 ")
    
    refresh_token = request.cookies.get("refresh_token")
    if refresh_token:
        await service.logout(refresh_token=refresh_token)
    
    # 클라이언트의 쿠키 삭제
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")
    
    
@router.get(
    "/me",
    response_model=UserResponse,
    summary="현재 사용자 정보 조회",
    description="인증된 현재 사용자의 정보를 반환합니다."
)
async def read_users_me(current_user: CurrentUserDep) -> UserResponse:
    """
    유효한 Access Token을 헤더에 포함하여 요청 시,
    현재 로그인된 사용자의 정보를 반환합니다.
    """
    return current_user