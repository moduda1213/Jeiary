FROM node:22-alpine AS build
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
# WORKDIR /app : Docker 이미지 내부에 /app이라는 디렉터리가 없으면 새로 생성합니다.
# COPY . . : 로컬(frontend)의 모든 파일을 이미지 속 /app 폴더로 덮어쓰며 복사합니다.

FROM nginx:alpine
COPY --from=build /app/build /usr/share/nginx/html
# API 요청을 백엔드로 프록시하기 위한 설정
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]