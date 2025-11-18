import pytest
import sys
import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

# 프로젝트 루트 디렉토리(backend)를 Python 경로에 추가
# 이렇게 하면 'from app.core...' 같은 절대 경로 임포트가 가능해집니다
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.db.base import Base
import app.models

from app.schemas.user import UserCreate
from app.repositories.user_repo import UserRepository
from app.models.user import User

from httpx import AsyncClient
from app.main import app
from app.db.session import get_db

from app.core.limiter import limiter

# 테스트용 비동기 엔진 생성 (인메모리 SQLite)
engine = create_async_engine(
    "sqlite+aiosqlite:///:memory:",
    connect_args={"check_same_thread": False}
)

# 테스트용 세션 메이커
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

@pytest.fixture(autouse=True) # 모든 테스트에 자동 적용
def reset_rate_limiter(monkeypatch):
    """
    Rate Limit 테스트가 다른 테스트에 영향받지 않도록
    각 테스트 실행 전에 Rate Limiter의 상태를 초기화
    """
    limiter._storage.reset()
    yield

@pytest.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    각 테스트 함수를 위한 독립적인 DB 세션을 제공하는 Fixture.
    테스트 시작 시 모든 테이블을 생성하고, 테스트 종료 시 롤백합니다.
    """
    # 테스트 시작 전, 모든 테이블 생성
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 세션 시작
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()
    
    # 테스트 종료 후, 모든 테이블 삭제
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        
@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """
    테스트용 사용자 한 명을 생성하고 DB에 저장한 후,
    해당 사용자 모델 객체를 반환하는 Fixture.
    """
    repo = UserRepository(db_session)
    user_to_create = UserCreate(email="test@example.com", password="testpassword123@")
    created_user = await repo.create(user_to_create)
    return created_user

@pytest.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """
    테스트용 API 클라이언트를 제공하는 Fixture
    실제 DB 대신 테스트용 DB 세션을 사용하도록 의존성을 오버라이드합니다.
    """
    # 테스트용 DB 세션을 사용하도록 get_db 의존성 오버라이드
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session
        
    app.dependency_overrides[get_db] = override_get_db
    
    # AsyncClient 생성
    async with AsyncClient(app=app, base_url="http://test") as c:
        yield c
    
    # 테스트 종료 후 오버라이드 초기화
    app.dependency_overrides.clear()
    
@pytest.fixture
async def authenticated_user_cookie(client: AsyncClient, test_user: User) -> dict[str, str]:
    """
    테스트 사용자로 로그인하여 인증 토큰이 담긴 쿠키를 반환하는 Fixture.
    API 테스트 시 인증이 필요한 엔드포인트에 사용됩니다.
    """
    login_data = {
        "username": test_user.email,
        "password": "testpassword123@",
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200, "테스트 사용자 로그인에 실패하였습니다."
    access_token = response.cookies.get("access_token")
    assert access_token is not None, "로그인 응답에 access_token 쿠키가 없습니다."
    
    return {"access_token": access_token}