import apiClient from "./client";

export interface AIParsedSchedule{
    title: string;
    date: string; // YYYY-MM-DD
    content: string | null;
    start_time: string; // HH:MM
    end_time: string; // HH:MM
}

export interface AIParseResponse{
    is_complete: boolean;
    data: AIParsedSchedule | null; // is_complete가 true일 경우 ScheduleData 객체
    question: string | null; // is_complete가 false일 경우 사용자에게 던질 질문
}

/**
 * AI 파싱 엔드포인트에 텍스트를 전송학 응답을 받습니다.
 * @param text 파싱할 자연어 텍스트
 * @returns AI 파싱 결과
 */
export const parseTextWithAI = async (text: string): Promise<AIParseResponse> => {
    try {
        const response = await apiClient.post<AIParseResponse>('/ai/parse', {text});
        return response.data;
    } catch (error) {
        console.error('AI에게 요청한 문자 파싱 작업 중 에러: ', error);
        throw error;
    }
}