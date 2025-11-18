from pydantic import BaseModel, EmailStr, Field

class AuthLogin(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    
class RefreshTokenRequest(BaseModel):
    refresh_token: str
    
class TokenPayload(BaseModel):
    """
    JWT 토큰의 페이로드(내용)를 검증하기 위한 스키마입니다.
    'sub' 클레임에 사용자 이메일이 포함되어야 합니다.
    """
    sub: EmailStr = Field(...)
    type: str = Field(...)