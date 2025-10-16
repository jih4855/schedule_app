import React, { useState } from 'react';
import './LoginForm.css';

const LoginForm = ({ onLoginSuccess, onSwitchToSignup }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const [message, setMessage] = useState({ text: '', type: '' });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: '', type: '' });

    const API_URL = process.env.REACT_APP_API_BASE_URL || '';

    try {
      const response = await fetch(`${API_URL}/api/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',  // 추가: 쿠키 전송/수신 활성화
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({
          text: `로그인 성공! ${formData.username}님 환영합니다!`,
          type: 'success'
        });
        setFormData({ username: '', password: '' });

        setTimeout(() => {
          onLoginSuccess(data.access_token);  // Access Token 전달
        }, 1000);
      } else if (response.status === 429) {
        const retryAfter = data.retry_after_seconds || 60;
        setMessage({
          text: `${data.message || '요청 제한 초과'} (${retryAfter}초 후 재시도)`,
          type: 'error'
        });
      } else {
        setMessage({
          text: data.detail || '로그인 중 오류가 발생했습니다.',
          type: 'error'
        });
      }
    } catch (error) {
      setMessage({
        text: '서버 연결에 실패했습니다. 잠시 후 다시 시도해주세요.',
        type: 'error'
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        <div className="login-form">
          <h2>로그인</h2>
          <p className="login-description">
            계정에 로그인하여 서비스를 이용해보세요
          </p>

        {message.text && (
          <div className={`message ${message.type}`}>
            {message.text}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label htmlFor="username">사용자명</label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              required
              placeholder="사용자명을 입력하세요"
              disabled={isLoading}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">비밀번호</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              placeholder="비밀번호를 입력하세요"
              disabled={isLoading}
            />
          </div>

          <button
            type="submit"
            className="submit-button"
            disabled={isLoading}
          >
            {isLoading ? '처리 중...' : '로그인'}
          </button>
        </form>

        <div className="service-intro">
          <h3 className="intro-title">자연어로 쉽게 관리하는 스마트 일정</h3>
          <div className="features-grid">
            <div className="feature-item">
              <div className="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <polyline points="12 6 12 12 16 14"/>
                </svg>
              </div>
              <h4>자연어 입력</h4>
              <p>내일 오후 2시 회의</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                  <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                  <line x1="12" y1="22.08" x2="12" y2="12"/>
                </svg>
              </div>
              <h4>AI 자동 파싱</h4>
              <p>스마트한 일정 분석</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/>
                  <line x1="16" y1="2" x2="16" y2="6"/>
                  <line x1="8" y1="2" x2="8" y2="6"/>
                  <line x1="3" y1="10" x2="21" y2="10"/>
                </svg>
              </div>
              <h4>직관적 캘린더</h4>
              <p>한눈에 보는 일정</p>
            </div>
            <div className="feature-item">
              <div className="feature-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="18" y1="20" x2="18" y2="10"/>
                  <line x1="12" y1="20" x2="12" y2="4"/>
                  <line x1="6" y1="20" x2="6" y2="14"/>
                </svg>
              </div>
              <h4>일정 통계</h4>
              <p>데이터 기반 분석</p>
            </div>
          </div>
        </div>

        <div className="form-footer">
          <p>
            계정이 없으신가요?{' '}
            <a href="#signup" onClick={(e) => { e.preventDefault(); onSwitchToSignup(); }}>
              회원가입
            </a>
          </p>
        </div>
        </div>

        <div className="project-info-panel">
          <div className="panel-header">
            <h3>이 프로젝트는</h3>
            <p className="project-subtitle">FastAPI + React로 구축된 AI 일정 관리 시스템입니다</p>
          </div>

          <div className="tech-features">
            <div className="tech-item">
              <span className="tech-icon">✓</span>
              <span className="tech-text">자연어 입력 → AI가 자동 파싱</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">✓</span>
              <span className="tech-text">JWT 인증으로 안전하게 보호</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">✓</span>
              <span className="tech-text">직관적인 캘린더 인터페이스</span>
            </div>
            <div className="tech-item">
              <span className="tech-icon">✓</span>
              <span className="tech-text">실시간 일정 통계</span>
            </div>
          </div>

          <div className="roadmap-section">
            <h4 className="roadmap-title">개발 예정</h4>
            <ul className="roadmap-list">
              <li>향상된 토큰 관리 시스템</li>
              <li>데이터베이스 마이그레이션 (SQLite → PostgreSQL)</li>
              <li>사용자 프로필 기능</li>
              <li>일정 공유 및 협업 기능</li>
            </ul>
          </div>

          <div className="portfolio-badge">
            <span className="badge-icon">📌</span>
            <div className="badge-content">
              <strong>포트폴리오 프로젝트</strong>
              <p>상세 구현 및 코드는 아래 GitHub Repository에서 확인하세요</p>
              <a href="https://github.com/jih4855/schedule_app.git" target="_blank" rel="noopener noreferrer" className="github-repo-link">
                GitHub Repository →
              </a>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;