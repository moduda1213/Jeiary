from pydantic import BaseModel, Field

class CreateScheduleTool(BaseModel):
    """
    일정을 새로 생성할 때 사용하는 도구입니다.
    사용자가 '약속 잡아줘', '일정 추가해줘' 등의 요청을 할 때 사용됩니다.
    """
    title: str = Field(description="일정의 제목 또는 핵심 내용 (예: '점심 약속', '팀 회의')")
    date: str = Field(description="일정 날짜 (YYYY-MM-DD 형식)")
    start_time: str = Field(description="시작 시간 (HH:MM 형식, 24시간제)")
    end_time: str = Field(description="종료 시간 (HH:MM 형식, 24시간제). 명시되지 않으면 시작 시간 +1시간으로 계산하세요.")
    content: str | None = Field(default=None, description="일정의 상세 내용, 장소, 또는 메모")

class UpdateScheduleTool(BaseModel):
    """
    기존 일정을 수정할 때 사용하는 도구입니다.
    사용자가 '시간 바꿔줘', '날짜 미뤄줘' 등의 요청을 할 때 사용됩니다.
    """
    search_keyword: str | None = Field(default=None, description="일정을 찾기 위한 검색어 (예: '점심', '회의')")
    
    # 수정할 필드들 (Optional)
    title: str | None = Field(default=None, description="변경할 제목")
    date: str | None = Field(default=None, description="변경할 날짜 (YYYY-MM-DD)")
    start_time: str | None = Field(default=None, description="변경할 시작 시간 (HH:MM)")
    end_time: str | None = Field(default=None, description="변경할 종료 시간 (HH:MM)")
    content: str | None = Field(default=None, description="변경할 상세 내용")

class DeleteScheduleTool(BaseModel):
    """
    일정을 삭제할 때 사용하는 도구입니다.
    """
    search_keyword: str | None = Field(default=None, description="ID를 모를 경우, 삭제할 일정을 찾기 위한 검색어")
    
class GeneralChatTool(BaseModel):
    """
    일정 관리와 무관한 일반적인 대화, 인사, 질문 등에 사용합니다.
    사용자가 '안녕', '날씨 어때?', '심심해' 등의 말을 할 때 이 도구를 선택하세요.
    """
    response: str = Field(description="사용자에게 건넬 적절한 대답")
    