import React from 'react';
import { formatDate, formatDateTime } from '../../utils/dateUtils';

/**
 * 일정 목록 컴포넌트
 * 선택된 날짜의 일정들을 표시
 * 순수 프레젠테이션 컴포넌트 (상태 없음)
 *
 * @param {Date} selectedDate - 선택된 날짜
 * @param {Array} schedules - 선택된 날짜의 일정 배열
 * @param {Function} onToggleComplete - 완료 상태 토글 핸들러
 * @param {Function} onDelete - 삭제 핸들러
 */
export const ScheduleList = ({
  selectedDate,
  schedules,
  onToggleComplete,
  onDelete
}) => {
  return (
    <div className="date-details">
      <h3>{formatDate(selectedDate)} 일정</h3>
      <div className="schedule-list">
        {schedules.length === 0 ? (
          <div className="empty-message">이 날짜에 등록된 일정이 없습니다.</div>
        ) : (
          schedules.map((schedule) => (
            <div
              key={schedule.id}
              className={`schedule-card ${schedule.is_completed ? 'completed' : ''}`}
            >
              <div className="schedule-card-header">
                <input
                  type="checkbox"
                  className="schedule-checkbox"
                  checked={schedule.is_completed}
                  onChange={() => onToggleComplete(schedule.id, schedule.is_completed)}
                />
                <h4 className="schedule-title">{schedule.title}</h4>
                <div className="schedule-actions">
                  <button
                    className={`complete-button ${schedule.is_completed ? 'completed' : ''}`}
                    onClick={() => onToggleComplete(schedule.id, schedule.is_completed)}
                  >
                    {schedule.is_completed ? '완료' : '미완료'}
                  </button>
                  <button
                    className="delete-button"
                    onClick={() => onDelete(schedule.id)}
                  >
                    삭제
                  </button>
                </div>
              </div>

              <div className="schedule-info-list">
                <div className="schedule-info-item">
                  <span className="schedule-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"/>
                      <polyline points="12 6 12 12 16 14"/>
                    </svg>
                  </span>
                  <span className="schedule-time">
                    {formatDateTime(schedule.scheduled_at)}
                  </span>
                </div>

                {schedule.description && (
                  <div className="schedule-info-item">
                    <span className="schedule-icon">
                      <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                        <polyline points="14 2 14 8 20 8"/>
                        <line x1="16" y1="13" x2="8" y2="13"/>
                        <line x1="16" y1="17" x2="8" y2="17"/>
                      </svg>
                    </span>
                    <span className="schedule-description">{schedule.description}</span>
                  </div>
                )}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
