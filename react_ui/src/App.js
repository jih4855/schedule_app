import React, { useState, useEffect } from 'react';
import SignupForm from './components/SignupForm';
import LoginForm from './components/LoginForm';
import MainPage from './components/MainPage';
import './App.css';

function App() {
  const [currentView, setCurrentView] = useState('login');
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  // 컴포넌트 마운트 시 토큰 확인
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsLoggedIn(true);
      setCurrentView('main');
    }
  }, []);

  const switchToSignup = () => setCurrentView('signup');
  const switchToLogin = () => {
    setCurrentView('login');
    setIsLoggedIn(false);
  };

  const handleLoginSuccess = () => {
    setIsLoggedIn(true);
    setCurrentView('main');
  };

  const handleLogout = () => {
    setIsLoggedIn(false);
    setCurrentView('login');
  };

  return (
    <div className="App">
      {!isLoggedIn ? (
        <>
          {currentView === 'login' ? (
            <LoginForm
              onSwitchToSignup={switchToSignup}
              onLoginSuccess={handleLoginSuccess}
            />
          ) : (
            <SignupForm onSwitchToLogin={switchToLogin} />
          )}
        </>
      ) : (
        <MainPage onLogout={handleLogout} />
      )}
    </div>
  );
}

export default App;