from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean, Date, Time
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.db.base import Base
from datetime import datetime, timezone

class Schedule(Base):
    """
    사용자 일정을 저장하는 ORM 모델
    """
    __tablename__ = "schedules"
    
    id = Column(Integer, primary_key=True, index=True, comment="일정 고유 ID")
    title = Column(String(255), nullable=False, index=True, comment="일정 제목")
    content = Column(Text, nullable=True, comment="일정 상세 내용") 
    
    date = Column(Date, nullable=False, index=True, comment="일정 날짜")
    
    start_time = Column(Time, nullable=False, index=True, comment="일정 시작 시간")
    end_time = Column(Time, nullable=False, comment="일정 종료 시간")
    
    is_deleted = Column(Boolean, default=False, nullable=False, index=True, comment="삭제 여부")
    deleted_at = Column(DateTime(timezone=True), nullable=True, comment="삭제일시")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="생성일시")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, comment="수정일시")
    
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True, comment="일정 소유자 ID")
    
    user = relationship("User", back_populates="schedules")
    
    def __repr__(self) -> str:
        return f"<Schedule(id={self.id}, title='{self.title}', user_id={self.user_id})>"
    
    def soft_delete(self):
        """소프트 삭제 헬퍼 메서드"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)
        
    def soft_restore(self):
        """소프트 삭제된 일정 복구 헬퍼 메서드"""
        self.is_deleted = False
        self.deleted_at = None
        
    def UTCtoKST(self) -> dict:
        """UTC시간 -> 대한민국 시간"""
        from zoneinfo import ZoneInfo
        created_at_utc = self.created_at
        created_at_kst = created_at_utc.astimezone(ZoneInfo("Asia/Seoul"))
        updated_at_utc = self.updated_at
        updated_at_kst = updated_at_utc.astimezone(ZoneInfo("Asia/Seoul"))
        return { "created_at_utc": self.created_at, "created_at_kst": created_at_kst, "updated_at_utc": self.updated_at, "updated_at_kst": updated_at_kst }
        
# 토막상식

## created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, comment="생성일시") 
## server_default=func.now():  DB 서버 시간은 UTC -> 한국시간 - 9시간으로 저장 될 것임
## DB에 UTC로 저장하고, 조회/표시할 때 한국 시간으로 변환하는 것이 베스트 프랙티스!!!

## 이유
### 1. 글로벌 서비스 확장 시 유리
### 2. 타임존 변환 로직이 명확
### 3. 서머타임 등의 이슈 방지