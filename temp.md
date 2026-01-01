  1. 회원가입 (Sign Up)
  목표: 새로운 사용자가 정상적으로 시스템에 등록되는지 검증

   * [v] 정상 회원가입
       * Input: 유효한 이메일 (test_e2e@example.com), 유효한 비밀번호 (Test1234!)
       * Expectation: HTTP 201 Created 응답, id, email, created_at 필드가 포함된 JSON 반환.
   * [v] 중복 이메일 방지
       * Input: 이미 가입된 이메일 (test_e2e@example.com)
       * Expectation: HTTP 400 Bad Request 또는 409 Conflict.
   * [v] 비밀번호 정책 검증
       * Input:
           1. 8자 미만 (Test1!)
           2. 특수문자 누락 (Test1234)
           3. 숫자 누락 (TestPassword!)
       * Expectation: HTTP 422 Unprocessable Entity (Validation Error).

  2. 로그인 (Login)
  목표: 등록된 사용자가 인증 토큰을 발급받을 수 있는지 검증

   * [v] 정상 로그인
       * Input: 가입한 이메일 & 비밀번호
       * Expectation: HTTP 200 OK, access_token, refresh_token
   * [v] 잘못된 비밀번호
       * Input: 올바른 이메일 & 틀린 비밀번호
       * Expectation: HTTP 401 Unauthorized.
   * [v] 존재하지 않는 사용자
       * Input: 가입하지 않은 이메일
       * Expectation: HTTP 401 Unauthorized.
   * [v] 토큰 유효성 (보안)
       * Action: 발급받은 access_token으로 보호된 엔드포인트(예: /users/me) 접근.
       * Expectation: HTTP 200 OK 및 내 정보 반환.
   * [v] 브루트 포스 방어 (보안)
       * Action: 일치하지 않은 id/pw 입력 후 반복적인 로그인 (1분 / 5회 설정). 
       * Expectation: HTTP 401 Unauthorized 그리고 HTTP 429 Too Many Requests

  3. 일정 관리 (Schedule Management)
  목표: 인증된 사용자가 일정을 생성, 조회, 수정, 삭제할 수 있는지 검증

   * [v] 일정 생성 (Create)
       * Input: title: "E2E 테스트 회의", date: "2025-12-31", start_time: "10:00", end_time: "11:00"
       * Expectation: HTTP 201 Created, 생성된 일정 객체 반환 (ID 포함).
   * [v] 일정 목록 조회 (Read)
       * Input: start_date: "2025-12-01", end_date: "2025-12-31" (Query Params)
       * Expectation: HTTP 200 OK, 위에서 생성한 일정이 포함된 리스트 반환.
   * [v] 일정 상세 수정 (Update)
       * Input: 생성된 일정 ID, 변경할 내용 (title: "변경수정된 회의", content: "내용 추가")
       * Expectation: HTTP 200 OK, 수정된 필드 반영 확인.
   * [v] 시간 유효성 검증 (Fail Case)
       * Input: end_time이 start_time보다 빠름 (예: 10:00 ~ 09:00)
       * Expectation: HTTP 422 Unprocessable Entity.
   * [v] 일정 삭제 (Delete)
       * Input: 생성된 일정 ID
       * Expectation: HTTP 204 No Content. 삭제 후 조회 시 404 Not Found.

  4. AI 채팅 시나리오 (AI Chat Scenario)
  목표: 자연어 대화를 통해 일정이 파싱되고 등록되는 전체 흐름 검증

   * [ ] 정보 불충분 대화 (Step 1)
       * Input: text: "내일 점심 약속 잡아줘" (시간 정보 누락)
       * Expectation:
           * HTTP 200 OK
           * is_complete: false
           * question: 시간을 묻는 질문 포함 (예: "몇 시에 약속을 잡을까요?")
           * data: null
   * [ ] 정보 보완 및 파싱 완료 (Step 2)
       * Input: text: "오후 1시에 강남역에서" (이전 컨텍스트 유지 필요)
       * Expectation:
           * HTTP 200 OK
           * is_complete: true
           * data:
               * title: "점심 약속" (또는 유사)
               * date: 내일 날짜 (YYYY-MM-DD)
               * start_time: "13:00"
               * end_time: "14:00" (기본 1시간 설정 등)
               * content: "강남역" 포함 여부 확인
   * [ ] 파싱된 일정 등록 연동 (Step 3)
       * Action: Step 2에서 받은 data를 그대로 일정 생성 API(POST /schedules)로 전송
       * Expectation: HTTP 201 Created, 일정이 정상적으로 DB에 저장됨.


function calling: Update & Delete 구현 [x]
일반 대화만 랭체인 =-> CRUD 요청한 대화도 포함 []
새로고침 및 홈 화면에 진입 시 최근 대화 내역 최대 10개까지 출력 []