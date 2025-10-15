import React, { useState, useEffect } from 'react';
import LoginForm from './components/LoginForm';
import SignupForm from './components/SignupForm';
import SchedulePage from './components/SchedulePage';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showSignup, setShowSignup] = useState(false);
  const [accessToken, setAccessToken] = useState(null);

  // 앱 시작 시 Refresh Token으로 Access Token 복원
  useEffect(() => {
    const restoreToken = async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || ''}/api/refresh`, {
          method: 'POST',
          credentials: 'include',  // 쿠키 전송
        });

        if (response.ok) {
          const data = await response.json();
          setAccessToken(data.access_token);
          setIsLoggedIn(true);
        }
      } catch (error) {
        console.log('No valid refresh token');
      }
    };

    restoreToken();
  }, []);

  const handleLoginSuccess = (token) => {
    setAccessToken(token);
    setIsLoggedIn(true);
  };

  // 자동 Refresh 타이머 (14분마다 토큰 갱신)
  useEffect(() => {
    // accessToken이 없으면 타이머 시작 안 함
    if (!accessToken) {
      return;
    }

    // 14분(840초)마다 자동 갱신
    const refreshInterval = setInterval(async () => {
      try {
        const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || ''}/api/refresh`, {
          method: 'POST',
          credentials: 'include',
        });

        if (response.ok) {
          const data = await response.json();
          setAccessToken(data.access_token);
          console.log('Access Token이 자동으로 갱신되었습니다.');
        } else {
          console.log('Refresh Token 만료. 로그아웃합니다.');
          setAccessToken(null);
          setIsLoggedIn(false);
        }
      } catch (error) {
        console.error('토큰 자동 갱신 실패:', error);
      }
    }, 14 * 60 * 1000);

    return () => {
      clearInterval(refreshInterval);
    };
  }, [accessToken]);

  const handleLogout = async () => {
    try {
      // 서버에 로그아웃 요청 (Refresh Token 쿠키 삭제)
      await fetch(`${process.env.REACT_APP_API_BASE_URL || ''}/api/logout`, {
        method: 'POST',
        credentials: 'include',
      });
    } catch (error) {
      console.error('로그아웃 요청 실패:', error);
    }

    // 클라이언트 상태 초기화
    setAccessToken(null);
    setIsLoggedIn(false);
  };

  const handleSwitchToSignup = () => {
    setShowSignup(true);
  };

  const handleSwitchToLogin = () => {
    setShowSignup(false);
  };

  return (
    <div className="App">
      {!isLoggedIn ? (
        showSignup ? (
          <SignupForm onSwitchToLogin={handleSwitchToLogin} />
        ) : (
          <LoginForm
            onLoginSuccess={handleLoginSuccess}
            onSwitchToSignup={handleSwitchToSignup}
          />
        )
      ) : (
        <SchedulePage onLogout={handleLogout} accessToken={accessToken} />
      )}
    </div>
  );
}

export default App;