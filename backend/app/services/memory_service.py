from langchain.memory import ConversationBufferWindowMemory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from app.repositories.chat_repo import ChatRepository
from app.models.chat import ChatRole

class MemoryService:
    """
    LangChain의 Memory 컴포넌트와 Jeiary의 ChatRepository를 연결하는 서비스
    """
    def __init__(self, chat_repo: ChatRepository):
        self.chat_repo = chat_repo
        
    async def get_memory(self, user_id: int, k: int = 10) -> ConversationBufferWindowMemory:
        """
        사용자의 최근 대화 내역을 조회하여 LangChain Memory 객체로 변환
        
        Args:
            user_id: 사용자 ID
            k: 기억할 대화 턴의 수(default 10)
        
        Returns:
            ConversationBufferMemory: 초기화된 메모리 객체
        """    
        recent_chats = await self.chat_repo.get_recent_chats(user_id, limit=k*2)
        
        sorted_chats = sorted(recent_chats, key=lambda x: x.created_at)
        
        # 변환: DB 모델 -> LangChain 메세지 객체
        history = ChatMessageHistory()
        for chat in sorted_chats:
            if chat.role == ChatRole.USER:
                history.add_message(HumanMessage(content=chat.content))
            elif chat.role == ChatRole.ASSISTANT:
                history.add_message(AIMessage(content=chat.content))
            elif chat.role == ChatRole.SYSTEM:
                history.add_message(SystemMessage(content=chat.content))
                
        # 메모리 객체 생성
        # return_messages=True : 문자열이 아닌 메세지 객체 리스트로 반환
        return ConversationBufferWindowMemory(
            chat_memory=history,
            k=k,
            return_messages=True
        )
        
    async def save_context(self, user_id: int, inputs: dict[str, str], outputs: dict[str, str]) -> None:
        """
        LangChain 체인 실행 후 발생한 대화를 DB에 저장
        
        Args:
            user_id: 사용자 ID
            inputs: 체인 입력
            outputs: 체인 출력
        """
        # LangChain은 설정에 따라 입력 키가 'input', 'question' 등으로 다를 수 있음
        user_msg = inputs.get("input") or inputs.get("question")
        
        ai_msg = outputs.get("output") or outputs.get("text") or outputs.get("response")
        
        if user_msg:
            await self.chat_repo.create(user_id=user_id, role=ChatRole.USER, content=user_msg)
        
        if ai_msg:
            await self.chat_repo.create(user_id=user_id, role=ChatRole.ASSISTANT, content=ai_msg)