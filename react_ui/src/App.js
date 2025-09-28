import React, { useState, useEffect } from 'react';
import './App.css';
import WorkflowBuilder from './components/WorkflowBuilder';
import WorkflowExecutor from './components/WorkflowExecutor';
import ModuleExplorer from './components/ModuleExplorer';

const API_BASE_URL = 'http://localhost:8000';

function App() {
  const [activeTab, setActiveTab] = useState('builder');
  const [modules, setModules] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  // API에서 모듈 정보 로드
  useEffect(() => {
    const loadModules = async () => {
      try {
        setLoading(true);
        const response = await fetch(`${API_BASE_URL}/workflow-builder`);
        if (!response.ok) {
          throw new Error(`API Error: ${response.status}`);
        }
        const data = await response.json();
        setModules(data.modules || {});
        setError('');
      } catch (err) {
        console.error('모듈 로딩 실패:', err);
        setError(`모듈 로딩 실패: ${err.message}`);
      } finally {
        setLoading(false);
      }
    };

    loadModules();
  }, []);

  if (loading) {
    return (
      <div className="app">
        <div className="loading-container">
          <div className="spinner"></div>
          <p>워크플로우 시스템을 로딩 중...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="error-container">
          <h2>⚠️ 연결 오류</h2>
          <p>{error}</p>
          <p>FastAPI 서버가 실행 중인지 확인하세요: <code>http://localhost:8000</code></p>
          <button onClick={() => window.location.reload()}>
            다시 시도
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <h1>🚀 AI Multi-Agent Workflow Builder</h1>
          <p>동적 모듈 오케스트레이션으로 복잡한 AI 파이프라인을 구성하세요</p>
        </div>
      </header>

      <nav className="tab-navigation">
        <button
          className={`tab-button ${activeTab === 'builder' ? 'active' : ''}`}
          onClick={() => setActiveTab('builder')}
        >
          <span className="tab-icon">🔧</span>
          워크플로우 빌더
        </button>
        <button
          className={`tab-button ${activeTab === 'executor' ? 'active' : ''}`}
          onClick={() => setActiveTab('executor')}
        >
          <span className="tab-icon">⚡</span>
          실행 & 결과
        </button>
        <button
          className={`tab-button ${activeTab === 'explorer' ? 'active' : ''}`}
          onClick={() => setActiveTab('explorer')}
        >
          <span className="tab-icon">📚</span>
          모듈 탐색기
        </button>
      </nav>

      <main className="main-content">
        {activeTab === 'builder' && (
          <WorkflowBuilder modules={modules} apiBaseUrl={API_BASE_URL} />
        )}
        {activeTab === 'executor' && (
          <WorkflowExecutor apiBaseUrl={API_BASE_URL} />
        )}
        {activeTab === 'explorer' && (
          <ModuleExplorer modules={modules} apiBaseUrl={API_BASE_URL} />
        )}
      </main>

      <footer className="app-footer">
        <p>
          🤖 AI Multi-Agent Toolkit v2.0 -
          <a href="http://localhost:8000/docs" target="_blank" rel="noopener noreferrer">
            API 문서
          </a>
        </p>
      </footer>
    </div>
  );
}

export default App;