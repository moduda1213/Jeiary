import pytest
import asyncio
from httpx import AsyncClient
from app.models.user import User
from app.core import security

@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient):
    """회원가입 성공 테스트"""
    
    user_data = {
        "email": "newuser@example.com",
        "password": "new_password123@"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 201, f"예상 상태 코드 201, 실제: {response.status_code}, 내용: {response.text}"
    
    response_data = response.json()
    
    assert response_data["email"] == user_data["email"]
    assert "id" in response_data
    assert "password_hash" not in response_data
    
@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient, test_user: User):
    """이미 존재하는 이메일로 회원가입 시도 시 409 에러 테스트"""
    user_data = {
        "email": test_user.email,
        "password": "any_password123@"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 409
    response_data = response.json()
    assert response_data["detail"] == "이미 사용중인 이메일입니다."
    
@pytest.mark.asyncio
async def test_register_user_fail_password_no_special_char(client: AsyncClient):
    """비밀번호에 특수문자가 없는 경우 회원가입 실패 (422 에러) 테스트"""
    user_data = {
        "email": "newuser@example.com",
        "password": "new_password123"
    }
    
    response = await client.post("/api/v1/auth/register", json=user_data)
    
    assert response.status_code == 422, f"예상 상태 코드 422, 실제: {response.status_code}, 내용: {response.text}"
    response_data = response.json()
    assert "비밀번호에 특수문자를 포함해야 합니다." in response_data["detail"][0]["msg"]

@pytest.mark.asyncio
async def test_login_success(client: AsyncClient, test_user: User):
    """로그인 성공 및 httpOnly 쿠키 발급 테스트"""
    # OAuth2PasswordRequestForm은 form-data를 사용하므로, json이 아닌 data 파라미터로 전달합니다.
    login_data = {
        "username": test_user.email,
        "password": "testpassword123@"
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 200
    
    response_data = response.json()
    assert response_data["message"] == "Login successful"
    
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    
    set_cookie_header = response.headers["set-cookie"]
    assert "httponly" in set_cookie_header.lower()
    
@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient, test_user: User):
    """잘못된 비밀번호로 로그인 시도 시 401 에러 테스트"""
    login_data = {
        "username": test_user.email,
        "password": "wrong_password@"
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 401, f"예상 상태 코드 401, 실제: {response.status_code}, 내용: {response.text}"
    response_data = response.json()
    assert response_data["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다."\
        
@pytest.mark.asyncio
async def test_login_wrong_username(client: AsyncClient, test_user: User):
    """잘못된 이메일로 로그인 시도 시 401 에러 테스트"""
    login_data = {
        "username": "nonexistent@example.com",
        "password": "testpassword123@"
    }
    
    response = await client.post("/api/v1/auth/login", data=login_data)
    
    assert response.status_code == 401, f"예상 상태 코드 401, 실제: {response.status_code}, 내용: {response.text}"
    response_data = response.json()
    assert response_data["detail"] == "이메일 또는 비밀번호가 올바르지 않습니다."   
    
@pytest.mark.asyncio
async def test_login_rate_limiting(client: AsyncClient):
    """로그인 엔드포인트에 대한 Rate Limit(5회/분) 테스트"""
    login_data = {
        "username": "rate.limit.test@example.com",
        "password": "password123@"
    }
    
    for i in range(5):
        response = await client.post("/api/v1/auth/login", data=login_data)
        assert response.status_code != 429, (
            f"{i+1}번째 요청이 차단됨 (5회까지 허용되어야 함)"
        )
    
    # "5회/분" 제한에 걸려 Rate Limiter에 의해 차단
    response = await client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 429, f"Rate limit 미적용: {response.status_code}, {response.text}"
    
    # 커스텀 에러 메시지 검증
    response_data = response.json()
    assert "detail" in response_data, "에러 응답에 detail 필드 없음"
    assert "Rate limit exceeded" in response_data["detail"]
    
    # Retry-After 헤더 검증
    assert "retry-after" in response.headers
    assert response.headers["retry-after"] == "60"
    
@pytest.mark.asyncio
async def test_refresh_token_success(client: AsyncClient, test_user: User):
    """성공: 쿠키를 사용하여 토큰 갱신 테스트"""
    login_data = {
        "username": test_user.email,
        "password": "testpassword123@"
    }
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    original_access_token = login_response.cookies.get("access_token")
    
    await asyncio.sleep(1)
    
    refresh_response = await client.post("/api/v1/auth/refresh")
    
    assert refresh_response.status_code == 200, (
        f"예상 상태 코드 200, 실제: {refresh_response.status_code}, 내용: {refresh_response.text}"
    )
    
    new_access_token = refresh_response.cookies.get("access_token")
    assert new_access_token is not None
    assert new_access_token != original_access_token

@pytest.mark.asyncio
async def test_logout_success(client: AsyncClient, test_user: User):
    """유효한 Refresh Token으로 로그아웃 및 쿠키 삭제 테스트"""
    # 1. 로그인하여 쿠키를 발급받음
    login_data = {
        "username": test_user.email,
        "password": "testpassword123@"
    }
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200
    assert "access_token" in login_response.cookies

    # 2. 본문 없이 로그아웃 요청 (클라이언트가 쿠키를 자동으로 전송)
    logout_response = await client.post("/api/v1/auth/logout")
    
    # 3. 상태 코드 및 쿠키 삭제 확인
    assert logout_response.status_code == 204
    # httpx에서 삭제된 쿠키는 max-age=0 으로 표현됨
    assert logout_response.cookies.get("access_token") is None
    assert logout_response.cookies.get("refresh_token") is None

    # 4. 로그아웃 후 토큰이 무효화되었는지 확인
    # httpx 클라이언트에 저장된 만료된 쿠키를 포함하여 refresh 시도
    refresh_response = await client.post("/api/v1/auth/refresh")
    assert refresh_response.status_code == 401
    assert "Refresh Token이 존재하지 않습니다." in refresh_response.json()["detail"]
    
@pytest.mark.asyncio
async def test_refresh_token_invalid(client: AsyncClient):
    """유효하지 않은 Refresh Token으로 갱신 시도 시 401 에러 테스트"""
    invalid_token = "this.is.an.invalid.token"
    client.cookies.set("refresh_token", invalid_token)
    
    response = await client.post("/api/v1/auth/refresh")
    
    assert response.status_code == 401
    response_data = response.json()
    # 'detail' 메시지가 예상대로 '토큰 검증 실패'로 시작하는지 확인
    assert str(response_data["detail"]).startswith("토큰 검증에 실패했습니다.")
    
@pytest.mark.asyncio
async def test_logout_invalid_token(client: AsyncClient):
    """유효하지 않은 토큰으로 로그아웃 시도 시에도 성공(204) 처리 테스트"""
    invalid_token = "this.is.an.invalid.token"
    client.cookies.set("refresh_token", invalid_token)
    
    response = await client.post("/api/v1/auth/logout")
    
    # 유효하지 않은 토큰이라도 에러를 반환하지 않고 성공 처리하는지 확인
    assert response.status_code == 204
    
    
@pytest.mark.asyncio
async def test_get_current_user_success(client: AsyncClient, test_user: User):
    """성공: 유효한 쿠키로 현재 사용자 정보를 정상적으로 가져오는 경우"""
    # 1. 로그인하여 쿠키 발급
    login_data = {"username": test_user.email, "password": "testpassword123@"}
    login_response = await client.post("/api/v1/auth/login", data=login_data)
    assert login_response.status_code == 200

    # 2. /api/v1/auth/me 엔드포인트 호출 (클라이언트가 쿠키를 자동으로 포함)
    response = await client.get("/api/v1/auth/me")

    # 3. 결과 검증
    assert response.status_code == 200, f"예상 200, 실제: {response.status_code}, 내용: {response.text}"
    data = response.json()
    assert data["email"] == test_user.email
    assert data["id"] == test_user.id
    
@pytest.mark.asyncio
async def test_get_current_user_no_token(client: AsyncClient):
    """실패 : 인증 토큰 없이 요청하는 경우"""
    response = await client.get("/api/v1/auth/me")
    
    ## FastAPI의 OAuth2PasswordBearer는 토큰이 없으면 401이 아닌 403을 반환할 수 있습니다.
    assert response.status_code == 401
    assert response.json()["detail"] == "인증 토큰이 존재하지 않습니다."
    
@pytest.mark.asyncio
async def test_get_current_user_expired_token(client: AsyncClient, test_user: User):
    """실패: 만료된 토큰으로 요청하는 경우"""
    import time
    from jose import jwt
    from app.config import settings
    
    expired_payload = {
        "sub": test_user.email,
        "exp": int(time.time()) -1,
        "type": "access" # verify_token에서 타입을 검증하므로 추가
    }
    expired_token = jwt.encode(
        expired_payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )
    
    client.cookies.set("access_token", expired_token)
    
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401
    assert "토큰 검증에 실패했습니다." in response.json()["detail"]
    
@pytest.mark.asyncio
async def test_get_current_user_user_not_found(client: AsyncClient):
    """실패: 토큰은 유효하지만 해당 사용자가 DB에 존재하지 않는 경우"""
    access_token = security.create_access_token(data={"sub": "deleted_user@example.com"})
    client.cookies.set("access_token", access_token)
    
    response = await client.get("/api/v1/auth/me")
    
    assert response.status_code == 401
    assert response.json()["detail"] == "사용자를 찾을 수 없습니다."