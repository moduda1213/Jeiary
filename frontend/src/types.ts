export const ViewState = {
    LOGIN: 'LOGIN',
    SIGNUP: 'SIGNUP',
    FORGOT_PASSWORD: 'FORGOT_PASSWORD',
    HOME: 'HOME', // Chat Dashboard     
    CALENDAR: 'CALENDAR'
} as const;

// 위 객체의 값들을 유니온 타입으로 추출 ('LOGIN' | 'SIGNUP' | ...
export type ViewState = typeof ViewState[keyof typeof ViewState];

// 사용자 인터페이스
export interface User {
    id: number; // 백엔드 ID는 number지만, UI 유연성을 위해 string 허용 (필요시 변환)
    name: string; // 백엔드에는 name 필드가 없을 수 있음 (email의 앞부분이나 별도 로직 필요)
    email: string;
    avatarUrl?: string; // 백엔드 미지원 시 기본 이미지 사용
}

// 캘린더 이벤트 (UI용 모델)
export interface CalendarEvent {
    id: number;
    title: string;
    content?: string; // 백엔드 'content' 매핑
    date: Date; 
    start_time: string; // "HH:MM"
    end_time: string;   // "HH:MM"
}

// 채팅 메시지 인터페이스
export interface ChatMessage {
    id: number;
    role: 'user' | 'model';
    text: string;
    timestamp: Date;
    isTyping?: boolean;
}

// 전체 일정 정보 타입
export interface Schedule {
    id: number;
    title: string;
    date: string; // 'YYYY-MM-DD' 형식
    start_time: string; // 'HH:MM' 형식
    end_time: string; // 'HH:MM' 형식
    content: string | null;
    created_at: string;
    updated_at: string;
    user_id: number;
}

// 인증 컨텍스트 타입
export interface AuthContextType {
    user: User | null;
    isLoggedIn: boolean;
    login: () => void; // 로그인 성공 후 상태 갱신용 트리거
    logout: () => void;
    loading: boolean;
}