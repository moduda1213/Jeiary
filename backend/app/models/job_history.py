from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from app.db.base import Base

class JobHistory(Base):
    """배치 작업 실행 이력을 저장하는 모델"""
    __tablename__ = "job_histories"
    
    # id SERIAL PRIMARY KEY,
    # job_name VARCHAR(50) NOT NULL, -- 'morning_briefing', 'daily_cleanup'
    # status VARCHAR(20) NOT NULL, -- 'SUCCESS', 'FAILED'
    # details TEXT, -- 처리 건수, 에러 메시지 등
    # created_at TIMESTAMP DEFAULT NOW(),
    
    id = Column(Integer, primary_key=True, index=True)
    job_name = Column(String(50), nullable=False, index=True, comment="작업명 (예: morning_briefing)")
    status = Column(String(20), nullable=False, comment="상태 (SUCCESS, FAILED)")
    details = Column(Text, nullable=True, comment="상세 결과 또는 에러 메세지")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<JobHistory(job={self.job_name}, status={self.status}, date={self.created_at})"