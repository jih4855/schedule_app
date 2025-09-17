# agent_ai (AudioStudy)

간단한 LLM 에이전트부터 STT, Discord 전송까지 빠르게 실험하고 공유할 수 있는 실용 예제 모음입니다. 멀티 에이전트(Scatter–Gather) 패턴과 메시지 집계를 지원하며, 다크 테마 문서와 사이드바 내비게이션을 제공합니다.

## 주요 기능
- LLM 에이전트 (ollama, openai, genai(Gemini) 지원)
- 멀티 에이전트 순차 호출 및 응답 집계
- Discord 웹훅 전송 (긴 메시지 청크/겹침 지원)
- 음성 → 텍스트(Whisper) 파이프라인
- 다크 테마 문서, 자동 사이드바(H3 + details 인덱싱)

## 요구 사항
- Python 3.10+
- 선택적 런타임: ffmpeg (yt-dlp 사용 시)

## 설치
```bash
# 가상환경 생성/활성화 (예: macOS zsh)
python3 -m venv venv
source venv/bin/activate

# 필수 패키지 설치
pip install -r requirements.txt
```

## 환경 변수
- OPENAI_API_KEY (OpenAI 사용 시)
- GOOGLE_API_KEY (Gemini 사용 시)
- DISCORD_WEBHOOK_URL (Discord 전송 예제)

`.env` 사용 시 module들이 자동 로드하도록 설계되어 있습니다.

# agent_ai (문서 중심 요약)

간단한 목적: LLM 에이전트 실행, 멀티에이전트 집계, Discord 전송, 음성→텍스트를 빠르게 실습하는 예제입니다. 자세한 안내는 `docs/index.html` 참고.

## 설치
order = ["Agent 1", "Agent 2", "Agent 3", "Agent 4"]
user_prompts = {
    "Agent 1": "환경 문제를 정리하고 시급 과제 제시",
    "Agent 2": "친환경 교통 인프라 제안",
    "Agent 3": "재생에너지 공급 방안 설계",
    "Agent 4": "도시 공간 최적화 방안",
}
systems = {
    "Agent 1": "환경 전문가",
    "Agent 2": "교통 전문가",
    "Agent 3": "에너지 전문가",
    "Agent 4": "도시 계획 전문가",
}

llm = LLM_Agent(model_name="gemini-2.5-flash", provider="genai", api_key="YOUR_KEY")
agent_responses = {n: llm.generate_response(systems[n], user_prompts[n], task=None) for n in order}
resp_list = [agent_responses[n] for n in order]
final = llm.aggregate_responses(
    "당신은 도시 계획 전문가입니다.",
    "아래 의견을 통합해서 최종 요약을 작성하세요.",
    "최종 요약 및 통합안 작성",
    resp_list,
)
print(final)
```

## Discord 전송 예시
```python
from module.discord import Send_to_discord
from module.llm_agent import LLM_Agent

a = LLM_Agent(model_name="gemma3:12b", provider="ollama")
resp = a.generate_response("도움이 되는 비서", "프랑스의 수도?")

bot = Send_to_discord(base_url="YOUR_WEBHOOK_URL", chunk_size=1900)
bot.send_message(resp)
```

## 음성 → 텍스트 예시
- yt-dlp로 다운로드 후 whisper로 변환.
- ffmpeg가 필요합니다.


- 네비바는 sticky, 사이드바는 네비바 아래로 오프셋되어 겹침이 없습니다.
