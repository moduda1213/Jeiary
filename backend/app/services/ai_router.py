from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.tools import tool

from app.config import settings
from app.core.tools import CreateScheduleTool, UpdateScheduleTool, DeleteScheduleTool, GeneralChatTool

class AIRouter:
    def __init__(self):
        """
        AI Router 초기화
        - ChatOllama 모델 설정
        - 도구(Tools) 바인딩
        """
        # 1. LLM 초기화
        # function calling을 잘 지원하는 모델 권장
        self.llm = ChatOllama(
            model = settings.OLLAMA_MODEL,
            base_url = settings.OLLAMA_BASE_URL,
            temperature = 0.1,
        )
        
        # 2. tools 리스트 정의
        # pydantic 모델을 LangChain Tool로 변환하지 않고 구조체 그대로 바인딩할 수도 있지만,
        # 최신 LangChain Ollama는 .bind_tools() 메서드에 Pydantic 클래스를 직접 넣는 것을 지원
        self.tools = [
            CreateScheduleTool,
            UpdateScheduleTool,
            DeleteScheduleTool,
            GeneralChatTool
        ]
        
        # 3. 모델에 tools 바인딩
        # bind_tools: LLM에게 도구 스키마를 주입하는 핵심 메서드
        self.llm_with_tools = self.llm.bind_tools(self.tools)
        
        # 4. Few-Shot 프롬프트 적용
        system_message = """
            당신은 사용자의 의도를 판단하여 일정 관리 도구를 호출할지 결정하는 '라우터'입니다.
            
            [현재 시각 정보]
            {current_time}
            (사용자가 '오늘', '내일', '이번 주' 등을 언급하면 위 시간을 기준으로 날짜를 정확히 계산해서 도구 인자(date)에 넣으세요.)
            
            [규칙]
            1. 사용자가 [일정 생성, 일정 수정, 일정 삭제]를 명확히 요청할 때만 도구를 호출하세요.
            2. 인사, 날씨, 안부 묻기, 단순 잡담 등 일정과 무관한 대화에는 절대로 도구를 호출하지 마세요.
            3. 도구를 호출할 필요가 없다면, 아무런 도구도 선택하지 말고 텍스트로만 응답하세요.
            4. 날짜는 반드시 YYYY-MM-DD 형식, 시간은 HH:MM (24시간제) 형식을 엄수하세요.
            
            [Few-Shot 예시... [현재 시각 정보]: 2025-12-25 (목요일) 13:16]
            User: "내일 점심 약속 잡아줘"
            Assistant: CreateScheduleTool(title="점심 약속", date="2025-12-26", start_time="12:00", end_time="13:00")

            User: "오늘 저녁 7시에 운동 일정 추가"
            Assistant: CreateScheduleTool(title="운동", date="2025-12-25", start_time="19:00", end_time="20:00")

            User: "이번 주 토요일 회의 취소해줘"
            Assistant: DeleteScheduleTool(search_keyword="회의", date="2025-12-27")

            User: "안녕, 반가워"
            Assistant: 안녕하세요! 무엇을 도와드릴까요?
        """
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            ("human", "{input}")
        ])
        
        self.chain = self.prompt | self.llm_with_tools
        
    async def route_request(self, message: str) -> dict:
        """
        사용자의 메세지를 분석하여 도구 호출이 필요한지 판단합니다.

        Args:
            message (str): 사용자 입력

        Returns:
            dict: 실행 결과
        """
        # 현재 시간 계산
        from datetime import datetime
        now = datetime.now()
        current_time_str = now.strftime("%Y년 %m월 %d일 %H시 %M분 (%A)")
        
        # 도구 호출이 필요한지 LLM에게 물어봄 (단발성 추론)
        # current_time 변수 주입
        response = await self.chain.ainvoke({
            "input": message,
            "current_time": current_time_str
        })
        return response