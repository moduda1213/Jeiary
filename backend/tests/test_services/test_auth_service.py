import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock

from app.services.auth_service import AuthService
from app.schemas.auth import AuthLogin
from app.schemas.user import UserCreate
from app.core.exceptions import CredentialException, InvalidTokenException
from app.models.user import User
from datetime import datetime


# 테스트에 사용할 가짜 User 모델 객체
class MockUser:
    def __init__(
        self,
        id=1,
        email="test@example.com",
        password_hash="hashed_password",
        created_at=None,
        updated_at=None
    ):
        self.id = id
        self.email = email
        self.password_hash = password_hash,
        self.created_at = created_at or datetime.now()
        self.updated_at = updated_at or datetime.now()
    
# 테스트에 사용할 가짜 RefreshToken 모델 객체      
class MockRefreshToken:
    def __init__(
        self,
        user_id=1,
        jti="test_jti",
        is_revoked=False
    ):
        self.user_id = user_id
        self.jti = jti
        self.is_revoked = is_revoked
        
@pytest.fixture
def mock_user_repo(mocker):
    return mocker.AsyncMock()

@pytest.fixture
def mock_refresh_token_repo(mocker):
    return mocker.AsyncMock()

@pytest.fixture
def auth_service(mock_user_repo, mock_refresh_token_repo):
    return AuthService(
        user_repo=mock_user_repo,
        refresh_token_repo=mock_refresh_token_repo
    )
    
@pytest.mark.asyncio
class TestAuthServiceRegister:
    async def test_register_success(self, auth_service, mock_user_repo):
        """회원가입 성공 케이스"""
        user_create = UserCreate(email="new@example.com", password="password123@")
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.create.return_value = MockUser(email=user_create.email)
        
        new_user = await auth_service.register(user_create)
        
        # assert_called_once_with : 정확히 1번, 올바른 인자로 호출되었는지 확인
        mock_user_repo.get_by_email.assert_called_once_with(user_create.email)
        mock_user_repo.create.assert_called_once_with(user_create)
        assert new_user.email == user_create.email
        
    async def test_register_fail_email_exists(self, auth_service, mock_user_repo):
        """회원가입 실패 케이스 - 이메일 중복"""
        user_create = UserCreate(email="exists@example.com", password="password123@")
        mock_user_repo.get_by_email.return_value = MockUser()
        
        with pytest.raises(HTTPException) as exc_info:
            await auth_service.register(user_create)
            
        assert exc_info.value.status_code == 409
        mock_user_repo.create.assert_not_called() # assert_not_called : 호출되지 않았는지 확인

@pytest.mark.asyncio
class TestAuthServiceLogin:
    async def test_login_success(self, auth_service, mock_user_repo, mock_refresh_token_repo, mocker):
        """로그인 성공 케이스""" 
        form_data = AuthLogin(email="test@example.com", password="password")
        mock_user = MockUser()
        
        mock_user_repo.get_by_email.return_value = mock_user
        mocker.patch("app.core.security.verify_password", return_value=True)
        mocker.patch("app.core.security.create_access_token", return_value="access_token")
        mocker.patch("app.core.security.create_refresh_token", return_value="refresh_token")
        mocker.patch("app.core.security.verify_token", return_value={"jti" : "test_jti", "exp" : 12345})
        
        response = await auth_service.login(form_data)
        
        assert response.access_token == "access_token"
        assert response.refresh_token == "refresh_token"
        mock_refresh_token_repo.create.assert_called_once()
        
    async def test_login_fail_wrong_password(self, auth_service, mock_user_repo, mocker):
        """로그인 실패 케이스 - 잘못된 비밀번호"""
        form_data = AuthLogin(email="test@example.com", password="wrong_password")
        mock_user_repo.get_by_email.return_value = MockUser()
        mocker.patch("app.core.security.verify_password", return_value=False)
        
        with pytest.raises(CredentialException):
            await auth_service.login(form_data)
            
