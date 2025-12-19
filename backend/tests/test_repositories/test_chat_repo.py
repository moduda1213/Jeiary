import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.chat_repo import ChatRepository
from app.models.chat import ChatRole
from app.models.user import User

@pytest.mark.asyncio
async def test_create_chat_history(db_session: AsyncSession, test_user: User):
    """채팅 내역이 정상적으로 저장되는지 테스트"""
    repo = ChatRepository(db_session)
    
    # User 메세지 저장
    user_msg = await repo.create(
        user_id = test_user.id,
        role = ChatRole.USER,
        content = "Hello AI"
    )
    
    assert user_msg.id is not None
    assert user_msg.role == "user"
    assert user_msg.content == "Hello AI"
    
    # Assistant 메세지 저장
    ai_msg = await repo.create(
        user_id = test_user.id,
        role = ChatRole.ASSISTANT,
        content = "Hello User"
    )
    
    assert ai_msg.role == "assistant"
    
@pytest.mark.asyncio
async def test_get_recent_chats(db_session: AsyncSession, test_user: User):
    """최신 채팅 내역 조회 및 Limit 동작 테스트"""
    repo = ChatRepository(db_session)
    
    for i in range(10):
        await repo.create(test_user.id, ChatRole.USER, f"msg {i}")
    
    recent_chats = await repo.get_recent_chats(test_user.id, limit=5)
    
    assert len(recent_chats) == 5
    assert recent_chats[0].content == "msg 9"
    
@pytest.mark.asyncio
async def test_delete_old_chat(db_session: AsyncSession, test_user: User):
    """(나중에 구현할 CleanUp을 위한) 소프트 삭제 테스트"""
    repo = ChatRepository(db_session)
    chat = await repo.create(test_user.id, ChatRole.USER, "to be deleted")
    
    delete_chat = await repo.delete(chat)
    assert delete_chat.is_deleted == True