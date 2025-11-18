from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    
class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="최소 8자 이상") # ...(ellipsis) : require=True
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('비밀번호에 영문자를 포함해야 합니다.')
        if not re.search(r'\d', v):
            raise ValueError('비밀번호에 숫자를 포함해야 합니다.')
        if not re.search(r'[!@#$%^&*]', v):
            raise ValueError('비밀번호에 특수문자를 포함해야 합니다.')
        return v

class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    model_config = ConfigDict(
        from_attributes=True
    )