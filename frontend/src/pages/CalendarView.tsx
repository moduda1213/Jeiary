import React, { useState, useEffect } from 'react';
import { format, addMonths, subMonths, startOfMonth, endOfMonth, startOfWeek, endOfWeek, eachDayOfInterval, isSameMonth, isSameDay } from 'date-fns';
import { ko } from 'date-fns/locale'; // 날짜 한국어 포맷
import { getSchedules, createSchedule, updateSchedule, deleteSchedule } from '@/api/schedule';
import type { CalendarEvent, Schedule } from '@/types';
import { EventModal } from '@/components/EventModal';
import { toast } from "sonner";

const CalendarView: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'view'>('view');

  // 7가지 색상 팔레트 (Tailwind CSS)
  const EVENT_COLORS = [
    'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',       // 파랑
    'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',     // 초록
    'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300', // 보라
    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300', // 노랑
    'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',             // 빨강
    'bg-pink-100 text-pink-800 dark:bg-pink-900/30 dark:text-pink-300',         // 분홍
    'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300', // 남색
  ];

  // ID를 기반으로 항상 같은 색상을 반환하는 함수
  const getEventColor = (id: number) => {
    return EVENT_COLORS[id % EVENT_COLORS.length];
  };

  // 일정 데이터 불러오기
  const fetchEvents = async () => {
    try {
      const data = await getSchedules(currentDate);
      // API 응답(Schedule)을 UI 모델(CalendarEvent)로 변환
      const mappedEvents: CalendarEvent[] = data.map((item: Schedule) => ({
        id: item.id,
        title: item.title,
        content: item.content || '',
        date: new Date(item.date), // YYYY-MM-DD -> Date 객체
        start_time: item.start_time,
        end_time: item.end_time,
        colorClass: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300' // 기본 색상
      }));
      setEvents(mappedEvents);
    } catch (error) {
      console.error("일정 로딩 실패:", error);
    }
  };

  useEffect(() => {
    fetchEvents();
  }, [currentDate]);
  // 월 이동 핸들러
  const handlePrevMonth = () => setCurrentDate(subMonths(currentDate, 1));
  const handleNextMonth = () => setCurrentDate(addMonths(currentDate, 1));
  const handleToday = () => setCurrentDate(new Date());
  // 날짜 클릭 (일정 생성)
  const handleDayClick = (date: Date) => {
    setSelectedEvent({ date } as CalendarEvent); // 날짜만 미리 채움
    setModalMode('create');
    setIsModalOpen(true);
  };
  // 일정 클릭 (상세 보기)
  const handleEventClick = (e: React.MouseEvent, event: CalendarEvent) => {
    e.stopPropagation();
    setSelectedEvent(event);
    setModalMode('view');
    setIsModalOpen(true);
  };
  // 일정 저장 (API 호출)
  const handleCreateEvent = async (eventData: Partial<CalendarEvent>) => {
    try {
      if (!eventData.date || !eventData.title || !eventData.start_time || !eventData.end_time) return;
      // Date 객체를 YYYY-MM-DD 문자열로 변환
      const dateStr = format(eventData.date, 'yyyy-MM-dd');
      await createSchedule({
        title: eventData.title,
        date: dateStr,
        start_time: eventData.start_time,
        end_time: eventData.end_time,
        content: eventData.content
      });
      await fetchEvents(); // 목록 갱신
      toast.success("일정이 생성되었습니다.");
    } catch (error) {
      toast.error("일정 생성에 실패했습니다.");
    }
  };

  // 일정 수정 (API 호출)
  const handleUpdateEvent = async (id:number, eventData: Partial<CalendarEvent>) => {
    try {
      if (!id || !eventData.date || !eventData.title || !eventData.start_time || !eventData.end_time) return;
      // Date 객체를 YYYY-MM-DD 문자열로 변환
      const dateStr = format(eventData.date, 'yyyy-MM-dd');
      await updateSchedule(id, {
        title: eventData.title,
        date: dateStr,
        start_time: eventData.start_time,
        end_time: eventData.end_time,
        content: eventData.content
      });
      await fetchEvents(); // 목록 갱신
      setIsModalOpen(false);
      toast.success("일정이 수정되었습니다.");
    } catch (error) {
      console.log(error);
      toast.error("일정 생성에 실패했습니다.");
    }
  };
  
  // 일정 삭제 (API 호출)
  const handleDeleteEvent = async (id: number) => {
    if (!confirm("정말 삭제하시겠습니까?")) return;
    try {
      await deleteSchedule(id);
      await fetchEvents();
      setIsModalOpen(false);
    } catch (error) {
      console.error("일정 삭제 실패:", error);
    }
  };
  // 캘린더 그리드 생성
  const monthStart = startOfMonth(currentDate);
  const monthEnd = endOfMonth(monthStart);
  const startDate = startOfWeek(monthStart);
  const endDate = endOfWeek(monthEnd);
  const calendarDays = eachDayOfInterval({ start: startDate, end: endDate });
  return (
     <div className="flex h-full flex-col">
       {/* 1. 헤더 스타일 개선 (publ 스타일 적용) */}
       <header className="flex flex-col gap-4 border-b border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-[#101922] sm:flex-row sm:items-center sm:justify-between">
         <div className="flex items-center gap-4">
           <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
             {format(currentDate, 'yyyy년 M월', { locale: ko })}
           </h1>
           <div className="flex items-center rounded-full bg-gray-100 p-0.5 dark:bg-gray-800">
             <button onClick={handlePrevMonth} className="flex h-8 w-8 items-center justify-center rounded-full text-gray-600 hover:bg-white hover:shadow-sm dark:text-gray-400 dark:hover:bg-gray-700">
               <span className="material-symbols-outlined text-[20px]">chevron_left</span>
             </button>
             <button onClick={handleNextMonth} className="flex h-8 w-8 items-center justify-center rounded-full text-gray-600 hover:bg-white hover:shadow-sm dark:text-gray-400 dark:hover:bg-gray-700">
               <span className="material-symbols-outlined text-[20px]">chevron_right</span>
             </button>
           </div>
         </div>
         <div>
           <button 
             onClick={handleToday}
             className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 
      dark:hover:bg-gray-700"
          >
            오늘
          </button>
        </div>
      </header>
      <div className="flex-1 overflow-auto bg-white dark:bg-[#101922]">
        {/* 요일 헤더 */}
        <div className="grid grid-cols-7 border-b border-gray-200 bg-gray-50 text-center text-sm font-semibold text-gray-500 dark:border-gray-700 dark:bg-[#161f29] dark:text-gray-400">
            {['일', '월', '화', '수', '목', '금', '토'].map(day => (
            <div key={day} className="py-3">{day}</div>
            ))}
        </div>
        {/* 2. 날짜 그리드 (publ 스타일 적용) */}
        <div className="grid grid-cols-7 auto-rows-fr border-l border-gray-200 dark:border-gray-700">
            {calendarDays.map((day) => {
                const dayEvents = events.filter(e => isSameDay(e.date, day));
                const isCurrentMonth = isSameMonth(day, monthStart);
                const isTodayDay = isSameDay(day, new Date());
                return (
                    <div
                        key={day.toISOString()}
                        onClick={() => handleDayClick(day)}
                        className={`
                            relative flex min-h-[120px] cursor-pointer flex-col border-b border-r border-[#E5E7EB] p-2 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800     
                            ${isTodayDay ? 'bg-primary/5 dark:bg-primary/10' : ''}
                            ${!isCurrentMonth ? 'bg-gray-100 text-gray-300 dark:bg-gray-800/20 dark:text-gray-600' : ''}
                        `}
                    >
                        <span className={`mb-1 flex h-7 w-7 items-center justify-center rounded-full text-sm font-medium ${isTodayDay ? 'bg-primary text-white font-bold' : 'text-gray-700 dark:text-gray-300'}`}>
                            {format(day, 'd')}
                        </span>
                        <div className="flex flex-col gap-1">
                            {dayEvents.map(event => (
                                <div
                                    key={event.id}
                                    onClick={(e) => handleEventClick(e, event)}
                                    className={`cursor-pointer truncate rounded-md px-2 py-1 text-xs font-medium ${getEventColor(event.id)}`}
                                >
                                    {event.title}
                                </div>
                            ))}
                        </div>
                    </div>
                );
            })}
        </div>
      </div>
      <EventModal
        isOpen={isModalOpen}
        mode={modalMode}
        event={selectedEvent}
        onClose={() => setIsModalOpen(false)}
        onCreate={handleCreateEvent}
        onUpdate={handleUpdateEvent}
        onDelete={handleDeleteEvent}
      />
    </div>
  );
};
export default CalendarView;