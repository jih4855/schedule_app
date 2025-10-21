import { useState, useEffect } from 'react';

/**
 * 일정 관리 커스텀 훅
 * API 호출 및 상태 관리를 담당
 *
 * @param {string} accessToken - 사용자 인증 토큰
 * @param {Function} onLogout - 로그아웃 콜백 함수
 * @returns {Object} schedules, isLoading, error, API 함수들
 */
export const useSchedules = (accessToken, onLogout) => {
  const API_URL = process.env.REACT_APP_API_BASE_URL || '';

  const [schedules, setSchedules] = useState([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSending, setIsSending] = useState(false);
  const [error, setError] = useState('');

  /**
   * 모든 일정 조회
   */
  const fetchSchedules = async () => {
    try {
      const response = await fetch(`${API_URL}/api/schedules`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 401) {
        setError('인증이 만료되었습니다. 다시 로그인해주세요.');
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

  /**
   * 자연어로 일정 생성
   * @param {string} text - 자연어 입력 텍스트
   * @returns {Promise<boolean>} 성공 여부
   */
  const createSchedule = async (text) => {
    if (!text.trim()) {
      return false;
    }

    setIsSending(true);
    setError('');

    try {
      const response = await fetch(`${API_URL}/api/schedules/parse-and-create`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: text
        }),
      });

      if (response.status === 401) {
        setError('인증이 만료되었습니다. 다시 로그인해주세요.');
        setTimeout(() => onLogout(), 2000);
        return false;
      }

      if (response.ok) {
        await fetchSchedules();
        return true;
      } else if (response.status === 429) {
        const errorData = await response.json();
        const retryAfter = errorData.retry_after_seconds || 60;
        setError(`${errorData.message || '요청 제한 초과'} (${retryAfter}초 후 재시도)`);
        return false;
      } else {
        const errorData = await response.json();
        setError(errorData.detail || '일정 생성에 실패했습니다.');
        return false;
      }
    } catch (error) {
      setError('서버 연결에 실패했습니다.');
      return false;
    } finally {
      setIsSending(false);
    }
  };

  /**
   * 일정 상태 업데이트 (완료/미완료 토글)
   * @param {number} scheduleId - 일정 ID
   * @param {boolean} currentStatus - 현재 완료 상태
   */
  const updateSchedule = async (scheduleId, currentStatus) => {
    try {
      const response = await fetch(`${API_URL}/api/schedules/${scheduleId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          is_completed: !currentStatus
        }),
      });

      if (response.status === 401) {
        setError('인증이 만료되었습니다. 다시 로그인해주세요.');
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

  /**
   * 일정 삭제
   * @param {number} scheduleId - 일정 ID
   */
  const deleteSchedule = async (scheduleId) => {
    if (!window.confirm('정말로 이 일정을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/schedules/${scheduleId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.status === 401) {
        setError('인증이 만료되었습니다. 다시 로그인해주세요.');
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

  // 초기 데이터 로딩
  useEffect(() => {
    fetchSchedules();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return {
    schedules,
    isLoading,
    isSending,
    error,
    fetchSchedules,
    createSchedule,
    updateSchedule,
    deleteSchedule
  };
};
