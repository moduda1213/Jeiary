import os
from starlette.config import Config

def _read_file_utf8(self, file_name: str | None) -> dict[str, str]:
    if file_name is None or not os.path.exists(file_name):
        return {}
    file_values: dict[str, str] = {}
    with open(file_name, encoding="utf-8") as input_file:
        for line in input_file.readlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                key, value = line.split("=", 1)
                key = key.strip()
                value = value.strip().strip("\"'")
                file_values[key] = value
    return file_values
   
Config._read_file = _read_file_utf8


from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from fastapi.responses import JSONResponse

# IP 주소를 기준으로 요청을 식별하는 limiter 인스턴스 생성
limiter = Limiter(key_func=get_remote_address)

# 커스텀 에러 핸들러 추가
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Rate Limit 초과 시 커스텀 에러 응답
    
    Args:
        request: FastAPI Request 객체
        exc: RateLimitExceeded 예외
    
    Returns:
        JSONResponse: 429 상태 코드와 에러 메시지
    """
    return JSONResponse(
        status_code=429,
        content={
            "detail": "Rate limit exceeded. Please try again later."
        },
        headers={"Retry-After": "60"}
    )