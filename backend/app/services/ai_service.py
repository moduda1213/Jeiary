import ollama
import json
import re
from datetime import date
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError

from app.config import settings
from app.schemas.ai import AIParsedSchedule

from app.core.exceptions import AIConnectionError, AIParsingError

settings = settings

# TODO. 추후 변경 OR 삭제 예정
SYSTEM_PROMPT = """
    당신은 일정 정보를 추출하는 AI입니다.
  
    # 기준 정보
    - 오늘 날짜: {today}

    # 중요: 날짜 계산 절대 규칙 (우선순위 1위)
    1. 모든 일정은 '미래'의 일입니다. 
    2. 따라서 추출된 날짜는 반드시 오늘(2025-11-25)보다 같거나 미래여야 합니다.
    3. 만약 계산된 날짜가 오늘보다 이전(과거)이라면, 자동으로 다음 주 날짜로 변경하세요.
        - (오답 예시) 오늘이 25일(화)인데 '이번주 일요일'을 23일(일)로 계산 -> 과거이므로 틀림.
        - (정답 예시) 오늘이 25일(화)이면 '이번주 일요일'은 30일(일)로 계산 -> 미래이므로 정답.

    # 응답 형식 (반드시 이 순서대로!)
    1단계: [체크리스트]
    2단계: [판단]
    3단계: [답변]

    # 1단계: [체크리스트] 작성 기준
    - 날짜 정보: (있음/없음)
    - 시작 시간 숫자: (있음/없음)
    - 오전/오후 구분: (명확함/불명확함)
    - 제목/목적: (있음/없음)
    - 미래 여부: (날짜가 오늘 이후인가? 예/아니오)

    # 2단계: [판단] 로직
    1. 필수 정보가 없거나 모호하면 질문.
    2. 날짜가 과거(오늘 이전)로 계산되면 미래 날짜(다음 주)로 보정하여 JSON 생성.

    # 날짜 계산 참조 (11/25 화요일 기준)
    - 이번주 금요일: 11/28
    - 이번주 토요일: 11/29
    - 이번주 일요일: 11/30 (오는 일요일)

    # 3단계: [답변] 생성

    # 중요: 시간 판단 및 변환 규칙
    - '6시 반' → 오전/오후 불명확함 (질문해야 함)
    - '저녁 6시 반' → 18:30 (명확함)
    - '18:30' → 18:30 (명확함)
    - '오후 3시' → 15:00 (명확함)
    
    # 날짜 계산 규칙
    - 오늘(11/20, 목) 기준:
        - 내일 = 11/21 (금)
        - 모레 = 11/22 (토)
        - 이번주 일요일 = 11/23 (일)
        - 다음주 월요일 = 11/24 (월)

    # 예시: 정보 불충분 (오전/오후 모호)
    입력: '일요일에 할머니 집에서 김장있어. 6시반까지 가야해'

    [체크리스트]
    - 날짜 정보: 있음 (일요일)
    - 시작 시간 숫자: 있음 (6시 반)
    - 오전/오후 구분: 불명확함 (오전인지 오후인지 모름)
    - 제목/목적: 있음 (할머니 집 김장)

    [판단]
    오전/오후 구분이 불명확하므로 → 질문

    [답변]
    오전 6시 30분인가요, 오후 6시 30분인가요?

    # JSON 출력 형식 (정보가 완벽할 때만)
    {{
    'date': 'YYYY-MM-DD',
    'start_time': 'HH:MM',
    'end_time': 'HH:MM',
    'title': '일정 제목',
    'content': null
    }}
"""
class AIService:
    
    def __init__(self):
        """
        AIService를 초기화하고 ollama 비동기 클라이언트를 설정합니다.
        설정 파일(config.py)에서 Ollama 서버의 URL을 가져옵니다.
        """
        self.client = ollama.AsyncClient(host=settings.OLLAMA_BASE_URL)
    
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
        now = date.now()
        days = ['월요일', '화요일', '수요일', '목요일', '금요일', '토요일', '일요일']
        current_date_str = f"{now.strftime('%Y-%m-%d')} ({days[now.weekday()]})"
        prompt = SYSTEM_PROMPT.format(today=current_date_str)
        # today_str = date.today().isoformat()
        # prompt = SYSTEM_PROMPT.format(today=today_str)
        
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
            
            match = re.search(r'\[답변\]\s*(.*)', content_str, re.DOTALL) # DTOALL :.(dot) 문자와 \n 문자도 매치
            if not match:
                raise AIParsingError("결과 포맷이 부정확합니다. [답변] 섹션이 없습니다.")
            
            answer_part = match.group(1).strip()
            
            # 답변 내용이 JSON인지 확인
            if answer_part.startswith('{'):
                json_str = answer_part.replace("'", '"')
                parsed_schedule = AIParsedSchedule.model_validate_json(json_str)
                return parsed_schedule
            else:
                # 질문으로 간주하고 그대로 받음
                return answer_part
        
        except RetryError as e:
            # 재시도 실패 시 발생
            raise AIConnectionError(f"여러 차례 AI 서버 접속에 실패하였습니다. {e}")
        except (json.JSONDecodeError, KeyError, TypeError, AttributeError) as e:
            # 응답이 비정상이거나, 파싱 실패 시 발생
            raise AIParsingError(f"AI 파싱에 실패했습니다. {e}")
        except Exception as e:
            # 그 외 모든 Ollama 관련 예외 처리
            raise AIConnectionError(f"예상치 못한 에러가 발생하였습니다. {e}")