from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.base import Base

class Notification(Base):
    # 브리핑 결과나 시스템 알림을 저장할 모델
    
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True, comment="알림 ID")
    type = Column(String(50), nullable=False, comment="알림 유형 (예: 'morning_briefing', 'alert')")
    content = Column(Text, nullable=False, comment="알림 내용") 
    is_read = Column(Boolean, default=False, comment="읽음 여부")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="생성일시")
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    user = relationship("User", back_populates="notifications")