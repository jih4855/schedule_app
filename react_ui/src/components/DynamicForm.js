import React from 'react';

const DynamicForm = ({ fields, values, onChange, availableOutputs = [] }) => {
  const handleFieldChange = (fieldName, value) => {
    const newValues = { ...values, [fieldName]: value };
    onChange(newValues);
  };

  const renderField = (fieldName, fieldConfig) => {
    const value = values[fieldName] || fieldConfig.default || '';
    const isRequired = fieldConfig.required;

    // step_output 참조를 위한 제안 목록
    const getSuggestions = () => {
      if (fieldConfig.type === 'textarea' || fieldConfig.type === 'string') {
        return availableOutputs;
      }
      return [];
    };

    switch (fieldConfig.type) {
      case 'string':
        return (
          <div key={fieldName} className="form-field">
            <label className={isRequired ? 'required' : ''}>
              {fieldConfig.description}
            </label>
            <input
              type="text"
              value={value}
              onChange={(e) => handleFieldChange(fieldName, e.target.value)}
              placeholder={fieldConfig.placeholder || ''}
              className="form-input"
              required={isRequired}
            />
            {getSuggestions().length > 0 && (
              <div className="field-suggestions">
                <small>이전 단계 참조: </small>
                {getSuggestions().map(output => (
                  <button
                    key={output}
                    type="button"
                    className="suggestion-btn"
                    onClick={() => handleFieldChange(fieldName, output)}
                  >
                    {output}
                  </button>
                ))}
              </div>
            )}
          </div>
        );

      case 'textarea':
        return (
          <div key={fieldName} className="form-field">
            <label className={isRequired ? 'required' : ''}>
              {fieldConfig.description}
            </label>
            <textarea
              value={value}
              onChange={(e) => handleFieldChange(fieldName, e.target.value)}
              placeholder={fieldConfig.placeholder || ''}
              className="form-textarea"
              rows={3}
              required={isRequired}
            />
            {getSuggestions().length > 0 && (
              <div className="field-suggestions">
                <small>이전 단계 참조: </small>
                {getSuggestions().map(output => (
                  <button
                    key={output}
                    type="button"
                    className="suggestion-btn"
                    onClick={() => handleFieldChange(fieldName, output)}
                  >
                    {output}
                  </button>
                ))}
              </div>
            )}
          </div>
        );

      case 'select':
        return (
          <div key={fieldName} className="form-field">
            <label className={isRequired ? 'required' : ''}>
              {fieldConfig.description}
            </label>
            <select
              value={value}
              onChange={(e) => handleFieldChange(fieldName, e.target.value)}
              className="form-select"
              required={isRequired}
            >
              {!isRequired && <option value="">선택하세요...</option>}
              {(fieldConfig.options || []).map(option => (
                <option key={option} value={option}>{option}</option>
              ))}
            </select>
          </div>
        );

      case 'multiselect':
        const multiValue = Array.isArray(value) ? value : (fieldConfig.default || []);
        return (
          <div key={fieldName} className="form-field">
            <label className={isRequired ? 'required' : ''}>
              {fieldConfig.description}
            </label>
            <div className="multi-select">
              {(fieldConfig.options || []).map(option => (
                <label key={option} className="checkbox-label">
                  <input
                    type="checkbox"
                    checked={multiValue.includes(option)}
                    onChange={(e) => {
                      const newValue = e.target.checked
                        ? [...multiValue, option]
                        : multiValue.filter(v => v !== option);
                      handleFieldChange(fieldName, newValue);
                    }}
                  />
                  <span>{option}</span>
                </label>
              ))}
            </div>
          </div>
        );

      case 'checkbox':
        return (
          <div key={fieldName} className="form-field">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={Boolean(value)}
                onChange={(e) => handleFieldChange(fieldName, e.target.checked)}
              />
              <span>{fieldConfig.description}</span>
            </label>
          </div>
        );

      case 'number':
        return (
          <div key={fieldName} className="form-field">
            <label className={isRequired ? 'required' : ''}>
              {fieldConfig.description}
            </label>
            <input
              type="number"
              value={value}
              onChange={(e) => handleFieldChange(fieldName, Number(e.target.value))}
              min={fieldConfig.min}
              max={fieldConfig.max}
              className="form-input"
              required={isRequired}
            />
          </div>
        );

      case 'url':
        return (
          <div key={fieldName} className="form-field">
            <label className={isRequired ? 'required' : ''}>
              {fieldConfig.description}
            </label>
            <input
              type="url"
              value={value}
              onChange={(e) => handleFieldChange(fieldName, e.target.value)}
              placeholder={fieldConfig.placeholder || 'https://...'}
              className="form-input"
              required={isRequired}
            />
          </div>
        );

      case 'password':
        return (
          <div key={fieldName} className="form-field">
            <label className={isRequired ? 'required' : ''}>
              {fieldConfig.description}
            </label>
            <input
              type="password"
              value={value}
              onChange={(e) => handleFieldChange(fieldName, e.target.value)}
              placeholder={fieldConfig.placeholder || ''}
              className="form-input"
              required={isRequired}
            />
          </div>
        );

      case 'array':
        const arrayValue = Array.isArray(value) ? value : [];
        return (
          <div key={fieldName} className="form-field">
            <label className={isRequired ? 'required' : ''}>
              {fieldConfig.description}
            </label>
            <div className="array-input">
              <textarea
                value={JSON.stringify(arrayValue, null, 2)}
                onChange={(e) => {
                  try {
                    const parsedValue = JSON.parse(e.target.value);
                    if (Array.isArray(parsedValue)) {
                      handleFieldChange(fieldName, parsedValue);
                    }
                  } catch (err) {
                    // 파싱 에러는 무시 (사용자가 입력 중일 수 있음)
                  }
                }}
                placeholder={fieldConfig.placeholder || '["item1", "item2"]'}
                className="form-textarea"
                rows={2}
                required={isRequired}
              />
              <small className="field-hint">JSON 배열 형식으로 입력하세요</small>
              {getSuggestions().length > 0 && (
                <div className="field-suggestions">
                  <small>이전 단계 참조 추가: </small>
                  {getSuggestions().map(output => (
                    <button
                      key={output}
                      type="button"
                      className="suggestion-btn"
                      onClick={() => {
                        const newArray = [...arrayValue, output];
                        handleFieldChange(fieldName, newArray);
                      }}
                    >
                      + {output}
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>
        );

      default:
        return (
          <div key={fieldName} className="form-field">
            <label>{fieldConfig.description}</label>
            <input
              type="text"
              value={value}
              onChange={(e) => handleFieldChange(fieldName, e.target.value)}
              className="form-input"
            />
          </div>
        );
    }
  };

  return (
    <div className="dynamic-form">
      {Object.entries(fields).map(([fieldName, fieldConfig]) =>
        renderField(fieldName, fieldConfig)
      )}
    </div>
  );
};

export default DynamicForm;