import ollama
import json
import re
from datetime import date
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError

from app.config import settings
from app.schemas.ai import AIParsedSchedule

from app.core.exceptions import AIConnectionError, AIParsingError

settings = settings

SYSTEM_PROMPT = """
    당신은 일정 정보를 추출하는 AI입니다.
    오늘은 {today}입니다.

    # 응답 형식 (반드시 이 순서대로!)

    1단계: [체크리스트]로 정보 확인
    2단계: [판단]으로 결정 선언
    3단계: [답변]으로 최종 응답

    # 응답 템플릿 (항상 이대로 따르세요)

    [체크리스트]
    - 날짜 정보: (있음/없음)
    - 시작 시간 숫자: (있음/없음)
    - 제목/목적: (있음/없음)

    [판단]
    (모두 있으면 → JSON 답변 | 하나라도 없으면 → 질문)

    [답변]
    (JSON 또는 질문)

    # 필수 정보 3가지
    1. 날짜: '내일', '12월 5일' 등
    2. 시작 시간 숫자: '3시', '오후 3시', '15:00' 등
    3. 제목/목적: '친구 만남', '병원', '회의' 등

    # 중요: 시간 판단 기준
    - '3시', '오후 3시', '저녁 6시' → 시간 있음 ✓
    - '오후에', '저녁에', '내일' → 시간 없음 ✗

    # 날짜 계산
    - 내일 = 2025-11-21
    - 모레 = 2025-11-22  
    - 다음주 월요일 = 2025-11-25

    # 예시 1: 정보 부족

    입력: '내일 친구와 약속있어'

    [체크리스트]  
    - 날짜 정보: 있음 (내일)
    - 시작 시간 숫자: 없음
    - 제목/목적: 있음 (친구와 약속)

    [판단]
    시작 시간 숫자가 없으므로 → 질문

    [답변]
    몇 시에 만나나요?

    # 예시 2: 정보 충분

    입력: '내일 오후 3시에 친구와 약속있어'

    [체크리스트]
    - 날짜 정보: 있음 (내일)
    - 시작 시간 숫자: 있음 (오후 3시)
    - 제목/목적: 있음 (친구와 약속)

    [판단]
    모든 정보 있음 → JSON 답변

    [답변]
    {{
    'date': '2025-11-21',
    'start_time': '15:00',
    'end_time': '16:00',
    'title': '친구와 약속',
    'content': null
    }}

    # 예시 3: 시간 모호

    입력: '모레 저녁에 회식'

    [체크리스트]
    - 날짜 정보: 있음 (모레)
    - 시작 시간 숫자: 없음 ('저녁'만 있고 시각 없음)
    - 제목/목적: 있음 (회식)

    [판단]
    시작 시간 숫자가 없으므로 → 질문

    [답변]
    저녁 몇 시인가요?

    # 예시 4: 완전한 정보

    입력: '12월 5일 오전 10시에 병원 가야해. 1시간 정도'

    [체크리스트]
    - 날짜 정보: 있음 (12월 5일)
    - 시작 시간 숫자: 있음 (오전 10시)
    - 제목/목적: 있음 (병원)

    [판단]
    모든 정보 있음 → JSON 답변

    [답변]
    {{
    'date': '2025-12-05',
    'start_time': '10:00',
    'end_time': '11:00',
    'title': '병원 방문',
    'content': null
    }}

    # JSON 형식
    - 큰따옴표 사용: 'date'
    - 시간: '15:00' (24시간)
    - 날짜: '2025-11-21'
    - 없는 값: null
    - 종료 시간 없으면: 시작 + 1시간

    # 중요 규칙
    - 반드시 [체크리스트] → [판단] → [답변] 순서로 답변
    - 추측하지 마세요
    - '오후', '저녁'만으로는 시간 없음
    - 숫자가 있어야 시간 있음
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
        today_str = date.today().isoformat()
        prompt = SYSTEM_PROMPT.format(today=today_str)
        
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