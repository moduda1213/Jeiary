# --- 1단계: 스크립트 수정용 임시 컨테이너 ---
FROM alpine:latest AS fixer

# dos2unix 도구 설치
RUN apk add --no-cache dos2unix

# 변환할 스크립트를 임시 컨테이너로 복사
COPY ./ollama/entrypoint.sh /entrypoint.sh

# 스크립트의 줄바꿈 형식을 리눅스(LF) 방식으로 변환
RUN dos2unix /entrypoint.sh


# --- 2단계: 최종 Ollama 이미지 빌드 ---
FROM ollama/ollama

# 백엔드의 Modelfile 복사
COPY ./backend/Modelfile /Modelfile

# 1단계(fixer)에서 변환된 '깨끗한' 스크립트를 최종 이미지로 복사
COPY --from=fixer /entrypoint.sh /entrypoint.sh

# 스크립트에 실행 권한 부여
RUN chmod +x /entrypoint.sh

# 최종 컨테이너의 시작 명령어로 지정
ENTRYPOINT ["/entrypoint.sh"]