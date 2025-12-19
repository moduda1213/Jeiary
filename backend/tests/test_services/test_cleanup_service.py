# Phase 6.4: 데이터 클린업 서비스(TDD) 테스트
import pytest
from freezegun import freeze_time
from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.chat_repo import ChatRepository
from app.services.cleanup_service import CleanupService
from app.models.user import User
from app.models.schedule import Schedule



@pytest.mark.asyncio
async def test_delete_old_schedules(db_session: AsyncSession, test_user: User) -> None:
    """
    [시나리오]
    1. 오늘 삭제된 일정 (보존되어야 함)
    2. 15일 전 삭제된 일정 (삭제되어야 함) -> CleanupService가 2번만 정확히 삭제하는지 검증
    """
    # Repo 및 Service 초기화
    schedule_repo = ScheduleRepository(db_session)
    chat_repo = ChatRepository(db_session) # Dummy
    cleanup_service = CleanupService(schedule_repo, chat_repo)
    
    # 15일 전으로 시간을 동결하고 '오래전 삭제된 일정' 생성 ---> 삭제 대상
    with freeze_time(datetime.now() - timedelta(days=15)):
        now = datetime.now()
        
        old_schedule = Schedule(
            user_id = test_user.id,
            title = "오래전 삭제된 일정",
            date = now.date(),
            start_time = now.time(),
            end_time = (now + timedelta(hours=1)).time(),
            is_deleted = True,
            created_at = now,
            updated_at = now
        )
        db_session.add(old_schedule)
        await db_session.commit()
        await db_session.refresh(old_schedule)
        
    # 오늘 날짜로 '방금 삭제된 일정' 생성 ---> 삭제 x
    now = datetime.now()
    recent_schedule = Schedule(
        user_id = test_user.id,
        title = "방금 삭제된 일정",
        date = now.date(),
        start_time = now.time(),
        end_time = (now + timedelta(hours=1)).time(),
        is_deleted = True,
        created_at = datetime.now(),
        updated_at = datetime.now()
    )
    
    db_session.add(recent_schedule)
    await db_session.commit()
    await db_session.refresh(recent_schedule)
    
    # 클린업 실행 (14일 지난 데이터 삭제 요청)
    deleted_count = await cleanup_service.delete_expired_schedules(retention_days=14)
    
    # 검증
    assert deleted_count == 1, "정확히 1개의 오래된 일정이 삭제되어야 합니다."
    
    result_old = await db_session.execute(
        select(Schedule).where(Schedule.id == old_schedule.id)
    )
    assert result_old.scalar_one_or_none() is None
    
    result_recent = await db_session.execute(
        select(Schedule).where(Schedule.id == recent_schedule.id)
    )
    assert result_recent.scalar_one_or_none is not None
    