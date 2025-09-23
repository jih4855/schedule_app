---
layout: default
title: Documentation
charset: utf-8
---

# AI Multi-Agent Toolkit Documentation

AI Multi-Agent Toolkit의 상세 사용법과 예제를 제공합니다.

## 1. 업데이트 현황

현재까지 구현된 기능에 대한 요약입니다.

- LLM 에이전트 생성 및 응답 받기 (ollama, openai, genai(gemini) 지원)
- Discord로 메시지 보내기 (메시지 청크 분할 및 겹침 지원)
- 음성 파일을 텍스트로 변환하기 (whisper 사용)
- 텍스트 청크 분할 및 겹침 지원
- 2025/09/17 에이전트 메모리 기능 구현
- 2025/09/21 LLM_Agent 클래스에 __call__ 매직 메서드가 추가되어 agent.generate_response() 대신 agent() 직접 호출이 가능해졌습니다.
- 2025/09/21 LLM_Agent 멀티모달 사용 추가
- 2025/09/22 멀티 에이전트 시험 문제 생성기 예제 추가 (YouTube → 시험 문제 자동 생성)
- 2025/09/23 메모리 저장 로직 개선 (실제 LLM 전송 컨텍스트와 메모리 저장 내용 일치화)

## 2. 모듈 소개

### LLM 에이전트 핵심 모듈

#### 1) 인스턴스 생성 - 📄 llm_agent.py

```python
# 기본 LLM 에이전트
from module.llm_agent import LLM_Agent

agent = LLM_Agent(
    model_name="gemini-2.5-flash",
    provider="genai",  # ollama, genai, openai
    api_key="your_api_key",
    session_id="chat_session",
    max_history=10
)

# 멀티모달 에이전트
from module.llm_agent import Multi_modal_agent

modal_agent = Multi_modal_agent(
    model_name="gemma3:12b",
    provider="ollama",  # ollama, genai
    api_key=None
)
```

**지원 기능:** 다중 LLM 프로바이더 지원 (Ollama, OpenAI, Google Gemini), 대화 기억 기능, 멀티 에이전트 협업, 이미지 분석 및 OCR (멀티모달), __call__ 매직 메서드로 간편한 호출

#### 2) 에이전트 호출하고 응답받기

```python
# 기본 텍스트 대화
response = agent(
    system_prompt="당신은 친근한 AI 비서입니다.",
    user_message="오늘 날씨가 어때요?"
)
print(response)  # AI의 답변이 출력됩니다

# 메모리 기능으로 이전 대화 기억하기
response_with_memory = agent(
    system_prompt="당신은 친근한 AI 비서입니다.",
    user_message="제 이름을 기억하시나요?",
    memory=True  # 이전 대화를 기억합니다
)

# 이미지와 함께 대화하기 (멀티모달)
image_response = modal_agent(
    system_prompt="당신은 이미지 분석 전문가입니다.",
    user_message="이 사진에 뭐가 보이나요?",
    image_path="my_photo.jpg"  # 분석할 이미지 파일
)
print(image_response)  # 이미지 분석 결과가 출력됩니다
```

### Discord 웹훅 연동 모듈

#### Discord 메시지 전송 - 📄 discord.py

```python
from module.discord import Send_to_discord

discord = Send_to_discord(
    base_url="https://discord.com/api/webhooks/your_webhook_url"
)

# 기본 메시지 전송
discord.send_message("안녕하세요! 이것은 테스트 메시지입니다.")

# 긴 텍스트 자동 분할 전송
long_text = "매우 긴 텍스트..." * 1000
discord.send_message(long_text)  # 자동으로 2000자씩 분할해서 전송
```

**주요 기능:** LLM 응답을 Discord 채널로 자동 전송, 긴 메시지 청크 분할 처리

### 음성 처리 모듈

#### 음성을 텍스트로 변환 - 📄 audio_tool.py

```python
from module.audio_tool import Audio_to_text

# 음성 변환 인스턴스 생성
audio_converter = Audio_to_text()

# 단일 파일 변환
result = audio_converter.convert_single_file("my_audio.mp3")
print(result)  # 변환된 텍스트가 출력됩니다

# 폴더 내 모든 오디오 파일 일괄 변환
audio_converter.convert_folder("audio_files/")
```

**주요 기능:** Whisper를 사용한 음성-텍스트 변환, 다양한 오디오 포맷 지원, 배치 처리

### 대화 기억 관리 모듈

#### 대화 기록 SQLite 저장 - 📄 memory.py

