from typing import Generic, TypeVar, Type
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base


ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: Type[ModelType], session: AsyncSession):
        self.model= model
        self.session= session
        
    async def get(self, pk: int) -> ModelType | None:
        return await self.session.get(self.model, pk)