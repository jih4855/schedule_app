# AI Multi-Agent Toolkit

Python 기반 LLM 에이전트 개발을 위한 도구모음과 실용 예제입니다. 여러 LLM 프로바이더 통합, 음성-텍스트 변환, Discord 연동 등을 지원합니다.

## 주요 기능

- **멀티 LLM 지원**: Ollama, OpenAI, Google Gemini 통합
- **에이전트 시스템**: 단일/멀티 에이전트 패턴 지원
- **음성 처리**: Whisper 기반 STT (Speech-to-Text)
- **Discord 연동**: 웹훅을 통한 메시지 전송 (청크 분할 지원)
- **대화 기억**: SQLite 기반 컨텍스트 관리
- **문서화**: 다크 테마 HTML 문서 제공

## 시스템 요구사항

- Python 3.10 이상
- pip (패키지 관리자)
- ffmpeg (음성 처리 시 필요, 선택사항)

## 설치 방법

### 1. 저장소 클론
```bash
git clone <repository-url>
cd agent
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
response = agent.generate_response(
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

response = agent.generate_response(
    system_prompt="You are a helpful assistant.",
    user_message="Explain machine learning in simple terms."
)
print(response)
```

## 프로젝트 구조

```
agent/
├── module/                 # 핵심 라이브러리
│   ├── llm_agent.py       # LLM 에이전트 클래스
│   ├── audio_tool.py      # 음성 처리 도구
│   ├── discord.py         # Discord 연동
│   ├── memory.py          # 대화 기억 관리
│   └── text_tool.py       # 텍스트 처리 유틸리티
├── test/                  # 사용 예제 및 테스트
├── docs/                  # HTML 문서
│   └── index.html         # 상세 사용법 가이드
├── .env.example           # 환경 변수 템플릿
├── requirements.txt       # Python 의존성
└── README.md             # 프로젝트 문서
```

## API 키 설정

### Google Gemini API
1. [Google AI Studio](https://aistudio.google.com/app/apikey)에서 API 키 발급
2. `.env` 파일에 `GOOGLE_API_KEY=your_key` 추가

### OpenAI API
1. [OpenAI Platform](https://platform.openai.com/api-keys)에서 API 키 발급
2. `.env` 파일에 `OPENAI_API_KEY=your_key` 추가

### Discord 웹훅 (선택사항)
1. Discord 서버 설정 > 연동 > 웹후크에서 생성
2. `.env` 파일에 `DISCORD_WEBHOOK_URL=your_webhook_url` 추가

## 문서

자세한 사용법과 예제는 `docs/index.html`을 브라우저에서 열어 확인하세요.

```bash
# 브라우저에서 문서 열기
open docs/index.html    # macOS
start docs/index.html   # Windows
xdg-open docs/index.html # Linux
```

**문서 주요 내용:**
- 단계별 설치 가이드 및 환경 설정
- 기본 LLM 에이전트 사용법
- 멀티 에이전트 시스템 구성 방법
- 음성-텍스트 변환 실습
- Discord 메시지 전송 및 청크 분할
- 대화 컨텍스트 기억 기능
- 트러블슈팅 및 문제 해결 가이드

## 테스트 실행

```bash

### 자주 발생하는 문제

**ModuleNotFoundError**
```bash
# 해결방법: 가상환경 활성화 확인 후 의존성 재설치
pip install -r requirements.txt
```

**API 키 관련 오류**
```bash
# 해결방법: .env 파일 설정 확인
cat .env  # 설정된 환경 변수 확인
```

**Ollama 연결 오류**
```bash
# 해결방법: Ollama 서비스 실행 확인
ollama list  # 설치된 모델 확인
```

**음성 처리 오류**
```bash
# 해결방법: ffmpeg 설치
# Windows (Chocolatey):
choco install ffmpeg

# macOS (Homebrew):
brew install ffmpeg

# Ubuntu/Debian:
sudo apt install ffmpeg

# 설치 확인:
ffmpeg -version
```