from datetime import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship

from app.db.base import Base

class RefreshToken(Base):
    """
    Refresh Token 저장을 위한 SQLAlchemy ORM 모델
    """
    __tablename__= "refresh_tokens"
    
    id: int = Column(Integer, primary_key=True, index=True)
    
    # 어느 사용자의 토큰인지 식별
    user_id: int = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # JWT의 고유 식별자(jti)를 저장하여 특정 토큰을 무효화
    token_id: str = Column(String(255), unique=True, nullable=False, index=True)
    
    # 토큰이 무효화되었는지 여부 (로그아웃 처리)
    is_revoked: bool = Column(Boolean, default=False, nullable=False)
    
    # 토큰 만료 시간
    expires_at: datetime = Column(DateTime(timezone=True), nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    user = relationship("User", back_populates="refresh_tokens")
    
    def __repr__(self) -> str:
        return f"<RefreshToken(id={self.id}, user_id={self.user_id}, token_id='{self.token_id[:10]}...')>"