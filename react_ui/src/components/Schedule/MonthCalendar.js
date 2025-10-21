import React from 'react';
import {
  getDaysInMonth,
  isSameDay,
  getSchedulesForDate,
  hasSchedulesOnDate
} from '../../utils/dateUtils';

/**
 * 월간 달력 컴포넌트
 * 순수 프레젠테이션 컴포넌트 (상태 없음)
 *
 * @param {Date} currentMonth - 현재 표시 중인 월
 * @param {Date} selectedDate - 선택된 날짜
 * @param {Array} schedules - 전체 일정 배열
 * @param {Function} onDateSelect - 날짜 선택 핸들러
 * @param {Function} onPrevMonth - 이전 달 핸들러
 * @param {Function} onNextMonth - 다음 달 핸들러
 */
export const MonthCalendar = ({
  currentMonth,
  selectedDate,
  schedules,
  onDateSelect,
  onPrevMonth,
  onNextMonth
}) => {
  const calendarDays = getDaysInMonth(currentMonth);

  return (
    <div className="calendar-section">
      <div className="calendar-header">
        <button onClick={onPrevMonth} className="month-nav-btn">&lt;</button>
        <h2>{currentMonth.getFullYear()}년 {currentMonth.getMonth() + 1}월</h2>
        <button onClick={onNextMonth} className="month-nav-btn">&gt;</button>
      </div>

      <div className="calendar-grid">
        <div className="calendar-weekdays">
          {['일', '월', '화', '수', '목', '금', '토'].map(day => (
            <div key={day} className="calendar-weekday">{day}</div>
          ))}
        </div>
        <div className="calendar-days">
          {calendarDays.map((day, index) => {
            const daySchedules = day ? getSchedulesForDate(schedules, day) : [];
            const displayLimit = 2;
            const remainingCount = daySchedules.length - displayLimit;

            return (
              <div
                key={index}
                className={`calendar-day ${day ? '' : 'empty'} ${
                  day && isSameDay(day, selectedDate) ? 'selected' : ''
                } ${day && isSameDay(day, new Date()) ? 'today' : ''} ${
                  day && hasSchedulesOnDate(schedules, day) ? 'has-schedule' : ''
                }`}
                onClick={() => day && onDateSelect(day)}
              >
                <span className="calendar-day-number">{day ? day.getDate() : ''}</span>
                {day && daySchedules.length > 0 && (
                  <div className="calendar-day-schedules">
                    {daySchedules.slice(0, displayLimit).map((schedule, idx) => (
                      <div
                        key={idx}
                        className={`calendar-schedule-item ${schedule.is_completed ? 'completed' : ''}`}
                        title={schedule.title}
                      >
                        {schedule.title}
                      </div>
                    ))}
                    {remainingCount > 0 && (
                      <div className="calendar-schedule-more">
                        외 {remainingCount}개
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
