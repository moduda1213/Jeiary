import { create } from 'zustand';
import { getSchedules, createSchedule, updateSchedule, deleteSchedule, type Schedule, type ScheduleCreate, type ScheduleUpdate } from '../api/schedule';

interface ScheduleState {
    schedules: Schedule[];
    isLoading: boolean;
    error: string | null;
    fetchSchedules: (date: Date) => Promise<void>;
    addSchedule: (ScheduleData: ScheduleCreate) => Promise<void>;
    editSchedule: (id: number, scheduleData: ScheduleUpdate) => Promise<void>;
    removeSchedule: (id: number) => Promise<void>;
}

export const useScheduleStore = create<ScheduleState>((set) => ({
    schedules: [],
    isLoading: false,
    error: null,

    // API 호출하여 schedules 상태를 업데이트하는 비동기 액션
    fetchSchedules: async (date: Date) => {
        set({ isLoading: true, error: null });
        try {
            const data = await getSchedules(date);
            set({ schedules: data, isLoading: false });
        } catch (err) {
            set({ error: '일정을 불러오는 데 실패했습니다.', isLoading: false });
            console.error("일정 조회 중 에러: ", err);
        }
    },

    addSchedule: async (scheduleData: ScheduleCreate) => {
        set({ isLoading: true, error: null });
        try {
            console.log("addSchedule 진입")
            const newSchedule = await createSchedule(scheduleData);
            set((state) => ({
                schedules: [...state.schedules, newSchedule],
                isLoading: false,
            }));
        } catch (err) {
            set({ error: '일정 생성에 실패했습니다.', isLoading: false });
            console.error("일정 생성 중 에러: ", err);
            throw err;
        }
    },

    editSchedule: async (id: number, scheduleData: ScheduleUpdate) => {
        set({ isLoading: true, error: null });
        try {
            const updatedSchedule = await updateSchedule(id, scheduleData);
            set((state) => ({
                schedules: state.schedules.map((s) =>
                    s.id === id ? { ...s, ...updatedSchedule } : s
                ),
                isLoading: false,
            }));
        } catch (err) {
            set({ error: '일정 수정에 실패했습니다.', isLoading: false });
            console.error("일정 수정 중 에러: ", err);
            throw err;
        }
    },

    removeSchedule: async (id: number) => {
        set({ isLoading: true, error: null });
        try {
            await deleteSchedule(id);
            set((state) => ({
                schedules: state.schedules.filter((s) => s.id !== id),
                isLoading: false,
            }));
        } catch (err) {
            set({ error: '일정 삭제에 실패했습니다.', isLoading: false });
            console.error("일정 삭제 중 에러: ", err);
            throw err;
        }
    },
}));