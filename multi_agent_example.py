from module.llm_agent import LLM_Agent

#각 에이전트의 시스템 프롬프트, 사용자 프롬프트, 작업을 정의합니다.
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
user_prompts ={
    "Agent 1": "도시에서 발생하는 환경 문제를 분석하고, 가장 시급한 문제를 제시하세요.",
    "Agent 2": "지속 가능한 교통 인프라 계획을 제안하세요.",
    "Agent 3": "재생에너지를 활용한 에너지 공급 방안을 설계하세요.",
    "Agent 4": "도시 공간 구조를 최적화하는 방안을 제시하세요."
}


order = ["Agent 1", "Agent 2", "Agent 3", "Agent 4"]

import dotenv
import os
dotenv.load_dotenv()

multi_agent = LLM_Agent(model_name="gemma3:1b", provider="ollama") #기본 파라미터는 다음과 같습니다. model, provider 필수로 입력, 나머지는 필요시 활성화 model_name:str, provider:str='ollama', api_key:str=None, session_id:str ="default_session", max_history:int =10

agent_responses = {
    name: multi_agent(multi_agent_system_prompts[name], user_prompts[name], multi_agent_tasks[name])
    for name in order
} #각 에이전트의 응답을 생성합니다.
response_list = [agent_responses[name] for name in order] #각 에이전트의 응답을 순서대로 리스트에 저장합니다.

multi_agent_responses = multi_agent(
    "당신은 도시 계획 전문가입니다. 지속 가능한 도시 설계 방안을 제시하세요.",
    "다음은 여러 전문가의 의견입니다. 이를 바탕으로 최종 요약 및 통합된 지속 가능한 도시 설계 방안을 제시하세요.",
    "최종 요약 및 통합된 지속 가능한 도시 설계 방안을 제시한다.",
    response_list
) #모든 에이전트의 응답을 통합하여 최종 응답을 생성합니다.

# 결과 출력
print("Agent 1 Response:", agent_responses["Agent 1"])
print("Agent 2 Response:", agent_responses["Agent 2"])
print("Agent 3 Response:", agent_responses["Agent 3"])
print("Agent 4 Response:", agent_responses["Agent 4"])
print("Multi-Agent Responses:", multi_agent_responses)