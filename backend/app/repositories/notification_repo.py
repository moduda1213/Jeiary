from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.base import BaseRepository
from app.models.notification import Notification

class NotificationRepository(BaseRepository[Notification]):
    def __init__(self, session: AsyncSession):
        super().__init__(Notification, session)
        
    async def create(self, user_id: int, type: str, content: str) -> Notification:
        """알림 생성"""
        return await super().create(
            user_id = user_id,
            type = type,
            content = content,
            is_read = False
        )
    
    