import { useScheduleStore } from "../stores/scheduleStore";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "./ui/button";
import type { Event } from "./CalendarView";

interface MonthCalendarProps {
  currentDate: Date;
  selectedDate: Date;
  onDateSelect: (date: Date) => void;
  onDateClick: (date: Date) => void;
  onEventClick: (event: Event) => void;
  onPrevMonth: () => void;
  onNextMonth: () => void;
  onToday: () => void;
}

export function MonthCalendar({
  currentDate,
  selectedDate, 
  onDateSelect,
  onDateClick,
  onEventClick,
  onPrevMonth,
  onNextMonth,
  onToday,
}: MonthCalendarProps) {
  const { schedules } = useScheduleStore(); // isLoading, error

  const year = currentDate.getFullYear();
  const month = currentDate.getMonth();

  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);
  const startDate = new Date(firstDayOfMonth);
  startDate.setDate(
    startDate.getDate() - firstDayOfMonth.getDay(),
  );

  const endDate = new Date(lastDayOfMonth);
  const daysFromStart =
    Math.ceil(
      (endDate.getTime() - startDate.getTime()) /
        (1000 * 60 * 60 * 24),
    ) + 1;
  const weeksNeeded = Math.ceil(daysFromStart / 7);
  const totalDays = weeksNeeded * 7;

  const days = [];
  const currentDay = new Date(startDate);

  for (let i = 0; i < totalDays; i++) {
    days.push(new Date(currentDay));
    currentDay.setDate(currentDay.getDate() + 1);
  }

  const getEventsForDate = (date: Date) => {
    return schedules
      .map(schedule => ({
        id: schedule.id,
        title: schedule.title,
        date: new Date(schedule.date),
        content: schedule.content,
        start_time: schedule.start_time,
        end_time: schedule.end_time,
      }))
      .filter(
        (event) => 
          event.date.getDate() === date.getDate() &&
          event.date.getMonth() === date.getMonth() &&
          event.date.getFullYear() === date.getFullYear(),
      )
  };

  const isToday = (date: Date) => {
    const today = new Date();
    return (
      date.getDate() === today.getDate() &&
      date.getMonth() === today.getMonth() &&
      date.getFullYear() === today.getFullYear()
    );
  };

  const isSelected = (date: Date) => {
    return (
      date.getDate() === selectedDate.getDate() &&
      date.getMonth() === selectedDate.getMonth() &&
      date.getFullYear() === selectedDate.getFullYear()
    );
  };

  // Adjust cell height based on number of weeks
  const cellHeight =
    weeksNeeded === 5 ? "min-h-[140px]" : "min-h-[115px]";

  return (
    <div className="flex-1 p-8">
      {/* TODO. 추후 UI 적용 */}
      {/* {isLoading && <div className="text-center py-4">일정을 불러오는 중...</div>} */}{/* 로딩 중 메세지 표시 */}
      {/* {isError && <div className="text-center py-4 text-red-500">{error}</div>} */}{/* 에러 발생 시 메세지 표시 */}

      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" onClick={onToday}>
            Today
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onPrevMonth}
          >
            <ChevronLeft className="w-4 h-4" />
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={onNextMonth}
          >
            <ChevronRight className="w-4 h-4" />
          </Button>
        </div>

        <div className="flex justify-center">
          <span className="font-bold">
            {year} {month + 1}월
          </span>
        </div>
      </div>

      <div className="border rounded-lg overflow-hidden bg-white">
        <div className="grid grid-cols-7 border-b">
          {[
            "Sun",
            "Mon",
            "Tue",
            "Wed",
            "Thu",
            "Fri",
            "Sat",
          ].map((day) => (
            <div
              key={day}
              className="p-3 text-center text-sm text-gray-600 border-r last:border-r-0"
            >
              {day}
            </div>
          ))}
        </div>

        <div className="grid grid-cols-7">
          {days.map((date, index) => {
            const dayEvents = getEventsForDate(date);
            const isCurrentMonth = date.getMonth() === month;
            const isTodayDate = isToday(date);
            const isSelectedDate = isSelected(date);

            return (
              <button
                key={index}
                onClick={() => {
                  onDateSelect(date);
                  onDateClick(date);
                }}
                className={`${cellHeight} p-2 border-r border-b last:border-r-0 text-left hover:bg-gray-50 transition-colors ${
                  !isCurrentMonth ? "bg-gray-50" : ""
                } ${isSelectedDate ? "bg-blue-50" : ""}`}
              >
                <div
                  className={`flex items-center justify-center w-7 h-7 rounded-full ${
                    isTodayDate ? "bg-blue-600 text-white" : ""
                  } ${!isCurrentMonth ? "text-gray-400" : ""}`}
                >
                  <span className="text-sm">
                    {date.getDate()}
                  </span>
                </div>

                <div className="space-y-1">
                  {dayEvents.slice(0, 3).map((event) => (
                    <div
                      key={event.id}
                      onClick={(e) => {
                        e.stopPropagation(); // 이벤트 버블링 방지
                        onEventClick(event);
                      }}
                      className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded truncate cursor-pointer hover:bg-blue-200"
                    >
                      {event.title}
                    </div>
                  ))}
                  {dayEvents.length > 3 && (
                    <div className="text-xs text-gray-500 px-2">
                      +{dayEvents.length - 3} more
                    </div>
                  )}
                </div>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}