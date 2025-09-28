// react_ui/src/App.js

import React, { useState } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('single'); // 'single' or 'multi'

  return (
    <div className="app">
      <div className="app-container">
        <header className="app-header">
          <h1>🤖 AI Multi-Agent Toolkit</h1>
          <p>단일 AI 또는 다중 AI 에이전트와 대화하세요</p>
        </header>

        <div className="tab-container">
          <button
            className={`tab-button ${activeTab === 'single' ? 'active' : ''}`}
            onClick={() => setActiveTab('single')}
          >
            단일 에이전트
          </button>
          <button
            className={`tab-button ${activeTab === 'multi' ? 'active' : ''}`}
            onClick={() => setActiveTab('multi')}
          >
            멀티 에이전트
          </button>
        </div>

        <main className="main-content">
          {activeTab === 'single' ? <SingleAgentMode /> : <MultiAgentMode />}
        </main>
      </div>
    </div>
  );
}

function SingleAgentMode() {
  const [systemPrompt, setSystemPrompt] = useState('당신은 도움이 되는 AI 어시스턴트입니다.');
  const [userMessage, setUserMessage] = useState('');
  const [response, setResponse] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!userMessage.trim()) return;

    setLoading(true);
    setError('');
    setResponse('');

    try {
      const res = await fetch('http://localhost:8000/generate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          system_prompt: systemPrompt,
          user_message: userMessage
        }),
      });

      if (!res.ok) throw new Error(`서버 에러: ${res.status}`);

      const data = await res.json();
      setResponse(data.response);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mode-container">
      <div className="input-section">
        <div className="input-group">
          <label className="input-label">
            <span className="label-icon">🎭</span>
            시스템 프롬프트
          </label>
          <textarea
            className="system-prompt-input"
            value={systemPrompt}
            onChange={(e) => setSystemPrompt(e.target.value)}
            placeholder="AI의 역할을 정의하세요..."
            rows={3}
          />
        </div>

        <div className="input-group">
          <label className="input-label">
            <span className="label-icon">💬</span>
            사용자 메시지
          </label>
          <textarea
            className="user-message-input"
            value={userMessage}
            onChange={(e) => setUserMessage(e.target.value)}
            placeholder="무엇을 물어보시겠습니까?"
            rows={4}
            required
          />
        </div>

        <button
          type="submit"
          className="submit-button"
          onClick={handleSubmit}
          disabled={loading || !userMessage.trim()}
        >
          {loading ? (
            <>
              <span className="loading-spinner"></span>
              AI가 생각하는 중...
            </>
          ) : (
            <>
              <span className="send-icon">🚀</span>
              전송하기
            </>
          )}
        </button>
      </div>

      <div className="response-section">
        {error && (
          <div className="error-message">
            <span className="error-icon">❌</span>
            {error}
          </div>
        )}

        {response && (
          <div className="response-card">
            <div className="response-header">
              <span className="response-icon">🤖</span>
              <h3>AI 응답</h3>
            </div>
            <div className="response-content">
              {response}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

function MultiAgentMode() {
  const [masterPrompts, setMasterPrompts] = useState({
    system_prompt: "당신은 여러 전문가의 의견을 종합하는 마스터 AI입니다.",
    user_message: "양자컴퓨팅의 미래에 대해 논하시오.",
    task: "아래 전문가들의 의견을 종합하여, 일반인도 이해하기 쉬운 최종 보고서를 작성하시오."
  });

  const [agents, setAgents] = useState([
    {
      name: '물리학자',
      role: '양자역학 전문가로서 기술의 원리를 설명합니다.',
      task: '양자컴퓨팅의 기본 원리와 현재 기술 수준을 설명하시오.'
    },
    {
      name: '경제학자',
      role: '기술 경제 전문가로서 산업에 미칠 영향을 분석합니다.',
      task: '양자컴퓨팅이 미래 산업과 경제에 미칠 파급효과를 분석하시오.'
    },
    {
      name: '윤리학자',
      role: '기술 윤리 전문가로서 사회적 영향을 고려합니다.',
      task: '양자컴퓨팅의 발전이 사회와 윤리에 미칠 영향을 논의하시오.'
    },
    {
      name: '엔지니어',
      role: '실무 엔지니어로서 실제 구현 가능성을 평가합니다.',
      task: '양자컴퓨팅의 현재 기술적 도전과제와 미래 발전 방향을 제시하시오.'
    }
  ]);

  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleMasterPromptChange = (e) => {
    const { name, value } = e.target;
    setMasterPrompts(prev => ({ ...prev, [name]: value }));
  };

  const handleAgentChange = (index, e) => {
    const { name, value } = e.target;
    const newAgents = [...agents];
    newAgents[index][name] = value;
    setAgents(newAgents);
  };

  const addAgent = () => {
    setAgents([...agents, { name: '', role: '', task: '' }]);
  };

  const removeAgent = (index) => {
    if (agents.length > 1) {
      const newAgents = agents.filter((_, i) => i !== index);
      setAgents(newAgents);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setResult(null);

    // 유효한 에이전트만 필터링 (이름, 역할, 태스크가 모두 있는 경우)
    const validAgents = agents.filter(agent =>
      agent.name.trim() && agent.role.trim() && agent.task.trim()
    );

    if (validAgents.length === 0) {
      setError('최소 1개 이상의 유효한 에이전트가 필요합니다.');
      setLoading(false);
      return;
    }

    const payload = {
      system_prompt: masterPrompts.system_prompt,
      user_message: masterPrompts.user_message,
      task: masterPrompts.task,
      agents: validAgents
    };

    try {
      const response = await fetch('http://localhost:8000/multi_agent', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) throw new Error(`서버 에러: ${response.status}`);

      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="mode-container">
      <form onSubmit={handleSubmit} className="multi-agent-form">
        <div className="master-section">
          <h3 className="section-title">
            <span className="section-icon">👑</span>
            마스터 AI 설정
          </h3>

          <div className="input-group">
            <label className="input-label">주제</label>
            <input
              type="text"
              name="user_message"
              value={masterPrompts.user_message}
              onChange={handleMasterPromptChange}
              placeholder="논의할 주제를 입력하세요"
            />
          </div>

          <div className="input-group">
            <label className="input-label">마스터 AI 역할</label>
            <textarea
              name="system_prompt"
              value={masterPrompts.system_prompt}
              onChange={handleMasterPromptChange}
              placeholder="마스터 AI의 역할을 정의하세요"
              rows={2}
            />
          </div>

          <div className="input-group">
            <label className="input-label">종합 태스크</label>
            <textarea
              name="task"
              value={masterPrompts.task}
              onChange={handleMasterPromptChange}
              placeholder="전문가들의 의견을 어떻게 종합할지 설명하세요"
              rows={3}
            />
          </div>
        </div>

        <div className="agents-section">
          <h3 className="section-title">
            <span className="section-icon">👥</span>
            전문가 에이전트들
          </h3>

          <div className="agents-grid">
            {agents.map((agent, index) => (
              <div key={index} className="agent-card">
                <div className="agent-header">
                  <span className="agent-number">{index + 1}</span>
                  <input
                    type="text"
                    name="name"
                    value={agent.name}
                    onChange={(e) => handleAgentChange(index, e)}
                    placeholder="전문가 이름"
                    className="agent-name-input"
                  />
                  {agents.length > 1 && (
                    <button
                      type="button"
                      className="remove-agent-btn"
                      onClick={() => removeAgent(index)}
                      title="이 에이전트 삭제"
                    >
                      <span className="remove-icon">✕</span>
                    </button>
                  )}
                </div>

                <div className="input-group">
                  <label className="input-label">역할</label>
                  <textarea
                    name="role"
                    value={agent.role}
                    onChange={(e) => handleAgentChange(index, e)}
                    placeholder="이 전문가의 역할을 설명하세요"
                    rows={2}
                  />
                </div>

                <div className="input-group">
                  <label className="input-label">태스크</label>
                  <textarea
                    name="task"
                    value={agent.task}
                    onChange={(e) => handleAgentChange(index, e)}
                    placeholder="이 전문가가 수행할 구체적인 작업을 설명하세요"
                    rows={3}
                  />
                </div>
              </div>
            ))}
          </div>

          {agents.length < 10 && (
            <div className="add-agent-section">
              <button
                type="button"
                className="add-agent-button"
                onClick={addAgent}
              >
                <span className="add-icon">➕</span>
                에이전트 추가 ({agents.length})
              </button>
            </div>
          )}
        </div>

        <div className="submit-section">
          <button
            type="submit"
            className="submit-button large"
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="loading-spinner"></span>
                전문가들이 협력하는 중...
              </>
            ) : (
              <>
                <span className="send-icon">🚀</span>
                멀티 에이전트 실행
              </>
            )}
          </button>
        </div>
      </form>

      <div className="response-section">
        {error && (
          <div className="error-message">
            <span className="error-icon">❌</span>
            {error}
          </div>
        )}

        {result && (
          <div className="multi-response">
            <h3 className="response-title">
              <span className="response-icon">📋</span>
              전문가별 의견
            </h3>

            <div className="individual-responses">
              {(() => {
                const validAgents = agents.filter(a => a.name.trim() && a.role.trim() && a.task.trim());
                return result.individual_responses?.map((item, index) => {
                  const displayName = item.name || validAgents[index]?.name || `에이전트 ${index+1}`;
                  return (
                    <div key={displayName + index} className="response-card agent-response">
                      <div className="response-header">
                        <span className="agent-avatar">👨‍🔬</span>
                        <h4>{displayName}의 의견</h4>
                      </div>
                      <div className="response-content">
                        {item.response || '(응답 없음)'}
                      </div>
                    </div>
                  );
                });
              })()}
            </div>

            <div className="final-response">
              <h3 className="response-title">
                <span className="response-icon">🎯</span>
                최종 종합 보고서
              </h3>
              <div className="response-card final">
                <div className="response-header">
                  <span className="response-icon">🤖</span>
                  <h4>마스터 AI의 종합 분석</h4>
                </div>
                <div className="response-content">
                  {result.final_response || '(최종 응답 없음)'}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;