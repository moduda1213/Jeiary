import axios, {AxiosError} from 'axios';

// 백엔드 API의 기본 URL을 설정하여 axios 인스턴스를 생성합니다.
// 이렇게 하면 모든 요청에서 도메인 부분을 반복해서 입력할 필요가 없습니다.
const apiClient = axios.create({
    baseURL: '/api/v1', // 백엔드 주소
    withCredentials: true, // 서버에 HTTP-only 쿠키(Refresh Token) 자동 전송
});

// 토큰 갱신 로직이 실행 중인지 여부를 추적하는 플래그
let isRefreshing = false;

// 토큰 갱신에 실패한 후, 다른 API 요청들이 또다시 갱신을 시도하는 것을 막기 위한 플래그
let refreshFailed = false;

// 진행 중인 토큰 갱신 후 실행되어야 할 콜백 함수들의 배열
let failedQueue: ((error: Error | null) => void)[] = [];

const processQueue = (error: Error | null) => {
    failedQueue.forEach(prom => {
        prom(error as any);
    });
    failedQueue = [];
};

apiClient.interceptors.response.use(
    (response) => {
        // 요청 성공 시, 갱신 실패 상태 초기화
        refreshFailed = false;
        return response;
    },
    async (error: AxiosError) => {
        const originalRequest = error.config as any;

        // 갱신 요청 자체가 실패한 경우 무한 루프 방지
        if (originalRequest.url?.includes('/auth/refresh')) {
            return Promise.reject(error);
        }

        // 1. 401 에러가 아니거나, 이미 갱신에 최종 실패한 경우, 더 이상 처리하지 않음
        if (error.response?.status !== 401 || refreshFailed) {
            return Promise.reject(error);
        }

        // 2. 토큰 갱신 로직이 이미 실행 중인 경우 (대기열 추가)
        if (isRefreshing) {
            return new Promise((resolve, reject) => {
                failedQueue.push((error) => {
                    if (error) {
                        reject(error);
                    } else {
                        // 헤더 설정 없이 재설정 (쿠키 사용)
                        resolve(apiClient(originalRequest));
                    }
                });
            });
        }

        // 3. 토큰 갱신 로직 최초 실행
        isRefreshing = true;
        originalRequest._retry = true; // 재시도된 요청임을 표시

        try {
            // 4. 토큰 갱신 요청
            await apiClient.post('/auth/refresh');

            // 갱신 성공
            isRefreshing = false;

            // 대기열에 있던 모든 요청들을 새로운 토큰으로 재실행
            processQueue(null);

            // 5. 원래 실패했던 요청을 새로운 토큰으로 재시도
            return apiClient(originalRequest);

        } catch (refreshError) {
            // 6. 토큰 갱신마저 실패한 경우 (Refresh Token 만료 등)
            isRefreshing = false;
            refreshFailed = true; // 갱신이 최종 실패했음을 기록

            // 대기열에 있던 요청들을 에러와 함께 모두 실패 처리
            processQueue(refreshError as Error);

            // 7. [핵심] 'auth:logout' 커스텀 이벤트를 발생시켜 React 영역에 알림
            console.error("Refresh token failed. Dispatching auth:logout event.");
            window.dispatchEvent(new CustomEvent('auth:logout'));

            // 8. 이 요청은 최종 실패로 처리
            return Promise.reject(refreshError);
        }
    }
);

export default apiClient;

// 회원가입 요청
export const registerUser = async (email: string, password: string) => {
    const response = await apiClient.post('/auth/register', {email, password});
    return response.data;
}
