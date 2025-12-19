from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from app.repositories.base import BaseRepository
from app.models.chat import ChatHistory, ChatRole
from datetime import datetime

class ChatRepository(BaseRepository[ChatHistory]): # 제네릭 상속
    def __init__(self, session: AsyncSession):
        super().__init__(ChatHistory, session)
    
    async def create(self, user_id: int, role: ChatRole, content: str) -> ChatHistory:
        """채팅 내역 저장"""
        chat = ChatHistory(
            user_id = user_id,
            role = role.value,
            content = content
        )
        self.session.add(chat)
        await self.session.flush()
        await self.session.refresh(chat)
        return chat
    
    async def get_recent_chats(self, user_id: int, limit: int = 20) -> list[ChatHistory]:
        """
        사용자의 최근 대화 내역 조회 (AI 컨텍스트용)
        최신순으로 가져옴 ---> 서비스 계층에서 필요시 역순 정렬
        """
        stmt = select(self.model).where(
            self.model.user_id == user_id,
            self.model.is_deleted == False
        ).order_by(
            self.model.created_at.desc(),
            self.model.id.desc()
        ).limit(limit)
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def delete(self, chat: ChatHistory) -> ChatHistory:
        """소프트 삭제"""
        chat.is_deleted = True
        self.session.add(chat)
        await self.session.flush()
        await self.session.refresh(chat)
        return chat
    
    async def delete_expired_chat(self, cutoff_date: datetime) -> int:
        """
        기준 날짜 이전에 생성된 채팅 로그 영구 삭제.
        채팅은 created_at 기준으로 삭제

        Args:
            cutoff_date (datetime): 이 날짜보다 created_at이 오래된 데이터를 삭제

        Returns:
            int: 삭제된 행의 개수
        """
        stmt = delete(self.model).where(self.model.created_at < cutoff_date)
        result = await self.session.execute(stmt)
        return result.rowcount
        
        