```python
from module.memory import MemoryManager

memory = MemoryManager(db_path="conversations.db")

# 대화 기록 저장
memory.save_history("session_1", [
    {"role": "user", "content": "안녕하세요"},
    {"role": "assistant", "content": "안녕하세요! 무엇을 도와드릴까요?"}
])

# 대화 기록 불러오기
history = memory.get_history("session_1")
print(history)
```

**주요 기능:** LLM 에이전트의 대화 기록을 SQLite에 저장하고 관리 (챗봇 메모리 기능에 사용)

### 텍스트 처리 유틸리티

#### 긴 텍스트 청킹 분할 - 📄 text_tool.py

```python
from module.text_tool import Text_tool

text_tool = Text_tool(
    chunk_size=1000,
    overlap=100
)

# 긴 텍스트를 청크로 분할
chunks = text_tool.split_text("매우 긴 텍스트 내용...")
print(f"총 {len(chunks)}개 청크로 분할됨")

# 결과를 JSON 파일로 자동 저장
text_tool.save_to_json(chunks, "output.json")
```

**주요 기능:** 긴 텍스트를 적절한 크기로 분할, JSON 결과 자동 저장 (Discord 메시지 전송, 대용량 문서 처리, 멀티 에이전트 결과 저장에 사용)

## 3. LLM 에이전트 사용하기

### 기본 에이전트 생성 및 대화

```python
from module.llm_agent import LLM_Agent

# Ollama 사용 (로컬 환경)
agent = LLM_Agent(model_name="gemma3", provider="ollama")

response = agent(
    system_prompt="당신은 도움이 되는 AI 비서입니다.",
    user_message="Python에서 리스트와 튜플의 차이점을 설명해주세요."
)
print(response)
```

### 메모리 기능으로 연속 대화

```python
# 메모리 기능이 있는 에이전트
memory_agent = LLM_Agent(
    model_name="gpt-4o-mini",
    provider="openai",
    api_key="your_openai_key",
    session_id="my_conversation",
    max_history=20
)

# 첫 번째 대화
response1 = memory_agent(
    system_prompt="당신은 친근한 AI 도우미입니다.",
    user_message="제 이름은 김철수입니다. 기억해주세요.",
    memory=True
)

# 두 번째 대화 (이전 내용을 기억함)
response2 = memory_agent(
    system_prompt="당신은 친근한 AI 도우미입니다.",
    user_message="제 이름이 뭐였죠?",
    memory=True
)
print(response2)  # "김철수님"이라고 답변할 것입니다
```

### 멀티모달 에이전트로 이미지 분석

```python
from module.llm_agent import Multi_modal_agent

# 이미지 분석 가능한 에이전트
vision_agent = Multi_modal_agent(
    model_name="gemini-2.5-flash",
    provider="genai",
    api_key="your_gemini_key"
)

# 이미지 OCR 및 분석
result = vision_agent(
    system_prompt="이미지를 분석하고 텍스트를 추출해주세요.",
    user_message="이 문서에서 중요한 정보를 요약해주세요.",
    image_path="document.jpg"
)
print(result)
```

## 4. 멀티 에이전트 시험 문제 생성기

YouTube 영상을 분석하여 자동으로 시험 문제를 생성하는 예제입니다.

```python
import os
from dotenv import load_dotenv
from module.llm_agent import LLM_Agent
import yt_dlp

load_dotenv()

# 에이전트 설정
agent = LLM_Agent(
    model_name="gemini-2.5-flash",
    provider="genai",
    api_key=os.getenv("GOOGLE_API_KEY")
)

# YouTube 영상 다운로드 및 분석
def generate_quiz_from_youtube(video_url):
    # 영상 정보 추출
    with yt_dlp.YoutubeDL({'writeinfojson': True}) as ydl:
        info = ydl.extract_info(video_url, download=False)
        title = info.get('title', 'Unknown')
        description = info.get('description', '')

    # 문제 생성 에이전트
    quiz_response = agent(
        system_prompt="당신은 교육 전문가입니다. 주어진 내용을 바탕으로 학습 효과가 높은 시험 문제를 생성해주세요.",
        user_message=f"제목: {title}\n설명: {description[:2000]}\n\n위 내용을 바탕으로 객관식 5문항을 만들어주세요."
    )

    return quiz_response

# 사용 예시
quiz = generate_quiz_from_youtube("https://youtube.com/watch?v=example")
print(quiz)
```

## 5. Discord로 메시지 보내기

LLM 응답을 Discord 채널로 자동 전송하는 방법입니다.

