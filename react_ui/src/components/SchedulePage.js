import React, { useState } from 'react';
import { useSchedules } from '../hooks/useSchedules';
import { MonthCalendar } from './Schedule/MonthCalendar';
import { ScheduleList } from './Schedule/ScheduleList';
import { WeeklySummary } from './Schedule/WeeklySummary';
import { ScheduleInput } from './Schedule/ScheduleInput';
import { getSchedulesForDate } from '../utils/dateUtils';
import './SchedulePage.css';

/**
 * 스케줄 페이지 메인 컴포넌트
 * 모든 자식 컴포넌트들을 조합하고 상태를 관리
 *
 * @param {Function} onLogout - 로그아웃 핸들러
 * @param {string} accessToken - 사용자 인증 토큰
 */
const SchedulePage = ({ onLogout, accessToken }) => {
  // 날짜 관련 상태만 관리
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [currentMonth, setCurrentMonth] = useState(new Date());

  // 일정 관련 상태 및 API 함수는 커스텀 훅에서 가져옴
  const {
    schedules,
    isLoading,
    isSending,
    error,
    createSchedule,
    updateSchedule,
    deleteSchedule
  } = useSchedules(accessToken, onLogout);

  // 월 이동 핸들러
  const handlePrevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const handleNextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  // 로딩 상태 처리
  if (isLoading) {
    return (
      <div className="schedule-container">
        <div className="loading">일정을 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="schedule-container">
      {/* 헤더 */}
      <header className="schedule-header">
        <h1>스케줄 관리</h1>
        <button className="logout-button" onClick={onLogout}>
          로그아웃
        </button>
      </header>

      {/* 에러 메시지 */}
      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      {/* 메인 콘텐츠 */}
      <div className="schedule-main">
        {/* 좌측: 월간 달력 */}
        <MonthCalendar
          currentMonth={currentMonth}
          selectedDate={selectedDate}
          schedules={schedules}
          onDateSelect={setSelectedDate}
          onPrevMonth={handlePrevMonth}
          onNextMonth={handleNextMonth}
        />

        {/* 우측: 상세 및 요약 */}
        <div className="details-section">
          {/* 선택된 날짜의 일정 목록 */}
          <ScheduleList
            selectedDate={selectedDate}
            schedules={getSchedulesForDate(schedules, selectedDate)}
            onToggleComplete={updateSchedule}
            onDelete={deleteSchedule}
          />

          {/* 이번 주 요약 */}
          <WeeklySummary schedules={schedules} />
        </div>
      </div>

      {/* 하단: 자연어 입력 폼 */}
      <ScheduleInput
        onSubmit={createSchedule}
        isSending={isSending}
      />
    </div>
  );
};

export default SchedulePage;
