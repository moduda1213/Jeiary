# 실제 DB와 로컬 Ollama를 연결하여 멀티턴 대화가 실제로 작동하는지 검증
import pytest
from app.services.ai_service import AIService
from app.repositories.chat_repo import ChatRepository
from app.models.chat import ChatRole

# 실제 DB 세션과 함께 실행
@pytest.mark.asyncio
async def test_multi_turn_conversation_integration(db_session, test_user):
    """
    [통합 테스트] 실제 DB와 Ollama를 연동하여 멀티턴 대화 검증
    주의: 로컬에 Ollama가 실행 중이어야 합니다.
    """
    chat_repo =ChatRepository(db_session)
    ai_service = AIService(chat_repo)
    user_id = test_user.id
    
    input_1 = f"내 이름은 {test_user.email}야 기억해줘."
    response_1 = await ai_service.process_chat(user_id, input_1)
    
    assert response_1 is not None
    assert len(response_1) > 0
    
    input_2 = "방금 내가 내 이름이 뭐라고 했지?"
    response_2 = await ai_service.process_chat(user_id, input_2)
    
    print(f"User: {input_2}")
    print(f"AI: {response_2}")
    
    assert test_user.email in response_2 or "이메일" in response_2
    
    saved_chats = await chat_repo.get_recent_chats(user_id, limit=10)
    assert len(saved_chats) >= 4
    
    last_ai_msg = saved_chats[0]
    if last_ai_msg.role == ChatRole.ASSISTANT:
        assert last_ai_msg.content == response_2