```python
from module.discord import Send_to_discord
from module.llm_agent import LLM_Agent

# 에이전트와 Discord 설정
agent = LLM_Agent(model_name="gemma3", provider="ollama")
discord = Send_to_discord(base_url="your_discord_webhook_url")

# LLM 응답을 Discord로 전송
system_prompt = "당신은 유능한 비서입니다."
user_prompt = "오늘의 날씨와 추천 활동을 알려주세요."

response = agent(system_prompt, user_prompt)
discord.send_message(f"🤖 AI 응답:\n{response}")
```

#### Discord 메시지 전송 고급 설정

```python
from module.discord import Send_to_discord

discord = Send_to_discord(
    base_url="your_discord_webhook_url",  # Discord 웹훅 URL
    chunk_size=1900,  # 메시지 청크 크기 (기본: 1900)
    overlap=0         # 청크 간 겹침 크기 (기본: 0)
)

# 긴 메시지 자동 분할 전송
long_response = agent(system_prompt, "매우 긴 답변이 필요한 질문")
discord.send_message(long_response)  # 자동으로 여러 메시지로 분할 전송
```

### 음성 처리 모듈 고급 사용법

#### 음성을 텍스트로 변환 - 📄 audio_tool.py

```python
from module.audio_tool import Audio

audio = Audio(
    text_output="transcripts",    # 텍스트 출력 폴더 (기본: "text")
    source_file="audio_files",    # 음성 파일 폴더 (기본: "source_file")
    whisper_model="large-v3",     # Whisper 모델 (기본: "large-v3")
    preferred_codec="mp3",        # 선호 오디오 코덱 (기본: "mp3")
    preferred_quality="192"       # 오디오 품질 (기본: "192")
)

# 단일 파일 변환
result = audio.convert_single_file("my_audio.wav")
print(result)

# 폴더 내 모든 파일 일괄 변환
audio.convert_folder_files()
```

### 대화 기억 관리 모듈 상세

#### 대화 기록 SQLite 저장 - 📄 memory.py

```python
from module.memory import MemoryManager

memory = MemoryManager(
    db_path="memory.db",           # 데이터베이스 파일 경로 (기본: "memory.db")
    session_id="user_session_01",  # 세션 ID (기본: None)
    messages=[]                    # 초기 메시지 리스트 (기본: [])
)

# 대화 저장
memory.save_history("session_1", [
    {"role": "user", "content": "안녕하세요"},
    {"role": "assistant", "content": "안녕하세요! 도움이 필요하시면 말씀해주세요."}
])

# 대화 불러오기
history = memory.get_history("session_1")
for msg in history:
    print(f"{msg['role']}: {msg['content']}")
```

### 텍스트 처리 유틸리티 상세

#### 긴 텍스트 청킹 분할 고급 설정

```python
from module.text_tool import Text_tool

text_tool = Text_tool(
    chunk_size=1000,  # 청크 크기 (기본: 1000)
    overlap=100,      # 청크 간 겹침 (기본: 0)
    max_length=5000   # 최대 길이 제한 (기본: None)
)

# 긴 텍스트 분할
long_text = "매우 긴 문서 내용..." * 1000
chunks = text_tool.split_text(long_text)
print(f"총 {len(chunks)}개 청크로 분할됨")

# 각 청크 처리
for i, chunk in enumerate(chunks):
    print(f"청크 {i+1}: {len(chunk)}자")
```

#### JSON 결과 저장 기능

```python
# JSON 결과 자동 저장 기능
text_tool = Text_tool()

# LLM 에이전트 결과를 JSON 파일로 저장
final_output = {
    "concepts_and_terms": ["관계대수", "조인", "차집합"],
    "questions": [
        {
            "question": "관계대수에서 '보타이기호'는 어떤 연산자를 의미하나요?",
            "options": ["셀렉트", "프로젝트", "조인", "디비전"],
            "answer": "조인",
            "explanation": "보타이기호는 관계대수에서 조인 연산자를 나타냅니다."
        }
    ]
}

# 자동으로 final_outputs/quiz_result.json 파일로 저장
text_tool.save_result_json(
    final_output=final_output,      # 저장할 데이터 (dict, list, 또는 JSON 문자열)
    output_filename="quiz_result",  # 파일명 (확장자 자동 추가)
    save_foldername="final_outputs" # 저장할 폴더명 (자동 생성)
)

print("✅ JSON 파일 저장 완료: final_outputs/quiz_result.json")
```

## 3. LLM 에이전트 상세 사용법

### 기본 에이전트 생성하기

#### 사전 요구사항

