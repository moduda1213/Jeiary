from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config import settings
from typing import AsyncGenerator

# 비동기 엔진 생성
async_engine = create_async_engine(
    settings.DATABASE_URL,
    pool_pre_ping = True,  # 간단한 sql(select 1)을 보내 db 커넥션 확인
    echo = True # 데이터베이스에 전송되는 모든 SQL 쿼리를 콘솔에 출력
)

# 비동기 세션 메이커
AsyncSessionFactory = async_sessionmaker(
    bind = async_engine,
    autoflush = False,
    expire_on_commit = False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
        FastAPI 의존성 주입을 위한 DB 세션 생성기
        요청마다 세션을 생성하고, 요청 처리가 끝나면 자동으로 트랜잭션을 관리합니다.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise