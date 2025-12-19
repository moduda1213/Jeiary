'''
- AsyncIOScheduler 사용 (비동기 지원)
- 각 Job 함수는 매 실행마다 새로운 DB 세션을 생성하여 독립성 보장
- AIService는 브리핑 생성 시 채팅 내역이 필요 없으므로 chat_repo=None으로 초기화하여 리소스를 절약
'''
import os
from datetime import datetime
from loguru import logger
from typing import Callable, Awaitable

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionFactory
from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.chat_repo import ChatRepository
from app.repositories.user_repo import UserRepository
from app.repositories.notification_repo import NotificationRepository
from app.repositories.job_history_repo import JobHistoryRepository

from app.services.cleanup_service import CleanupService
from app.services.briefing_service import BriefingService
from app.services.ai_service import AIService

scheduler = AsyncIOScheduler()

# ---------------------------------------------------------------------------
# 1. 로깅 설정
# ---------------------------------------------------------------------------
def setup_batch_logger():
    """배치 작업 전용 파일 로거 설정"""
    log_dir = "logs/batch"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # "batch" in record["extra"] -> "이 로그의 꼬리표 중에 'batch'라는 스티커가 붙어 있니?" 라고 묻습니다.
    #   * Yes: 이 로그 파일(logs/batch/...)에 저장합니다.
    #   * No: 일반 로그이므로 무시하고 다른 곳(콘솔 등)으로 보냅니다.
    logger.add(
        os.path.join(log_dir, "{time:YYYY-MM-DD}_batch.log"),
        filter=lambda record: "batch" in record["extra"],
        format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}",
        rotation="00:00", # 매일 자정 로테이션
        retention="30 days" # 30일 보관
    )

# ---------------------------------------------------------------------------
# 2. 배치 실행 래퍼
# Callable[[AsyncSession], Awaitable[str]]: DB 세션을 받아서 비동기로 실행되고, 끝나면 문자열 결과를 돌려주는 함수
# ---------------------------------------------------------------------------
async def run_job_with_logging(job_name: str, logic_func: Callable[[AsyncSession], Awaitable[str]]):
    """
    배치 작업 실행 공통 래퍼
    - DB 세션 관리
    - JobHistory 기록 (SUCCESS/FAILED)
    - 파일 로깅
    """
    # 배치 전용 로거 바인딩
    # 코드에서 logger.bind(batch=True).info(...)라고 로그를 찍으면, 그 로그 메시지에는 보이지 않는 꼬리표(extra 정보)로 {'batch': True}가 붙습니다.
    # ==> 마치 택배 상자에 "취급주의" 스티커를 붙이는 것과 같습니다.
    batch_logger = logger.bind(batch=True)
    batch_logger.info(f"[{job_name}] STARTING...")
    
    async with AsyncSessionFactory() as session:
        repo = JobHistoryRepository(session)
        status = "FAILED",
        details = ""
        
        try:
            # 비즈니스 로직 실행
            result_msg = await logic_func(session)
            status = "SUCCESS"
            details = result_msg
            batch_logger.info(f"[{job_name}] COMPLETED. {details}")
        
        except Exception as e:
            status = "FAILED"
            details = str(e)
            batch_logger.error(f"[{job_name}] FAILED. Error: {details}")
            batch_logger.exception(e) # 에러 스택트레이스 로그
            
        finally:
            try:
                await repo.create_log(job_name, status, details)
                await session.commit()
            except Exception as db_err:
                batch_logger.error(f"[{job_name}] Failed to save job history: {db_err}")
            
            
# ---------------------------------------------------------------------------
# 3. 비즈니스 로직
# ---------------------------------------------------------------------------
async def _cleanup_logic(session: AsyncSession) -> str:
    """데이터 클린업 배치 (매일 새벽 3시)"""
    cleanup_service = CleanupService(
        schedule_repo = ScheduleRepository(session),
        chat_repo = ChatRepository(session)
    )
    
    # 만료된 일정 삭제
    deleted_schedules = await cleanup_service.delete_expired_schedules()
    
    # 만료된 채팅 삭제
    deleted_chats = await cleanup_service.delete_expired_chats()
    
    return f"Schedules: {deleted_schedules}, Chats: {deleted_chats}"

