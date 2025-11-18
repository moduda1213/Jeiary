from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.refresh_token import RefreshToken
from app.repositories.base import BaseRepository
from datetime import datetime

class RefreshTokenRepository(BaseRepository[RefreshToken]):
    def __init__(self, session: AsyncSession):
        super().__init__(RefreshToken, session)
        
    async def create(self, user_id: int, jti: str, expires_at: datetime) -> RefreshToken:
        token = RefreshToken(user_id=user_id, token_id=jti, expires_at=expires_at)
        self.session.add(token)
        await self.session.flush()
        await self.session.refresh(token)
        return token
    
    async def get_by_jti(self, jti: str) -> RefreshToken | None:
        result = await self.session.execute(select(self.model).filter(self.model.token_id == jti))
        return result.scalars().first()
    
    # 토큰 무효화
    async def revoke(self, jti: str) -> RefreshToken | None:
        token = await self.get_by_jti(jti)
        if token:
            token.is_revoked = True
            await self.session.flush()
            await self.session.refresh(token)
        return token