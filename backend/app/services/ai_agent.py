from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

from app.config import settings
from app.services.memory_service import MemoryService

class AIAgent:
    def __init__(self, memory_serivce: MemoryService):
        """
        AIAgent 초기화
        
        Args:
            memory_service: 대화 내역 관리를 위한 서비스
        """
        self.memory_service = memory_serivce
        
        # LLM 초기화(Ollama)
        self.llm = ChatOllama(
            model = settings.OLLAMA_MODEL,
            base_url = settings.OLLAMA_BASE_URL,
            temperature = 0.7
        )
        
        # 프롬프트 템플릿 설정
        # system: 역할 부여
        # history: 이전 대화 내역 삽입 위치 (MessagesPlaceholder 사용)
        # input: 현재 사용자 입력
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "당신은 사용자의 일정을 관리하고 돕는 친절하고 유능한 AI 비서 'Jeiary'입니다. 한국어로 자연스럽게 대답하세요."),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        # LCEL Chain 구성: Prompt -> LLM -> String Output
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    async def run(self, user_id: int, message: str) -> str:
        """
        사용자 메세지를 처리하고 AI 응답을 반환합니다.

        Args:
            user_id (int): 사용자 ID
            message (str): 사용자 입력 메세지

        Returns:
            str: AI 응답 메세지
        """
        # 1. 이전 대화 내역 로드 (LangChain Memory 객체 -> 메세지 리스트)
        memory = await self.memory_service.get_memory(user_id)
        # load_memory_variables는 dict 반환 ( e.g. {'history': [...]})
        memory_vars = await memory.aload_memory_variables({})
        history = memory_vars.get("history", [])
        
        # 2. Chain 실행
        # history와 input을 프롬프트에 주입
        response_text = await self.chain.ainvoke({
            "history": history,
            "input": message
        })
        
        # 3. 대화 내역 저장
        # 사용자의 입력과 AI의 응답을 DB에 저장
        await self.memory_service.save_context(
            user_id = user_id,
            inputs = {"input": message},
            outputs = {"output": response_text}
        )
        return response_text