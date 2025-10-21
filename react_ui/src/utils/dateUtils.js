/**
 * 날짜 유틸리티 함수 모음
 * SchedulePage.js에서 분리된 순수 함수들
 */

/**
 * 특정 월의 모든 날짜를 배열로 반환
 * @param {Date} date - 기준 날짜
 * @returns {Array<Date|null>} 날짜 배열 (빈 칸은 null)
 */
export const getDaysInMonth = (date) => {
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

/**
 * 두 날짜가 같은 날인지 확인
 * @param {Date} date1 - 첫 번째 날짜
 * @param {Date} date2 - 두 번째 날짜
 * @returns {boolean} 같은 날이면 true
 */
export const isSameDay = (date1, date2) => {
  return date1.getFullYear() === date2.getFullYear() &&
         date1.getMonth() === date2.getMonth() &&
         date1.getDate() === date2.getDate();
};

/**
 * 날짜를 YYYY-MM-DD 형식으로 포맷
 * @param {Date} date - 포맷할 날짜
 * @returns {string} YYYY-MM-DD 형식 문자열
 */
export const formatDate = (date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  return `${year}-${month}-${day}`;
};

/**
 * ISO 날짜 문자열을 HH:MM 형식으로 포맷
 * @param {string} dateString - ISO 형식 날짜 문자열
 * @returns {string} HH:MM 형식 시간 문자열
 */
export const formatDateTime = (dateString) => {
  const date = new Date(dateString);
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  return `${hours}:${minutes}`;
};

/**
 * 특정 날짜의 일정들을 필터링
 * @param {Array} schedules - 전체 일정 배열
 * @param {Date} date - 필터링할 날짜
 * @returns {Array} 해당 날짜의 일정 배열
 */
export const getSchedulesForDate = (schedules, date) => {
  if (!date) return [];
  return schedules.filter(schedule => {
    const scheduleDate = new Date(schedule.scheduled_at);
    return isSameDay(scheduleDate, date);
  });
};

/**
 * 특정 날짜에 일정이 있는지 확인
 * @param {Array} schedules - 전체 일정 배열
 * @param {Date} date - 확인할 날짜
 * @returns {boolean} 일정이 있으면 true
 */
export const hasSchedulesOnDate = (schedules, date) => {
  if (!date) return false;
  return schedules.some(schedule => {
    const scheduleDate = new Date(schedule.scheduled_at);
    return isSameDay(scheduleDate, date);
  });
};

/**
 * 이번 주의 일정을 요일별로 정리
 * @param {Array} schedules - 전체 일정 배열
 * @returns {Array} 요일별 일정 배열
 */
export const getWeekSchedules = (schedules) => {
  const today = new Date();
  const weekStart = new Date(today);
  weekStart.setDate(today.getDate() - today.getDay()); // 이번 주 일요일

  const weekSchedules = [];
  for (let i = 0; i < 7; i++) {
    const date = new Date(weekStart);
    date.setDate(weekStart.getDate() + i);

    const daySchedules = getSchedulesForDate(schedules, date);
    weekSchedules.push({
      date: date,
      dayName: ['일', '월', '화', '수', '목', '금', '토'][i],
      schedules: daySchedules
    });
  }

  return weekSchedules;
};

/**
 * 이번 주 일정 통계 계산
 * @param {Array} schedules - 전체 일정 배열
 * @returns {Object} 주간 통계 객체
 */
export const getWeekStatistics = (schedules) => {
  const weekSchedules = getWeekSchedules(schedules);
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
