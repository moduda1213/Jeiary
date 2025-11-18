import { useScheduleStore } from "../stores/scheduleStore";
import { useEffect, useState } from "react";
import {
  Dialog,
  DialogContent,
  DialogTitle,
  DialogDescription,
  DialogPortal,
  DialogOverlay,
} from "./ui/dialog";
import type { Event } from "./CalendarView";
import { Calendar, Clock, Pencil, Trash } from "lucide-react";
import { Badge } from "./ui/badge";
import { Button } from "./ui/button";

import { Card } from "./ui/card";
import * as VisuallyHidden from "@radix-ui/react-visually-hidden";

interface ScheduleDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  events: Event[];
  date: Date | null;
  onEditClick: (event: Event) => void;
}

export function ScheduleDialog({
  open,
  onOpenChange,
  events,
  date,
  onEditClick,
}: ScheduleDialogProps) {
  const { removeSchedule } = useScheduleStore();
  const [localError, setLocalError] = useState<string | null>(null);

  useEffect(() => {
    if(open) {
      setLocalError(null);
    }
  }, [open]);

  const handleDelete = async (id: number) => {
    if (window.confirm("정말로 이 일정을 삭제하시겠습니까?")) {
      try {
        await removeSchedule(id);
        onOpenChange(false);
      }catch (error) {
        setLocalError ("일정 삭제에 실패했습니다.");
      }
    } 
  }

  if (!date) return null;

  const formatTimeForDisplay = (time: string): string => {
    if(!time) return "";
    const [hour, minute] = time.split(':').map(Number);
    const ampm = hour < 12 ? '오전' : '오후';
    const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
    return `${ampm} ${displayHour}시 ${minute.toString().padStart(2,'0')}분`;
  }

  const formatTimeRangeForDisplay = (startTime: string, endTime: string): string => {
    const formattedStartTime = formatTimeForDisplay(startTime);
    const formattedEndTime = formatTimeForDisplay(endTime);
    return `${formattedStartTime} - ${formattedEndTime}`;
  }

  const formatDate = (date: Date) => {
    const days = [
      "일요일",
      "월요일",
      "화요일",
      "수요일",
      "목요일",
      "금요일",
      "토요일",
    ];
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일 ${
      days[date.getDay()]
    }`;
  };

  const isSingleEventView = events.length === 1;

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogPortal>
        <DialogOverlay className="bg-black/20 backdrop-blur-sm" />
        <DialogContent className="max-w-4xl h-[600px] p-0 gap-0 border-0 shadow-2xl overflow-hidden">
          <VisuallyHidden.Root>
            <DialogTitle>일정 상세</DialogTitle>
            <DialogDescription>
              {formatDate(date)}의 일정 목록을 표시합니다
            </DialogDescription>
          </VisuallyHidden.Root>

          <div className="flex flex-col h-full">
            <div className="p-6 border-b bg-white">
              {isSingleEventView && (
                <div className="flex items-center justify-start gap-4">
                  <Button variant="outline" size="icon" onClick={() => onEditClick(events[0])}>
                    <Pencil className="w-4 h-4" />
                  </Button>
                  <Button variant="destructive" size="icon" onClick={() => handleDelete(events[0].id)}>
                    <Trash className="w-4 h-4" />
                  </Button>
                </div>
              )}
            </div>

            <div className="flex-1 overflow-y-auto p-6 bg-gray-50">
              {/* 에러 메세지 표시 */}
              {localError && (
                <div className="text-center text-red-500 text-sm mb-4">
                  {localError}
                </div>
              )}
              {events.length > 0 ? (
                <div className="space-y-4 max-w-2xl mx-auto">
                  {events.map((event) => (
                    <Card
                      key={event.id}
                      className="p-6 bg-white"
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div>
                          <h3 className="mb-2">
                            {event.title}
                          </h3>
                          <div className="flex items-center gap-2 text-gray-600 mb-2">
                            <Calendar className="w-4 h-4" />
                            <span>{formatDate(event.date)}</span>
                          </div>
                          <div className="flex items-center gap-2 text-gray-600">
                            <Clock className="w-4 h-4" />
                            <span>
                              {formatTimeRangeForDisplay(event.start_time, event.end_time)}
                            </span>
                          </div>
                        </div>
                        <Badge>일정</Badge>
                      </div>
                      <div className="border-t pt-4">
                        <h4 className="mb-2 text-sm">
                          상세 내용
                        </h4>
                        <p className="text-gray-700">
                          {event.content}
                        </p>
                      </div>
                    </Card>
                  ))}
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="mb-4 flex justify-center">
                    <div className="w-16 h-16 rounded-full bg-gray-100 flex items-center justify-center">
                      <Calendar className="w-8 h-8 text-gray-400" />
                    </div>
                  </div>
                  <h3 className="mb-2">일정이 없습니다</h3>
                  <p className="text-sm text-gray-500">
                    이 날짜에 등록된 일정이 없습니다
                  </p>
                </div>
              )}
            </div>
          </div>
        </DialogContent>
      </DialogPortal>
    </Dialog>
  );
}