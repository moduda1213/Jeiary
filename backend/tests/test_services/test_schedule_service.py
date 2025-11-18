import pytest
from unittest.mock import AsyncMock
from fastapi import HTTPException

from app.services.schedule_service import ScheduleService
from app.models.user import User
from app.models.schedule import Schedule
from app.schemas.schedule import ScheduleUpdate, ScheduleCreate

@pytest.fixture
def mock_schedule_repo():
    """가짜 ScheduleRepository 객체 생성"""
    return AsyncMock()

@pytest.fixture
def schedule_service(mock_schedule_repo):
    """테스트할 ScheduleService 인스턴스 생성"""
    return ScheduleService(mock_schedule_repo)

@pytest.fixture
def test_user():
    """테스트용 User 모델 객체"""
    return User(id=1, email="test@example.com")

@pytest.fixture
def test_schedule(test_user):
    """테스트용 Schedule 모델 객체"""
    return Schedule(id=1, title="Test Schedule", user_id=test_user.id)

@pytest.mark.asyncio
async def test_get_schedule_by_id_success(schedule_service, mock_schedule_repo, test_user, test_schedule):
    """성공: 소유주가 자신의 일정을 조회하는 경우"""
    mock_schedule_repo.get_by_id_and_user_id.return_value = test_schedule
    
    result = await schedule_service.get_schedule_by_id(schedule_id=1, user=test_user)
    
    # assert
    mock_schedule_repo.get_by_id_and_user_id.assert_called_once_with(1, test_user.id)
    assert result == test_schedule
    
@pytest.mark.asyncio
async def test_get_schedule_by_id_not_found(schedule_service, mock_schedule_repo, test_user):
    """실패: 다른 사람의 일정을 조회하거나 일정이 없는 경우 (404 예외 발생)"""
    mock_schedule_repo.get_by_id_and_user_id.return_value = None
    
    # get_schedule_by_id에서 HTTPException에러가 발생하길 기대하고 있어
    # 발생하면 exc_info 에 저장
    # 발생하지 않는다면 테스트 실패 발생
    with pytest.raises(HTTPException) as exc_info:
        await schedule_service.get_schedule_by_id(schedule_id=99, user=test_user)
        
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "일정을 찾을 수 없습니다."
    
@pytest.mark.asyncio
async def test_update_schedule_success(schedule_service, mock_schedule_repo, test_user, test_schedule):
    """성공: 소유주가 자신의 일정을 수정하는 경우"""
    update_data = ScheduleUpdate(title="Updated Title")
    mock_schedule_repo.get_by_id_and_user_id.return_value = test_schedule
    mock_schedule_repo.update.return_value = test_schedule
    
    await schedule_service.update_schedule(schedule_id=1, schedule_data=update_data, user=test_user)
    
    # assert
    mock_schedule_repo.get_by_id_and_user_id.assert_called_once_with(1, test_user.id)
    mock_schedule_repo.update.assert_called_once_with(test_schedule, update_data)
    
@pytest.mark.asyncio
async def test_update_schedule_not_owner(schedule_service, mock_schedule_repo, test_user):
    """실패: 다른 사람의 일정을 수정하려는 경우"""
    mock_schedule_repo.get_by_id_and_user_id.return_value = None
    update_data = ScheduleUpdate(title="Updated Title")
    
    with pytest.raises(HTTPException) as exc_info:
        await schedule_service.update_schedule(schedule_id=1, schedule_data=update_data, user=test_user)
        
    assert exc_info.value.status_code == 404
    mock_schedule_repo.update.asset_not_called()
    
@pytest.mark.asyncio
async def test_create_schedule(mocker):
    """
    ScheduleService.create_schedule 단위 테스트
    - Repository의 create 메서드를 올바른 인자와 함께 호출하는지 검증
    """
    mock_repo = mocker.patch(
        "app.repositories.schedule_repo.ScheduleRepository",
        spec = True # 원본 클래스의 명세를 따르도록 설정
    )
    mock_repo.create = AsyncMock() # create 메서드를 비동기 Mock으로 설정
    
    service = ScheduleService(schedule_repo=mock_repo)
    schedule_data = ScheduleCreate(title="단위 테스트", date="2025-11-13")
    user = User(id=1, email='test@example.com')
    
    await service.create_schedule(schedule_data, user)
    mock_repo.create.assert_called_once_with(schedule_data, user.id)

async def test_get_schedule_by_id_found(mocker):
    """
    ScheduleService.get_schedule_by_id 단위 테스트 (성공 케이스)
    - Repository가 스케줄을 반환했을 때, 해당 스케줄을 그대로 반환하는지 검증
    """
    # GIVEN: Repository가 특정 Schedule 객체를 반환하도록 설정
    mock_repo = mocker.patch("app.repositories.schedule_repo.ScheduleRepository", spec=True)

    expected_schedule = Schedule(id=1, user_id=1, title="테스트")
    mock_repo.get_by_id_and_user_id = AsyncMock(return_value=expected_schedule)

    service = ScheduleService(schedule_repo=mock_repo)
    user = User(id=1, email="test@example.com")

    # WHEN: 서비스 메서드 호출
    schedule = await service.get_schedule_by_id(schedule_id=1, user=user)

    # THEN: Repository로부터 받은 객체를 그대로 반환하는지 확인
    assert schedule == expected_schedule
    mock_repo.get_by_id_and_user_id.assert_called_once_with(1, user.id)


async def test_get_schedule_by_id_not_found(mocker):
    """
    ScheduleService.get_schedule_by_id 단위 테스트 (실패 케이스)
    - Repository가 None을 반환했을 때, HTTPException(404)을 발생시키는지 검증
    """
    # GIVEN: Repository가 None을 반환하도록 설정
    mock_repo = mocker.patch("app.repositories.schedule_repo.ScheduleRepository", spec=True)
    mock_repo.get_by_id_and_user_id = AsyncMock(return_value=None)

    service = ScheduleService(schedule_repo=mock_repo)
    user = User(id=1, email="test@example.com")

    # WHEN/THEN: HTTPException이 발생하는지 확인
    with pytest.raises(HTTPException) as exc_info:
        await service.get_schedule_by_id(schedule_id=1, user=user)

    assert exc_info.value.status_code == 404