import ollama
import json
import re
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_fixed, RetryError

from app.config import settings
from app.schemas.ai import AIParsedSchedule

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