import { useState } from "react";
import { Calendar } from "./ui/calendar";
import { Card } from "./ui/card";
import { Badge } from "./ui/badge";

export interface Event {
  id: number;
  date: Date;
  title: string;
  content: string | null;
  start_time: string,
  end_time: string
}

interface CalendarViewProps {
  events: Event[];
  onDateClick: (date: Date, dayEvents: Event[]) => void;
}

export function CalendarView({ events, onDateClick }: CalendarViewProps) {
  const [selectedDate, setSelectedDate] = useState<Date | undefined>(new Date());

  const getEventsForDate = (date: Date) => {
    return events.filter(
      (event) =>
        event.date.getDate() === date.getDate() &&
        event.date.getMonth() === date.getMonth() &&
        event.date.getFullYear() === date.getFullYear()
    );
  };

  const handleDateSelect = (date: Date | undefined) => {
    if (date) {
      setSelectedDate(date);
      const dayEvents = getEventsForDate(date);
      onDateClick(date, dayEvents);
    }
  };

  return (
    <div className="p-6 flex flex-col items-center">
      <Card className="p-6">
        <Calendar
          mode="single"
          selected={selectedDate}
          onSelect={handleDateSelect}
          className="rounded-md"
          components={{
            Day: ({ date, ...props }) => {
              const dayEvents = getEventsForDate(date);
              const hasEvents = dayEvents.length > 0;
              
              return (
                <div className="relative">
                  <button
                    {...props}
                    className={`h-9 w-9 p-0 font-normal aria-selected:opacity-100 hover:bg-gray-100 rounded-md ${
                      hasEvents ? "font-semibold" : ""
                    }`}
                  >
                    {date.getDate()}
                  </button>
                  {hasEvents && (
                    <div className="absolute bottom-1 left-1/2 transform -translate-x-1/2 flex gap-0.5">
                      {dayEvents.slice(0, 3).map((_, i) => (
                        <div key={i} className="w-1 h-1 rounded-full bg-blue-500" />
                      ))}
                    </div>
                  )}
                </div>
              );
            },
          }}
        />
      </Card>

      {selectedDate && (
        <div className="mt-6 w-full max-w-2xl">
          <h2 className="mb-4">
            {selectedDate.getFullYear()}년 {selectedDate.getMonth() + 1}월{" "}
            {selectedDate.getDate()}일 일정
          </h2>
          <div className="space-y-3">
            {getEventsForDate(selectedDate).length > 0 ? (
              getEventsForDate(selectedDate).map((event) => (
                <Card
                  key={event.id}
                  className="p-4 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => onDateClick(selectedDate, [event])}
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h3 className="mb-1">{event.title}</h3>
                      <p className="text-gray-600 text-sm">
                        {event.start_time && event.end_time
                          ? `${event.start_time} - ${event.end_time}`
                          : event.start_time || event.end_time || '시간 미정'}
                      </p>
                    </div>
                    <Badge variant="secondary">일정</Badge>
                  </div>
                </Card>
              ))
            ) : (
              <p className="text-gray-500 text-center py-8">
                일정이 없습니다
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