```python
# 필요한 모듈 임포트
from module.llm_agent import LLM_Agent

# LLM 에이전트 인스턴스 생성
agent = LLM_Agent(
    model_name="gemini-2.5-flash",  # 사용할 모델명 (예: "gemma:12b", "gpt-4", "gemini-2.5-flash")
    provider="genai",               # LLM 제공자 ("ollama", "openai", "genai")
    api_key="your_api_key",         # API 키 (ollama는 None, 나머지는 필수)
    session_id="chat_session",      # 메모리 기능용 세션 ID (선택사항)
    max_history=10                  # 기억할 대화 수 (선택사항, 기본: 10)
)
```

#### 기본 사용 예제

```python
model_name = 'gemma:12b' # 사용할 모델명을 입력하세요
system_prompt = '당신은 유능한 비서입니다. 이용자에게 도움이 되는 답변을 제공합니다.'
user_prompt = '프랑스의 수도는 어디인가요?'
provider = 'ollama'  # 현재 사용가능한 provider는 "ollama", "openai","genai(gemini)"입니다

agent = LLM_Agent(model_name, provider, api_key=None)

response = agent(system_prompt, user_prompt, task=None)
print(response)
```

**설명:**
- `model_name`: 사용할 모델의 이름을 지정합니다
- `system_prompt`: 모델에게 주어지는 시스템 메시지이므로 역할 및 페르소나를 지정하세요
- `user_prompt`: LLM에게 질문 및 작업을 요청하세요
- `provider`: 사용할 LLM 제공자를 지정합니다
- `task`의 기본값은 None이고 필요시 추가하세요
- `api_key`의 기본값은 None이므로, ollama를 사용할 경우 API 키가 필요하지 않습니다

### 멀티 에이전트 활용하기

#### 기본 멀티 에이전트 설정

```python
# 필요한 모듈 임포트
from module.llm_agent import LLM_Agent

# 멀티 에이전트용 LLM 에이전트 생성
multi_agent = LLM_Agent(
    model_name="gemma3n",           # 사용할 모델명
    provider="ollama"               # LLM 제공자 (ollama/openai/genai)
)

# 첫 번째 에이전트 실행
agent1_response = multi_agent(
    system_prompt="You are a helpful assistant.",
    user_message="리눅스에 대해서 설명해주세요.",
    task=None                       # 추가 작업 내용 (선택사항)
)

# 두 번째 에이전트 실행 (첫 번째 응답 활용)
agent2_response = multi_agent(
    system_prompt="You are a helpful assistant.",
    user_message="앞선 답변을 읽고 내용을 보충해 주세요",
    task=None,
    multi_agent_response=agent1_response  # 이전 에이전트 응답을 전달
)
```

#### 순차적 멀티 에이전트 예제

```python
from module.llm_agent import LLM_Agent

system_prompt = "You are a helpful assistant."
agent1_user_prompt = "리눅스에 대해서 설명해주세요."
agent2_user_prompt = "앞선 답변을 읽고 내용을 보충해 주세요"

# 복수의 에이전트의 프롬프트를 정의합니다.
multi_agent = LLM_Agent(model_name="gemma3n", provider="ollama")
agent1 = multi_agent(system_prompt, agent1_user_prompt, task=None)
agent2 = multi_agent(system_prompt, agent2_user_prompt, task=None, multi_agent_response=agent1)

# agent1의 답변을 이어 받아, agent2의 프롬프트에 포함시킵니다.
print("Agent 1 Response:", agent1)
print("Agent 2 Response:", agent2)
```

**멀티 에이전트 활용 방법:**
- 여러개의 LLM 에이전트를 구성하세요
- 순차적으로 에이전트를 호출하고, 앞의 에이전트의 응답을 다음 에이전트의 프롬프트에 포함시킵니다
- `multi_agent_response` 매개변수를 사용하여 이전 에이전트의 응답을 다음 에이전트에게 전달합니다
- 작업을 분할하고 각 에이전트에 맞게 프롬프트를 조정할 수 있습니다

### 모든 에이전트의 응답 통합하기

#### 고급 멀티 에이전트 시스템

