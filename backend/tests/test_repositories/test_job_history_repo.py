import pytest
from datetime import datetime, timedelta
from app.repositories.job_history_repo import JobHistoryRepository
from app.models.job_history import JobHistory

@pytest.mark.asyncio
async def test_create_log(db_session):
    repo = JobHistoryRepository(db_session)
    
    # 로그 생성
    job_name = "test_job"
    status = "SUCCESS"
    details = "Test details"
    
    log = await repo.create_log(job_name, status, details)
    
    assert log.id is not None
    assert log.job_name == job_name
    assert log.status == status
    assert log.details == details
    assert log.created_at is not None

@pytest.mark.asyncio
async def test_exists_successful_job_today(db_session):
    repo = JobHistoryRepository(db_session)
    job_name = "daily_cleanup"
    
    # 1. 아무 기록 없을 때 -> False
    assert await repo.exists_successful_job_today(job_name) is False
    
    # 2. 실패 기록만 있을 때 -> False
    await repo.create_log(job_name, "FAILED", "Error")
    assert await repo.exists_successful_job_today(job_name) is False
    
    # 3. 어제 성공 기록 있을 때 -> False
    # (어제 날짜 데이터를 강제로 넣어야 하므로 모델 직접 생성)
    yesterday = datetime.now() - timedelta(days=1)
    old_log = JobHistory(
        job_name=job_name,
        status="SUCCESS",
        created_at=yesterday
    )
    db_session.add(old_log)
    await db_session.commit()
    assert await repo.exists_successful_job_today(job_name) is False
    # 4. 오늘 성공 기록 있을 때 -> True
    await repo.create_log(job_name, "SUCCESS", "Done")
    assert await repo.exists_successful_job_today(job_name) is True