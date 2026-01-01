import pytest
from datetime import date, time
from app.services.ai_service import AIService
from app.services.schedule_service import ScheduleService
from app.repositories.chat_repo import ChatRepository
from app.repositories.schedule_repo import ScheduleRepository
from app.repositories.user_repo import UserRepository

@pytest.mark.asyncio
async def test_ai_agent_e2e_flow(db_session, test_user):
    """
    [E2E] AI 에이전트 통합 테스트
    1. 일반 대화 처리 (GeneralChatTool -> AIAgent)
    2. 일정 생성 요청 (CreateScheduleTool -> ScheduleService -> DB)
    """
    
    # 1. Setup
    chat_repo = ChatRepository(db_session)
    user_repo = UserRepository(db_session)
    schedule_repo = ScheduleRepository(db_session)
    
    schedule_service =ScheduleService(schedule_repo)
    
    ai_service = AIService(
        chat_repo = chat_repo,
        schedule_service = schedule_service,
        user_repo = user_repo
    )
    
    user_id = test_user.id
    
    # ---------------------------------------------------------
    # 1. 일반 대화
    # ---------------------------------------------------------
    chat_input = "안녕, 반가워! 나는 테스트 유저야."
    print(f"\n[User] {chat_input}")
    
    chat_response = await ai_service.process_chat(user_id, chat_input)
    print(f"[AI] {chat_response}")
    
    assert chat_response is not None
    assert "일정이 등록되었습니다." not in chat_response
    
    # ---------------------------------------------------------
    # 2: 일정 생성 (명확한 날짜/시간 지정)
    # 주의: 현재 AI에게 '오늘' 날짜를 알려주지 않았으므로 절대 날짜 사용 권장
    # ---------------------------------------------------------
    schedule_input = "2025-12-25 14:00에 '크리스마스 파티' 일정 잡아줘. 종료는 16:00야."
    print(f"\n[User] {schedule_input}")
    
    schedule_response = await ai_service.process_chat(user_id, schedule_input)
    print(f"[AI] {schedule_response}")
    
    # 검증 1: 응답 메시지에 성공 확인
    assert "일정이 등록되었습니다" in schedule_response
    assert "크리스마스 파티" in schedule_response
    
    # 검증 2: 실제 DB 조회
    # 해당 날짜의 일정을 조회하여 생성되었는지 확인
    schedules = await schedule_repo.get_schedules_by_user_and_month(user_id, 2025, 12)
    
    created_schedule = None
    for s in schedules:
        if s.title == "크리스마스 파티" and s.date == date(2025, 12, 25):
            created_schedule = s
            break
    
    assert created_schedule is not None
    assert created_schedule.start_time == time(14, 0)
    assert created_schedule.end_time == time(16, 0)
    print(f"\n DB Verification Passed: ID={created_schedule.id}, Title={created_schedule.title}")