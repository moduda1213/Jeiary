import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repo import UserRepository
from app.schemas.user import UserCreate

# 모든 테스트는 비동기로 실행되어야 함을 표시
@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession):
    """
    UserRepository.create 메서드가 사용자를 성공적으로 생성하는지 테스트
    """
    # 1. 준비 (Arrange)
    repo = UserRepository(db_session)
    password = "testpassword123@"
    user_to_create = UserCreate(email="test@example.com", password=password)

    # 2. 실행 (Act)
    created_user = await repo.create(user_to_create)

    # 3. 단언 (Assert)
    assert created_user is not None
    assert created_user.id is not None
    assert created_user.email == user_to_create.email
    assert created_user.password_hash != password  # 비밀번호가 해시되었는지 확인
    assert created_user.password_hash is not None


@pytest.mark.asyncio
async def test_get_by_email(db_session: AsyncSession):
    """
    UserRepository.get_by_email 메서드가 이메일로 사용자를 정확히 찾아내는지 테스트
    """
    # 1. 준비 (Arrange)
    repo = UserRepository(db_session)
    password = "testpassword123@"
    email = "test_get@example.com"
    user_to_create = UserCreate(email=email, password=password)
    # 테스트할 데이터를 먼저 생성
    await repo.create(user_to_create)
    # 2. 실행 (Act)
    found_user = await repo.get_by_email(email)
    not_found_user = await repo.get_by_email("nonexistent@example.com")
    # 3. 단언 (Assert)
    assert found_user is not None
    assert found_user.email == email
    assert not_found_user is None