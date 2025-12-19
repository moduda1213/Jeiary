from loguru import logger
from datetime import date

from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.notification_repo import NotificationRepository
from app.services.ai_service import AIService

class BriefingService:
    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        notification_repo: NotificationRepository,
        ai_service: AIService
    ):
        self.schedule_repo = schedule_repo
        self.notification_repo = notification_repo
        self.ai_service = ai_service
    
    async def create_daily_briefing(self, user_id: int) -> None:
        """
        사용자의 오늘 일정을 조회하여 AI 요약 브리핑을 생성하고 저장합니다.
        """
        today = date.today()
        
        # 오늘 일정 조회
        schedules = await self.schedule_repo.get_schedules_by_user_and_date(user_id, today)
        
        # AI 브리핑 생성
        if not schedules:
            briefing_content = "오늘을 예정된 일정이 없습니다. 편안한 하루 보내세요!"
        else:
            briefing_content = await self.ai_service.generate_briefing(schedules)
            
        # 알림 저장
        await self.notification_repo.create(
            user_id=user_id,
            type="morning_briefing",
            content=briefing_content
        )
        logger.info(f"Briefing created for user {user_id}")