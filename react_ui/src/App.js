import React, { useState, useEffect } from 'react';
import LoginForm from './components/LoginForm';
import SignupForm from './components/SignupForm';
import SchedulePage from './components/SchedulePage';
import './App.css';

function App() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [showSignup, setShowSignup] = useState(false);

  // 컴포넌트 마운트 시 토큰 확인
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    const expiration = localStorage.getItem('token_expiration');

    if (token && expiration) {
      const now = Date.now();
      if (now < parseInt(expiration)) {
        setIsLoggedIn(true);
      } else {
        localStorage.removeItem('access_token');
        localStorage.removeItem('token_expiration');
        setIsLoggedIn(false);
      }
    }
  }, []);

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('token_expiration');
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
        <SchedulePage onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;