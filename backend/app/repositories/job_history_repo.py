'''
    로그 저장: 배치 실행 결과를 DB - INSERT
    중복 체크: "오늘 이 작업을 성공했는가?" - SELECT
'''
from sqlalchemy import select, and_, extract
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date

from app.repositories.base import BaseRepository
from app.models.job_history import JobHistory

class JobHistoryRepository(BaseRepository[JobHistory]):
    def __init__(self, session: AsyncSession):
        super().__init__(JobHistory, session)
        
    async def create_log(self, job_name: str, status: str, details: str = None) -> JobHistory:
        """배치 실행 이력 저장"""
        history = JobHistory(
            job_name = job_name,
            status = status,
            details = details
        )
        self.session.add(history)
        await self.session.flush()
        return history
    
    async def exists_successful_job_today(self, job_name: str) -> bool:
        """오늘 날짜에 해당 작업이 'SUCCESS'로 끝난 기록이 있는지 확인"""
        today = date.today()
        print(f"exists_successful_job_today - today: {today}")
        stmt = select(self.model).where(
            and_(
                self.model.job_name == job_name,
                self.model.status == "SUCCESS",
                extract('year', self.model.created_at) == today.year,
                extract('month', self.model.created_at) == today.month,
                extract('day', self.model.created_at) == today.day
            )
        )
        result = await self.session.execute(stmt)
        return result.scalars().first() is not None