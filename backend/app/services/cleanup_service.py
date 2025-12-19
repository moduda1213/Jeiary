from loguru import logger

from datetime import datetime, timedelta
from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.chat_repo import ChatRepository

class CleanupService:
    def __init__(
        self,
        schedule_repo: ScheduleRepository,
        chat_repo: ChatRepository
    ):
        self.schedule_repo = schedule_repo
        self.chat_repo = chat_repo
    
    async def delete_expired_schedules(self, retention_days: int = 14) -> int:
        """
        보존 기간이 지난 삭제된 일정을 영구 삭제합니다.

        Args:
            retention_days (int, optional): 보존 기간(일), 기본값:14일

        Returns:
            int: 삭제된 행의 개수
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        count = await self.schedule_repo.delete_expired_schedules(cutoff_date)
        
        if count > 0:
            logger.info(f"Cleanup: 만료된 일정 영구 삭제 {count}")
        
        return count
    
    async def delete_expired_chats(self, retention_days: int = 14) -> int:
        """
        보존 기간이 채팅 로그를 영구 삭제합니다.

        Args:
            retention_days (int, optional): 보존 기간(일), 기본값:14일

        Returns:
            int: 삭제된 행의 개수
        """
        cutoff_date = datetime.now() - timedelta(days=retention_days)
        count = await self.chat_repo.delete_expired_chat(cutoff_date)
        
        if count > 0:
            logger.info(f"Cleanup: 만료된 채팅 영구 삭제 {count}")
            
        return count