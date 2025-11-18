"""
   1. 일정 생성 (POST /schedules/)
       - 성공: 인증된 사용자가 유효한 데이터로 일정을 생성하고 201 Created 응답을 받는지 확인.
       - 실패: 인증되지 않은 사용자의 요청을 거부하는지 확인 (401 Unauthorized).
       - 실패: 유효하지 않은 데이터(예: 제목이 비어있음)로 요청 시 422 Unprocessable Entity 응답을 받는지 확인.

   2. 일정 목록 조회 (GET /schedules/)
       - 성공: 인증된 사용자가 자신의 일정 목록을 200 OK로 받는지 확인.
       - 실패: 인증되지 않은 사용자의 요청을 거부하는지 확인 (401 Unauthorized).

   3. 특정 일정 조회 (GET /schedules/{schedule_id})
       - 성공: 자신의 특정 일정을 200 OK로 받는지 확인.
       - 실패: 존재하지 않는 일정 ID로 요청 시 404 Not Found 응답을 받는지 확인.
       - 실패: 다른 사용자의 일정 ID로 요청 시 404 Not Found 응답을 받는지 확인 (보안 규칙).

   4. 일정 수정 (PUT /schedules/{schedule_id})
       - 성공: 자신의 일정을 수정한 뒤 200 OK와 함께 수정된 데이터를 받는지 확인.
       - 실패: 다른 사용자의 일정을 수정하려고 할 때 404 Not Found 응답을 받는지 확인.

   5. 일정 삭제 (DELETE /schedules/{schedule_id})
       - 성공: 자신의 일정을 삭제한 뒤 204 No Content 응답을 받는지 확인.
       - 실패: 다른 사용자의 일정을 삭제하려고 할 때 404 Not Found 응답을 받는지 확인.
"""
import pytest
from httpx import AsyncClient
from fastapi import status
from sqlalchemy.ext.asyncio import AsyncSession

#========================= 일정 생성 테스트 ==================================================
@pytest.mark.asyncio
async def test_create_schedule_success(
    client: AsyncClient,
    authenticated_user_cookie: dict[str, str]
):
    """ 인증된 사용자가 유효한 데이터로 일정을 생성하는 경우 """
    schedule_data = {
        "title": "성공 테스트 일정",
        "date": "2025-12-25",
        "content": "크리스마스 계획 세우기",
        "start_time": "14:00:00",
        "end_time": "15:00:00"
    }
    
    response = await client.post(
        "/api/v1/schedules/",
        json=schedule_data,
        cookies=authenticated_user_cookie
    )
    
    # 307 Temporary Redirect
    # "요청한 주소가 약간 다른 곳에 있으니, 그쪽으로 같은 요청(POST)을 다시 보내라"는 의미의 HTTP 상태 코드
    #  "/api/v1/schedules" ->  "/api/v1/schedules/" 흔한 상황
    assert response.status_code == status.HTTP_201_CREATED
    
    response_data = response.json()
    assert response_data["title"] == schedule_data["title"]
    assert response_data["content"] == schedule_data["content"]
    assert "id" in response_data
    assert "user_id" in response_data
    
@pytest.mark.asyncio
async def test_create_schedule_unauthenticated(client: AsyncClient):
    """인증되지 않은 사용자가 일정 생성을 시도하는 경우"""
    schedule_data = {
        'title': "인증 실패 테스트",
        "date": "2025-11-14",
    }
    response = await client.post(
        "/api/v1/schedules/",
        json=schedule_data,
        # 쿠키 전달 x
    )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
