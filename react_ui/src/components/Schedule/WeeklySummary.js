import React from 'react';
import { getWeekSchedules, getWeekStatistics, isSameDay } from '../../utils/dateUtils';

/**
 * 주간 요약 컴포넌트
 * 이번 주의 일정 통계 및 요약 정보를 표시
 * 순수 프레젠테이션 컴포넌트 (상태 없음)
 *
 * @param {Array} schedules - 전체 일정 배열
 */
export const WeeklySummary = ({ schedules }) => {
  const weekSchedules = getWeekSchedules(schedules);
  const weekStats = getWeekStatistics(schedules);

  return (
    <div className="week-summary">
      <h3>이번 주 일정 요약 ({weekStats.dateRange})</h3>

      <div className="week-summary-simple">
        <p>총 {weekStats.totalCount}개 | 완료 {weekStats.completedCount}개 ({weekStats.completionRate}%) | 미완료 {weekStats.pendingCount}개</p>
        <p>가장 바쁜 날: {weekStats.busiestDay}</p>

        <div className="week-daily-simple">
          {weekSchedules
            .filter(day => day.schedules.length > 0)
            .map((day, index) => {
              const isToday = isSameDay(day.date, new Date());
              const isBusiest = day.schedules.length === Math.max(...weekSchedules.map(d => d.schedules.length));

              return (
                <div key={index} className={`daily-simple-item ${isToday ? 'today-highlight' : ''}`}>
                  <div className="daily-header-text">
                    {day.dayName}요일 ({day.date.getMonth() + 1}/{day.date.getDate()}): {day.schedules.length}개
                    {isBusiest ? <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="#fbbf24" stroke="#fbbf24" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{display: 'inline-block', verticalAlign: 'middle', marginLeft: '4px'}}><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg> : ''}
                  </div>
                  <div className="daily-schedule-brief">
                    {day.schedules.map((schedule, idx) => (
                      <span key={idx} className="schedule-brief-item">
                        {schedule.is_completed ? <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{display: 'inline-block', verticalAlign: 'middle', marginRight: '2px'}}><polyline points="20 6 9 17 4 12"/></svg> : <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{display: 'inline-block', verticalAlign: 'middle', marginRight: '2px'}}><circle cx="12" cy="12" r="10"/></svg>} {schedule.title}
                        {idx < day.schedules.length - 1 ? ', ' : ''}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
        </div>
      </div>
    </div>
  );
};
