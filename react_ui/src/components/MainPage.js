import React, { useState, useEffect } from 'react';
import './MainPage.css';

const MainPage = ({ onLogout }) => {
  const [mainData, setMainData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchMainData();
  }, []);

  const fetchMainData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/', {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        setMainData(data);
      } else {
        setError('데이터를 불러올 수 없습니다.');
      }
    } catch (error) {
      setError('서버 연결에 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    onLogout();
  };

  if (isLoading) {
    return (
      <div className="main-container">
        <div className="loading">데이터를 불러오는 중...</div>
      </div>
    );
  }

  return (
    <div className="main-container">
      <header className="main-header">
        <h1>AI Multi-Agent Toolkit</h1>
        <button className="logout-button" onClick={handleLogout}>
          로그아웃
        </button>
      </header>

      <main className="main-content">
        <div className="welcome-section">
          <h2>환영합니다!</h2>
          <p>AI Multi-Agent Toolkit 메인 페이지입니다.</p>
        </div>

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        {mainData && (
          <div className="data-section">
            <h3>서버 응답</h3>
            <div className="data-card">
              <pre>{JSON.stringify(mainData, null, 2)}</pre>
            </div>
          </div>
        )}

        <div className="features-section">
          <h3>주요 기능</h3>
          <div className="feature-grid">
            <div className="feature-card">
              <h4>워크플로우 관리</h4>
              <p>AI 에이전트 워크플로우를 설계하고 관리합니다.</p>
            </div>
            <div className="feature-card">
              <h4>멀티 에이전트</h4>
              <p>여러 AI 에이전트를 협력하여 작업을 수행합니다.</p>
            </div>
            <div className="feature-card">
              <h4>API 통합</h4>
              <p>다양한 API와 연동하여 확장성을 제공합니다.</p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default MainPage;