import React from 'react';

function Features() {
  const features = [
    {
      title: "LLM Agent 상호작용",
      description: "Send prompts to the LLM agent",
      icon: "🤖"
    },
    {
      title: "응답 관리",
      description: "Receive and display responses",
      icon: "💬"
    },
    {
      title: "멀티 에이전트",
      description: "Manage multiple agents",
      icon: "👥"
    }
  ];

  return (
    <section className="features" id="features">
      <div className="features-container">
        <h2>Features</h2>
        <div className="features-grid">
          {features.map((feature, index) => (
            <div key={index} className="feature-card">
              <div className="feature-icon">{feature.icon}</div>
              <h3>{feature.title}</h3>
              <p>{feature.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

export default Features;
