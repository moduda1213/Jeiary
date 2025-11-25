# API 엔드포인트에서는 구현된 Service 로직을 의존성으로 주입받아 사용
# 이를 위한 설정 파일
from loguru import logger
from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.services.auth_service import AuthService
from app.services.schedule_service import ScheduleService
from app.services.ai_service import AIService

from app.core.exceptions import CredentialException, ExpiredTokenException, InvalidTokenException
from app.core.security import oauth2_scheme, verify_token
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import TokenPayload

# DB 세션 의존성
DBSessionDep = Annotated[AsyncSession, Depends(get_db)]

# Repository 의존성
def get_user_repo(db: DBSessionDep) -> UserRepository:
    return UserRepository(session=db)

def get_refresh_token_repo(db: DBSessionDep) -> RefreshTokenRepository:
    return RefreshTokenRepository(session=db)

def get_schedule_repo(db: DBSessionDep) -> ScheduleRepository:
    return ScheduleRepository(session=db)

UserRepoDep = Annotated[UserRepository, Depends(get_user_repo)]
RefreshTokenRepoDep = Annotated[RefreshTokenRepository, Depends(get_refresh_token_repo)]
ScheduleRepoDep = Annotated[ScheduleRepository, Depends(get_schedule_repo)]

# Service 의존성
def get_auth_service(
    user_repo: UserRepoDep,
    refresh_token_repo: RefreshTokenRepoDep,
) -> AuthService:
    return AuthService(user_repo=user_repo, refresh_token_repo=refresh_token_repo)

def get_schedule_service(
    schedule_repo: ScheduleRepoDep,
) -> ScheduleService:
    return ScheduleService(schedule_repo=schedule_repo)

AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
ScheuduleServiceDep = Annotated[ScheduleService, Depends(get_schedule_service)]

async def get_current_user(
    request: Request,
    user_repo: UserRepoDep,
) -> User:
    """
    HTTPOnly 쿠키에서 JWT Access Token을 검증하고 현재 인증된 사용자 객체를 반환합니다.
    """
    token = request.cookies.get("access_token")
    
    if not token:
        raise CredentialException(detail="인증 토큰이 존재하지 않습니다.")
     
    try:
        payload = verify_token(token, token_type="access")
        token_data = TokenPayload(**payload)
    
    except (InvalidTokenException, ExpiredTokenException):
        raise CredentialException(detail="토큰 검증에 실패했습니다.")
    
    user = await user_repo.get_by_email(email=token_data.sub)
    
    if user is None:
        raise CredentialException(detail="사용자를 찾을 수 없습니다.")
    
    return user

CurrentUserDep = Annotated[User, Depends(get_current_user)]

# AI Service 의존성 주입 함수
def get_ai_service() -> AIService:
    """AIService 인스턴스를 제공합니다."""
    return AIService()

AIServiceDep = Annotated[AIService, Depends(get_ai_service)]