@pytest.mark.asyncio
class TestAuthServiceRefreshToken:
    async def test_refresh_access_token_success(self, auth_service, mock_user_repo, mock_refresh_token_repo, mocker):
        """Access Token 갱신 성공 케이스"""
        mocker.patch("app.core.security.verify_token", return_value={"jti" : "test_jti", "sub" : "test@example.com"})
        mock_refresh_token_repo.get_by_jti.return_value = MockRefreshToken()
        mock_user_repo.get_by_email.return_value = MockUser()
        mocker.patch("app.core.security.create_access_token", return_value="new_access_token")
        
        response = await auth_service.refresh_access_token("valid_refresh_token")
        
        assert response.access_token == "new_access_token"
        mock_refresh_token_repo.get_by_jti.assert_called_once_with("test_jti")
        mock_user_repo.get_by_email.assert_called_once_with("test@example.com")
        
    async def test_refresh_fail_revoked_token(self, auth_service, mock_refresh_token_repo, mocker):
        """Access Token 갱신 실패 - 무효화된 토큰 사용"""
        mocker.patch("app.core.security.verify_token", return_value={"jti" : "revoked_jti", "sub" : "test@example.com"})
        mock_refresh_token_repo.get_by_jti.return_value = MockRefreshToken(is_revoked=True)
        
        with pytest.raises(CredentialException, match="보안 위협 감지로 모든 세션이 종료되었습니다."):
            await auth_service.refresh_access_token("revoked_refresh_token")
        
    async def test_refresh_fail_token_not_in_db(self, auth_service, mock_refresh_token_repo, mocker):
        """Access Token 갱신 실패 - DB에 존재하지 않는 토큰"""
        mocker.patch("app.core.security.verify_token", return_value={"jti" : "unknown_jti", "sub" : "test@example.com"})
        mock_refresh_token_repo.get_by_jti.return_value = None
        
        with pytest.raises(CredentialException, match="토큰이 무효화되었거나 존재하지 않습니다."):
            await auth_service.refresh_access_token("unknown_refresh_token")
        
    async def test_refresh_fail_invalid_token_payload(self, auth_service, mocker):
        """Access Token 갱신 실패 - 페이로드가 불완전한 토큰"""
        mocker.patch("app.core.security.verify_token", return_value={"sub" : "test@example.com"})
        
        with pytest.raises(CredentialException, match="토큰에 필요한 정보가 없습니다."):
            await auth_service.refresh_access_token("bad_payload_token")
        
@pytest.mark.asyncio
class TestAuthServiceLogout:
    async def test_logout_success(self, auth_service, mock_refresh_token_repo, mocker):
        """로그아웃 성공 케이스"""
        mocker.patch("app.core.security.verify_token", return_value={"jti" : "test_jti"})
        
        await auth_service.logout("valid_refresh_token")
        
        mock_refresh_token_repo.revoke.assert_called_once_with("test_jti")
        
    async def test_logout_invalid_token_should_not_raise_error(self, auth_service, mock_refresh_token_repo, mocker):
        """유효하지 않은 토큰으로 로그아웃 시도 시, 에러가 발생하지 않아야 함"""
        mocker.patch("app.core.security.verify_token", side_effect=InvalidTokenException)
        
        try:
            await auth_service.logout("invalid_refresh_token")
        except Exception as e:
            pytest.fail(f"logout should not raise error for invalid token, but raised {e}")
        
        mock_refresh_token_repo.revoke.assert_not_called()
        
    # pytest-mock의 mocker fixture를 사용합니다.
    @pytest.mark.asyncio
    async def test_login_user_not_found(self, mock_user_repo, mock_refresh_token_repo, mocker):
        """
        단위 테스트: 존재하지 않는 이메일로 로그인 시 CredentialException 발생 여부
        """
        # 1. 의존성(Repository) 모킹
        mock_user_repo = mocker.MagicMock()
        # get_by_email이 None을 반환하도록 설정
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        
        mock_refresh_token_repo = mocker.MagicMock()
    
        # 2. 모킹된 의존성으로 서비스 객체 생성
        auth_service = AuthService(
            user_repo=mock_user_repo, 
            refresh_token_repo=mock_refresh_token_repo
        )
        
        # 3. 테스트 실행 및 예외 검증
        with pytest.raises(CredentialException) as excinfo:
            await auth_service.login(AuthLogin(email="no-user@example.com", password="password"))

        # 예외 메시지 검증
        assert "이메일 또는 비밀번호가 올바르지 않습니다." in str(excinfo.value)
    
    
    @pytest.mark.asyncio
    async def test_login_wrong_password(self, mock_user_repo, mock_refresh_token_repo, mocker):
        """
        단위 테스트: 비밀번호가 틀렸을 경우 CredentialException 발생 여부
        """
        # 1. 의존성 모킹
        mock_user_repo = mocker.MagicMock()
        # get_by_email이 테스트용 User 객체를 반환하도록 설정
        test_user = User(id=1, email="test@example.com", password_hash="hashed_password")
        mock_user_repo.get_by_email = AsyncMock(return_value=test_user)

        mock_refresh_token_repo = mocker.MagicMock()

        # security.verify_password가 False를 반환하도록 모킹
        mocker.patch("app.core.security.verify_password", return_value=False)

        # 2. 서비스 객체 생성
        auth_service = AuthService(
            user_repo=mock_user_repo,
            refresh_token_repo=mock_refresh_token_repo
        )

        # 3. 테스트 실행 및 예외 검증
        with pytest.raises(CredentialException) as excinfo:
            await auth_service.login(AuthLogin(email="test@example.com", password="wrong_password"))

        assert "이메일 또는 비밀번호가 올바르지 않습니다." in str(excinfo.value)