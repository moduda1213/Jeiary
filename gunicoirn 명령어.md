   * 권장 실행 명령어:

   gunicorn -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000 --workers 4 --timeout 120
   * 주요 옵션 설명:
       * -k uvicorn.workers.UvicornWorker: Gunicorn이 Uvicorn의 비동기 능력을 빌려 쓰도록 설정합니다.
       * --bind 0.0.0.0:8000: 컨테이너 내부의 모든 네트워크 인터페이스에서 8000번 포트로 수신 대기합니다.
       * --workers 4: 실행할 요리사(워커)의 수입니다. 보통 (CPU 코어 수 * 2) + 1을 권장하지만, 가벼운 앱이므로 4 정도로 시작하는 것이 적절합니다.
       * --timeout 120: AI 응답이 3~5초 이상 걸릴 수 있으므로, 응답 지연으로 인해 프로세스가 강제 종료되지 않도록 넉넉하게(2분) 설정합니다.