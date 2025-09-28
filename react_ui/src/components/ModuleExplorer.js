import React, { useState, useEffect } from 'react';

const ModuleExplorer = ({ modules, apiBaseUrl }) => {
  const [selectedModule, setSelectedModule] = useState('');
  const [moduleDetails, setModuleDetails] = useState(null);
  const [availableModules, setAvailableModules] = useState({});

  // API에서 모듈 상세 정보 로드
  useEffect(() => {
    const loadModuleDetails = async () => {
      try {
        const response = await fetch(`${apiBaseUrl}/modules`);
        const data = await response.json();
        setAvailableModules(data.available_modules || {});
      } catch (err) {
        console.error('모듈 상세 정보 로딩 실패:', err);
      }
    };
    loadModuleDetails();
  }, [apiBaseUrl]);

  // 선택된 모듈 변경
  const handleModuleSelect = (moduleName) => {
    setSelectedModule(moduleName);
    setModuleDetails(modules[moduleName] || null);
  };

  // 모듈 아이콘 매핑
  const getModuleIcon = (moduleName) => {
    const icons = {
      'Audio': '🎵',
      'LLM_Agent': '🤖',
      'Multi_modal_agent': '👁️',
      'Discord': '💬'
    };
    return icons[moduleName] || '📦';
  };

  // 파라미터 타입 아이콘
  const getTypeIcon = (type) => {
    const icons = {
      'string': '📝',
      'textarea': '📄',
      'select': '📋',
      'multiselect': '☑️',
      'checkbox': '✅',
      'number': '🔢',
      'url': '🔗',
      'password': '🔒',
      'array': '📚'
    };
    return icons[type] || '❓';
  };

  return (
    <div className="module-explorer">
      <div className="explorer-header">
        <h2>📚 모듈 탐색기</h2>
        <p>사용 가능한 모듈들과 그 기능을 탐색하세요</p>
      </div>

      <div className="explorer-content">
        {/* 모듈 목록 */}
        <div className="module-list">
          <h3>사용 가능한 모듈</h3>
          <div className="module-grid">
            {Object.entries(modules).map(([moduleName, moduleConfig]) => {
              const details = availableModules[moduleName];
              return (
                <div
                  key={moduleName}
                  className={`module-card ${selectedModule === moduleName ? 'selected' : ''}`}
                  onClick={() => handleModuleSelect(moduleName)}
                >
                  <div className="module-header">
                    <span className="module-icon">{getModuleIcon(moduleName)}</span>
                    <h4>{moduleConfig.name}</h4>
                  </div>
                  <p className="module-description">{moduleConfig.description}</p>
                  <div className="module-stats">
                    <span className="stat">
                      {Object.keys(moduleConfig.actions || {}).length} 액션
                    </span>
                    {details && !details.error && (
                      <span className="stat">
                        {details.methods?.length || 0} 메서드
                      </span>
                    )}
                  </div>
                  {details?.error && (
                    <div className="module-error">
                      <small>⚠️ {details.error}</small>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* 선택된 모듈 상세 정보 */}
        {selectedModule && moduleDetails && (
          <div className="module-details">
            <div className="details-header">
              <span className="module-icon">{getModuleIcon(selectedModule)}</span>
              <h3>{moduleDetails.name}</h3>
            </div>

            <p className="module-description">{moduleDetails.description}</p>

            {/* 초기화 파라미터 */}
            {moduleDetails.init_params && Object.keys(moduleDetails.init_params).length > 0 && (
              <div className="param-section">
                <h4>🔧 모듈 초기화 설정</h4>
                <div className="param-list">
                  {Object.entries(moduleDetails.init_params).map(([paramName, paramConfig]) => (
                    <div key={paramName} className="param-item">
                      <div className="param-header">
                        <span className="param-icon">{getTypeIcon(paramConfig.type)}</span>
                        <span className="param-name">{paramName}</span>
                        <span className="param-type">{paramConfig.type}</span>
                        {paramConfig.required && <span className="required-badge">필수</span>}
                      </div>
                      <p className="param-description">{paramConfig.description}</p>
                      {paramConfig.default !== undefined && (
                        <div className="param-default">
                          기본값: <code>{JSON.stringify(paramConfig.default)}</code>
                        </div>
                      )}
                      {paramConfig.options && (
                        <div className="param-options">
                          옵션: <code>{paramConfig.options.join(', ')}</code>
                        </div>
                      )}
                      {paramConfig.placeholder && (
                        <div className="param-placeholder">
                          예시: <code>{paramConfig.placeholder}</code>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 액션 목록 */}
            {moduleDetails.actions && Object.keys(moduleDetails.actions).length > 0 && (
              <div className="actions-section">
                <h4>⚙️ 사용 가능한 액션</h4>
                <div className="actions-list">
                  {Object.entries(moduleDetails.actions).map(([actionName, actionConfig]) => (
                    <div key={actionName} className="action-item">
                      <div className="action-header">
                        <h5>{actionConfig.name}</h5>
                        <code className="action-code">{actionName}</code>
                      </div>

                      {/* 액션 파라미터 */}
                      {actionConfig.params && Object.keys(actionConfig.params).length > 0 && (
                        <div className="action-params">
                          <h6>파라미터:</h6>
                          <div className="param-list">
                            {Object.entries(actionConfig.params).map(([paramName, paramConfig]) => (
                              <div key={paramName} className="param-item small">
                                <div className="param-header">
                                  <span className="param-icon">{getTypeIcon(paramConfig.type)}</span>
                                  <span className="param-name">{paramName}</span>
                                  <span className="param-type">{paramConfig.type}</span>
                                  {paramConfig.required && <span className="required-badge">필수</span>}
                                </div>
                                <p className="param-description">{paramConfig.description}</p>
                                {paramConfig.placeholder && (
                                  <div className="param-placeholder">
                                    예시: <code>{paramConfig.placeholder}</code>
                                  </div>
                                )}
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 실제 모듈 메서드 (API에서 가져온 정보) */}
            {availableModules[selectedModule]?.methods && (
              <div className="methods-section">
                <h4>🔍 실제 모듈 메서드</h4>
                <div className="methods-list">
                  {availableModules[selectedModule].methods.map(method => (
                    <span key={method} className="method-tag">{method}</span>
                  ))}
                </div>
              </div>
            )}

            {/* 사용 예제 */}
            <div className="usage-example">
              <h4>💡 사용 예제</h4>
              <div className="example-code">
                <pre>{`{
  "step": 1,
  "module": "${selectedModule}",
  "action": "${Object.keys(moduleDetails.actions || {})[0] || '__call__'}",
  "init_params": {${Object.entries(moduleDetails.init_params || {})
    .filter(([_, config]) => config.required)
    .map(([key, config]) => `\n    "${key}": "${config.default || config.placeholder || 'value'}"`)
    .join(',')}
  },
  "params": {${Object.entries(moduleDetails.actions?.[Object.keys(moduleDetails.actions || {})[0]]?.params || {})
    .filter(([_, config]) => config.required)
    .map(([key, config]) => `\n    "${key}": "${config.placeholder || 'value'}"`)
    .join(',')}
  }
}`}</pre>
              </div>
            </div>
          </div>
        )}

        {/* 모듈이 선택되지 않은 경우 */}
        {!selectedModule && (
          <div className="no-selection">
            <div className="no-selection-content">
              <span className="icon">👆</span>
              <h3>모듈을 선택하세요</h3>
              <p>왼쪽에서 모듈을 클릭하면 상세 정보를 볼 수 있습니다</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ModuleExplorer;