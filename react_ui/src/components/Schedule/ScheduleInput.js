import React, { useState } from 'react';

/**
 * 일정 입력 폼 컴포넌트
 * 자연어 입력을 통한 일정 생성
 *
 * @param {Function} onSubmit - 일정 생성 핸들러
 * @param {boolean} isSending - 전송 중 상태
 */
export const ScheduleInput = ({ onSubmit, isSending }) => {
  const [inputText, setInputText] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!inputText.trim()) {
      return;
    }

    const success = await onSubmit(inputText);
    if (success) {
      setInputText('');
    }
  };

  return (
    <form className="schedule-input-form" onSubmit={handleSubmit}>
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
  );
};
