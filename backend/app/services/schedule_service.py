from loguru import logger
# from typing import List ->  Python 3.8 및 이전 버전의 방식

from fastapi import HTTPException, status
from app.repositories.schedule_repo import ScheduleRepository
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.models.schedule import Schedule
from app.models.user import User

class ScheduleService:
    def __init__(self, schedule_repo: ScheduleRepository):
        self.schedule_repo = schedule_repo
        
    async def create_schedule(self, schedule_data: ScheduleCreate, user: User) -> Schedule:
        """
        새로운 일정을 생성합니다.

        Args:
            schedule_data (ScheduleCreate): 생성할 일정 데이터
            user (User): 현재 인증된 소유자

        Returns:
            Schedule: Schedule ORM 모델
        """
        logger.debug(f"일정 생성 서비스 진입")
        logger.debug(f"{schedule_data.model_dump}")
        return await self.schedule_repo.create(schedule_data, user.id)
    
    async def get_schedule_by_id(self, schedule_id: int, user: User) -> Schedule:
        """
        ID로 특정 일정을 조회합니다.
        요청한 사용자가 해당 일정의 소유주인지 검증합니다.

        Args:
            schedule_id (int): 조회할 일정의 ID
            user (User): 현재 인증된 사용자

        Returns:
            Schedule: 조회된 Schedule ORM 객체
            
        Raises:
            HTTPException: 404 Not Found (일정이 없거나 소유주가 아닐 경우)
        """
        logger.debug(f"특정 일정을 조회 서비스 진입")
        logger.debug(f"schedule_id:{schedule_id}, user:{user}")
        
        schedule = await self.schedule_repo.get_schedule_by_id_and_user_id(
            schedule_id, user.id
        )
        
        if not schedule:
            # 일정이 존재하지 않거나, 다른 사람의 일정을 요청한 경우
            # 보안을 위해 동일한 "Not Found" 에러를 반환
            raise HTTPException(
                status_code = status.HTTP_404_NOT_FOUND,
                detail = "일정을 찾을 수 없습니다.",
            )
            
        return schedule
    
    async def get_schedule_by_month(self, user: User, year: int, month:int) -> list[Schedule]:
        """
        특정 사용자의 모든 일정을 페이지네이션을 하여 조회합니다.

        Args:
            user (User): 현재 인증된 사용자
            year (int): 조회할 연도
            month (int): 조회할 월

        Returns:
            List[Schedule]: Schedule ORM 객체의 리스트
        """
        logger.debug("모든 일정 조회 서비스 진입")
        logger.debug(f"user:{user.email}, year:{year}, month:{month}")
        
        return await self.schedule_repo.get_schedules_by_user_and_month(user.id, year, month)
    
    async def update_schedule(self, schedule_id: int, schedule_data: ScheduleUpdate, user: User) -> Schedule:
        """
        기존 일정을 수정합니다. 수정 전 소유권을 반드시 확인합니다.

        Args:
            schedule_id (int): 수정할 일정의 ID
            schedule_data (ScheduleUpdate): 수정할 데이터
            user (User): 현재 인증된 사용자

        Returns:
            Schedule: 수정된 Schedule ORM 객체
        """
        logger.debug("일정 수정 서비스 진입")
        logger.debug(f"schedule_id:{schedule_id}, schedule_data:{schedule_data.model_dump}, user:{user}")
        
        # 소유권 검증 및 일정 객체 확보 (실패 시 404)
        schedule = await self.get_schedule_by_id(schedule_id, user)
        
        # 소유권이 확인되면 Repository에 수정을 위임
        return await self.schedule_repo.update(
            schedule, schedule_data
        )
        
    async def delete_schedule(self, schedule_id: int, user: User) -> Schedule:
        """
        일정을 소프트 삭제합니다. 삭제 전 소유권을 반드시 확인합니다.

        Args:
            schedule_id (int): 삭제할 일정의 ID
            user (User): 현재 인증된 사용자

        Returns:
            Schedule: 소프트 삭제 처리된 Schedule ORM 객체
        """
        logger.debug(f"일정 삭제 서비스 진입")
        logger.debug(f"schedule_id:{schedule_id}, user:{user}")
        
        # 소유권 검증 및 일정 객체 확보 (실패 시 404)
        schedule = await self.get_schedule_by_id(schedule_id, user)
        
        # 소유권이 확인되면 Repository에 삭제를 위임
        return await self.schedule_repo.delete(schedule)