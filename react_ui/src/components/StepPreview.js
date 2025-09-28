import React from 'react';

const StepPreview = ({ steps }) => {
  return (
    <div className="step-preview">
      <h3>🔍 워크플로우 미리보기</h3>
      <div className="preview-flow">
        {steps.map((step, index) => (
          <div key={step.id} className="preview-step">
            <div className="step-card">
              <div className="step-header">
                <span className="step-number">{index + 1}</span>
                <div className="step-info">
                  <h4>{step.module || '모듈 미선택'}</h4>
                  <p>{step.action || '액션 미선택'}</p>
                </div>
              </div>

              {(Object.keys(step.init_params || {}).length > 0 ||
                Object.keys(step.params || {}).length > 0) && (
                <div className="step-params">
                  {Object.keys(step.init_params || {}).length > 0 && (
                    <div className="param-group">
                      <small>모듈 설정:</small>
                      <ul>
                        {Object.entries(step.init_params).map(([key, value]) => (
                          <li key={key}>
                            <strong>{key}:</strong> {JSON.stringify(value)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {Object.keys(step.params || {}).length > 0 && (
                    <div className="param-group">
                      <small>액션 파라미터:</small>
                      <ul>
                        {Object.entries(step.params).map(([key, value]) => (
                          <li key={key}>
                            <strong>{key}:</strong> {JSON.stringify(value)}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </div>

            {index < steps.length - 1 && (
              <div className="flow-arrow">
                <span>⬇️</span>
                <small>step_output_{index + 1}</small>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="preview-summary">
        <h4>📊 요약</h4>
        <ul>
          <li>총 {steps.length}개 단계</li>
          <li>사용 모듈: {[...new Set(steps.map(s => s.module).filter(Boolean))].join(', ')}</li>
          <li>예상 출력: step_output_{steps.length}</li>
        </ul>
      </div>
    </div>
  );
};

export default StepPreview;