@pytest.mark.asyncio
async def test_create_schedule_invalid_data(client: AsyncClient, authenticated_user_cookie: dict[str, str]):
    """인증된 사용자가 유효하지 않은 데이터로 일정 생성을 시도하는 경우"""
    invalid_schedule_data = {
        "title": "  ",
        "date": "2025-11-15",
    }
    response = await client.post(
        "/api/v1/schedules/",
        json=invalid_schedule_data,
        cookies=authenticated_user_cookie
    )
    
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    
#===========================================================================================
#========================= 일정 조회 테스트 (월별) ==================================================
@pytest.mark.asyncio
async def test_get_schedules_month_success(client: AsyncClient, authenticated_user_cookie: dict[str, str]):
    """인증된 사용자가 자신의 일정 목록을 성공적으로 조회하는 경우"""
    await client.post("/api/v1/schedules/", json={"title": "11월 일정 1", "date": "2025-11-10", "start_time":"10:00", "end_time":"11:00"}, cookies=authenticated_user_cookie)
    await client.post("/api/v1/schedules/", json={"title": "11월 일정 2", "date": "2025-11-20", "start_time":"14:00", "end_time":"15:00"}, cookies=authenticated_user_cookie)
    await client.post("/api/v1/schedules/", json={"title": "12월 일정 1", "date": "2025-12-5", "start_time":"09:00", "end_time":"10:00"}, cookies=authenticated_user_cookie)
    
    response = await client.get("/api/v1/schedules/", params={"year":2025, "month":11}, cookies=authenticated_user_cookie)
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 2
    assert response_data[0]["title"] == "11월 일정 1"
    assert response_data[1]["title"] == "11월 일정 2"
    
@pytest.mark.asyncio
async def test_get_schedules_month_empty(client: AsyncClient, authenticated_user_cookie: dict[str, str]):
    """인증된 사용자가 일정이 없는 월을 조회한 경우, 빈 리스트를 반환"""
    
    response = await client.get("/api/v1/schedules/", params={"year":2024, "month":1}, cookies=authenticated_user_cookie)
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert isinstance(response_data, list)
    assert len(response_data) == 0

@pytest.mark.asyncio
async def test_get_schedules_missing_params(client: AsyncClient, authenticated_user_cookie: dict[str, str]):
    """year or month 파라미터 없이 요청하는 경우"""
    response_no_params = await client.get("/api/v1/schedules/", params={}, cookies=authenticated_user_cookie)
    assert response_no_params.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    """month 파라미터 없이 요청하는 경우"""
    response_no_params = await client.get("/api/v1/schedules/", params={"year":2024}, cookies=authenticated_user_cookie)
    assert response_no_params.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
@pytest.mark.asyncio
async def test_get_schedules_month_empty(client: AsyncClient):
    """인증되지 않은 사용자가 일정 목록 조회를 시도하는 경우"""
    response = await client.get("/api/v1/schedules/", params={"year": 2025, "month": 11})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
@pytest.mark.asyncio
async def test_get_schedules_success(client: AsyncClient, authenticated_user_cookie: dict[str, str]):
    """자신이 소유한 특정 일정을 성공적으로 조회하는 경우"""
    schedule_data = {"title": "상세 조회용 일정", "date": "2025-11-15"}
    create_response = await client.post(
        "/api/v1/schedules/", 
        json=schedule_data,
        cookies=authenticated_user_cookie,
    )
    schedule_id = create_response.json()["id"]
    
    response = await client.get(
        f"/api/v1/schedules/{schedule_id}", cookies=authenticated_user_cookie
    )
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == schedule_id
    assert response_data["title"] == schedule_data["title"]
    
