import ollama
from loguru import logger
from datetime import datetime
from tenacity import retry, stop_after_attempt, wait_fixed

from app.config import settings
from app.core.exceptions import AIConnectionError
from app.schemas.schedule import ScheduleCreate, ScheduleUpdate
from app.schemas.ai import AIParsedSchedule
from app.repositories.user_repo import UserRepository
from app.repositories.chat_repo import ChatRepository
from app.models.schedule import Schedule
from app.models.user import User
from app.services.schedule_service import ScheduleService
from app.services.memory_service import MemoryService
from app.services.ai_agent import AIAgent
from app.services.ai_router import AIRouter

class AIService:
    
    def __init__(self, chat_repo: ChatRepository = None, schedule_service: ScheduleService = None, user_repo: UserRepository = None):
        """
        AIService 초기화
        """
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        self.chat_repo = chat_repo
        self.schedule_service = schedule_service
        self.user_repo = user_repo
        
        # chat_repo가 있을 때만 에이전트 기능을 활성화
        if self.chat_repo:
            self.memory_service = MemoryService(self.chat_repo)
            self.ai_agent = AIAgent(self.memory_service)
            self.ai_router = AIRouter()
        else:
            self.ai_agent = None
            self.ai_router = None
        
    @retry(
        stop=stop_after_attempt(3), # 최대 3번 재시도
        wait=wait_fixed(2) # 재시도 사이 2초 대기
    )
    async def _send_chat_request(self, model: str, messages: list) -> dict:
        """
        Ollam 서버에 실제 chat 요청을 보내는 내부 메서드
        """
        return await self.client.chat(model=model, messages=messages)
    
    async def _find_schedule(self, user: User, keyword: str | None, date_str: str | None) -> Schedule | None:
        """
        [Helper] 수정/삭제 대상을 찾기 위한 검색 메서드
        User 객체를 직접 받아 불필요한 DB 조회를 줄입니다.
        """
        if not self.schedule_service:
            return None
        # 1. 날짜 파싱 (필수)
        target_date = None
        if date_str:
            try:
                target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            except ValueError:
                return None # 날짜 형식이 아니면 검색 불가
        # 2. 검색 수행
        if target_date:
            # 해당 월의 모든 일정 조회 (이미 조회된 user 객체 사용)
            schedules = await self.schedule_service.get_schedule_by_month(user, target_date.year, target_date.month)
            
            # 해당 날짜로 1차 필터링
            daily_schedules = [s for s in schedules if s.date == target_date]
            
            logger.debug(f"daily_schedules: {daily_schedules}")
            
            if not daily_schedules:
                return None
            
            # 키워드가 있다면 제목(title)으로 2차 필터링
            if keyword:
                matched = [s for s in daily_schedules if keyword in s.title]
                return matched[0] if len(matched) == 1 else None
            
            # 키워드가 없다면, 그 날 일정이 딱 하나일 때만 반환 (모호성 방지)
            return daily_schedules[0] if len(daily_schedules) == 1 else None
        return None
    
    async def process_chat(self, user_id: int, message: str) -> str | AIParsedSchedule:
        """
        사용자의 채팅 메세지를 처리하고 응답을 생성합니다.
        1. 라우터로 의도 파악
        2. 도구(tool) 호출 시 해당 기능 실행
        3. 일반 대화 시 AIAgent 실행
        """
        if not self.ai_agent or not self.ai_router:
            raise AIConnectionError("AI 기능이 활성화되지 않았습니다. (ChatRepository 필요)")
        try:
            # 1. 라우팅 (의도 파악)
            route_result = await self.ai_router.route_request(message)
            
            # LangChain AIMessage 객체에서 tool_calls 속성 접근
            tool_calls = getattr(route_result, 'tool_calls', [])
            logger.debug(f"tool_calls: {tool_calls}")
            
            # 2. 도구 실행 로직
            if tool_calls:
                # 첫 번째 도구만 처리 (복잡도 관리)
                tool_call = tool_calls[0]
                tool_name = tool_call["name"]
                args = tool_call["args"]
                
                logger.debug(f"Tool Call Detected: {tool_name} | Args: {args}")
                # [최적화] 일반 대화가 아니라면 User 객체를 미리 조회하여 재사용
                if tool_name != "GeneralChatTool":
                    if not self.user_repo or not self.schedule_service:
                        return "일정 관리 서비스를 사용할 수 없는 상태입니다."
                    
                    user = await self.user_repo.get(user_id)
                    if not user:
                        return "사용자 정보를 찾을 수 없습니다."
                    
                    # [Case A] 일정 생성 요청
                    if tool_name == "CreateScheduleTool":
                        try:
                            date_str = args.get("date")
                            start_time_str = args.get("start_time")
                            end_time_str = args.get("end_time")
                            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                            start_time_obj = datetime.strptime(start_time_str, "%H:%M").time()
                            end_time_obj = datetime.strptime(end_time_str, "%H:%M").time()
                            
                            schedule_data = ScheduleCreate(
                                title = args.get("title"),
                                date = date_obj,
                                start_time = start_time_obj,
                                end_time = end_time_obj,
                                content = args.get("content")
                            )
                            
                            # DB 즉시 저장 (user 객체 재사용)
                            new_schedule = await self.schedule_service.create_schedule(schedule_data, user)
                            logger.info(f"AI Auto-Save: Schedule {new_schedule.id} created.")
                            
                            return AIParsedSchedule(
                                title = new_schedule.title,
                                date = new_schedule.date,
                                start_time = new_schedule.start_time,
                                end_time = new_schedule.end_time,
                                content = new_schedule.content
                            )
                            
                        except ValueError as ve:
                            logger.error(f"Date/Time Parsing Error: {ve}")
                            return "날짜 또는 시간 형식이 올바르지 않습니다. (YYYY-MM-DD, HH:MM)"
                        
                        except Exception as e:
                            logger.error(f"Schedule Creation Failed: {e}")
                            return f"일정 생성 중 오류가 발생했습니다: {str(e)}"
                        
                    # [Case B] 일정 수정 요청
                    elif tool_name == "UpdateScheduleTool":
                        try:
                            target = await self._find_schedule(
                                user,
                                args.get("search_keyword"),
                                args.get("date")
                            )
                            
                            if not target:
                                return "수정할 일정을 찾을 수 없습니다. (날짜와 키워드를 정확히 말씀해 주세요)"
                            
                            # 업데이트 데이터 구성
                            update_data = ScheduleUpdate()
                            if args.get("title"): update_data.title = args.get("title")
                            if args.get("content"): update_data.content = args.get("content")
                            if args.get("date"): update_data.date = datetime.strptime(args.get("date"), "%Y-%m-%d").date()
                            if args.get("start_time"): update_data.start_time = datetime.strptime(args.get("start_time"), "%H:%M").time()
                            if args.get("end_time"): update_data.end_time = datetime.strptime(args.get("end_time"), "%H:%M").time()
                            
                            updated_schedule = await self.schedule_service.update_schedule(target.id, update_data, user)
                            return f"일정이 수정되었습니다: {updated_schedule.title}"
                        
                        except Exception as e:
                            logger.error(f"Schedule Update Failed: {e}")
                            return f"일정 수정 중 오류가 발생했습니다: {str(e)}"
                        
                    # [Case C] 일정 삭제 요청
                    elif tool_name == "DeleteScheduleTool":
                        try:
                            target = await self._find_schedule(
                                user,
                                args.get("search_keyword"),
                                args.get("date")
                            )
                            
                            if not target:
                                return "삭제할 일정을 찾을 수 없습니다."
                            
                            await self.schedule_service.delete_schedule(target.id, user)
                            return f"일정이 삭제되었습니다: {target.title}"
                        
                        except Exception as e:
                            logger.error(f"Schedule Delete Failed: {e}")
                            return f"일정 삭제 중 오류가 발생했습니다: {str(e)}"
                        
                # [Case D] 일반 대화 (GeneralChatTool)
                elif tool_name == "GeneralChatTool":
                    return await self.ai_agent.run(user_id, message)
                
            # 3. 도구가 없거나 매칭되지 않으면 일반 대화로 처리
            return await self.ai_agent.run(user_id, message)
        
        except Exception as e:
            logger.error(f"AI Chat Error: {e}")
            raise AIConnectionError(f"대화 처리 중 오류가 발생했습니다: {e}")
        
    async def generate_briefing(self, schedules: list[Schedule]) -> str:
        """
        사용자의 일정 리스트를 바탕으로 AI 요약 브리핑을 생성합니다.
        """
        if not schedules:
            return "오늘은 예정된 일정이 없습니다. 편안한 하루 보내세요."
        
        # 일정 데이터를 텍스트로 변환
        schedule_texts = []
        for s in schedules:
            time_str = f"{s.start_time.strftime('%H:%M')} ~ {s.end_time.strftime('%H:%M')}"
            schedule_texts.append(f"- {s.title} ({time_str})")
            
        schedule_context = "\n".join(schedule_texts)
        
        # 브리핑 전용 프롬프트 생성
        prompt = f"""
            당신은 상냥한 개인 비서입니다. 아래는 사용자의 오늘 일정입니다.
            이 일정들을 바탕으로 사용자가 기분 좋게 하루를 시작할 수 있는 '모닝 브리핑' 메시지를 작성해주세요.
            
            [오늘 일정]
            {schedule_context}
            
            [작성 규칙]
            1. 시간 순서대로 요약해서 언급해주세요.
            2. 말투는 정중하고 활기차게 해주세요.
            3. 마지막에는 응원의 한마디를 덧붙여주세요.
            4. 분량은 3~5문장 정도로 간결하게 작성하세요.
        """
        
        try:
            response = await self._send_chat_request(
                model = settings.OLLAMA_MODEL,
                messages = [{"role": "user", "content": prompt}]
            )
            return response["message"]["content"]
        
        except Exception as e:
            logger.error(f"Failed to generate briefing: {e}")
            return f"오늘 총 {len(schedules)}개의 일정이 있습니다.\n{schedule_context}"