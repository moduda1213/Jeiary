import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from langchain_core.messages import HumanMessage, AIMessage
from app.services.ai_agent import AIAgent

@pytest.mark.asyncio
async def test_ai_agent_run_flow():
    """
        AIAgent.run() 메서드의 전체 흐름을 검증합니다.
        1. MemoryService에서 history 로드
        2. Chain 실행 (입력 + history 주입)
        3. 결과 반환 및 MemoryService에 저장
    """
    mock_memory_service = AsyncMock()
    
    # 메모리 객체 Mocking
    mock_memory_obj = MagicMock()
    mock_memory_obj.aload_memory_variables = AsyncMock(return_value = {
        "history": [HumanMessage(content="이전 대화"), AIMessage(content="네, 알겠습니다.")]
    })
    mock_memory_service.get_memory.return_value = mock_memory_obj
    
    # ChatOllama가 __init__에서 실제 연결을 시도하지 않도록 Patch
    with patch("app.services.ai_agent.ChatOllama") as MockOllama:
        agent = AIAgent(mock_memory_service)
        
        # 내부 Chain을 Mocking하여 실제 LLM 호출 방지
        agent.chain = AsyncMock()
        agent.chain.ainvoke.return_value = "AI 응답입니다."
        
        user_id = 1
        user_message = "안녕하세요"
        response = await agent.run(user_id, user_message)
        
        assert response == "AI 응답입니다."
        
        mock_memory_service.get_memory.assert_called_once_with(user_id)
        mock_memory_obj.aload_memory_variables.assert_called_once()
        
        agent.chain.ainvoke.assert_called_once()
        call_args = agent.chain.ainvoke.call_args[0][0]
        assert call_args["input"] == user_message
        assert len(call_args["history"]) == 2
        
        mock_memory_service.save_context.assert_called_once_with(
            user_id = user_id,
            inputs = {"input": user_message},
            outputs = {"output": "AI 응답입니다."}
        )