import React, { useState, useEffect } from 'react';

const WorkflowExecutor = ({ apiBaseUrl }) => {
  const [examples, setExamples] = useState({});
  const [selectedExample, setSelectedExample] = useState('');
  const [customWorkflow, setCustomWorkflow] = useState('');
  const [executionMode, setExecutionMode] = useState('example'); // 'example' or 'custom'
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [executionHistory, setExecutionHistory] = useState([]);

  // 예제 워크플로우 로드
  useEffect(() => {
    const loadExamples = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/examples`);
        const data = await response.json();
        setExamples(data.workflow_examples || {});
      } catch (err) {
        console.error('예제 로딩 실패:', err);
      }
    };
    loadExamples();
  }, [apiBaseUrl]);

  // 워크플로우 실행
  const executeWorkflow = async (workflowData) => {
    setLoading(true);
    setError('');
    setResult(null);

    const startTime = Date.now();

    try {
      const response = await fetch(`${apiBaseUrl}/execute_workflow`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(workflowData)
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || '워크플로우 실행 실패');
      }

      const result = await response.json();
      const executionTime = Date.now() - startTime;

      setResult(result);

      // 실행 이력에 추가
      const historyItem = {
        id: Date.now(),
        timestamp: new Date().toLocaleString(),
        type: executionMode,
        name: executionMode === 'example' ? examples[selectedExample]?.name : 'Custom Workflow',
        executionTime,
        status: result.status,
        stepCount: Object.keys(result.step_outputs || {}).length
      };
      setExecutionHistory(prev => [historyItem, ...prev.slice(0, 9)]); // 최근 10개만 유지

    } catch (err) {
      console.error('워크플로우 실행 실패:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 예제 워크플로우 실행
  const runExample = () => {
    if (!selectedExample || !examples[selectedExample]) {
      setError('예제를 선택하세요.');
      return;
    }

    const exampleWorkflow = examples[selectedExample].workflow;
    executeWorkflow(exampleWorkflow);
  };

  // 커스텀 워크플로우 실행
  const runCustom = () => {
    if (!customWorkflow.trim()) {
      setError('워크플로우 JSON을 입력하세요.');
      return;
    }

    try {
      const workflowData = JSON.parse(customWorkflow);
      executeWorkflow(workflowData);
    } catch (err) {
      setError('잘못된 JSON 형식입니다: ' + err.message);
    }
  };

  return (
    <div className="workflow-executor">
      <div className="executor-header">
        <h2>⚡ 워크플로우 실행기</h2>
        <p>예제 워크플로우를 실행하거나 직접 JSON을 입력하여 테스트하세요</p>
      </div>

      {/* 실행 모드 선택 */}
      <div className="execution-mode">
        <div className="mode-tabs">
          <button
            className={`tab-button ${executionMode === 'example' ? 'active' : ''}`}
            onClick={() => setExecutionMode('example')}
          >
            📚 예제 실행
          </button>
          <button
            className={`tab-button ${executionMode === 'custom' ? 'active' : ''}`}
            onClick={() => setExecutionMode('custom')}
          >
            🔧 커스텀 JSON
          </button>
        </div>
      </div>

      {/* 예제 실행 모드 */}
      {executionMode === 'example' && (
        <div className="example-mode">
          <div className="example-selector">
            <label>실행할 예제 선택:</label>
            <select
              value={selectedExample}
              onChange={(e) => setSelectedExample(e.target.value)}
              className="form-select"
            >
              <option value="">예제를 선택하세요...</option>
              {Object.entries(examples).map(([key, example]) => (
                <option key={key} value={key}>{example.name}</option>
              ))}
            </select>
          </div>

          {selectedExample && examples[selectedExample] && (
            <div className="example-preview">
              <h3>{examples[selectedExample].name}</h3>
              <p>{examples[selectedExample].description}</p>
              <details className="example-details">
                <summary>워크플로우 JSON 보기</summary>
                <pre className="json-preview">
                  {JSON.stringify(examples[selectedExample].workflow, null, 2)}
                </pre>
              </details>
              <button
                className="btn-primary"
                onClick={runExample}
                disabled={loading}
              >
                {loading ? '실행 중...' : '예제 실행'}
              </button>
            </div>
          )}
        </div>
      )}

      {/* 커스텀 JSON 모드 */}
      {executionMode === 'custom' && (
        <div className="custom-mode">
          <div className="json-input">
            <label>워크플로우 JSON:</label>
            <textarea
              value={customWorkflow}
              onChange={(e) => setCustomWorkflow(e.target.value)}
              placeholder={`{
  "workflow": [
    {
      "step": 1,
      "module": "LLM_Agent",
      "action": "__call__",
      "init_params": {"model_name": "gemma3n", "provider": "ollama"},
      "params": {
        "system_prompt": "당신은 도움이 되는 AI입니다.",
        "user_message": "안녕하세요!"
      }
    }
  ]
}`}
              className="json-textarea"
              rows={15}
            />
            <button
              className="btn-primary"
              onClick={runCustom}
              disabled={loading}
            >
              {loading ? '실행 중...' : 'JSON 실행'}
            </button>
          </div>
        </div>
      )}

      {/* 에러 표시 */}
      {error && (
        <div className="error-message">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* 실행 결과 */}
      {result && (
        <div className="execution-result">
          <h3>
            {result.status === 'success' ? '✅ 실행 완료' : '❌ 실행 실패'}
          </h3>

          {result.status === 'success' ? (
            <div className="success-result">
              {/* 단계별 결과 */}
              {result.step_outputs && Object.keys(result.step_outputs).length > 0 && (
                <div className="step-outputs">
                  <h4>📝 단계별 결과</h4>
                  {Object.entries(result.step_outputs).map(([step, output]) => (
                    <div key={step} className="step-output">
                      <h5>Step {step}</h5>
                      <div className="output-content">
                        <pre>{JSON.stringify(output, null, 2)}</pre>
                      </div>
                    </div>
                  ))}
                </div>
              )}

              {/* 최종 결과 */}
              {result.final_result && (
                <div className="final-result">
                  <h4>🎯 최종 결과</h4>
                  <div className="output-content">
                    <pre>{JSON.stringify(result.final_result, null, 2)}</pre>
                  </div>
                </div>
              )}
            </div>
          ) : (
            <div className="error-result">
              <p>오류 메시지: {result.error_message}</p>
              {result.step_outputs && Object.keys(result.step_outputs).length > 0 && (
                <div className="partial-outputs">
                  <h4>부분 실행 결과</h4>
                  <pre>{JSON.stringify(result.step_outputs, null, 2)}</pre>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* 실행 이력 */}
      {executionHistory.length > 0 && (
        <div className="execution-history">
          <h3>📜 실행 이력</h3>
          <div className="history-list">
            {executionHistory.map((item) => (
              <div key={item.id} className="history-item">
                <div className="history-header">
                  <span className={`status-badge ${item.status}`}>
                    {item.status === 'success' ? '✅' : '❌'}
                  </span>
                  <span className="history-name">{item.name}</span>
                  <span className="history-time">{item.timestamp}</span>
                </div>
                <div className="history-details">
                  <small>
                    {item.stepCount}단계 · {item.executionTime}ms
                  </small>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default WorkflowExecutor;