```python
# 필요한 모듈 임포트
from module.llm_agent import LLM_Agent

# 멀티 에이전트 시스템 생성
multi_agent = LLM_Agent(
    model_name="gemini-2.5-flash",  # 사용할 모델명
    provider="genai",               # LLM 제공자
    api_key="your_api_key"          # API 키
)

# 각 에이전트별 역할과 작업 정의
multi_agent_tasks = {
    "Agent 1": "환경 문제 분석 작업",
    "Agent 2": "교통 인프라 계획 작업",
    "Agent 3": "에너지 공급 방안 설계",
    "Agent 4": "도시 공간 구조 최적화"
}

# 각 에이전트 실행 후 응답 수집
agent_responses = {
    name: multi_agent(system_prompt, user_prompt, task)
    for name, task in multi_agent_tasks.items()
}

# 최종 통합 에이전트 실행
final_response = multi_agent(
    "통합 전문가 시스템 프롬프트",
    "모든 전문가 의견을 종합하여 최종 결론을 내려주세요",
    "최종 통합 작업",
    list(agent_responses.values())  # 모든 에이전트 응답을 리스트로 전달
)
```

#### 실제 구현 예제 (도시 계획)

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
response_list = [agent_responses[name] for name in order]  # 각 에이전트의 응답을 순서대로 리스트에 저장합니다.

multi_agent_responses = multi_agent(
    "당신은 도시 계획 전문가입니다. 지속 가능한 도시 설계 방안을 제시하세요.",
    "다음은 여러 전문가의 의견입니다. 이를 바탕으로 최종 요약 및 통합된 지속 가능한 도시 설계 방안을 제시하세요.",
    "최종 요약 및 통합된 지속 가능한 도시 설계 방안을 제시한다.",
    response_list
)  # 모든 에이전트의 응답을 통합하여 최종 응답을 생성합니다.

print("Agent 1 Response:", agent_responses["Agent 1"])
print("Agent 2 Response:", agent_responses["Agent 2"])
print("Agent 3 Response:", agent_responses["Agent 3"])
print("Agent 4 Response:", agent_responses["Agent 4"])
print("Multi-Agent Responses:", multi_agent_responses)
```

**에이전트 통합 방법:**
- 에이전트에게 작업을 각각 할당하고 통합하여 최종 응답을 생성합니다
- 각 에이전트는 특정 작업을 수행하고, 그 응답은 최종 통합 응답을 생성하는 데 사용됩니다
- 에이전트 별로 각각의 작업을 할당하고, 하나로 통합한 답을 생성합니다

### LLM 에이전트에 기억력 붙이기

#### 메모리 기능 설정

```python
# 필요한 모듈 임포트
import dotenv, os
from module.llm_agent import LLM_Agent

# 환경변수 로드
dotenv.load_dotenv()

# 메모리 기능이 있는 LLM 에이전트 생성
llm = LLM_Agent(
    model_name="gemini-2.5-flash",     # 사용할 모델명
    provider="genai",                  # LLM 제공자
    api_key=os.getenv("GENAI_API_KEY"), # API 키 (환경변수에서 불러오기)
    session_id="user_chat_session",    # 대화 세션 구분 ID (선택사항)
    max_history=10                     # 기억할 대화 수 (선택사항, 기본: 10)
)

# 메모리 기능 활성화하여 대화하기
response = llm(
    system_prompt="You are a helpful assistant.",
    user_message="안녕하세요, 제 이름은 김철수입니다.",
    memory=True                        # 메모리 기능 활성화 (중요!)
)

# 다음 대화에서 이전 내용 기억됨
next_response = llm(
    system_prompt="You are a helpful assistant.",
    user_message="제 이름이 뭐라고 했죠?",
    memory=True                        # 이전 대화 기억하여 응답
)
```

#### 연속 대화 예제

```python
import dotenv
import os
dotenv.load_dotenv()

# LLM_Agent 인스턴스 생성
llm = LLM_Agent(
    model_name="gemini-2.5-flash",
    provider="genai",
    api_key=os.getenv("GENAI_API_KEY"),
    max_history=10  # max_history = 기억할 대화 수
)

# 대화 루프 예시
while True:
    user_input = input("You: ")
    response = llm(
        system_prompt="You are a helpful assistant.",
        user_message=user_input,
        memory=True  # memory=True로 설정하여 기억력 활성화
    )
    print("Assistant:", response)

    if user_input.lower() in ['exit', 'quit']:
        break
```

**메모리 기능 활용 방법:**
- LLM 에이전트에 기억력을 추가하여 이전 대화 내용을 기억하고 활용할 수 있습니다
- `max_history=10`으로 설정하여 10개의 이전 대화를 기억합니다
- 메모리 기능은 SQLite 데이터베이스에 대화 기록을 저장하여 연속적인 대화를 가능하게 합니다

---

이 문서는 AI Multi-Agent Toolkit의 주요 기능과 사용법을 다룹니다. 더 자세한 정보는 각 모듈의 소스 코드를 참고하세요.