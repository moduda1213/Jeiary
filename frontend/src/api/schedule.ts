import apiClient from "./client";

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

// 일정 생성을 위한 타입
export interface ScheduleCreate {
    title: string;
    date: string;
    start_time: string;
    end_time: string;
    content?: string | null;
}

// 일정 수정을 위한 타입
export interface ScheduleUpdate {
    title?: string;
    date?: string;
    start_time?: string;
    end_time?: string;
    content?: string | null;
}

// 일정 조회
export const getSchedules = async (date: Date): Promise<Schedule[]> => {
    const year = date.getFullYear();
    const month = date.getMonth() + 1;

    try {
        const response = await apiClient.get<Schedule[]>('/schedules/', {
            params: {
                year: year,
                month: month,
            },
        });
        return response.data;
    } catch (error) {
        console.error("일정 조회 중 에러: ", error);
        // 실제 프로덕션에서는 에러를 좀 더 잘 처리해야 합니다. (ex: Sentry로 로깅)
        throw error;
    }
}

// 일정 생성
export const createSchedule = async (scheduleData: ScheduleCreate): Promise<Schedule> => {
    try {
        const response = await apiClient.post<Schedule>('/schedules/', scheduleData);
        return response.data;
    } catch (error) {
        console.error("일정 생성 중 에러: ", error);
        throw error;
    }
}

// 일정 수정
export const updateSchedule = async (id: number, scheduleData: ScheduleUpdate): Promise<Schedule> => {
    try {
        const response = await apiClient.put<Schedule>(`/schedules/${id}`, scheduleData);
        return response.data;

    } catch (error) {
        console.error(`일정 수정 중 에러 ${id}: `, error);
        throw error;
    }
}

// 일정 삭제
export const deleteSchedule = async (id: number): Promise<void> => {
    try {
        await apiClient.delete<Schedule>(`/schedules/${id}`);

    } catch (error) {
        console.error(`일정 삭제 중 에러 ${id}: `, error);
        throw error;
    }
}