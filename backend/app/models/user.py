from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base

class User(Base):
    """
    사용자 정보를 저장하는 ORM 모델
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, comment="사용자 고유 ID")
    email = Column(String(255), unique=True, index=True, nullable=False, comment="이메일 주소 (로그인 ID)")
    password_hash = Column(String(255), nullable=False, comment="해시된 비밀번호")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False,comment="생성일시")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False,comment="수정일시")
    
    # Relationships 
    # back_populates : 양방향 관계 설정
    # cascade : 사용자가 삭제될 때 관련된 일정도 함께 삭제(데이터 무결성)
    schedules = relationship("Schedule", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    chats = relationship("ChatHistory", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}')>"