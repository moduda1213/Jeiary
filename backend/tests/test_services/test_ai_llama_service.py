import pytest
from unittest.mock import AsyncMock
from tenacity import RetryError

from app.services.ai_service import AIService
from backend.app.schemas.ai import AIParsedSchedule
from app.core.exceptions import AIConnectionError, AIParsingError

pytestmark = pytest.mark.asyncio

async def test_parse_schedule_from_text_success(mocker):
    """
    AI가 유효한 JSON을 포함한 답변을 반환했을 때, 성공적으로 파싱하는지 테스트
    """
    mock_ai_response = {
        "message": {
            "content": """
                [체크리스트]
                - 날짜 정보: 있음
                - 시작 시간 숫자: 있음
                - 제목/목적: 있음

                [판단]
                모든 정보 있음 → JSON 답변

                [답변]
                {
                    'date': '2025-12-25',
                    'start_time': '19:00',
                    'end_time': '21:00',
                    'title': '크리스마스 저녁 식사',
                    'content': '가족과 함께'
                }
            """
        }
    }
    mocker.patch(
        "ollama.AsyncClient.chat",
        return_value=mock_ai_response
    )
    
    service = AIService()
    result = await service.parse_schedule_from_text("크리스마스에 가족이랑 저녁 7시부터 2시간 동안 식사")

    assert isinstance(result, AIParsedSchedule)
    assert result.title == "크리스마스 저녁 식사"
    assert result.date.isoformat() == "2025-12-25"
    assert result.start_time.strftime('%H:%M') == "19:00"
    
async def test_parse_schedule_from_text_needs_clarification(mocker):
    """
    AI가 정보가 부족하여 추가 질문을 반환했을 때, 해당 질문을 문자열로 잘 반환하는지 테스트
    """
    mock_ai_response = {
        "message": {
            "content": """
                [체크리스트]
                - 날짜 정보: 있음
                - 시작 시간 숫자: 없음
                - 제목/목적: 있음

                [판단]
                시작 시간 숫자가 없으므로 → 질문

                [답변]
                저녁 몇 시에 시작하나요?
            """
        }
    }
    mocker.patch(
        "ollama.AsyncClient.chat",
        return_value=mock_ai_response
    )

    service = AIService()
    result = await service.parse_schedule_from_text("내일 저녁에 회식")

    assert isinstance(result, str)
    assert result == "저녁 몇 시에 시작하나요?"

async def test_parse_schedule_from_text_connection_error(mocker):
    """
    AI 서버 연결 시 재시도에 모두 실패했을 때, AIConnectionError를 발생시키는지 테스트
    """
    mocker.patch(
        "ollama.AsyncClient.chat",
        side_effect=RetryError("Connection failed")
    )

    service = AIService()
    with pytest.raises(AIConnectionError):
        await service.parse_schedule_from_text("아무 텍스트")