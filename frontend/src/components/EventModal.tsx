import React, { useState, useEffect } from 'react';
import { type CalendarEvent } from '@/types';
import { format, addHours } from 'date-fns';
 
interface EventModalProps {
    isOpen: boolean;
    mode: 'create' | 'view';
    event?: CalendarEvent | null;
    onClose: () => void;
    onCreate?: (event: Partial<CalendarEvent>) => void;
    onUpdate?: (id: number, event: Partial<CalendarEvent>) => void;
    onDelete?: (id: number) => void;
}
 
export const EventModal: React.FC<EventModalProps> = ({ isOpen, mode, event, onClose, onCreate, onUpdate, onDelete }) => {
    const [title, setTitle] = useState('');
    const [date, setDate] = useState('');
    const [startTime, setStartTime] = useState('10:00');
    const [endTime, setEndTime] = useState('11:30');
    const [content, setContent] = useState('');
    const [isEditing, setIsEditing] = useState(false);

    // 모달이 열릴 때 데이터 초기화
    useEffect(() => {
        if (isOpen) {
            setIsEditing(false);
            if (mode === 'view' && event) {
                setTitle(event.title);
                const dateStr = event.date instanceof Date 
                    ? format(event.date, 'yyyy-MM-dd')
                    : String(event.date).split('T')[0];
                
                setDate(dateStr);
                setStartTime(event.start_time);
                setEndTime(event.end_time);
                setContent(event.content || '');
            } else {
                // 생성 모드 초기값
                setTitle('');

                const now = new Date();
                const minutes = now.getMinutes();

                if (minutes < 30) {
                    now.setMinutes(30);
                } else {
                    now.setHours(now.getHours() + 1);
                    now.setMinutes(0);
                }
                now.setSeconds(0);

                const end = addHours(now, 1);
                const targetDate = event?.date ? event.date : now;

                setDate(format(targetDate, 'yyyy-MM-dd'));
                setStartTime(format(now, 'HH:mm'));
                setEndTime(format(end, 'HH:mm'));
                setContent('');
            }
        }
    }, [isOpen, mode, event]);

    if (!isOpen) return null;

    const handleSubmit = () => {
        const eventData = {
            title,
            date: new Date(date),
            start_time:startTime,
            end_time: endTime,
            content,
        };
        if (isEditing && event && onUpdate) {
            onUpdate(event.id, eventData);
            onClose();

        } else if (onCreate) {
            onCreate(eventData);
            onClose()
        }
    };

    return (
    // Backdrop
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm transition-opacity"
        onClick={(e) => {if (e.target === e.currentTarget) onClose()} }>

        <div className="relative w-full max-w-lg overflow-hidden rounded-xl bg-white shadow-2xl dark:bg-[#101922] dark:border dark:border-gray-700 animate-scale-in">
        {mode === 'view' && event && !isEditing ? (
            // VIEW MODE (publ 스타일)
            <div className="p-6">
                <div className="flex items-center justify-between">
                    <h2 className="text-xl font-bold text-gray-900 dark:text-white">{title}</h2>
                    <div className="flex items-center gap-2">
                        <button 
                            onClick={() => setIsEditing(true)}
                            type = "button"
                            className="rounded-full p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700">
                            <span className="material-symbols-outlined text-[20px]">edit</span>
                        </button>
                        {onDelete && (
                            <button
                                onClick={() => onDelete(event.id)}
                                className="rounded-full p-1.5 text-gray-500 hover:bg-gray-100 hover:text-red-600 dark:text-gray-400 dark:hover:bg-gray-700"
                            >
                                <span className="material-symbols-outlined text-[20px]">delete</span>
                            </button>
                        )}
                        <button onClick={onClose} type="button" className="rounded-full p-1.5 text-gray-500 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-700">
                            <span className="material-symbols-outlined text-[20px]">close</span>
                        </button>
                    </div>
                </div>
                <div className="mt-6 space-y-4">
                    {/* 날짜 표시 */}
                    <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                        <span className="material-symbols-outlined text-gray-500 text-[20px]">calendar_today</span>
                        <p className="text-sm font-medium">{date}</p>
                    </div>

                    {/* 시간 표시 */}
                    <div className="flex items-center gap-3 text-gray-700 dark:text-gray-300">
                        <span className="material-symbols-outlined text-gray-500 text-[20px]">schedule</span>
                        <p className="text-sm">
                            {startTime} - {endTime}
                        </p>
                    </div>
                    {content && (
                    <div className="flex items-start gap-3 text-gray-700 dark:text-gray-300">
                        <span className="material-symbols-outlined mt-0.5 text-gray-500 text-[20px]">notes</span>
                        <p className="text-sm whitespace-pre-wrap">{content}</p>
                    </div>
                    )}
                </div>
            </div>
        ) : (
            // CREATE MODE (publ 스타일)
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
                        className="form-input w-full rounded-lg border-gray-300 bg-gray-50 text-gray-900 placeholder:text-gray-400 focus:border-primary focus:ring-primary dark:border-gray-600
                                dark:bg-gray-700 dark:text-white dark:focus:border-primary"
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
                    <label htmlFor="content" className="mb-2 text-sm font-medium text-gray-700 dark:text-gray-300">내용</label>
                    <textarea
                        id="content"
                        rows={4}
                        value={content}
                        onChange={(e) => setContent(e.target.value)}
                        placeholder="일정에 대한 상세 내용을 입력하세요."
                        className="form-textarea w-full resize-none rounded-lg border-gray-300 bg-gray-50 text-gray-900 placeholder:text-gray-400 focus:border-primary focus:ring-primary dark:border-gray-60
                                dark:bg-gray-700 dark:text-white dark:focus:border-primary"
                    ></textarea>
                    </div>
                </div>
                <div className="flex flex-col-reverse justify-end gap-3 border-t border-gray-200 bg-gray-50 p-6 dark:border-gray-700 dark:bg-gray-800/50 sm:flex-row">
                    <button 
                        type="button" 
                        onClick={() => {
                            if (isEditing) setIsEditing(false);
                            else onClose();
                        }} 
                        className="flex h-10 w-full items-center justify-center rounded-lg bg-white px-4 text-sm font-medium text-gray-700 ring-1 ring-inset ring-gray-300 hover:bg-gray-
                                dark:bg-gray-700 dark:text-gray-200 dark:ring-gray-600 dark:hover:bg-gray-600 sm:w-auto">
                        취소
                    </button>
                    <button 
                        type="button" 
                        onClick={handleSubmit} 
                        className="flex h-10 w-full items-center justify-center rounded-lg bg-primary px-4 text-sm font-medium text-white shadow-sm hover:bg-primary/90 sm:w-auto"> 
                        {isEditing ? '수정' : '생성'}
                    </button>
                </div>
            </div>
            )}
        </div>
    </div>
    );
};