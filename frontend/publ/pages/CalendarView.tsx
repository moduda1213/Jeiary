import React, { useState } from 'react';
import { CalendarEvent } from '@/types';
import { EventModal } from '@/components/EventModal';

interface CalendarViewProps {
  events: CalendarEvent[];
  onAddEvent: (event: CalendarEvent) => void;
  onDeleteEvent: (id: string) => void;
}

export const CalendarView: React.FC<CalendarViewProps> = ({ events, onAddEvent, onDeleteEvent }) => {
  const [currentDate, setCurrentDate] = useState(new Date(2024, 7, 1)); // August 2024 as per design
  const [selectedEvent, setSelectedEvent] = useState<CalendarEvent | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [modalMode, setModalMode] = useState<'create' | 'view'>('view');

  const daysInMonth = new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 0).getDate();
  const startDayOfWeek = new Date(currentDate.getFullYear(), currentDate.getMonth(), 1).getDay();

  const handlePrevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };

  const handleNextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const handleDayClick = (day: number) => {
    // Optional: pre-fill date in create modal
    setModalMode('create');
    setIsModalOpen(true);
  };

  const handleEventClick = (e: React.MouseEvent, event: CalendarEvent) => {
    e.stopPropagation();
    setSelectedEvent(event);
    setModalMode('view');
    setIsModalOpen(true);
  };

  // Generate calendar grid days
  const renderDays = () => {
    const days = [];
    // Previous month padding
    for (let i = 0; i < startDayOfWeek; i++) {
      days.push(
        <div key={`prev-${i}`} className="relative flex min-h-[120px] flex-col border-b border-r border-[#E5E7EB] bg-gray-50/30 p-2 text-gray-300 dark:border-gray-700 dark:bg-gray-800/20 dark:text-gray-600">
          {/* Placeholder for prev month dates if needed */}
        </div>
      );
    }
    // Current month
    for (let day = 1; day <= daysInMonth; day++) {
      const currentDayDate = new Date(currentDate.getFullYear(), currentDate.getMonth(), day);
      const dayEvents = events.filter(e => {
        const eDate = new Date(e.date);
        return eDate.getDate() === day && eDate.getMonth() === currentDate.getMonth() && eDate.getFullYear() === currentDate.getFullYear();
      });

      const isToday = day === 12; // Hardcoded for demo visuals as per design (Aug 12 highlighted)

      days.push(
        <div 
            key={day} 
            onClick={() => handleDayClick(day)}
            className={`relative flex min-h-[120px] cursor-pointer flex-col border-b border-r border-[#E5E7EB] p-2 transition-colors hover:bg-gray-50 dark:border-gray-700 dark:hover:bg-gray-800 ${isToday ? 'bg-primary/5 dark:bg-primary/10' : ''}`}
        >
          <span className={`mb-1 flex h-7 w-7 items-center justify-center rounded-full text-sm font-medium ${isToday ? 'bg-primary text-white font-bold' : 'text-gray-700 dark:text-gray-300'}`}>
            {day}
          </span>
          <div className="flex flex-col gap-1">
            {dayEvents.map(event => (
              <div 
                key={event.id}
                onClick={(e) => handleEventClick(e, event)}
                className={`cursor-pointer truncate rounded-md px-2 py-1 text-xs font-medium ${event.colorClass}`}
              >
                {event.title}
              </div>
            ))}
          </div>
        </div>
      );
    }
    // Next month padding to fill 35 or 42 cells if needed
    // Omitted for brevity, CSS grid handles layout
    return days;
  };

  return (
    <div className="flex h-full flex-col">
      <header className="flex flex-col gap-4 border-b border-gray-200 bg-white p-6 dark:border-gray-700 dark:bg-[#101922] sm:flex-row sm:items-center sm:justify-between">
        <div className="flex items-center gap-4">
          <h1 className="text-3xl font-bold tracking-tight text-gray-900 dark:text-white">
            {currentDate.getFullYear()}년 {currentDate.getMonth() + 1}월
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
          <button className="rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-gray-800 dark:text-gray-300 dark:hover:bg-gray-700">
            오늘
          </button>
        </div>
      </header>
      
      <div className="flex-1 overflow-auto bg-white dark:bg-[#101922]">
        <div className="grid grid-cols-7 border-b border-gray-200 bg-gray-50 text-center text-sm font-semibold text-gray-500 dark:border-gray-700 dark:bg-[#161f29] dark:text-gray-400">
          {['일', '월', '화', '수', '목', '금', '토'].map(d => (
            <div key={d} className="py-3">{d}</div>
          ))}
        </div>
        <div className="grid grid-cols-7 auto-rows-fr border-l border-gray-200 dark:border-gray-700">
           {renderDays()}
        </div>
      </div>

      <EventModal 
        isOpen={isModalOpen} 
        mode={modalMode} 
        event={selectedEvent} 
        onClose={() => setIsModalOpen(false)}
        onCreate={onAddEvent}
        onDelete={(id) => {
            onDeleteEvent(id);
            setIsModalOpen(false);
        }}
      />
    </div>
  );
};
