# Step 6.5.2: 모닝 브리핑 서비스 테스트
import pytest
from unittest.mock import AsyncMock
from datetime import time

from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.notification_repo import NotificationRepository
from app.services.briefing_service import BriefingService
from app.models.schedule import Schedule

@pytest.fixture
def mock_schedule_repo():
    return AsyncMock(spec=ScheduleRepository)

@pytest.fixture
def mock_notification_repo():
    return AsyncMock(spec=NotificationRepository)

@pytest.mark.asyncio
async def test_create_briefing_with_schedules(
    mock_schedule_repo,
    mock_notification_repo,
    mock_ai_service,
    test_user
):
    """
    [시나리오]

    1. 오늘 일정이 2개가 있다.
    2. AI가 이를 요약한다. Mock
    3. Notification 테이블에 요약 내용이 저장된다.
    """
    
    # Serivce 초기화
    bridfing_service = BriefingService(
        schedule_repo = mock_schedule_repo,
        notification_repo = mock_notification_repo,
        ai_service = mock_ai_service
    )
    
    # Mock 동작 설정
    mock_schedule_repo.get_schedules_by_user_and_date.return_value = [
        Schedule(title="Meeting", start_time=time(10, 0), end_time=time(11, 0)),
        Schedule(title="Lunch", start_time=time(12, 0), end_time=time(13, 0))
    ]
    
    mock_ai_service.generate_briefing.return_value = "오전 미팅과 점심 약속이 있습니다."
    
    # 브리핑 생성
    await bridfing_service.create_daily_briefing(user_id=test_user.id)
    
    # 검증
    mock_schedule_repo.get_schedules_by_user_and_date.assert_called_once()
    
    mock_ai_service.generate_briefing.assert_called_once()
    
    mock_notification_repo.create.assert_called_once()
    
    call_args = mock_notification_repo.create.call_args
    assert call_args.kwargs['content'] == "오전 미팅과 점심 약속이 있습니다."
    assert call_args.kwargs['type'] == "morning_briefing"