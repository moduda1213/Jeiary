from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash
from app.repositories.base import BaseRepository

class UserRepository(BaseRepository[User]):
    def __init__(self, session: AsyncSession):
        super().__init__(User, session)
        
    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(self.model).filter(self.model.email== email))
        return result.scalars().first()
    
    async def get_all_users(self) -> list[User]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())
    
    async def create(self, user_create: UserCreate) -> User:
        hashed_password = get_password_hash(user_create.password)
        user_data= user_create.model_dump(exclude={"password"})
        
        new_user = self.model(**user_data, password_hash=hashed_password)
        self.session.add(new_user)
        await self.session.flush()
        await self.session.refresh(new_user)
        return new_user