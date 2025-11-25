import sys
from loguru import logger
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1 import auth as auth_router
from app.api.v1 import schedules as schedules_router
from app.api.v1 import ai as ai_router
from app.core.limiter import limiter, rate_limit_handler
from slowapi.middleware import SlowAPIMiddleware
from slowapi.errors import RateLimitExceeded

log_level = "DEBUG" if settings.ENVIRONMENT == "development" else "INFO"

# loguru 설정
logger.remove()
logger.add(
    sys.stderr,
    level = log_level, # INFO 레벨 이상의 로그를 출력하도록 설정
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
    
)

# FastAPI 애플리케이션 인스턴스 생성
app = FastAPI(
    title="Jeiary API",
    description="일정 관리 서비스, Jeiary의 API 문서입니다.",
    version="1.0.0",
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.add_middleware(SlowAPIMiddleware)

# CORS 미들웨어 설정
# .env 파일의 CORS_ORIGINS 변수에 정의된 출처 목록을 사용합니다.
# 예 : "http://localhost:3000,http://127.0.0.1:3000"
if settings.CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(',')],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(auth_router.router, prefix="/api/v1")
app.include_router(schedules_router.router, prefix="/api/v1")
app.include_router(ai_router.router, prefix="/api/v1")

@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["Health Check"],
    summary="API 상태 확인"
)
def health_check() -> dict[str, str]:
    """
    API 서버의 상태를 확인하는 엔드포인트입니다.
    서버가 정상적으로 실행 중이면 'status: ok'를 반환합니다.
    """
    return {"status": "ok"}
