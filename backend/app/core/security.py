
from passlib.context import CryptContext
from datetime import datetime, timezone, timedelta
from jose import jwt
from jose.exceptions import JWTError, ExpiredSignatureError, JWTClaimsError
from uuid import uuid4

from app.config import settings
from app.core.exceptions import (
    CredentialException,
    InvalidTokenException,
    ExpiredTokenException,
)

from fastapi.security import OAuth2PasswordBearer
# /api/v1/auth/login URL에 저장된 Bearer tokenText.... 
# Bearer tokenText.... 값에 Bearer를 지운 토큰값만 oauth2_scheme에 저장
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login") 

import logging
logger = logging.getLogger(__name__)
# ==============================================================================
# Password Hashing
# ==============================================================================

# `bcrypt`를 사용하는 CryptContext 설정
from passlib.context import CryptContext
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=settings.BCRYPT_ROUNDS)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    입력된 비밀번호와 해시된 비밀번호를 비교합니다.
    
    Args:
        plain_password: 사용자가 입력한 비밀번호 (평문)
        hashed_password: 데이터베이스에 저장된 해시된 비밀번호
        
    Return:
        비밀번호가 일치하면 True, 그렇지 않으면 False
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    비밀번호를 해시 처리합니다.
    Args:
        password (str): 해시할 비밀번호 (평문)

    Return:
        str: 해시된 비밀번호 문자열
    """
    return pwd_context.hash(password)

# ==============================================================================
# Token Creation & Verification
# ==============================================================================

def create_access_token(data: dict) -> str:
    """
    Access Token을 생성합니다.

    Args:
        data (dict): 토큰에 포함될 데이터 (e.g., {'sub' : 'user_email@example.com'})

    Return:
        str: 생성된 JWT Access Token 문자열
    """
    to_encode= data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({
        "exp":expire,
        "iat": datetime.now(timezone.utc),
        "type": "access"
    })
    
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    
def create_refresh_token(data: dict) -> str:
    """
    Refresh Token을 생성합니다.

    Args:
        data (dict): 토큰에 포함될 데이터 

    Return:
        str: 생성된 JWT Refresh Token 문자열
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp":expire,
        "iat": datetime.now(timezone.utc),
        "type": "refresh",
        "jti": str(uuid4()) # 고유 식별자(JTI) 추가
    })
    return jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM 
    )

def verify_token(token: str, token_type: str = "access") -> dict:
    """
    토큰을 검증하고 페이로드를 반환합니다

    Args:
        token (str): 검증할 jwt 토큰
        token_type (str): 예상되는 토큰 타입 ("access" 또는 "refresh")
        
    Return:
        dict: 토큰의 페이로드(payload)
        
    Raises:
        ExpiredTokenException: 토큰이 만료되었을 때
        InvalidTokenException: 토큰 형식이 잘못되었을 때
        CredentialException: 자격 증명 오류 시
    """
    logger.debug(f"토큰 검즘 시작 : {token} [Type: {token_type}]")
    
    try:
        payload= jwt.decode(
            token, 
            settings.JWT_SECRET_KEY, 
            algorithms=[settings.JWT_ALGORITHM]
        )
        
        payload_token_type = payload.get("type")
        if payload_token_type != token_type:
            logger.warning(f"잘못된 토큰 타입 - 기대: {token_type}, 실제: {payload_token_type}")
            raise InvalidTokenException(f"잘못된 토큰 타입입니다.: Expected: {token_type}")
        
        return payload
    
    except ExpiredSignatureError:
        raise ExpiredTokenException()
    
    except JWTClaimsError as e:
        logger.warning(f"유효하지 않은 토큰 클레임 - {str(e)}")
        raise InvalidTokenException("토큰의 클레임(claims)이 유효하지 않습니다.")
    
    except JWTError as e:
        logger.warning(f"JWT 검증 실패 - {type(e).__name__}: {str(e)}")
        raise InvalidTokenException(f"토큰 검증에 실패했습니다.: {str(e)}")
    
    except Exception as e:
        logger.error(f"예상치 못한 오류", exc_info=True)
        raise CredentialException(f"토큰 처리 중 오류 발생: {str(e)}")
    