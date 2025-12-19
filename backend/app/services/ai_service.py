import ollama
import json
import re
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError

from app.config import settings
from app.schemas.ai import AIParsedSchedule
from app.repositories.chat_repo import ChatRepository
from app.models.chat import ChatRole
from app.models.schedule import Schedule

from app.core.exceptions import AIConnectionError, AIParsingError

from loguru import logger

settings = settings

# TODO. 추후 변경 OR 삭제 예정 
SYSTEM_PROMPT = """
    당신은 일정 관리 비서입니다. 사용자의 입력을 분석하여 정확한 JSON 데이터를 추출하거나, 정보가 부족하면 질문을 하세요.

    # [1] 시간/날짜 참조 정보 (이 정보를 바탕으로 날짜를 매핑하세요)
    {date_context}

    # [2] 중요 규칙
    1. **제목(Title) 추출:** 사용자가 하려는 행동(예: 식사, 회의, 병원, 운동)을 그대로 'title'에 넣으세요. 절대 null로 두지 마세요.
    2. **종료 시간(End Time):** 사용자가 종료 시간을 말하지 않았다면, **시작 시간 + 1시간**으로 자동 설정하세요.
    3. **오전/오후 판단:** '7시'라고만 하면 문맥을 보십시오. (식사/술 -> 오후 19:00, 조찬/등교 -> 오전 07:00). 불확실하면 질문하세요.

    # [3] Few-shot 예시 (이 패턴을 따라하세요)

    예시 1 (제목 추출 및 종료 시간 자동 계산):
    입력: "오늘 저녁 7시에 가족과 식사약속 있어"
    출력:
    {{
    "date": "2025-12-04",
    "start_time": "19:00",
    "end_time": "20:00",
    "title": "가족과 식사약속",
    "content": null
    }}

    예시 2 (날짜 매핑):
    입력: "이번주 일요일 아침 9시 축구"
    출력: (참조 정보에서 '이번주 일요일' 날짜를 찾아 입력)
    {{
    "date": "2025-12-07",
    "start_time": "09:00",
    "end_time": "11:00",
    "title": "축구",
    "content": "일반적으로 운동은 2시간으로 잡음"
    }}

    예시 3 (정보 부족 - 질문):
    입력: "내일 친구 만나"
    출력: 몇 시에 만나기로 하셨나요?

    # [4] 실제 수행
    입력: "{{user_input}}"
    출력 (JSON 또는 질문만):
"""
class AIService:
    
    def __init__(self, chat_repo: ChatRepository = None):
        """
        AIService를 초기화하고 ollama 비동기 클라이언트를 설정합니다.
        설정 파일(config.py)에서 Ollama 서버의 URL을 가져옵니다.
        """
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
        self.chat_repo = chat_repo
    
    @retry(
        stop=stop_after_attempt(3), # 최대 3번 재시도
        wait=wait_fixed(2) # 재시도 사이 2초 대기
    )
    async def _send_chat_request(self, model: str, messages: list) -> dict:
        """
        Ollam 서버에 실제 chat 요청을 보내는 내부 메서드
        tenacity의 @retry 데코레이터가 이 메서드에만 적용
        """
        return await self.client.chat(model=model, messages=messages)
        
    async def parse_schedule_from_text(self, text: str) -> AIParsedSchedule | str:
        """
        자연어 텍스트를 파싱하여 구조화된 일정 객체를 반환합니다.

        Args:
            text (str): 사용자가 입력한 자연어 텍스트

        Returns:
            AIParsedSchedule: AI가 파싱한 일정 데이터 객체
            
        Raises:
            AIConnectionError: AI 서버 연결 또는 요청 중 오류 발생 시
            AIParsingError: AI 응답 파싱 또는 유효성 검사 실패 시
        """
        logger.info("========= /paparse_schedule_from_textrse 진입 ===================")
        now = datetime.now()
        
        weekday_map = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        
        # llama3.1:8b 프롬프트가 기존 방법을 이해하지 못하여
        # 해결책1. 날짜 계산은 python에서 처리(like 컨닝페이퍼)
        upcoming_dates = []
        for i in range(8): # 오늘 포함 8일치
            target_date = now + timedelta(days=i)
            w_str = weekday_map[target_date.weekday()]
            date_str = target_date.strftime('%Y-%m-%d')
            
            # 예: "오늘(목): 2025-12-04", "내일(금): 2025-12-05", "일요일: 2025-12-07"
            if i == 0:
                upcoming_dates.append(f"- 오늘({w_str}): {date_str}")
            elif i == 1:
                upcoming_dates.append(f"- 내일({w_str}): {date_str}")
            elif i == 2:
                upcoming_dates.append(f"- 모레({w_str}): {date_str}")
            else:
                upcoming_dates.append(f"- 이번주 {w_str}요일: {date_str}" if i < 7 else f"- 다음주 {w_str}요일: {date_str}")

        date_context = "\n    ".join(upcoming_dates)
        logger.debug(f"date_context ========> {date_context}")
        
        prompt = SYSTEM_PROMPT.format(date_context=date_context)
        try:
            response = await self._send_chat_request(
                model = settings.OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": text}
                ],
            )
            # AI 응답을 Pydantic 모델로 파싱
            content_str = response["message"]["content"]
            json_match = re.search(r'\{.*\}', content_str, re.DOTALL)
            if json_match:
                try:
                    # JSON 후보 문자열 추출
                    json_str = json_match.group(0)
                    # 혹시 모를 작은따옴표(')를 큰따옴표(")로 변환 (JSON 표준)
                    # 단, 데이터 내부에 '가 있을 수 있으므로 주의 필요. 
                    # Llama 3.1은 보통 표준 JSON을 잘 지키므로 이 라인은 상황 봐서 제거 가능
                    # json_str = json_str.replace("'", '"') 
                    
                    # Pydantic 모델로 변환 시도
                    parsed_schedule = AIParsedSchedule.model_validate_json(json_str)
                    return parsed_schedule
                    
                except (json.JSONDecodeError, ValueError):
                    # '{ }'가 있지만 유효한 JSON이 아니거나 스키마가 안 맞는 경우
                    # 그냥 AI의 답변(질문)으로 처리
                    return content_str
            else:
                # JSON 패턴('{...}')이 아예 없으면 질문으로 간주
                return content_str
        
        except RetryError as e:
            # 재시도 실패 시 발생
            raise AIConnectionError(f"여러 차례 AI 서버 접속에 실패하였습니다. {e}")
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
            # 응답이 비정상이거나, 파싱 실패 시 발생
            raise AIParsingError(f"AI 파싱에 실패했습니다. {e}")
        except Exception as e:
            # 그 외 모든 Ollama 관련 예외 처리
            raise AIConnectionError(f"예상치 못한 에러가 발생하였습니다. {e}")
    
    async def process_chat(self, user_id: int, message: str) -> str:
        """
        사용자의 채팅 메세지를 처리하고 응답을 생성합니다.
        대화 내역을 DB에 저장합니다.
        """
        # 사용자 메세지 DB 저장
        if self.chat_repo:
            await self.chat_repo.create(user_id, ChatRole.USER, message)
        
        # 대화 문맥 조회    
        context_messages = []
        if self.chat_repo:
            recent_chats = await self.chat_repo.get_recent_chats(user_id, limit=10)
            for chat in reversed(recent_chats):
                context_messages.append({"role": chat.role, "content": chat.content})
        else:
            # 현재 메세지 추가
            context_messages.append({"role": "user", "content": message})
        
        # AI 요청
        # TODO. 채팅 전용 프롬프트나 모델 분리 고려.
        try:
            response = await self._send_chat_request(
                model = settings.OLLAMA_MODEL,
                messages = context_messages
            )
            ai_content = response["message"]["content"]
            
            # ai응답 DB 저장
            if self.chat_repo:
                await self.chat_repo.create(user_id, ChatRole.ASSISTANT, ai_content)
                
            return ai_content
        
        except Exception as e:
            logger.error(f"AI Chat Error: {e}")
            raise AIConnectionError(f"대화 처리 중 오류가 발생했습니다: {e}")
        
    async def generate_briefing(self, schedules: list[Schedule]) -> str:
        """
        사용자의 일정 리스트를 바탕으로 AI 요약 브리핑을 생성합니다.
        Args:
            schedules: Schedule 객체 리스트
        Returns:
            str: 요약된 브리핑 텍스트
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