import { useEffect, useState } from "react";
import { Header } from "./Header";
import { Sidebar } from "./Sidebar";
import { MonthCalendar } from "./MonthCalendar";
import { VoiceAssistantPanel, type ConversationMessage } from "./VoiceAssistantPanel";
import { ScheduleDialog } from "./ScheduleDialog";
import { useScheduleStore } from "../stores/scheduleStore";
import { AddScheduleDialog, type EventSubmitData } from "./AddScheduleDialog";

import { LoginPage } from "./LoginPage";
import type { Event } from "./CalendarView";

import { useAuth } from "../contexts/AuthContext";


// Mock 데이터
// const mockEvents: Event[] = [
//   {
//     id: 1,
//     date: new Date(2025, 9, 12),
//     title: "팀 회의",
//     content: "분기별 목표 설정 및 프로젝트 진행 상황 공유",
//     start_time: "10:00",
//     end_time: "11:30",
//   },
//   {
//     id: 2,
//     date: new Date(2025, 9, 12),
//     title: "점심 약속",
//     content: "고객사 담당자와 점심 미팅",
//     start_time: "12:30",
//     end_time: "14:00",
//   },
//   {
//     id: 3,
//     date: new Date(2025, 9, 18),
//     title: "프로젝트 발표",
//     content: "신규 서비스 기획안 발표 및 피드백",
//     start_time: "15:00",
//     end_time: "17:00",
//   },
//   {
//     id: 4,
//     date: new Date(2025, 9, 20),
//     title: "개발자 컨퍼런스",
//     content: "최신 기술 트렌드 세미나 참석",
//     start_time: "09:00",
//     end_time: "18:00",
//   },
//   {
//     id: 5,
//     date: new Date(2025, 9, 25),
//     title: "월간 보고",
//     content: "월간 실적 보고 및 다음 달 계획 수립",
//     start_time: "14:00",
//     end_time: "15:30",
//   },
// ];

export function Mainlayout() {
  const {isLoggedIn, logout} = useAuth();

  const { fetchSchedules, addSchedule, editSchedule } = useScheduleStore();

  const [currentDate, setCurrentDate] = useState(new Date());
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [conversations, setConversations] = useState<ConversationMessage[]>([]);
  const [isDetailDialogOpen, setIsDetailDialogOpen] = useState(false);
  const [dialogDate, setDialogDate] = useState<Date | null>(null);
  const [dialogEvents, setDialogEvents] = useState<Event[]>([]);
  const [isAddScheduleDialogOpen, setIsAddScheduleDialogOpen] = useState(false);
  const [eventToEdit, setEventToEdit] = useState<Event | null>(null);

  useEffect(() => {
    fetchSchedules(currentDate);
  }, [currentDate, fetchSchedules]);

  const handleDateSelect = (date: Date) => {
    setSelectedDate(date);
  };

  // 날짜 셀 전체 클릭 시 해당 날짜의 모든 일정을 보여주도록 수정
  const handleDateClick = (date: Date) => {
    setSelectedDate(date); // 날짜를 선택 상태로 업데이트
    setIsAddScheduleDialogOpen(true); // '일정 추가' 다이얼로그를 엶
  };

  // 개별 일정 클릭 시 해당 일정만 보여주는 핸들러 추가
  const handleEventClick = (event: Event) => {
    setDialogDate(event.date);
    setDialogEvents([event]); // 클릭한 이벤트 하나만 배열에 담아 설정
    setIsDetailDialogOpen(true);
  };

  const handleAddOrUpdateEvent = async (submitData: EventSubmitData) => {
    try {
      if (eventToEdit) {
        await editSchedule(eventToEdit.id, submitData);

      } else {
        let year = selectedDate.getFullYear();
        let month = String(selectedDate.getMonth() + 1).padStart(2, '0');
        let day = String(selectedDate.getDate()).padStart(2, '0');
        let formatDate = `${year}-${month}-${day}`;
        const scheduleData = {
          ...submitData,
          date: formatDate
        }
        
        await addSchedule(scheduleData);
      }

      setIsAddScheduleDialogOpen(false); // 다이얼로그 닫기
      setEventToEdit(null); // 수정 상태 초기화

    } catch (error) {
      // TODO. 더 친절한 UI로 교체
      // 스토어 액션에서 throw된 에러를 여기서 다시 throw하여 AddScheduleDialog의 handleSubmit에서 catch하도록 합니다.
      // AddScheduleDialog에서 localError를 설정할 수 있도록 에러를 다시 던집니다.
      throw error;
    }

  };

  const handlePrevMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1)
    )
  }

  const handleNextMonth = () => {
    setCurrentDate(
      new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1)
    )
  }

  const handleToday = () => {
    const today = new Date();
    setCurrentDate(today);
    setSelectedDate(today);
  };

  const handleEditClick = (event: Event) => {
    setEventToEdit(event); // 수정할 이벤트를 상태에 저장
    setIsDetailDialogOpen(false); // 상세 다이얼로그는 닫고
    setIsAddScheduleDialogOpen(true); // 추가/수정 다이얼로그를 열음
  };

  const handleNavigateHome = () => {
    handleToday();
  };

  const handleVoiceInput = (userMessage: string, aiResponse: string) => {
    const timestamp = new Date();
    
    setConversations((prev) => [
      ...prev,
      {
        id: `user-${timestamp.getTime()}`,
        type: "user",
        message: userMessage,
        timestamp: timestamp,
      },
      {
        id: `assistant-${timestamp.getTime()}`,
        type: "assistant",
        message: aiResponse,
        timestamp: new Date(timestamp.getTime() + 1000),
      },
    ]);
  };

  const handleSendMessage = (message: string) => {
    // Mock AI 응답 생성
    const aiResponse = "네, 알겠습니다. 일정을 확인하고 도와드리겠습니다.";
    handleVoiceInput(message, aiResponse);
  };

  // 로그인하지 않은 경우 로그인 페이지 표시
  if (!isLoggedIn) {
    return <LoginPage />;
  }

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <Header
        isLoggedIn={isLoggedIn}
        onLogout={logout}
        onNavigateHome={handleNavigateHome}
      />
      
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        
        <MonthCalendar
          currentDate={currentDate}
          selectedDate={selectedDate}
          onDateSelect={handleDateSelect}
          onDateClick={handleDateClick}
          onEventClick={handleEventClick} 
          onPrevMonth={handlePrevMonth}
          onNextMonth={handleNextMonth}
          onToday={handleToday}
        />

        <VoiceAssistantPanel 
          conversations={conversations} 
          onSendMessage={handleSendMessage}
          onVoiceInput={handleVoiceInput}
        />
      </div>

      <ScheduleDialog
        open={isDetailDialogOpen}
        onOpenChange={setIsDetailDialogOpen}
        events={dialogEvents} // dialogEvents 상태를 props로 전달
        date={dialogDate}
        onEditClick={handleEditClick}
      />
      <AddScheduleDialog
        open={isAddScheduleDialogOpen}
        onOpenChange={(isOpen) => {
          if (!isOpen) {
            setEventToEdit(null);
          }
          setIsAddScheduleDialogOpen(isOpen);
        }}
        onSubmit={handleAddOrUpdateEvent}
        date={selectedDate}
        eventToEdit={eventToEdit}
      />
      
    </div>
  );
}
