import React, { useState, useEffect } from 'react';
import { CalendarEvent } from '@/types';

interface EventModalProps {
  isOpen: boolean;
  mode: 'create' | 'view';
  event?: CalendarEvent | null;
  onClose: () => void;
  onCreate?: (event: CalendarEvent) => void;
  onDelete?: (id: string) => void;
}

export const EventModal: React.FC<EventModalProps> = ({ isOpen, mode, event, onClose, onCreate, onDelete }) => {
  const [title, setTitle] = useState('');
  const [date, setDate] = useState(new Date().toISOString().split('T')[0]);
  const [startTime, setStartTime] = useState('10:00');
  const [endTime, setEndTime] = useState('11:30');
  const [description, setDescription] = useState('');

  useEffect(() => {
    if (isOpen) {
      if (mode === 'view' && event) {
        setTitle(event.title);
        // Adjust date for timezone if needed, simplifying for demo
        setDate(event.date.toISOString().split('T')[0]);
        setStartTime(event.startTime);
        setEndTime(event.endTime);
        setDescription(event.description || '');
      } else {
        // Reset for create
        setTitle('');
        setStartTime('10:00');
        setEndTime('11:00');
        setDescription('');
      }
    }
  }, [isOpen, mode, event]);

  if (!isOpen) return null;

  const handleSubmit = () => {
    if (onCreate) {
      onCreate({
        id: Math.random().toString(36).substr(2, 9),
        title: title || '새 일정',
        date: new Date(date),
        startTime,
        endTime,
        description,
        colorClass: 'bg-blue-100 text-blue-800' // Default color
      });
      onClose();
    }
  };

  // Backdrop
  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm transition-opacity">
      <div className="relative w-full max-w-lg overflow-hidden rounded-xl bg-white shadow-2xl dark:bg-[#101922] dark:border dark:border-gray-700 animate-scale-in">
        
        {mode === 'view' && event ? (
          // VIEW MODE
          <div className="p-6">
            <div className="flex items-center justify-between">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">{title}</h2>
              <div className="flex items-center gap-2">
                <button className="rounded-full p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700">
                  <span className="material-symbols-outlined text-[20px]">edit</span>
                </button>
                <button 
                    onClick={() => onDelete && onDelete(event.id)}
                    className="rounded-full p-1.5 text-gray-500 hover:bg-gray-100 hover:text-red-600 dark:text-gray-400 dark:hover:bg-gray-700"
                >
                  <span className="material-symbols-outlined text-[20px]">delete</span>
                </button>
                <button onClick={onClose} className="rounded-full p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700">
                  <span className="material-symbols-outlined text-[20px]">close</span>
                </button>
              </div>
            </div>
            <div className="mt-6 space-y-4">
              <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                <span className="material-symbols-outlined text-gray-500 text-[20px]">schedule</span>
                <p className="text-sm">
                  {date}, {startTime} - {endTime}
                </p>
              </div>
              {description && (
                <div className="flex items-start gap-3 text-gray-700 dark:text-gray-300">
                    <span className="material-symbols-outlined mt-0.5 text-gray-500 text-[20px]">notes</span>
                    <p className="text-sm">{description}</p>
                </div>
              )}
            </div>
          </div>
        ) : (
          // CREATE MODE
          <div className="flex flex-col">
            <div className="border-b border-gray-200 p-6 dark:border-gray-700">
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">새 일정 생성</h2>
            </div>
            <div className="space-y-6 p-6">
              <div className="flex flex-col">
                <label htmlFor="title" className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">제목</label>
                <input 
                    id="title" 
                    type="text"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    placeholder="예: 팀 회의" 
                    className="form-input w-full rounded-lg border-gray-300 bg-gray-50 text-gray-900 placeholder:text-gray-400 focus:border-primary focus:ring-primary dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-primary"
                />
              </div>
              
              <div className="flex flex-col">
                <label htmlFor="date" className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">날짜</label>
                <input 
                    id="date" 
                    type="date" 
                    value={date}
                    onChange={(e) => setDate(e.target.value)}
                    className="form-input w-full rounded-lg border-gray-300 bg-gray-50 text-gray-900 focus:border-primary focus:ring-primary dark:border-gray-600 dark:bg-gray-700 dark:text-white"
                />
              </div>

              <div className="flex items-end gap-2">
                <div className="relative flex flex-1 flex-col">
                  <label className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">시작 시간</label>
                  <input 
                    type="time" 
                    value={startTime}
                    onChange={(e) => setStartTime(e.target.value)}
                    className="form-input w-full rounded-lg border-gray-300 bg-gray-50 text-gray-900 focus:border-primary focus:ring-primary dark:border-gray-600 dark:bg-gray-700 dark:text-white" 
                  />
                </div>
                <div className="pb-2.5">
                   <span className="material-symbols-outlined text-gray-400 dark:text-gray-500">arrow_forward</span>
                </div>
                <div className="relative flex flex-1 flex-col">
                  <label className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">종료 시간</label>
                   <input 
                    type="time" 
                    value={endTime}
                    onChange={(e) => setEndTime(e.target.value)}
                    className="form-input w-full rounded-lg border-gray-300 bg-gray-50 text-gray-900 focus:border-primary focus:ring-primary dark:border-gray-600 dark:bg-gray-700 dark:text-white" 
                  />
                </div>
              </div>
              
              <div className="flex flex-col">
                <label htmlFor="description" className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">내용</label>
                <textarea 
                    id="description" 
                    rows={4}
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="일정에 대한 상세 내용을 입력하세요."
                    className="form-textarea w-full resize-none rounded-lg border-gray-300 bg-gray-50 text-gray-900 placeholder:text-gray-400 focus:border-primary focus:ring-primary dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-primary"
                ></textarea>
              </div>
            </div>
            <div className="flex flex-col-reverse justify-end gap-3 border-t border-gray-200 bg-gray-50 p-6 dark:border-gray-700 dark:bg-gray-800/50 sm:flex-row">
              <button onClick={onClose} className="flex h-10 w-full items-center justify-center rounded-lg bg-white px-4 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-50 dark:bg-gray-700 dark:text-gray-200 dark:ring-gray-600 dark:hover:bg-gray-600 sm:w-auto">
                취소
              </button>
              <button onClick={handleSubmit} className="flex h-10 w-full items-center justify-center rounded-lg bg-primary px-4 text-sm font-medium text-white shadow-sm hover:bg-primary/90 sm:w-auto">
                생성
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};
