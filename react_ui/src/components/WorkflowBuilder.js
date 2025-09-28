import React, { useState, useEffect } from 'react';
import DynamicForm from './DynamicForm';
import StepPreview from './StepPreview';

const WorkflowBuilder = ({ modules, apiBaseUrl }) => {
  const [workflowName, setWorkflowName] = useState('');
  const [workflowDescription, setWorkflowDescription] = useState('');
  const [steps, setSteps] = useState([]);
  const [templates, setTemplates] = useState([]);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  // 워크플로우 템플릿 로드
  useEffect(() => {
    const loadTemplates = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/workflow-builder`);
        const data = await response.json();
        setTemplates(data.workflow_templates || []);
      } catch (err) {
        console.error('템플릿 로딩 실패:', err);
      }
    };
    loadTemplates();
  }, [apiBaseUrl]);

  // 새 단계 추가
  const addStep = () => {
    const newStep = {
      id: Date.now(),
      module: '',
      action: '',
      init_params: {},
      params: {}
    };
    setSteps([...steps, newStep]);
  };

  // 단계 삭제
  const removeStep = (stepId) => {
    setSteps(steps.filter(step => step.id !== stepId));
  };

  // 단계 업데이트
  const updateStep = (stepId, updates) => {
    setSteps(steps.map(step =>
      step.id === stepId ? { ...step, ...updates } : step
    ));
  };

  // 단계 순서 변경
  const moveStep = (fromIndex, toIndex) => {
    const newSteps = [...steps];
    const [moved] = newSteps.splice(fromIndex, 1);
    newSteps.splice(toIndex, 0, moved);
    setSteps(newSteps);
  };

  // 템플릿 적용
  const applyTemplate = (template) => {
    const templateSteps = template.template.map((tStep, index) => ({
      id: Date.now() + index,
      module: tStep.module,
      action: tStep.action,
      init_params: {},
      params: {}
    }));
    setSteps(templateSteps);
    setWorkflowName(template.name);
    setWorkflowDescription(template.description);
  };

  // 워크플로우 실행
  const executeWorkflow = async () => {
    if (!workflowName.trim()) {
      setError('워크플로우 이름을 입력하세요.');
      return;
    }

    if (steps.length === 0) {
      setError('최소한 하나의 단계를 추가하세요.');
      return;
    }

    // 빈 필드 검증
    const hasEmptyFields = steps.some(step => !step.module || !step.action);
    if (hasEmptyFields) {
      setError('모든 단계의 모듈과 액션을 선택하세요.');
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const workflowData = {
        name: workflowName,
        description: workflowDescription,
        steps: steps.map(step => ({
          module: step.module,
          action: step.action,
          init_params: step.init_params,
          params: step.params
        }))
      };

      const response = await fetch(`${apiBaseUrl}/build-workflow`, {
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
      setResult(result);
    } catch (err) {
      console.error('워크플로우 실행 실패:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  // 워크플로우 초기화
  const resetWorkflow = () => {
    setSteps([]);
    setWorkflowName('');
    setWorkflowDescription('');
    setResult(null);
    setError('');
  };

  return (
    <div className="workflow-builder">
      {/* 헤더 */}
      <div className="builder-header">
        <h2>🔧 워크플로우 빌더</h2>
        <div className="header-actions">
          <button className="btn-secondary" onClick={resetWorkflow}>
            초기화
          </button>
          <button
            className="btn-primary"
            onClick={executeWorkflow}
            disabled={loading || steps.length === 0}
          >
            {loading ? '실행 중...' : '실행'}
          </button>
        </div>
      </div>

      {/* 기본 정보 */}
      <div className="workflow-info">
        <div className="form-group">
          <label>워크플로우 이름 *</label>
          <input
            type="text"
            value={workflowName}
            onChange={(e) => setWorkflowName(e.target.value)}
            placeholder="예: 음성 분석 파이프라인"
            className="form-input"
          />
        </div>
        <div className="form-group">
          <label>설명</label>
          <textarea
            value={workflowDescription}
            onChange={(e) => setWorkflowDescription(e.target.value)}
            placeholder="워크플로우에 대한 간단한 설명을 입력하세요..."
            className="form-textarea"
            rows="2"
          />
        </div>
      </div>

      {/* 템플릿 선택 */}
      {templates.length > 0 && (
        <div className="template-section">
          <h3>📋 빠른 시작 템플릿</h3>
          <div className="template-grid">
            {templates.map((template, index) => (
              <div key={index} className="template-card">
                <h4>{template.name}</h4>
                <p>{template.description}</p>
                <small>{template.steps}단계</small>
                <button
                  className="btn-outline"
                  onClick={() => applyTemplate(template)}
                >
                  적용
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 단계 목록 */}
      <div className="steps-section">
        <div className="steps-header">
          <h3>📝 워크플로우 단계</h3>
          <button className="btn-add" onClick={addStep}>
            + 단계 추가
          </button>
        </div>

        {steps.length === 0 ? (
          <div className="empty-state">
            <p>아직 단계가 없습니다. 첫 번째 단계를 추가하세요!</p>
          </div>
        ) : (
          <div className="steps-list">
            {steps.map((step, index) => (
              <StepEditor
                key={step.id}
                step={step}
                stepNumber={index + 1}
                modules={modules}
                onUpdate={(updates) => updateStep(step.id, updates)}
                onRemove={() => removeStep(step.id)}
                onMoveUp={index > 0 ? () => moveStep(index, index - 1) : null}
                onMoveDown={index < steps.length - 1 ? () => moveStep(index, index + 1) : null}
                availableOutputs={steps.slice(0, index).map((_, i) => `step_output_${i + 1}`)}
              />
            ))}
          </div>
        )}
      </div>

      {/* 에러 표시 */}
      {error && (
        <div className="error-message">
          <span>⚠️ {error}</span>
        </div>
      )}

      {/* 워크플로우 미리보기 */}
      {steps.length > 0 && (
        <StepPreview steps={steps} />
      )}

      {/* 실행 결과 */}
      {result && (
        <div className="execution-result">
          <h3>✅ 실행 완료</h3>
          <div className="result-content">
            <pre>{JSON.stringify(result, null, 2)}</pre>
          </div>
        </div>
      )}
    </div>
  );
};

// 개별 단계 편집 컴포넌트
const StepEditor = ({
  step,
  stepNumber,
  modules,
  onUpdate,
  onRemove,
  onMoveUp,
  onMoveDown,
  availableOutputs
}) => {
  const [isExpanded, setIsExpanded] = useState(true);

  const handleModuleChange = (moduleName) => {
    onUpdate({
      module: moduleName,
      action: '',
      init_params: {},
      params: {}
    });
  };

  const handleActionChange = (actionName) => {
    onUpdate({
      action: actionName,
      init_params: {},
      params: {}
    });
  };

  const currentModule = modules[step.module];
  const currentAction = currentModule?.actions?.[step.action];

  return (
    <div className="step-editor">
      <div className="step-header">
        <div className="step-title">
          <span className="step-number">{stepNumber}</span>
          <select
            value={step.module}
            onChange={(e) => handleModuleChange(e.target.value)}
            className="module-select"
          >
            <option value="">모듈 선택...</option>
            {Object.entries(modules).map(([key, module]) => (
              <option key={key} value={key}>{module.name}</option>
            ))}
          </select>

          {step.module && (
            <select
              value={step.action}
              onChange={(e) => handleActionChange(e.target.value)}
              className="action-select"
            >
              <option value="">액션 선택...</option>
              {Object.entries(currentModule.actions || {}).map(([key, action]) => (
                <option key={key} value={key}>{action.name}</option>
              ))}
            </select>
          )}
        </div>

        <div className="step-controls">
          <button
            className="btn-icon"
            onClick={() => setIsExpanded(!isExpanded)}
            title={isExpanded ? "접기" : "펼치기"}
          >
            {isExpanded ? '📄' : '📋'}
          </button>
          {onMoveUp && (
            <button className="btn-icon" onClick={onMoveUp} title="위로">⬆️</button>
          )}
          {onMoveDown && (
            <button className="btn-icon" onClick={onMoveDown} title="아래로">⬇️</button>
          )}
          <button className="btn-icon btn-danger" onClick={onRemove} title="삭제">🗑️</button>
        </div>
      </div>

      {isExpanded && step.module && step.action && (
        <div className="step-content">
          {/* 모듈 초기화 파라미터 */}
          {currentModule?.init_params && Object.keys(currentModule.init_params).length > 0 && (
            <div className="param-section">
              <h4>🔧 모듈 설정</h4>
              <DynamicForm
                fields={currentModule.init_params}
                values={step.init_params}
                onChange={(values) => onUpdate({ init_params: values })}
                availableOutputs={availableOutputs}
              />
            </div>
          )}

          {/* 액션 파라미터 */}
          {currentAction?.params && Object.keys(currentAction.params).length > 0 && (
            <div className="param-section">
              <h4>⚙️ 액션 파라미터</h4>
              <DynamicForm
                fields={currentAction.params}
                values={step.params}
                onChange={(values) => onUpdate({ params: values })}
                availableOutputs={availableOutputs}
              />
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default WorkflowBuilder;