import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import time

from app.repositories.schedule_repo import ScheduleRepository
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.models.user import User  # test_user fixture를 위해 필요


# conftest.py의 test_user fixture를 사용하기 위해 임포트 (User 모델이 필요)
# 이 라인은 실제 코드에선 필요 없지만, 린터 에러 방지를 위해 명시적으로 둘 수 있습니다.
from tests.conftest import test_user

@pytest.mark.asyncio
async def test_create_schedule(db_session: AsyncSession, test_user: User):
    """ScheduleRepository.create가 일정을 성공적으로 생성하는지 테스트"""
    repo = ScheduleRepository(db_session)
    schedule_data = ScheduleCreate(title="Test Schedule", date="2025-10-31", start_time=time(10, 30), end_time=time(11,30))

    created_schedule = await repo.create(schedule_data, user_id=test_user.id)
    
    assert created_schedule is not None
    assert created_schedule.id is not None
    assert created_schedule.title == schedule_data.title
    assert created_schedule.user_id == test_user.id

@pytest.mark.asyncio
async def test_get_schedule_by_id_and_user_id(db_session: AsyncSession, test_user: User):
    """ID와 사용자 ID로 일정을 정확히 조회하는지, 소유권이 없으면 조회되지 않는지 테스트"""
    repo = ScheduleRepository(db_session)
    schedule_data = ScheduleCreate(
        title="Owned Schedule",
        date="2025-11-01",
        start_time=time(9, 0), # start_time 추가
        end_time=time(10, 0)
    )

    created_schedule = await repo.create(schedule_data, user_id=test_user.id)

    # 올바른 소유자로 조회
    found_schedule = await repo.get_schedule_by_id_and_user_id(created_schedule.id, test_user.id)
    assert found_schedule is not None
    assert found_schedule.id == created_schedule.id

    # 다른 사용자 ID로 조회
    not_found_schedule = await repo.get_schedule_by_id_and_user_id(created_schedule.id, 9999) # 존재하지 않는 user_id
    assert not_found_schedule is None

@pytest.mark.asyncio
async def test_get_schedule_excludes_soft_deleted(db_session: AsyncSession, test_user: User):
    """소프트 삭제된 일정은 조회되지 않는지 테스트"""
    repo = ScheduleRepository(db_session)
    schedule_data = ScheduleCreate(
        title="To Be Deleted",
        date="2025-11-02",
        start_time=time(11, 0), # start_time 추가
        end_time=time(12, 0)
    )
    created_schedule = await repo.create(schedule_data, user_id=test_user.id)

    # 삭제 실행
    await repo.delete(created_schedule)

    # 삭제된 일정 조회 시도
    found_schedule = await repo.get_schedule_by_id_and_user_id(created_schedule.id, test_user.id)
    assert found_schedule is None

@pytest.mark.asyncio
async def test_get_schedules_by_user_and_month(db_session: AsyncSession, test_user: User):
    """특정 사용자의 특정 월 일정을 조회하는지 테스트"""
    repo = ScheduleRepository(db_session)

    # 2025년 12월 일정 2개 생성
    await repo.create(ScheduleCreate(title="Dec 1", date="2025-12-01", start_time=time(9,0), end_time=time(10,0)), user_id=test_user.id)
    await repo.create(ScheduleCreate(title="Dec 2", date="2025-12-15", start_time=time(10,0), end_time=time(11,0)), user_id=test_user.id)
    
    # 2025년 11월 일정 1개 생성 (조회되지 않아야 함)
    await repo.create(ScheduleCreate(title="Nov 1", date="2025-11-01", start_time=time(9,0), end_time=time(10,0)), user_id=test_user.id)
    
    # 2025년 12월 조회
    schedules = await repo.get_schedules_by_user_and_month(test_user.id, year=2025, month=12)
    
    assert len(schedules) == 2
    assert "Dec" in schedules[0].title
    assert "Dec" in schedules[1].title

@pytest.mark.asyncio
async def test_update_schedule(db_session: AsyncSession, test_user: User):
    """일정 정보가 올바르게 수정되는지 테스트"""
    repo = ScheduleRepository(db_session)
    schedule_data = ScheduleCreate(
        title="Original Title",
        date="2025-11-03",
        start_time=time(13, 0), # start_time 추가
        end_time=time(14, 0),
    )
    created_schedule = await repo.create(schedule_data, user_id=test_user.id)

    update_data = ScheduleUpdate(title="Updated Title")
    updated_schedule = await repo.update(created_schedule, update_data)

    assert updated_schedule.title == "Updated Title"
    assert updated_schedule.id == created_schedule.id

@pytest.mark.asyncio
async def test_delete_schedule(db_session: AsyncSession, test_user: User):
    """일정이 올바르게 소프트 삭제되는지 테스트"""
    repo = ScheduleRepository(db_session)
    schedule_data = ScheduleCreate(
        title="Delete Me",
        date="2025-11-04",
        start_time=time(14, 0), # start_time 추가
        end_time=time(15,0),
    )
    created_schedule = await repo.create(schedule_data, user_id=test_user.id)

    deleted_schedule = await repo.delete(created_schedule)

    assert deleted_schedule.is_deleted is True
    assert deleted_schedule.deleted_at is not None