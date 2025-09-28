import React from 'react';
import toolkitLogo from '../assets/toolkit-logo.png';

function Hero() {
  return (
    <section className="hero">
      <div className="hero-container">
        <div className="hero-content">
          <img src={toolkitLogo} alt="AI Multi-Agent Toolkit Logo" className="hero-logo" />
          <h2>Welcome to the AI Multi-Agent Toolkit!</h2>
          <p>This is a simple React UI to interact with the FastAPI backend.</p>
          <button className="hero-button">시작하기</button>
        </div>
      </div>
    </section>
  );
}

export default Hero;
