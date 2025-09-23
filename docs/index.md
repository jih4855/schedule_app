---
layout: default
title: Home
---

# AI Multi-Agent Toolkit

Python 기반 LLM 에이전트 개발을 위한 도구모음과 실용 예제입니다. 여러 LLM 프로바이더 통합, 음성-텍스트 변환, Discord 연동 등을 지원합니다.

**📖 문서:** [https://jih4855.github.io/AI-Multi-Agent-Toolkit/](https://jih4855.github.io/AI-Multi-Agent-Toolkit/)
**📁 Repository:** [https://github.com/jih4855/AI-Multi-Agent-Toolkit](https://github.com/jih4855/AI-Multi-Agent-Toolkit)

## 주요 기능

- **멀티 LLM 지원**: Ollama, OpenAI, Google Gemini 통합
- **에이전트 시스템**: 단일/멀티 에이전트 패턴 지원
- **음성 처리**: Whisper 기반 STT (Speech-to-Text)
- **Discord 연동**: 웹훅을 통한 메시지 전송 (청크 분할 지원)
- **대화 기억**: SQLite 기반 컨텍스트 관리
- **멀티모달 지원**: 비전 + 언어 모델을 활용한 이미지 분석
- **문서화**: 다크 테마 HTML 문서 제공

## 시스템 요구사항

- Python 3.10 이상
- pip (패키지 관리자)
- ffmpeg (음성 처리 시 필요, 선택사항)

## 설치 방법

### 1. 저장소 클론
```bash
git clone https://github.com/jih4855/AI-Multi-Agent-Toolkit.git
cd AI-Multi-Agent-Toolkit
```

### 2. 가상환경 생성 (권장)
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
```bash
# .env.example을 .env로 복사
cp .env.example .env

# .env 파일을 편집하여 실제 API 키로 교체
# GOOGLE_API_KEY=your_google_api_key_here
# OPENAI_API_KEY=your_openai_api_key_here
# DISCORD_WEBHOOK_URL=your_discord_webhook_url_here
```

**참고:** Ollama 사용 시에는 API 키가 필요하지 않습니다.

## 빠른 시작

### 기본 LLM 에이전트 사용

```python
from module.llm_agent import LLM_Agent

# Ollama 사용 (로컬, API 키 불필요)
agent = LLM_Agent(model_name="gemma:2b", provider="ollama")
response = agent(
    system_prompt="당신은 도움이 되는 비서입니다.",
    user_message="안녕하세요, 자기소개를 해주세요."
)
print(response)
```

### 환경 변수를 사용한 API 연동

```python
import os
from dotenv import load_dotenv
from module.llm_agent import LLM_Agent

load_dotenv()

# Google Gemini 사용
agent = LLM_Agent(
    model_name="gemini-2.5-flash",
    provider="genai",
    api_key=os.getenv("GOOGLE_API_KEY")
)

response = agent(
    system_prompt="You are a helpful assistant.",
    user_message="Explain machine learning in simple terms."
)
print(response)
```

## 문서

자세한 사용법과 예제는 다음 페이지에서 확인하세요:

- **[📖 상세 문서](docs/)**: 완전한 사용법 가이드
- **[🔧 개발 로그](dev-log/)**: 개발 과정 및 문제 해결 기록

---

이 프로젝트는 AI 에이전트 개발을 쉽게 만들기 위해 설계되었습니다. 기여와 피드백을 환영합니다!