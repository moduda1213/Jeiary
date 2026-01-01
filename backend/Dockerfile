# backend 서비스의 Docker 이미지를 만드는 방법을 정의합니다. Python 환경 설정, 의존성 설치, 애플리케이션 실행 명령 등을 포함합니다.
# 1. 베이스 이미지 설정
FROM python:3.11-slim

# 2. 작업 디렉토리 설정
WORKDIR /app

# 3. 시스템 패키지 업데이트 및 의존성 설치 (필요 시)
# RUN apt-get update && apt-get install -y ...

# 4. Python 의존성 파일 복사 및 설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. 애플리케이션 소스 코드 복사
# (docker-compose.yml의 volumes 설정으로 인해 개발 중에는 이 부분이 덮어쓰여집니다)
COPY . .

# 6. 포트 노출
EXPOSE 8000

# 7. 컨테이너 실행 시 기본 명령어
# (개발 환경에서는 docker-compose.yml의 command가 우선 적용됩니다)
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]