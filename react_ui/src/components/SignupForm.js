import React, { useState } from 'react';
import './SignupForm.css';

const SignupForm = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
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

  // 에러 메시지를 사용자 친화적으로 변환하는 함수
  const formatErrorMessage = (detail) => {
    // 문자열인 경우 그대로 반환
    if (typeof detail === 'string') {
      return detail;
    }

    // Pydantic 검증 에러 배열인 경우
    if (Array.isArray(detail)) {
      return detail.map(err => {
        // err.msg가 있으면 사용, 없으면 기본 메시지
        return err.msg || '입력 정보를 확인해주세요.';
      }).join('\n');
    }

    // 기본 메시지
    return '입력 정보를 확인해주세요.';
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setMessage({ text: '', type: '' });

    try {
      const response = await fetch('http://localhost:8000/api/signup', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        setMessage({
          text: `회원가입 성공! 환영합니다, ${data.username}님!`,
          type: 'success'
        });
        setFormData({ username: '', email: '', password: '' });
      } else {
        setMessage({
          text: formatErrorMessage(data.detail),
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
    <div className="signup-container">
      <div className="signup-form">
        <h2>회원가입</h2>
        <p className="signup-description">
          새로운 계정을 만들어 서비스를 이용해보세요
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
            <label htmlFor="email">이메일</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              placeholder="이메일을 입력하세요"
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
            {isLoading ? '처리 중...' : '회원가입'}
          </button>
        </form>

        <div className="form-footer">
          <p>
            이미 계정이 있으신가요?{' '}
            <a href="#login" onClick={(e) => { e.preventDefault(); onSwitchToLogin(); }}>
              로그인
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default SignupForm;