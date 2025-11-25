from fastapi import APIRouter, Depends, HTTPException, status, Body
from app.schemas.ai import AITextRequest, AIParsedSchedule, AIParseResponse
from app.dependencies import CurrentUserDep, AIServiceDep
from app.core.exceptions import AIConnectionError, AIParsingError

router = APIRouter(prefix="/ai", tags=["AI"])

@router.post(
    "/parse",
    response_model=AIParseResponse,
    summary="AI를 사용하여 텍스트를 일정으로 파싱",
    description="인증된 사용자로부터 자연어 텍스트를 받아 AI가 파싱한 일정 데이터 또는 추가 질문을 반환합니다.",
    status_code=status.HTTP_200_OK
)
async def parse_text_with_ai(
    request: AITextRequest,
    user: CurrentUserDep,
    ai_serivce: AIServiceDep
) -> AIParseResponse:
    """
    사용자 텍스트를 AI에게 전달하여 일정을 파싱하고 그 결과를 반환합니다.
    AI가 추가 정보가 필요할 경우 질문을 반환
    """
    try:
        result = await ai_serivce.parse_schedule_from_text(request.text)
        
        if isinstance(result, AIParsedSchedule):
            return AIParseResponse(is_complete=True, data=result, question=None)
        else:
            return AIParseResponse(is_complete=False, data=None, question=result)
    
    except AIConnectionError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"AI 서비스 연결 오류: {e}"
        )
    except AIParsingError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"AI 응답 파싱 오류: {e}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"예상치 못한 서버 오류가 발생했습니다.: {e}"
        )