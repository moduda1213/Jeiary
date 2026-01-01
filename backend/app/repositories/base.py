from typing import Generic, TypeVar, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.base import Base
from pydantic import BaseModel
from datetime import datetime, timezone

ModelType = TypeVar("ModelType", bound=Base)

class BaseRepository(Generic[ModelType]):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self.model= model
        self.session= session
        
    async def get(self, pk: Any) -> ModelType | None:
        return await self.session.get(self.model, pk)
    
    async def create(self, schema: BaseModel | dict[str, Any] | None = None, **kwargs: Any) -> ModelType:
        """ kwargs가 schema 데이터보다 우선순위 높음 """
        if isinstance(schema, BaseModel):
            obj_data = schema.model_dump(exclude_unset=True)
        elif isinstance(schema, dict):
            obj_data = schema.copy()
        else:
            obj_data = {}
            
        obj_data.update(kwargs)
        
        db_obj = self.model(**obj_data)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj
    
    async def delete(self, db_obj: ModelType) -> None:
        """Hard Delete"""
        await self.session.delete(db_obj)
        await self.session.flush()
        
    async def soft_delete(self, db_obj: ModelType) -> ModelType:
        """
        Soft Delete
        - UTC 시간 기준 deleted_at 설정
        """
        if hasattr(db_obj, "is_deleted"):
            db_obj.is_deleted = True
            if hasattr(db_obj, "deleted_at"):
                db_obj.deleted_at = datetime.now(timezone.utc)
                
            self.session.add(db_obj)
            await self.session.flush()
            await self.session.refresh(db_obj)
            
        return db_obj