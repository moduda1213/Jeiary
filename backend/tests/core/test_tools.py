import pytest
from pydantic import ValidationError
from app.core.tools import CreateScheduleTool, UpdateScheduleTool, DeleteScheduleTool

def test_create_schedule_tool_validation():
    """
    [Unit] 일정 생성 도구의 입력값 검증 테스트
    """
    valid_data = {
        "title": "팀 회의",
        "date": "2025-12-25",
        "start_date": "14:00",
        "end_time": "15:00",
        "content": "4분기 리뷰"
    }
    tool = CreateScheduleTool(**valid_data)
    assert tool.title == "팀 회의"
    assert tool.content == "4분기 리뷰"
    
    invalid_data = {
        "title": "팀 회의",
        "date": "2025-12-25",
        "start_date": "14:00",
    }
    with pytest.raises(ValidationError):
        CreateScheduleTool(**invalid_data)
        
def test_update_schedule_tool_optional_fields():
    """
    [Unit] 일정 수정 도구는 필드가 선택적이어야 함
    """
    # 1. ID만 있고 변경할 필드가 없는 경우
    tool = UpdateScheduleTool(schedule_id=1)
    assert tool.schedule_id == 1
    assert tool.title is None
    
    # 2. 검색어로 찾아서 날짜만 변경하는 경우
    tool = UpdateScheduleTool(search_keyword="점심", date="2025-12-26")
    assert tool.search_keyword == "점심"
    assert tool.date == "2025-12-26"
    assert tool.start_time is None
    
def test_delete_schedule_tool_validation():
    """
    [Unit] 일정 삭제 도구 검증
    """
    tool = DeleteScheduleTool(schedule_id=10)
    assert tool.schedule_id == 10
    
    tool = DeleteScheduleTool(search_keyword="취소할 회의")
    assert tool.search_keyword == "취소할 회의"