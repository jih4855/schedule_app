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

    try {
      const response = await fetch('http://localhost:8000/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        const expirationTime = Date.now() + (30 * 60 * 1000);
        localStorage.setItem('token_expiration', expirationTime.toString());

        setMessage({
          text: `로그인 성공! ${formData.username}님 환영합니다!`,
          type: 'success'
        });
        setFormData({ username: '', password: '' });

        setTimeout(() => {
          onLoginSuccess();
        }, 1000);
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

        <div className="form-footer">
          <p>
            계정이 없으신가요?{' '}
            <a href="#signup" onClick={(e) => { e.preventDefault(); onSwitchToSignup(); }}>
              회원가입
            </a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginForm;