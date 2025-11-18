from app.repositories.base import BaseRepository
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, extract


class ScheduleRepository(BaseRepository[Schedule]):
    def __init__(self, session: AsyncSession):
        super().__init__(Schedule, session)
        
    async def create(self, schedule_data: ScheduleCreate, user_id: int) -> Schedule:
        """새로운 일정을 생성하고 DB에 추가합니다."""
        schedule = Schedule(
            **schedule_data.model_dump(),
            user_id=user_id
        )
        self.session.add(schedule)
        await self.session.flush()
        await self.session.refresh(schedule)
        return schedule
    
    async def get_schedule_by_id_and_user_id(self, schedule_id: int, user_id: int) -> Schedule | None:
        """ID와 사용자 ID로 특정 일정을 조회합니다."""
        stmt = select(self.model).where(
            self.model.id == schedule_id,
            self.model.user_id == user_id,
            self.model.is_deleted == False
        )
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()
    
    async def get_schedules_by_user_and_month(self, user_id: int, year: int = 0, month: int = 100) -> list[Schedule]:
        """특정 사용자의 특정 월에 해당하는 모든 일정을 조회합니다. (소프트 삭제 제외)"""
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.is_deleted == False,
            extract("year", self.model.date) == year,
            extract("month", self.model.date) == month,
        ).order_by(self.model.date.asc(), self.model.start_time.asc())
        
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def update(self, schedule: Schedule, update_data: ScheduleUpdate) -> Schedule:
        """특정 일정을 수정합니다."""
        update_dict = update_data.model_dump(exclude_unset=True)
        
        for key, value in update_dict.items():
            setattr(schedule, key, value)
            
        self.session.add(schedule)
        await self.session.flush()
        await self.session.refresh(schedule)
        return schedule
    
    async def delete(self, schedule: Schedule) -> Schedule:
        """특정 일정을 소프트 삭제 처리합니다."""
        schedule.soft_delete()
        self.session.add(schedule)
        await self.session.flush()
        await self.session.refresh(schedule)
        return schedule
    