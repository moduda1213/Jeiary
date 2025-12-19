import pytest
from unittest.mock import patch, AsyncMock, MagicMock
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, time

from app.core.scheduler import run_cleanup_job, run_morning_briefing_job
from app.models.schedule import Schedule
from app.models.user import User
from app.models.notification import Notification

@pytest.mark.asyncio
async def test_run_cleanup_job_intergration(db_session: AsyncSession, test_user: User) -> None:
    """
    배치 작업(Clean up) 통합 테스트
    - 실제로 만료된 일정을 DB에 넣고 run_cleanup_job을 호출하여 삭제되는지 확인
    """
    # 만료된 일정 데이터 준비
    expired_date = datetime.now() - timedelta(days=15)
    
    schedule = Schedule(
        user_id = test_user.id,
        title = "Expired Schedule",
        date = expired_date.date(),
        start_time = expired_date.time(),
        end_time = (expired_date + timedelta(hours=1)).time(),
        is_deleted = True,
        deleted_at = expired_date,
        created_at = expired_date,
        updated_at = expired_date,
    )
    db_session.add(schedule)
    await db_session.commit()
    await db_session.refresh(schedule)
    schedule_id = schedule.id
    
    mock_session_factory = MagicMock()
    mock_session_factory.return_value = AsyncMock()
    mock_session_factory.return_value.__aenter__.return_value = db_session  # "팩토리를 호출해서(`AsyncSessionFactory()`) 나온 객체가, `async with` 문으로 들어갈 때(`__aenter__`), 최종적으로 내 테스트용 `db_session`을 뱉어내게 해라"
    
    # job 실행
    with patch("app.core.scheduler.AsyncSessionFactory", mock_session_factory):
        await run_cleanup_job()
        
    # 검증: 해당 일정이 DB에서 영구 삭제되었는지 확인
    result = await db_session.execute(select(Schedule).where(Schedule.id == schedule_id))
    assert result.scalars().first() is None
    
@pytest.mark.asyncio
async def test_run_morning_briefing_job_intergration(db_session: AsyncSession, test_user: User) -> None:
    """
    배치 작업 통합 테스트
    - AI 서비스만 Mocking하고, 실제 DB 흐름을 타서 알림이 생성되는지 확인
    """
    today = datetime.now()
    schedule = Schedule(
        user_id=test_user.id,
        title="Today Meeting",
        content="Important",
        date=today.date(),
        start_time=today.time(),
        end_time=(today + timedelta(hours=1)).time(),
        is_deleted=False
    )
    db_session.add(schedule)
    await db_session.commit()
    
    
    mock_session_factory = MagicMock()
    mock_session_factory.return_value = AsyncMock()
    mock_session_factory.return_value.__aenter__.return_value = db_session
    
    with patch("app.core.scheduler.AsyncSessionFactory", mock_session_factory), \
        patch("app.core.scheduler.AIService") as mock_ai_service_cls:
            
        mock_ai_instance = mock_ai_service_cls.return_value
        mock_ai_instance.generate_briefing = AsyncMock(return_value = "Intergration Test Briefing Content")
        
        await run_morning_briefing_job()
        
    result = await db_session.execute(select(Notification).where(Notification.user_id == test_user.id))
    notification = result.scalars().first()
    
    assert notification is not None
    assert notification.type == "morning_briefing"
    assert notification.content == "Intergration Test Briefing Content"