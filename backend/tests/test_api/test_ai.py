import pytest
from fastapi import status
from datetime import date as dateType, time
from httpx import AsyncClient
from unittest.mock import AsyncMock

from app.main import app
from app.dependencies import get_current_user, get_ai_service
from app.models.user import User
from app.services.ai_service import AIService
from app.schemas.ai import AIParsedSchedule, AIParseResponse
from app.core.exceptions import AIConnectionError, AIParsingError, CredentialException

pytestmark = pytest.mark.asyncio

TEST_USER = User(
    id=1,
    email="testuser@example.com",
    password_hash="hashed_password",
)

@pytest.fixture
def mock_ai_service() -> AsyncMock:
    """AIService에 대한 모의 객체를 생성하고 반환"""
    return AsyncMock(spec=AIService)

@pytest.fixture(autouse=True)
async def override_dependencies(mock_ai_service: AsyncMock):
    """모든 테스트에 대해 의존성을 모의 객체로 오버라이드"""
    async def override_get_current_user():
        return TEST_USER
    
    def override_get_ai_service():
        return mock_ai_service
    
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[get_ai_service] = override_get_ai_service
    yield
    app.dependency_overrides.clear()
    
async def test_parse_text_with_ai_authenticated_success(client: AsyncClient, mock_ai_service: AsyncMock):
    """인증된 사용자가 유효한 텍스트를 보냈을 때 AI가 성공적으로 파싱하는지 테스트."""
    expected_schedule = AIParsedSchedule(
        title="테스트 일정",
        date=dateType(2025,12,25),
        start_time=time(19,0),
        end_time=time(21,0),
        content="가족과 함께",
    )
    mock_ai_service.parse_schedule_from_text.return_value = expected_schedule
    
    response = await client.post(
        "/api/v1/ai/parse",
        json={"text": "크리스마스에 가족이랑 저녁 7시부터 2시간 동안 식사"}
    )
    assert response.status_code == status.HTTP_200_OK
    parsed_response = AIParseResponse(**response.json())
    assert parsed_response.is_complete is True
    assert parsed_response.data == expected_schedule
    assert parsed_response.question is None
    
async def test_parse_text_with_ai_authenticated_question(client: AsyncClient, mock_ai_service: AsyncMock):
    """인증된 사용자가 텍스트를 보냈을 때 AI가 추가 질문을 반환하는지 테스트"""
    expected_question = "저녁 몇 시에 시작하나요?"
    mock_ai_service.parse_schedule_from_text.return_value = expected_question
    
    response = await client.post("/api/v1/ai/parse", json={"text": "내일 저녁에 회식"})
    
    assert response.status_code == status.HTTP_200_OK
    parsed_response = AIParseResponse(**response.json())
    assert parsed_response.is_complete is False
    assert parsed_response.question == expected_question
    
async def test_parse_text_with_ai_authenticated(client: AsyncClient):
    """인증되지 않는 사용자가 /ai/parse 엔드포인트에 접근하는 경우를 테스트"""
    app.dependency_overrides[get_current_user] = lambda: (_ for _ in ()).throw(CredentialException("Token required"))
    
    response = await client.post("/api/v1/ai/parse", json={"text": "아무 텍스트"})
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert "Token required" in response.json()["detail"]
    
    app.dependency_overrides.clear()
    
async def test_parse_text_with_ai_authenticated_connection_error(client: AsyncClient, mock_ai_service: AsyncMock):
    """AI 서비스 연결 오류가 발생했을 때 503 에러를 반환하는지 테스트"""
    mock_ai_service.parse_schedule_from_text.side_effect = AIConnectionError("Ollama 서버 연결 실패")
    
    response = await client.post("/api/v1/ai/parse", json={"text": "아무 텍스트"})
    
    assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
    assert "AI 서비스 연결 오류: Ollama 서버 연결 실패" in response.json()["detail"]

            
async def test_parse_text_with_ai_authenticated_parsing_error(client: AsyncClient, mock_ai_service: AsyncMock):
    """AI 응답 파싱 오류가 발생했을 때 400 에러를 반환하는지 테스트"""
    mock_ai_service.parse_schedule_from_text.side_effect = AIParsingError("AI 응답 포맷 오류")
    
    response = await client.post("/api/v1/ai/parse", json={"text": "아무 텍스트"})
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "AI 응답 파싱 오류: AI 응답 포맷 오류" in response.json()["detail"]