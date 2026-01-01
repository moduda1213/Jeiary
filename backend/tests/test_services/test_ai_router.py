import pytest
from app.services.ai_router import AIRouter

@pytest.mark.asyncio
async def test_router_tool_selection():
    """
    [Integration] 실제 Ollama가 도구를 올바르게 선택하는지 검증
    (로컬 Ollama 실행 필요)
    """
    router = AIRouter()
    
    # 1. 일정 생성 요청
    message = "내일 오후 2시에 팀 미팅 일정 잡아줘"
    result = await router.route_request(message)
    
    print(f"\n[Create] Input: {message}")
    print(f"[Create] Tool Calls: {result['tool_calls']}")
    
    assert len(result["tool_calls"]) > 0
    assert result["tool_calls"][0]["name"] == "CreateScheduleTool"
    
    # 2. 일반 대화
    message_chat = "안녕, 오늘 날씨 어때?"
    result_chat = await router.route_request(message_chat)
    
    print(f"\n[Chat] Input: {message_chat}")
    print(f"[Chat] Tool Calls: {result_chat['tool_calls']}")
    
    assert len(result_chat["tool_calls"]) > 0
    assert result_chat["tool_calls"][0]["name"] == "GeneralChatTool"
    