async def _briefing_logic(session: AsyncSession) -> str:
    """AI 모닝 브리핑 생성 (매일 아침 7시)"""
    user_repo = UserRepository(session)
    briefing_service = BriefingService(
        schedule_repo = ScheduleRepository(session),
        notification_repo = NotificationRepository(session),
        ai_service = AIService()
    )
    
    # 모든 사용자 조회
    users = await user_repo.get_all_users()
    success_count = 0
    fail_count = 0
    
    for user in users:
        try:
            await briefing_service.create_daily_briefing(user.id)
            success_count += 1
        except Exception:
            fail_count += 1
    return f"Total Users: {len(users)}, Success: {success_count}, Failed: {fail_count}"

# ---------------------------------------------------------------------------
# 4. Job 진입점 (Entry Point)
# ---------------------------------------------------------------------------
async def run_cleanup_job():
    await run_job_with_logging("daily_cleanup", _cleanup_logic)
    
async def run_morning_briefing_job():
    await run_job_with_logging("morning_briefing", _briefing_logic)


# ---------------------------------------------------------------------------
# 5. Startup Check (Smart Recovery)
#   * 정책 A (모닝 브리핑):
#       * 시간: 07:00 ~ 12:00 사이 기동
#       * 조건: 오늘 성공한 morning_briefing 로그가 없음
#       * 행동: run_morning_briefing_job() 즉시 실행
#
#   * 정책 B (데이터 클린업):
#       * 시간: 03:00 ~ 07:00 사이 기동 (새벽 점검 후 재기동 시나리오)
#       * 조건: 오늘 성공한 daily_cleanup 로그가 없음
#       * 행동: run_cleanup_job() 즉시 실행
# ---------------------------------------------------------------------------
async def check_and_run_missed_jobs():
    """
    서버 시작 시 실행되지 않은 배치 작업이 있는지 확인하고 복구(Recovery) 수행
    """
    now = datetime.now()
    logger.info(f"Checking for missed batch jobs at {now}...")
    
    async with AsyncSessionFactory() as session:
        repo = JobHistoryRepository(session)
        
        # 1. 모닝 브리핑 복구(07:00 ~ 12:00)
        if 0 <= now.hour < 24:
            if not await repo.exists_successful_job_today("morning_briefing"):
                logger.warning("Recovery: Missed 'morning_briefing' detected. Executing now...")
                await run_morning_briefing_job()
            else:
                logger.info("Recovery: 'morning_briefing' already executed today")
                
        # 2. 데이터 클린업 복구 (03:00 ~ 07:00)
        if 0 <= now.hour < 24:
            if not await repo.exists_successful_job_today("daily_cleanup"):
                logger.warning("Recovery: Missed 'daily_cleanup' detected. Executing now...")
                await run_cleanup_job()
            else:
                logger.info("Recovery: 'daily_cleanup' already executed today.")

# ---------------------------------------------------------------------------
# 6. 스케줄러 설정
# ---------------------------------------------------------------------------
async def start_scheduler():
    """스케줄러 시작 및 Job 등록 + 복구 로직 수행"""
    setup_batch_logger()
    
    if not scheduler.running:
        # Job 1: 데이터 클린업 (매일 03:00)
        scheduler.add_job(
            run_cleanup_job,
            CronTrigger(hour=3, minute=0),
            id="daily_cleanup",
            replace_existing=True
        )
        # Job 2: 모닝 브리핑 (매일 07:00)
        scheduler.add_job(
            run_morning_briefing_job,
            CronTrigger(hour=7, minute=0),
            id="morning_briefing",
            replace_existing=True
        )
        scheduler.start()
        logger.info("Scheduler started...")
        
        await check_and_run_missed_jobs()
        
def shutdown_scheduler():
    """스케줄러 종료"""
    if scheduler.running:
        scheduler.shutdown()
        logger.info("Scheduler shutdown.")

