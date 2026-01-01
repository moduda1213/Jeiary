import pytest
from unittest.mock import AsyncMock
from app.services.memory_service import MemoryService
from app.models.chat import ChatHistory, ChatRole

# 최근 k개의 대화만 유지하는 메모리 클래스
from langchain.memory import ConversationBufferWindowMemory

@pytest.mark.asyncio
async def test_get_memory_loads_history():
    """
    DB에 저장된 채팅 내역을 LangChain Memory 객체로 올바르게 변환하는지 테스트
    """
    mock_chat_repo = AsyncMock()
    user_id = 1
    
    # DB에서 최신순(DESC)로 조회됨을 가정
    mock_chats = [
        ChatHistory(id=2, user_id=user_id, role=ChatRole.ASSISTANT.value, content="반갑습니다.", created_at="2025-12-19 10:01:00"),
        ChatHistory(id=1, user_id=user_id, role=ChatRole.USER.value, content="안녕", created_at="2025-12-19 10:00:00")
    ]
    mock_chat_repo.get_recent_chats.return_value = mock_chats
    
    service = MemoryService(mock_chat_repo)
    
    # 메모리 로드 요청
    memory = await service.get_memory(user_id)
    
    # 반환된 객체가 LangChain 메모리 클래스 인지
    assert isinstance(memory, ConversationBufferWindowMemory)
    
    # 메모리 내부의 chat_memory에 메세지가 시간순으로 정렬되어 들어갔는지
    messages = memory.chat_memory.messages
    assert len(messages) == 2
    
    # LangChain은 type="human"으로 관리
    assert messages[0].content == "안녕"
    assert messages[0].type == "human"
    
    # LangChain은 type="ai"으로 관리
    assert messages[1].content == "반갑습니다."
    assert messages[1].type == "ai"

@pytest.mark.asyncio
async def test_save_context_saves_to_db():
    """
    LangChain 스타일의 입/출력을 받아 DB에 저장하는 테스트
    """
    mock_chat_repo = AsyncMock()
    service = MemoryService(mock_chat_repo)
    user_id = 1
    
    inputs = {"input": "내일 날씨 어때?"}
    outputs = {"output": "맑을 예정입니다."}
    
    await service.save_context(user_id, inputs, outputs)
    
    assert mock_chat_repo.create.call_count == 2
    
    mock_chat_repo.create.assert_any_call(
        user_id = user_id,
        role = ChatRole.USER,
        content = "내일 날씨 어때?"
    )
    
    mock_chat_repo.create.assert_any_call(
        user_id = user_id,
        role = ChatRole.ASSISTANT,
        content = "맑을 예정입니다."
    )