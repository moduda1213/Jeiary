from pydantic import BaseModel, Field
from datetime import date as DateType, time as TimeType

class AIParsedSchedule(BaseModel):
    """
    AI에 의해 파싱된 일정 정보 응답 스키마
    Modelfile의 시스템 프롬프트에서 정의한 JSON 형식과 일치해야 합니다.
    """
    title: str = Field(..., description="파싱된 일정 제목")
    date: DateType = Field(..., description="파싱된 날짜 (YYYY-MM-DD)")
    content: str | None = Field(None, description="파싱된 내용")
    start_time: TimeType = Field(..., description="파싱된 시작 시간 (HH:MM)")
    end_time: TimeType = Field(..., description="파싱된 종료 시간 (HH:MM)")

class AITextRequest(BaseModel):
    """ AI 텍스트 파싱을 위한 요청 스키마"""
    text: str = Field(..., min_length=1, description="AI가 파싱할 자연어 텍스트")
    
class AIParseResponse(BaseModel):
    """AI 파싱 결과 응답"""
    is_complete: bool = Field(...,description="일정 정보 파싱이 완료되었는지 여부")
    data: AIParsedSchedule | None = Field(None, description="파싱 완료된 일정 데이터 (is_complete가 false이면 null)")
    question: str | None = Field(None, description="정보가 부족하여 AI가 되묻는 질문 (is_complete가 true이면 null)")
