import pytest
from datetime import datetime, timedelta, timezone
from jose import jwt
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    verify_token
)

from app.core.exceptions import ExpiredTokenException, InvalidTokenException
from app.config import settings

def test_password_hashing_and_verification():
    """
    비밀번호 해싱 및 검증 기능 테스트
    - get_password_hash로 생성된 해시가 verify_password로 검증되어야 한다.
    - 다른 비밀번호와는 검증에 실패해야 한다.
    """
    password = "testpassword123@"
    hashed_password = get_password_hash(password)
    
    # 해시된 비밀번호는 원본과 달라야 함
    assert password != hashed_password
    
    # 올바른 비밀번호로 검증 성공
    assert verify_password(password, hashed_password) is True
    
    # 잘못된 비밀번호로 검증 실패
    assert verify_password("wrongpassword123@", hashed_password) is False
    
def test_create_and_verify_access_token():
    """
    Access Token 생성 및 검증 기능 테스트
    - 생성된 토큰은 verify_token으로 페이로드를 올바르게 반환
    - 페이로드에는 'sub'와 'exp' 클레임이 포함되어야 한다.
    """
    user_email = "test@example"
    data = {"sub": user_email}
    
    token = create_access_token(data)
    payload = verify_token(token)
    
    assert payload["sub"] == user_email
    assert "exp" in payload

    # 만료 시간이 현재 시간보다 미래인지 확인
    exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    assert exp_time > datetime.now(timezone.utc)    
    
def test_create_and_verify_refresh_token():
    """
    Refresh Token 생성 및 검증 기능 테스트
    - 생성된 토큰은 'sub', 'exp', 'jti' 클레임을 포함해야 한다.
    """
    user_email= "test@example.com"
    data= {"sub": user_email}
    
    token = create_refresh_token(data)
    payload = verify_token(token, "refresh")
    
    assert payload["sub"] == user_email
    assert "exp" in payload
    assert "jti" in payload

def test_verify_expired_token():
    """
    만료된 토큰 검증 시 ExpiredTokenException 발생 테스트
    """
    user_email= "test@example.com"
    
    # 만료 시간을 과거로 설정하여 토큰 생성
    
    expire = datetime.now(timezone.utc) - timedelta(minutes=1)
    to_encode= {"sub": user_email, "exp": expire}
    
    expired_token= jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm= settings.JWT_ALGORITHM
    )
    
    with pytest.raises(ExpiredTokenException):
        verify_token(expired_token)
        
def test_verify_invalid_token_signature():
    """
    잘못된 시그니처를 가진 토큰 검증 시 InvalidTokenException 발생 테스트
    """
    user_email= "test@example.com"
    data= {"sub": user_email}
    
    # 다른 비밀 키로 토큰 생성
    invalid_secret_key= "this-is-a-wrong-secret-key"
    invalid_token= jwt.encode(
        data, invalid_secret_key, algorithm= settings.JWT_ALGORITHM
    )
    with pytest.raises(InvalidTokenException):
        verify_token(invalid_token)

def test_verify_invalid_token_format():
    """
    잘못된 형식의 토큰 검증 시 InvalidTokenException 발생 테스트
    """
    invalid_token = "this.is.not.a.valid.token"
    
    with pytest.raises(InvalidTokenException):
        verify_token(invalid_token)