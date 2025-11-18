import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from uuid import uuid4

from app.repositories.refresh_token_repo import RefreshTokenRepository
from app.models.user import User  # test_user fixture의 타입 힌트를 위해 import

@pytest.mark.asyncio
async def test_create_refresh_token(db_session: AsyncSession, test_user: User):
    """
    RefreshTokenRepository.create 메서드가 토큰을 성공적으로 생성하는지 테스트
    """
    # 1. 준비 (Arrange)
    repo = RefreshTokenRepository(db_session)
    jti = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    # 2. 실행 (Act)
    # test_user fixture가 제공한 사용자의 id를 사용
    created_token = await repo.create(
        user_id=test_user.id, 
        jti=jti, 
        expires_at=expires_at
    )

    # 3. 단언 (Assert)
    assert created_token is not None
    assert created_token.id is not None
    assert created_token.user_id == test_user.id
    assert created_token.token_id == jti
    assert not created_token.is_revoked


@pytest.mark.asyncio
async def test_get_and_revoke_token(db_session: AsyncSession, test_user: User):
    """
    토큰을 JTI로 조회하고, 성공적으로 무효화하는지 테스트
    """
    # 1. 준비 (Arrange)
    repo = RefreshTokenRepository(db_session)
    jti = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)
    # 테스트할 토큰을 먼저 생성
    await repo.create(user_id=test_user.id, jti=jti, expires_at=expires_at)
    # 2. 실행 및 단언 (Act & Assert)
    
    # 2-1. JTI로 토큰 조회
    found_token = await repo.get_by_jti(jti)
    assert found_token is not None
    assert found_token.token_id == jti
    assert not found_token.is_revoked
    
    # 2-2. 토큰 무효화
    revoked_token = await repo.revoke(jti)
    assert revoked_token is not None
    assert revoked_token.is_revoked is True
    
    # 2-3. 다시 조회하여 무효화 확인
    found_token_after_revoke = await repo.get_by_jti(jti)
    assert found_token_after_revoke is not None
    assert found_token_after_revoke.is_revoked is True