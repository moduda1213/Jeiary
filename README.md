# Jeiary (Smart Calendar AI Assistant)

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688?logo=fastapi&logoColor=white)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=black)
![Docker](https://img.shields.io/badge/Docker-Compose-2496ED?logo=docker&logoColor=white)

Jeiary는 사용자의 자연어 입력(텍스트/음성)을 로컬 LLM(Llama 3.1)이 분석하여 자동으로 일정을 생성하고 관리해주는 지능형 캘린더 애플리케이션입니다.
"내일 오후 2시에 팀 미팅 잡아줘"와 같은 단순한 명령만으로 복잡한 일정 등록을 완료할 수 있습니다.

## ✨ 주요 기능 (Features)

*   📅 **스마트 캘린더**: 월간/주간 뷰를 지원하는 직관적인 일정 관리 인터페이스
*   🤖 **On-Device AI**: 외부 API 없이 로컬에서 실행되는 Llama 3.1 모델로 개인정보 유출 없는 안전한 자연어 처리
*   🔐 **보안 인증**: JWT (Access/Refresh Token) 기반의 안전한 회원가입 및 로그인
*   🖥️ **반응형 UI**: 데스크탑, 태블릿, 모바일 환경을 완벽하게 지원하는 Modern UI
*   🚀 **Dockerized**: 단일 명령어로 데이터베이스, 백엔드, 프론트엔드, AI 엔진을 한 번에 배포

## 🛠️ 기술 스택 (Tech Stack)

| Category | Technology |
|----------|------------|
| **Frontend** | React, TypeScript, Tailwind CSS, Vite |
| **Backend** | Python 3.11+, FastAPI, SQLAlchemy (Async), Pydantic |
| **Database** | PostgreSQL 15 |
| **AI Engine** | Ollama, Llama 3.1 (8B) |
| **Infra** | Docker, Docker Compose, Nginx |

## 🚀 설치 및 실행 (Installation & Usage)

Docker Compose를 사용하여 복잡한 환경 설정 없이 즉시 실행할 수 있습니다.

### 1. 사전 요구사항 (Prerequisites)
*   [Docker Desktop](https://www.docker.com/products/docker-desktop/) 설치 및 실행 중이어야 합니다.
*   최소 8GB 이상의 RAM 권장 (AI 모델 구동용)

### 2. 프로젝트 설정
저장소를 클론하고 환경 변수 파일을 생성합니다.

```bash
# Clone Repository
git clone <repository-url>
cd Jeiary

# Setup Environment Variables
# Windows (PowerShell)
copy .env.example .env
# Mac / Linux
cp .env.example .env
```
> `.env` 파일을 열어 `DB_PASSWORD`, `SECRET_KEY` 등을 운영 환경에 맞게 수정하는 것을 권장합니다.

### 3. 애플리케이션 실행

#### 🅰️ 일반 사용자 / 운영 모드 (Production Mode)
안정적인 서비스 운영을 위한 모드입니다. Nginx가 프론트엔드를 서빙합니다.

```bash
docker-compose up -d --build
```

#### 🅱️ 개발자 모드 (Development Mode)
코드 수정 시 서버가 자동으로 재시작되는 **Hot-Reloading** 모드입니다.

```bash
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --build
```

### 4. AI 모델 초기화 (최초 1회 필수)
최초 실행 시 `ollama` 컨테이너가 Llama 3.1 모델(약 4.7GB)을 다운로드합니다.
*   **소요 시간**: 네트워크 환경에 따라 5~20분
*   다운로드 중에는 백엔드 기능이 제한될 수 있습니다. 진행 상황은 로그로 확인하세요:

```bash
docker-compose logs -f ollama
```
`success` 메시지가 뜨면 AI 기능 사용 준비가 완료된 것입니다.

## 🌐 접속 정보 (Access)

| 서비스 | URL | 설명 |
|--------|-----|------|
| **Web Client** | http://localhost:5173 | 메인 애플리케이션 |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **Ollama** | http://localhost:11434 | AI 엔진 상태 확인 |

## ❓ 트러블슈팅 (Troubleshooting)

**Q. "Connection refused" 에러가 발생해요.**
*   데이터베이스나 AI 컨테이너가 아직 초기화 중일 수 있습니다. 1~2분 정도 기다렸다가 다시 시도해보세요.
*   `docker-compose logs backend`로 백엔드 로그를 확인해보세요.

**Q. 포트가 이미 사용 중이라고 나와요.**
*   5432(PostgreSQL), 8000(Backend), 5173(Frontend), 11434(Ollama) 포트를 다른 프로세스가 점유 중인지 확인하세요.
*   `docker-compose down`으로 기존 컨테이너를 정리하고 다시 실행하세요.

---
© 2025 Jeiary Project. All Rights Reserved.