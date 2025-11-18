import { useState, useEffect, useMemo } from "react";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogFooter,
  DialogTitle,
  DialogDescription,
  DialogClose,
} from "./ui/dialog";
import { Button } from "./ui/button";
import { Input } from "./ui/input";
import { Textarea } from "./ui/textarea";
import { Label } from "./ui/label";
import type { Event } from "./CalendarView";

export type EventSubmitData = {
  title: string;
  content: string | null;
  start_time: string;
  end_time: string;
};

interface AddEventDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onSubmit: (eventData: EventSubmitData) => void;
  date: Date | null;
  eventToEdit?: Event | null;
}

// 시간 관련 헬퍼 함수
const generateTimeSlots = () => {
  const slots: string[] = [];
  for (let h = 0; h < 24; h++) {
    for (let m = 0; m < 60; m += 15) {
      const hour = h.toString().padStart(2, '0');
      const minute = m.toString().padStart(2, '0');
      slots.push(`${hour}:${minute}`);
    }
  }
  return slots;
};

const formatTimeForDisplay = (time: string): string => {
  if (!time) return "";
  const [hour, minute] = time.split(':').map(Number);
  const ampm = hour < 12 ? '오전' : '오후';
  const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
  return `${ampm} ${displayHour}시 ${minute.toString().padStart(2, '0')}분`;
};

const getDefaultTimes = () => {
  const now = new Date();
  const minutes = now.getMinutes();
  const roundedMinutes = Math.ceil(minutes / 15) * 15;

  const startTime = new Date(now);
  startTime.setSeconds(0);
  startTime.setMilliseconds(0);
  startTime.setMinutes(roundedMinutes);
  
  if (roundedMinutes === 60) {
      startTime.setHours(startTime.getHours() + 1);
      startTime.setMinutes(0);
  }

  const endTime = new Date(startTime.getTime() + 60 * 60 * 1000); // 1시간 추가

  const formatToHHMM = (date: Date) => {
    const hour = date.getHours().toString().padStart(2, '0');
    const minute = date.getMinutes().toString().padStart(2, '0');
    return `${hour}:${minute}`;
  };

  return {
    start: formatToHHMM(startTime),
    end: formatToHHMM(endTime),
  };
};

export function AddScheduleDialog({ open, onOpenChange, onSubmit, date, eventToEdit }: AddEventDialogProps) {
  const [title, setTitle] = useState("");
  const [startTime, setStartTime] = useState("");
  const [endTime, setEndTime] = useState("");
  const [content, setContent] = useState("");
  const [localError, setLocalError] = useState<string | null>(null);

  const timeSlots = useMemo(() => generateTimeSlots(), []);
  const isEditMode = !!eventToEdit;

  useEffect(() => {
    if (open) {
      setLocalError(null);
      if (isEditMode && eventToEdit) {
        setTitle(eventToEdit.title);
        setContent(eventToEdit.content || "");

        setStartTime(eventToEdit.start_time.substring(0,5));
        setEndTime(eventToEdit.end_time.substring(0,5));

      } else {
        // 추가 모드: 기본값으로 상태 초기화
        const { start, end } = getDefaultTimes();
        setTitle("");
        setStartTime(start);
        setEndTime(end);
        setContent("");
      }
    }
  }, [open, isEditMode, eventToEdit]);

  const handleSubmit = async () => {
    if (!title.trim()) {
      setLocalError("일정 제목을 입력해주세요.");
      return;
    }
    setLocalError(null);
    try {
      await onSubmit({
        title,
        content,
        start_time: startTime,
        end_time: endTime
      });

    } catch (error) {
      setLocalError("일정 저장에 실패했습니다. 다시 시도해주세요.")
    }
    
  };

  const formatDate = (d: Date) => 
    `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{isEditMode ? '일정 수정' : '새로운 일정 추가'}</DialogTitle>
          {(date || eventToEdit?.date) && (
            <DialogDescription>
              {formatDate(date || eventToEdit!.date)}
            </DialogDescription>
          )}
        </DialogHeader>
        
        <div className="grid gap-6 py-4">
          {/* 에러 메세지 표시 */}
          {localError && (
            <div className="col-span-4 text-center text-red-500 text-sm">
              {localError}
            </div>
          )}
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="title" className="text-right">
              일정 제목
            </Label>
            <Input 
              id="title" 
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="col-span-3" 
              placeholder="예: 팀 주간 회의"
            />
          </div>

          <div className="grid grid-cols-4 items-center gap-4">
            <Label className="text-right">시간</Label>
            <div className="col-span-3 grid grid-cols-2 items-center gap-2">
              <select
                value={startTime}
                onChange={(e) => setStartTime(e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                {timeSlots.map(slot => (
                  <option key={`start-${slot}`} value={slot}>
                    {formatTimeForDisplay(slot)}
                  </option>
                ))}
              </select>
              <select
                value={endTime}
                onChange={(e) => setEndTime(e.target.value)}
                className="w-full p-2 border rounded-md"
              >
                {timeSlots.map(slot => (
                  <option key={`end-${slot}`} value={slot}>
                    {formatTimeForDisplay(slot)}
                  </option>
                ))}
              </select>
            </div>
          </div>
          
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="description" className="text-right self-start pt-2">
              상세 내용
            </Label>
            <Textarea
              id="description"
              value={content}
              onChange={(e) => setContent(e.target.value)}
              className="col-span-3"
              rows={5}
              placeholder="일정에 대한 상세 내용을 입력하세요."
            />
          </div>
        </div>

        <DialogFooter>
          <DialogClose asChild>
            <Button type="button" variant="outline">취소</Button>
          </DialogClose>
          <Button type="button" onClick={handleSubmit}>
            {isEditMode ? '수정하기' : '저장하기'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  );
}