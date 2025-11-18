from datetime import date
from loguru import logger
from fastapi import APIRouter, status

from app.dependencies import CurrentUserDep, ScheuduleServiceDep
from app.services.schedule_service import ScheduleService
from app.schemas.schedule import ScheduleResponse, ScheduleCreate, ScheduleUpdate
from app.models.user import User

router = APIRouter(
    prefix = "/schedules",
    tags = ["schedules"],
)

@router.post(
    "/",
    response_model=ScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="새로운 일정 생성"
)
async def create_schedule(
    schedule_data: ScheduleCreate,
    user: CurrentUserDep,
    service: ScheuduleServiceDep,
) -> ScheduleResponse:
    """새로운 일정을 생성"""
    logger.info("일정 생성 엔드포인트 진입")
    
    return await service.create_schedule(schedule_data, user)

@router.get(
    "/",
    response_model=list[ScheduleResponse],
    summary="사용자 선택한 날짜 표기에 따라 일정 조회"
)
async def get_schedules(
    user: CurrentUserDep,
    service: ScheuduleServiceDep,
    year: int,
    month: int
) -> list[ScheduleResponse]:
    """현재 사용자의 모든 일정을 조회"""
    logger.info(f"월별 일정 조회 엔드포인트 진입 -->  Year:{year}, Month: {month}")
    
    return await service.get_schedule_by_month(user, year, month)

@router.get(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="특정 일정 상세 조회"
)
async def get_schedule(
    schedule_id: int,
    user: CurrentUserDep,
    service: ScheuduleServiceDep,
) -> ScheduleResponse:
    """ID로 특정 일정을 조회"""
    logger.info("특정 일정 조회 엔드포인트 진입")
    
    return await service.get_schedule_by_id(schedule_id, user)

@router.put(
    "/{schedule_id}",
    response_model=ScheduleResponse,
    summary="일정 수정"
)
async def update_schedule(
    schedule_id: int,
    schedule_data: ScheduleUpdate,
    user: CurrentUserDep,
    service: ScheuduleServiceDep,
) -> ScheduleResponse:
    """ID로 특정 일정을 수정"""
    logger.info("일정 수정 엔드포인트 진입")
    
    return await service.update_schedule(schedule_id, schedule_data, user)

@router.delete(
    "/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="일정 삭제"
)
async def delete_schedule(
    schedule_id: int,
    user: CurrentUserDep,
    service: ScheuduleServiceDep,
) -> None:
    """ID로 특정 일정을 삭제합니다."""
    logger.info("일정 삭제 엔드포인트 진입")
    
    success = await service.delete_schedule(schedule_id, user)
    return None