'''
  🏛️ 코드의 핵심 구조 (Architecture Overview)

  이 코드는 "책임의 분리(Separation of Concerns)" 원칙을 따릅니다.
  하나의 거대한 run_job 함수가 모든 일(DB연결, 로직실행, 로깅, 예외처리)을 다 하는 대신, 역할을 명확히 쪼갰습니다.

   1. Wrapper (껍데기/관리자): run_job_with_logging
       * "나는 일(Logic)을 시키고, 결과만 기록해. 무슨 일인지는 관심 없어."
       * DB 세션 생성, 성공/실패 여부 판단, 로그 파일 기록, JobHistory 저장을 담당합니다.

   2. Logic (알맹이/작업자): _cleanup_logic, _briefing_logic
       * "나는 시키는 일만 해. 기록이나 DB 연결은 몰라."
       * 실제 서비스(CleanupService 등)를 호출하고, 결과 메시지(문자열)만 반환합니다.

   3. Entry Point (호출 버튼): run_cleanup_job
       * 스케줄러가 누르는 버튼입니다. 단순히 "관리자야(Wrapper), 청소부(Logic) 좀 시켜줘"라고 연결만 해줍니다.

  ---

  🌊 코드 실행 흐름 (Execution Flow)

  매일 새벽 3시, daily_cleanup 작업이 실행될 때의 시나리오입니다.

  1단계: 스케줄러 트리거
   * APScheduler가 03:00에 run_cleanup_job() 함수를 호출합니다.

  2단계: 래퍼 호출 (위임)
   * run_cleanup_job은 즉시 run_job_with_logging("daily_cleanup", _cleanup_logic)을 호출합니다.
       * "작업 이름은 'daily_cleanup'이고, 할 일은 `_cleanup_logic` 함수에 있어." 라고 전달합니다.

  3단계: 관리자(Wrapper)의 준비
   * run_job_with_logging이 시작됩니다.
   * 파일 로그: logs/batch/2025-12-16_batch.log 파일에 [daily_cleanup] STARTING...이라고 적습니다.
   * DB 세션: AsyncSessionFactory()로 새 DB 세션을 엽니다.

  4단계: 알맹이(Logic) 실행
   * await logic_func(session) 코드가 실행되면서, 실제로 _cleanup_logic(session) 함수가 돌아갑니다.
       * CleanupService가 생성되고, delete_expired_schedules() 등을 수행합니다.
       * 작업이 끝나면 결과 문자열("Schedules: 5, Chats: 0")을 리턴합니다.

  5단계: 결과 처리 (성공 시)
   * 래퍼는 리턴받은 문자열을 details 변수에 담습니다.
   * status를 "SUCCESS"로 설정합니다.
   * 파일 로그: [daily_cleanup] COMPLETED. Schedules: 5...라고 적습니다.

  6단계: 이력 저장 (Finally)
   * 성공하든 실패하든 finally 블록으로 갑니다.
   * JobHistoryRepository.create_log("daily_cleanup", "SUCCESS", "Schedules: 5...")를 호출합니다.
   * DB Commit: job_histories 테이블에 한 줄이 추가됩니다.

  ---

  💡 왜 이렇게 복잡하게 나누나요?

  처음엔 복잡해 보일 수 있지만, 이렇게 하면 엄청난 장점이 생깁니다.

   1. 새 작업 추가가 매우 쉽습니다.
       * 만약 "매주 월요일 주간 리포트" 기능을 추가하고 싶다면?
       * _report_logic 함수 하나만 짜면 됩니다. 로그 남기고, DB 저장하고, 예외 처리하는 코드는 run_job_with_logging이 알아서 다 해주니까요. (복사-붙여넣기 할 필요 없음)

   2. 모든 로그 형식이 통일됩니다.
       * 어떤 작업이든 로그 포맷이 똑같아서(STARTING -> COMPLETED/FAILED), 나중에 로그 분석기나 모니터링 툴을 붙이기 편합니다.

   3. 에러 관리가 안전합니다.
       * 개발자가 실수로 try-except를 빼먹어도, 래퍼 함수가 잡아주기 때문에 서버가 죽지 않고 "FAILED"로 기록됩니다.

"템플릿 메서드 패턴(Template Method Pattern)"
'''