#!/bin/sh

# 스크립트가 오류를 만나면 즉시 중단되도록 설정
set -e

# 1. Ollama 서버를 백그라운드에서 실행
ollama serve &

# 서버 프로세스의 PID 저장
PID=$!

# 2. 서버가 준비될 때까지 잠시 대기 (약 5초)
echo "Waiting for Ollama server to be ready..."
sleep 5

# 3. Modelfile을 사용하여 jeiary-scheduler 모델 생성
echo "Creating 'jeiary-scheduler' model..."
ollama create jeiary-scheduler -f /Modelfile
echo "Model creation complete."

# 4. 백그라운드에서 실행 중인 Ollama 서버 프로세스를 포그라운드로 가져와서 컨테이너가 종료되지 않도록 함
wait $PID