@pytest.mark.asyncio
async def test_get_schedule_by_id_not_found(client: AsyncClient, authenticated_user_cookie: dict[str, str]):
    """존재하지 않는 ID로 일정을 조회하는 경우"""
    non_existent_id = 99999
    response = await client.get(
        f"/api/v1/schedules/{non_existent_id}", cookies=authenticated_user_cookie
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_get_schedule_by_id_not_owner(
    client: AsyncClient, authenticated_user_cookie: dict[str, str], db_session: AsyncSession):
    """다른 사용자의 일정을 조회하려고 시도하는 경우 (보안 테스트)"""
    from app.repositories.user_repo import UserRepository
    from app.schemas.user import UserCreate
    
    user_repo = UserRepository(db_session)
    user_b_data = UserCreate(email="user_b@example.com", password="password_b1@")
    user_b = await user_repo.create(user_b_data)
    
    login_b_data = {"username": user_b.email, "password": "password_b1@"}
    login_b_response = await client.post("/api/v1/auth/login", data=login_b_data)
    cookie_b = login_b_response.cookies
    
    schedule_b_data = {"title": "사용자 B의 일정", "date": "2025-11-16"}
    create_b_response = await client.post(
         "/api/v1/schedules/", json=schedule_b_data, cookies=cookie_b
    )
    schedule_b_id = create_b_response.json()["id"]
    
    response = await client.get(
        f"/api/v1/schedules/{schedule_b_id}", cookies=authenticated_user_cookie
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
#===========================================================================================
#========================= 일정 수정 테스트 ==================================================
@pytest.mark.asyncio
async def test_update_schedule_success(client: AsyncClient, authenticated_user_cookie: dict[str, str]):
    """자신이 소유한 일정을 성공적으로 수정하는 경우"""
    schedule_data = {"title": "수정 전 제목", "date": "2025-11-17"}
    create_response = await client.post(
        "/api/v1/schedules/", 
        json=schedule_data,
        cookies=authenticated_user_cookie,
    )
    schedule_id = create_response.json()["id"]
    
    update_data = {"title": "수정 후 제목", "content": "내용이 수정되었습니다."}
    
    response = await client.put(
        f"/api/v1/schedules/{schedule_id}", json=update_data, cookies=authenticated_user_cookie
    )
    
    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    print(f"{response_data['title']}, {response_data['content']}")
    assert response_data["title"] == update_data["title"]
    assert response_data["content"] == update_data["content"]
    
@pytest.mark.asyncio
async def test_update_schedule_not_owner(
    client: AsyncClient, authenticated_user_cookie: dict[str, str], db_session: AsyncSession):
    """다른 사용자의 일정을 수정하려고 시도하는 경우"""
    from app.repositories.user_repo import UserRepository
    from app.schemas.user import UserCreate
    
    user_repo = UserRepository(db_session)
    user_b_data = UserCreate(email="user_b@example.com", password="password_b1@")
    user_b = await user_repo.create(user_b_data)
    
    login_b_data = {"username": user_b.email, "password": "password_b1@"}
    login_b_response = await client.post("/api/v1/auth/login", data=login_b_data)
    cookie_b = login_b_response.cookies
    
    schedule_b_data = {"title": "사용자 B의 일정", "date": "2025-11-17"}
    create_b_response = await client.post(
         "/api/v1/schedules/", json=schedule_b_data, cookies=cookie_b
    )
    schedule_b_id = create_b_response.json()["id"]
    
    update_data = {"title": "해킹 시도"}
    response = await client.put(
        f"/api/v1/schedules/{schedule_b_id}", json=update_data, cookies=authenticated_user_cookie
    )
    
    assert response.status_code == status.HTTP_404_NOT_FOUND
    
#===========================================================================================
#========================= 일정 삭제 테스트 ==================================================
@pytest.mark.asyncio
async def test_delete_schedule_success(client: AsyncClient, authenticated_user_cookie: dict[str, str]):
    """자신이 소유한 일정을 성공적으로 삭제하는 경우"""
    schedule_data = {"title": "삭제될 일정", "date": "2025-11-18"}
    create_response = await client.post(
        "/api/v1/schedules/", 
        json=schedule_data,
        cookies=authenticated_user_cookie,
    )
    schedule_id = create_response.json()["id"]
    
    delete_response = await client.delete(
        f"/api/v1/schedules/{schedule_id}", cookies=authenticated_user_cookie
    )
    
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    
    get_response = await client.get(
        f"/api/v1/schedules/{schedule_id}", cookies=authenticated_user_cookie
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

@pytest.mark.asyncio
async def test_delete_schedule_not_found(client: AsyncClient, authenticated_user_cookie: dict[str, str]):
    """존재하지 않는 ID로 일정 삭제를 시도하는 경우"""
    non_existent_id = 99988
    response = await client.delete(
        f"/api/v1/schedules/{non_existent_id}", cookies=authenticated_user_cookie
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND

#===========================================================================================