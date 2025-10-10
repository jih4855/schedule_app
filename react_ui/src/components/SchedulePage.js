import React, { useState, useEffect } from 'react';
import './SchedulePage.css';

const SchedulePage = ({ onLogout }) => {
  const API_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

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

      const response = await fetch(`${API_URL}/api/schedules`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 401) {
        setError('인증이 만료되었습니다. 다시 로그인해주세요.');
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_expiration');
        setTimeout(() => onLogout(), 2000);
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

      const response = await fetch(`${API_URL}/api/schedules/parse-and-create`, {
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
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_expiration');
        setTimeout(() => onLogout(), 2000);
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

      const response = await fetch(`${API_URL}/api/schedules/${scheduleId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          is_completed: !currentStatus
        }),
      });

      if (response.status === 401) {
        setError('인증이 만료되었습니다. 다시 로그인해주세요.');
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_expiration');
        setTimeout(() => onLogout(), 2000);
        return;
      }

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

      const response = await fetch(`${API_URL}/api/schedules/${scheduleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 401) {
        setError('인증이 만료되었습니다. 다시 로그인해주세요.');
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_expiration');
        setTimeout(() => onLogout(), 2000);
        return;
      }

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
                      <input
                        type="checkbox"
                        className="schedule-checkbox"
                        checked={schedule.is_completed}
                        onChange={() => handleToggleComplete(schedule.id, schedule.is_completed)}
                      />
                      <h4 className="schedule-title">{schedule.title}</h4>
                      <div className="schedule-actions">
                        <button
                          className={`complete-button ${schedule.is_completed ? 'completed' : ''}`}
                          onClick={() => handleToggleComplete(schedule.id, schedule.is_completed)}
                        >
                          {schedule.is_completed ? '완료' : '미완료'}
                        </button>
                        <button
                          className="delete-button"
                          onClick={() => handleDelete(schedule.id)}
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
        </div>
      </div>

      {/* 하단: 자연어 입력창 */}
      <form className="schedule-input-form" onSubmit={handleSendMessage}>
        <div className="input-with-tooltip">
          <input
            type="text"
            className="schedule-input"
            placeholder="예: 10월 15일 오후 1시 회의, 내일 13시 치과"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            disabled={isSending}
          />
          <div className="input-tooltip">
            <div className="tooltip-header">
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{display: 'inline-block', verticalAlign: 'middle', marginRight: '4px'}}>
                <path d="M9 18h6"/>
                <path d="M10 22h4"/>
                <path d="M15.09 14c.18-.98.65-1.74 1.41-2.5A4.65 4.65 0 0 0 18 8 6 6 0 0 0 6 8c0 1 .23 2.23 1.5 3.5A4.61 4.61 0 0 1 8.91 14"/>
              </svg>
              정확한 입력 팁 (베타)
            </div>
            <div className="tooltip-content">
              <strong>
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{display: 'inline-block', verticalAlign: 'middle', marginRight: '4px'}}>
                  <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
                  <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
                  <line x1="9" y1="12" x2="9" y2="12.01"/>
                  <line x1="13" y1="12" x2="15" y2="12"/>
                  <line x1="9" y1="16" x2="9" y2="16.01"/>
                  <line x1="13" y1="16" x2="15" y2="16"/>
                </svg>
                주요 기능:
              </strong>
              <ul>
                <li>자연어로 단일 또는 다중 일정 등록</li>
                <li>날짜, 시간, 상대 표현 인식</li>
                <li>설명 추가 가능</li>
              </ul>
              <strong>📝 입력 예시:</strong>
              <ul>
                <li>단일등록 : 10월 15일 오후 1시 회의</li>
                <li>다중등록  : 오늘 오후 3시 디자인 회의, 내일 오전 10시 클라이언트 미팅, 금요일 저녁 7시 저녁약속</li>
                <li>설명추가 : 내일 13시 치과 예약, 16일 14시 팀 미팅 프로젝트 관련</li>
              </ul>
              <strong>✅ 잘 인식되는 표현:</strong>
              <ul>
                <li>시간: "오후 1시", "13시", "16시"</li>
                <li>날짜: "10일", "15일", "10월 20일"</li>
                <li>상대: "내일", "모레", "이번주 일요일"</li>
              </ul>
              <strong>⚠️ 인식 어려운 표현(추후 개선 예정):</strong>
              <ul>
                <li>1주일 이후 날짜 등록(예: 2주후 수요일 회의 등록)</li>
                </ul>
                <strong>주의사항:</strong>
                <p>현재는 테스트 기간이므로, 개인정보 및 기밀 정보 입력은 권장하지 않습니다.</p>
            </div>
          </div>
        </div>
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
