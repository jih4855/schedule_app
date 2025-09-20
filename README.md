# AI Multi-Agent Toolkit

<div align="center">
  <img src="docs/image.png" alt="AI Multi-Agent Toolkit" width="800"/>
</div>

Python 기반 LLM 에이전트 개발을 위한 도구모음과 실용 예제입니다. 여러 LLM 프로바이더 통합, 음성-텍스트 변환, Discord 연동 등을 지원합니다.

**📖 문서:** https://jih4855.github.io/AI-Multi-Agent-Toolkit/
**📁 Repository:** https://github.com/jih4855/AI-Multi-Agent-Toolkit

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

response = agent(
    system_prompt="You are a helpful assistant.",
    user_message="Explain machine learning in simple terms."
)
print(response)
```

## 사용 예제

### 1. 멀티 에이전트 활용하기

```python
from module.llm_agent import LLM_Agent

system_prompt = "You are a helpful assistant."
agent1_user_prompt = "리눅스에 대해서 설명해주세요."
agent2_user_prompt = "앞선 답변을 읽고 내용을 보충해 주세요"

# 복수의 에이전트의 프롬프트를 정의합니다.
multi_agent = LLM_Agent(model_name="gemma3n", provider="ollama")
agent1 = multi_agent(system_prompt, agent1_user_prompt, task=None)
agent2 = multi_agent(system_prompt, agent2_user_prompt, task=None, multi_agent_response=agent1)

print("Agent 1 Response:", agent1)
print("Agent 2 Response:", agent2)
```

### 2. 모든 에이전트의 응답 통합하기

```python
from module.llm_agent import LLM_Agent

# 각 에이전트의 시스템 프롬프트, 사용자 프롬프트, 작업을 정의합니다.
multi_agent_tasks = {
    "Agent 1": "도시에서 발생하는 환경 문제(대기, 수질, 쓰레기 등)를 정리하고, 가장 시급한 과제를 제시한다.",
    "Agent 2": "친환경 교통수단(대중교통, 자전거, 전기차 등)을 기반으로 지속 가능한 교통 인프라 계획을 제안한다.",
    "Agent 3": "재생에너지(태양광, 풍력, 스마트 그리드 등)를 활용하여 효율적인 에너지 공급 방안을 설계한다.",
    "Agent 4": "도시 공간 구조(공원, 주거, 상업지구 배치 등)를 최적화한다."
}

multi_agent_system_prompts = {
    "Agent 1": "당신은 환경 전문가입니다. 도시의 환경 문제를 분석하고, 가장 시급한 문제를 제시하세요.",
    "Agent 2": "당신은 교통 전문가입니다. 지속 가능한 교통 인프라 계획을 제안하세요.",
    "Agent 3": "당신은 에너지 전문가입니다. 재생에너지를 활용한 에너지 공급 방안을 설계하세요.",
    "Agent 4": "당신은 도시 계획 전문가입니다. 도시 공간 구조를 최적화하는 방안을 제시하세요."
}

user_prompts = {
    "Agent 1": "도시에서 발생하는 환경 문제를 분석하고, 가장 시급한 문제를 제시하세요.",
    "Agent 2": "지속 가능한 교통 인프라 계획을 제안하세요.",
    "Agent 3": "재생에너지를 활용한 에너지 공급 방안을 설계하세요.",
    "Agent 4": "도시 공간 구조를 최적화하는 방안을 제시하세요."
}

order = ["Agent 1", "Agent 2", "Agent 3", "Agent 4"]

multi_agent = LLM_Agent(model_name="gemini-2.5-flash", provider="genai", api_key="your_api_key")

agent_responses = {
    name: multi_agent(multi_agent_system_prompts[name], user_prompts[name], multi_agent_tasks[name])
    for name in order
}

response_list = [agent_responses[name] for name in order]

multi_agent_responses = multi_agent(
    "당신은 도시 계획 전문가입니다. 지속 가능한 도시 설계 방안을 제시하세요.",
    "다음은 여러 전문가의 의견입니다. 이를 바탕으로 최종 요약 및 통합된 지속 가능한 도시 설계 방안을 제시하세요.",
    "최종 요약 및 통합된 지속 가능한 도시 설계 방안을 제시한다.",
    response_list
)

print("Agent 1 Response:", agent_responses["Agent 1"])
print("Agent 2 Response:", agent_responses["Agent 2"])
print("Agent 3 Response:", agent_responses["Agent 3"])
print("Agent 4 Response:", agent_responses["Agent 4"])
print("Multi-Agent Responses:", multi_agent_responses)
```

### 3. LLM 에이전트에 기억력 붙이기

```python
import dotenv
import os
dotenv.load_dotenv()

# LLM_Agent 인스턴스 생성
llm = LLM_Agent(model_name="gemini-2.5-flash", provider="genai", api_key=os.getenv("GENAI_API_KEY"), max_history=10)

# 대화 루프 예시
while True:
    user_input = input("You: ")
    response = llm(system_prompt="You are a helpful assistant.", user_message=user_input, memory=True)
    print("Assistant:", response)

    if user_input.lower() in ['exit', 'quit']:
        break
```

### 4. Discord로 메시지 보내기

```python
from module.discord import Send_to_discord
from module.llm_agent import LLM_Agent

model_name = 'gemma3:12b'
system_prompt = '당신은 유능한 비서입니다. 이용자에게 도움이 되는 답변을 제공합니다.'
user_prompt = '프랑스의 수도는 어디인가요?'
provider = 'ollama'

agent = LLM_Agent(model_name, provider, api_key=None)
response = agent(system_prompt, user_prompt, task=None)

discord = Send_to_discord(base_url="your_discord_webhook_url")
discord.send_message(response)
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

자세한 사용법과 예제는 온라인 문서에서 확인하세요:

**📖 온라인 문서:** https://jih4855.github.io/AI-Multi-Agent-Toolkit/

또는 로컬에서 `docs/index.html`을 브라우저로 열어 확인할 수 있습니다:

```bash
# 브라우저에서 로컬 문서 열기
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
