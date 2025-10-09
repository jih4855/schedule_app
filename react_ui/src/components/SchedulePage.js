import React, { useState, useEffect } from 'react';
import './SchedulePage.css';

const SchedulePage = ({ onLogout }) => {
  const [schedules, setSchedules] = useState([]);
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [currentMonth, setCurrentMonth] = useState(new Date());
  const [inputText, setInputText] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchSchedules();
  }, []);

  const fetchSchedules = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setError('인증 토큰이 없습니다. 다시 로그인해주세요.');
        return;
      }

      const response = await fetch('http://localhost:8000/api/schedules', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 401) {
        setError('인증이 만료되었습니다. 다시 로그인해주세요.');
        return;
      }

      if (response.ok) {
        const data = await response.json();
        setSchedules(data);
        setError('');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || '일정을 불러올 수 없습니다.');
      }
    } catch (error) {
      setError('서버 연결에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();

    if (!inputText.trim()) {
      return;
    }

    setIsSending(true);
    setError('');

    try {
      const token = localStorage.getItem('access_token');

      const response = await fetch('http://localhost:8000/api/schedules/parse-and-create', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: inputText
        }),
      });

      if (response.status === 401) {
        setError('인증이 만료되었습니다. 다시 로그인해주세요.');
        return;
      }

      if (response.ok) {
        setInputText('');
        await fetchSchedules();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || '일정 생성에 실패했습니다.');
      }
    } catch (error) {
      setError('서버 연결에 실패했습니다.');
    } finally {
      setIsSending(false);
    }
  };

  const handleToggleComplete = async (scheduleId, currentStatus) => {
    try {
      const token = localStorage.getItem('access_token');

      const response = await fetch(`http://localhost:8000/api/schedules/${scheduleId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          is_completed: !currentStatus
        }),
      });

      if (response.ok) {
        await fetchSchedules();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || '일정 상태 변경에 실패했습니다.');
      }
    } catch (error) {
      setError('서버 연결에 실패했습니다.');
    }
  };

  const handleDelete = async (scheduleId) => {
    if (!window.confirm('정말로 이 일정을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const token = localStorage.getItem('access_token');

      const response = await fetch(`http://localhost:8000/api/schedules/${scheduleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        await fetchSchedules();
      } else {
        const errorData = await response.json();
        setError(errorData.detail || '일정 삭제에 실패했습니다.');
      }
    } catch (error) {
      setError('서버 연결에 실패했습니다.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_expiration');
    onLogout();
  };

  // 달력 관련 유틸리티 함수들
  const getDaysInMonth = (date) => {
    const year = date.getFullYear();
    const month = date.getMonth();
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    const startingDayOfWeek = firstDay.getDay();

    const days = [];
    // 이전 달의 날짜들로 빈 칸 채우기
    for (let i = 0; i < startingDayOfWeek; i++) {
      days.push(null);
    }
    // 현재 달의 날짜들
    for (let i = 1; i <= daysInMonth; i++) {
      days.push(new Date(year, month, i));
    }

    return days;
  };

  const isSameDay = (date1, date2) => {
    return date1.getFullYear() === date2.getFullYear() &&
           date1.getMonth() === date2.getMonth() &&
           date1.getDate() === date2.getDate();
  };

  const formatDate = (date) => {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  };

  const formatDateTime = (dateString) => {
    const date = new Date(dateString);
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');
    return `${hours}:${minutes}`;
  };

  const getSchedulesForDate = (date) => {
    if (!date) return [];
    return schedules.filter(schedule => {
      const scheduleDate = new Date(schedule.scheduled_at);
      return isSameDay(scheduleDate, date);
    });
  };

  const hasSchedulesOnDate = (date) => {
    if (!date) return false;
    return schedules.some(schedule => {
      const scheduleDate = new Date(schedule.scheduled_at);
      return isSameDay(scheduleDate, date);
    });
  };

  const getWeekSchedules = () => {
    const today = new Date();
    const weekStart = new Date(today);
    weekStart.setDate(today.getDate() - today.getDay()); // 이번 주 일요일

    const weekSchedules = [];
    for (let i = 0; i < 7; i++) {
      const date = new Date(weekStart);
      date.setDate(weekStart.getDate() + i);

      const daySchedules = getSchedulesForDate(date);
      weekSchedules.push({
        date: date,
        dayName: ['일', '월', '화', '수', '목', '금', '토'][i],
        schedules: daySchedules
      });
    }

    return weekSchedules;
  };

  const getWeekStatistics = () => {
    const weekSchedules = getWeekSchedules();
    const allSchedules = weekSchedules.flatMap(day => day.schedules);

    const totalCount = allSchedules.length;
    const completedCount = allSchedules.filter(s => s.is_completed).length;
    const pendingCount = totalCount - completedCount;
    const completionRate = totalCount > 0 ? ((completedCount / totalCount) * 100).toFixed(1) : 0;

    // 가장 바쁜 날 찾기
    let busiestDay = { dayName: '-', count: 0 };
    weekSchedules.forEach(day => {
      if (day.schedules.length > busiestDay.count) {
        busiestDay = { dayName: day.dayName, count: day.schedules.length };
      }
    });

    const weekStart = weekSchedules[0].date;
    const weekEnd = weekSchedules[6].date;
    const dateRange = `${weekStart.getMonth() + 1}/${weekStart.getDate()} ~ ${weekEnd.getMonth() + 1}/${weekEnd.getDate()}`;

    return {
      dateRange,
      totalCount,
      completedCount,
      pendingCount,
      completionRate,
      busiestDay: busiestDay.count > 0 ? `${busiestDay.dayName}요일 (${busiestDay.count}개)` : '없음'
    };
  };

  const prevMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() - 1));
  };

  const nextMonth = () => {
    setCurrentMonth(new Date(currentMonth.getFullYear(), currentMonth.getMonth() + 1));
  };

  const calendarDays = getDaysInMonth(currentMonth);
  const selectedDateSchedules = getSchedulesForDate(selectedDate);
  const weekSchedules = getWeekSchedules();
  const weekStats = getWeekStatistics();

  if (isLoading) {
    return (
      <div className="schedule-container">
        <div className="loading">일정을 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="schedule-container">
      <header className="schedule-header">
        <h1>스케줄 관리</h1>
        <button className="logout-button" onClick={handleLogout}>
          로그아웃
        </button>
      </header>

      {error && (
        <div className="error-message">
          {error}
        </div>
      )}

      <div className="schedule-main">
        {/* 좌측: 월간 달력 (40%) */}
        <div className="calendar-section">
          <div className="calendar-header">
            <button onClick={prevMonth} className="month-nav-btn">&lt;</button>
            <h2>{currentMonth.getFullYear()}년 {currentMonth.getMonth() + 1}월</h2>
            <button onClick={nextMonth} className="month-nav-btn">&gt;</button>
          </div>

          <div className="calendar-grid">
            <div className="calendar-weekdays">
              {['일', '월', '화', '수', '목', '금', '토'].map(day => (
                <div key={day} className="calendar-weekday">{day}</div>
              ))}
            </div>
            <div className="calendar-days">
              {calendarDays.map((day, index) => (
                <div
                  key={index}
                  className={`calendar-day ${day ? '' : 'empty'} ${
                    day && isSameDay(day, selectedDate) ? 'selected' : ''
                  } ${day && isSameDay(day, new Date()) ? 'today' : ''} ${
                    day && hasSchedulesOnDate(day) ? 'has-schedule' : ''
                  }`}
                  onClick={() => day && setSelectedDate(day)}
                >
                  {day ? day.getDate() : ''}
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* 우측: 상세 및 요약 */}
        <div className="details-section">
          {/* 우측 상단: 선택된 날짜 상세 (50%) */}
          <div className="date-details">
            <h3>{formatDate(selectedDate)} 일정</h3>
            <div className="schedule-list">
              {selectedDateSchedules.length === 0 ? (
                <div className="empty-message">이 날짜에 등록된 일정이 없습니다.</div>
              ) : (
                selectedDateSchedules.map((schedule) => (
                  <div
                    key={schedule.id}
                    className={`schedule-card ${schedule.is_completed ? 'completed' : ''}`}
                  >
                    <div className="schedule-card-header">
                      <h4 className="schedule-title">{schedule.title}</h4>
                      <button
                        className="delete-button"
                        onClick={() => handleDelete(schedule.id)}
                      >
                        삭제
                      </button>
                    </div>

                    {schedule.description && (
                      <p className="schedule-description">{schedule.description}</p>
                    )}

                    <div className="schedule-footer">
                      <span className="schedule-time">
                        {formatDateTime(schedule.scheduled_at)}
                      </span>
                      <button
                        className={`complete-button ${schedule.is_completed ? 'completed' : ''}`}
                        onClick={() => handleToggleComplete(schedule.id, schedule.is_completed)}
                      >
                        {schedule.is_completed ? '완료됨' : '미완료'}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          {/* 우측 하단: 이번 주 요약 (50%) */}
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
                          {isBusiest ? ' ⭐' : ''}
                        </div>
                        <div className="daily-schedule-brief">
                          {day.schedules.map((schedule, idx) => (
                            <span key={idx} className="schedule-brief-item">
                              {schedule.is_completed ? '✓' : '○'} {schedule.title}
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
        </div>
      </div>

      {/* 하단: 자연어 입력창 */}
      <form className="schedule-input-form" onSubmit={handleSendMessage}>
        <input
          type="text"
          className="schedule-input"
          placeholder="예: 내일 오후 3시에 회의, 다음주 월요일 오전 9시 프로젝트 발표"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          disabled={isSending}
        />
        <button
          type="submit"
          className="send-button"
          disabled={isSending || !inputText.trim()}
        >
          {isSending ? '전송 중...' : '전송'}
        </button>
      </form>
    </div>
  );
};

export default SchedulePage;
