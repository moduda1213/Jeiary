from loguru import logger

from fastapi import HTTPException, status
from datetime import datetime

# Repositories
from app.repositories.user_repo import UserRepository
from app.repositories.refresh_token_repo import RefreshTokenRepository

# Schemas
from app.schemas.user import UserCreate
from app.schemas.auth import AuthLogin, TokenResponse

# Models
from app.models.user import User

# Core
from app.core import security
from app.core.exceptions import CredentialException, ExpiredTokenException, InvalidTokenException


class AuthService:
    """
    __init__: UserRepository를 의존성으로 주입받습니다.
    register:
        * UserCreate 스키마로 사용자 정보를 받습니다.
        * UserRepository를 사용해 새로운 사용자를 생성합니다.
    login:
       * 이메일로 사용자를 조회하고, 없으면 CredentialException을 발생시킵니다.
       * 비밀번호를 검증하고, 일치하지 않으면 CredentialException을 발생시킵니다.
       * core.security를 사용하여 Access Token과 Refresh Token을 생성합니다.
       * 생성된 Refresh Token의 고유 식별자(jti)와 만료 시간을 DB에 저장하여 토큰 탈취 시 무효화할 수 있도록 대비합니다.
       * 두 토큰을 TokenResponse 스키마에 담아 반환합니다.
    refresh_access_token
    logout
    """
    def __init__(
        self, 
        user_repo: UserRepository,
        refresh_token_repo: RefreshTokenRepository
    ):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
    
    async def register(self, user_create: UserCreate) -> User:
        """
        신규 사용자 등록

        Args:
            user_create (UserCreate): 생성할 사용자 정보(Pydantic 스키마)

        Returns:
            User: 생성된 User ORM 객체
            
        Raises:
            HTTPException: 이메일이 이미 존재할 경우 (409 Conflict)
        """
        existing_user = await self.user_repo.get_by_email(user_create.email)
        if existing_user:
            raise HTTPException(
                status_code = status.HTTP_409_CONFLICT,
                detail = "이미 사용중인 이메일입니다.",
            )
        
        new_user = await self.user_repo.create(user_create)
        return new_user
    
    async def login(self, form_data: AuthLogin) -> TokenResponse:
        """
        사용자 로그인 및 토큰 발급
        Args:
            form_data: 로그인 정보 (이메일, 비밀번호)
        Returns:
            TokenResponse: Access Token 및 Refresh Token
        Raises:
            CredentialException: 인증 실패 시
        """
        
        logger.debug(f"로그인 시도 - 이메일: {form_data.email}")
        
        try:
            user = await self.user_repo.get_by_email(form_data.email)
            # 유효한 bcrypt 해시로 Timing Attack 방지
            dummy_hash = "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5ztRfN8C9F7re"
            
            # Timing Attack 방지
            if not user:
                logger.warning(f"로그인 실패 - 존재하지 않는 이메일: {form_data.email}")
                security.verify_password(form_data.password, dummy_hash)
                raise CredentialException(detail="이메일 또는 비밀번호가 올바르지 않습니다.")
            
            if not security.verify_password(form_data.password, user.password_hash):
                logger.warning(
                    f"로그인 실패 - 잘못된 비밀번호, "
                    f"사용자ID: {user.id}, 이메일: {user.email}"
                )
                raise CredentialException(detail="이메일 또는 비밀번호가 올바르지 않습니다.")
            
            logger.debug(f"토큰 생성 시작 - 사용자ID: {user.id}")
            
            # Access Token 생성
            access_token = security.create_access_token(data={"sub": user.email})
                
            # Refresh Token 생성 및 저장
            refresh_token = security.create_refresh_token(data={"sub": user.email}) 
            
            # Refresh Token 정보 추출 및 DB 저장
            payload = security.verify_token(refresh_token, token_type="refresh")
            jti = payload.get("jti")
            exp = datetime.fromtimestamp(payload.get("exp"))
            
            await self.refresh_token_repo.create(
                user_id=user.id,
                jti=jti,
                expires_at=exp
            )
            
            logger.debug(f"Refresh Token 저장 완료 - JTI: {jti}, 사용자ID: {user.id}")
            
            return TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token
            )
            
        except (ExpiredTokenException, CredentialException, InvalidTokenException):
            # 이미 로깅된 예외는 재발생만
            raise
            
        except Exception as e:
            # 예상치 못한 오류
            logger.error(
                f"토큰 갱신 중 예상치 못한 오류 - 에러: {str(e)}",
                exc_info=True
            )
            raise CredentialException("토큰 갱신 중 오류가 발생했습니다.")
        
    async def refresh_access_token(self, refresh_token: str) -> TokenResponse:
        """
        Refresh Token을 사용하여 새로운 Access Token을 발급합니다.

        Args:
            refresh_token (str): 클라이언트로부터 받은 Refresh Token

        Returns:
            TokenResponse: 새로운 Access Token과 기존 Refresh Token
        
        Raises:
            CredentialException: Refresh Token이 유효하지 않거나 탈취된 경우
        """
        logger.debug(f"Refresh Token 검증")
        
        try:
            # Refresh Token 검증
            payload = security.verify_token(refresh_token, token_type="refresh")
            
            # 페이로드에서 jti와 sub(이메일) 추출
            jti = payload.get("jti")
            email = payload.get("sub")
            
            if not jti or not email:
                logger.warning(f"토큰 페이로드 불완전 - JTI: {jti}, Email: {bool(email)}")
                raise CredentialException(detail="토큰에 필요한 정보가 없습니다.")
            
            logger.debug(f"토큰 검증 완료 - JTI: {jti}, Email: {email}")
            
            # DB에 저장된 Refresh Token 정보와 대조 (탈튀 여부 확인)
            stored_token = await self.refresh_token_repo.get_by_jti(jti)
            
            if not stored_token:
                logger.error(
                    f"DB에 존재하지 않는 Refresh Token 사용 시도 - "
                    f"JTI: {jti}, Email: {email}"
                )
                raise CredentialException(detail="토큰이 무효화되었거나 존재하지 않습니다.")

            if stored_token.is_revoked:
                logger.error(
                    f"무효화된 Refresh Token 재사용 감지 (탈취 가능성) - "
                    f"JTI: {jti}, UserID: {stored_token.user_id}, Email: {email}"
                )
                # TODO. revoke_all_by_user 구현 시 적용
                raise CredentialException(detail="보안 위협 감지로 모든 세션이 종료되었습니다.")
            
            # 사용자 정보 확인
            user = await self.user_repo.get_by_email(email)
            if not user:
                logger.warning(
                    f"존재하지 않는 사용자로 토큰 갱신 시도 - "
                    f"Email: {email}, JTI: {jti}"
                )
                raise CredentialException(detail="사용자를 찾을 수 없습니다.")
            
            new_access_token = security.create_access_token(data={"sub": user.email})
            logger.info(
                f"Access Token 갱신 성공 - UserID: {user.id}, Email: {user.email}"
            )
            return TokenResponse(
                access_token=new_access_token,
                refresh_token=refresh_token
            )
        except (ExpiredTokenException, CredentialException, InvalidTokenException):
            # 이미 로깅된 예외는 재발생만
            raise
            
        except Exception as e:
            # 예상치 못한 오류
            logger.error(
                f"토큰 갱신 중 예상치 못한 오류 - 에러: {str(e)}",
                exc_info=True
            )
            raise CredentialException("토큰 갱신 중 오류가 발생했습니다.")
        
    async def logout(self, refresh_token: str) -> None:
        """
        사용자 로그아웃을 처리하고 Refresh Token을 무효화합니다.

        Args:
            refresh_token (str): 무효화할 Refresh Token
        
        Returns:
            None: 항상 성공 (만료/유효하지 않은 토큰도 성공으로 처리)
    
        Raises:
            CredentialException: 예상치 못한 오류 발생 시
        """
        logger.debug("로그아웃 시도 - Refresh Token 무효화")
        try:
            payload = security.verify_token(refresh_token, token_type="refresh")
            
            jti = payload.get("jti")
            if not jti:
                logger.warning("로그아웃 실패 - 토큰에 JTI 클레임이 없습니다.")
                raise InvalidTokenException(detail="토큰에 JTI 정보가 없습니다.")
            
            revoked = await self.refresh_token_repo.revoke(jti)
            
            if not revoked:
                logger.info(f"무효화하려는 Refresh Token을 DB에서 찾지 못했습니다. JTI: {jti}")
                
            logger.info(f"로그아웃 성공 - Refresh Token 무효화 완료. JTI: {jti}")
        
        except (ExpiredTokenException, InvalidTokenException) as e:
            logger.warning(f"유효하지 않은 토큰으로 로그아웃 시도 : {e.detail}")
            return
        except Exception as e:
            logger.error(f"로그아웃 처리 중 예상치 못한 오류 발생: {str(e)}", exc_info=True)
            raise CredentialException("로그아웃 처리 중 오류가 발생했습니다.")
            