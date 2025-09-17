import ollama
import google.generativeai as genai
from openai import OpenAI

class LLM_Agent:
    def __init__(self, model_name, provider='ollama', api_key=None):
        self.model_name = model_name
        self.provider = provider.lower()
        self.api_key = api_key
        if self.provider not in ['ollama', 'genai', 'openai']:
            raise ValueError("Provider must be either 'ollama', 'genai' or 'openai'")

    def generate_response(self, system_prompt, user_message, task, multi_agent_response=None):

        if not system_prompt or not user_message:
            raise ValueError("Both system_prompt and user_message must be provided.")
        try:
            if self.provider == 'ollama':
                return self._generate_ollama_response(system_prompt, user_message, task, multi_agent_response)
            elif self.provider == 'genai':
                return self._generate_genai_response(system_prompt, user_message, task, multi_agent_response)
            elif self.provider == 'openai':
                return self._generate_openai_response(system_prompt, user_message, task, multi_agent_response)
            else:
                return "Unsupported provider."
        except Exception as e:
            return f"Error generating response: {e}"

    def _generate_ollama_response(self, system_prompt, user_message, task=None, multi_agent_response=None):
        try:
            # messages 리스트 먼저 구성
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_message}
            ]

            # task가 있으면 추가
            if task:
                messages.append({"role": "user", "content": f' task: {str(task)}'})
            # multi_agent_response가 있으면 추가
            if multi_agent_response:
                messages.append({"role": "user", "content": f' 다른 에이전트의 응답: {str(multi_agent_response)}'})
            # 한 번만 호출
            response = ollama.chat(model=self.model_name, messages=messages)
            return response["message"]["content"]
        except Exception as e:
            return f"Error generating response with Ollama: {e}"


    def _generate_genai_response(self, system_prompt, user_message, task, multi_agent_response=None):
        try:
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name)

            # 모든 내용을 하나의 문자열로 결합
            combined_prompt = system_prompt
            if user_message:
                combined_prompt += f"\n\n{user_message}"
            if task:
                combined_prompt += f"\n\n작업: {task}"
            if multi_agent_response:
                combined_prompt += f"\n\n다른 에이전트의 응답: {str(multi_agent_response)}"

            # 문자열 하나만 전달!
            response = model.generate_content(combined_prompt)
            return response.text
        except Exception as e:
            return f"Error generating response with GenAI: {e}"

    def _generate_openai_response(self, system_prompt, user_message, task, multi_agent_response=None):
      try:
          client = OpenAI(api_key=self.api_key)

          # messages 리스트 구성 (Ollama와 유사한 방식)
          messages = [
              {"role": "system", "content": system_prompt},
              {"role": "user", "content": user_message}
          ]

          # task가 있으면 추가
          if task:
              messages.append({"role": "user", "content": f' task: {str(task)}'})

          # multi_agent_response가 있으면 추가
          if multi_agent_response:
              messages.append({"role": "user", "content": f' 다른 에이전트의 응답: {str(multi_agent_response)}'})

          response = client.chat.completions.create(
              model=self.model_name,
              messages=messages
          )

          return response.choices[0].message.content

      except Exception as e:
          return f"Error generating response with OpenAI: {e}"
      


    def multi_agent_interaction(self, system_prompt, user_message, task=None, responses=None):
        # 다른 에이전트의 응답을 수집
        messages = [{"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}]
        for idx, resp in enumerate(responses):
            messages.append({"role": "user", "content": f"Agent {idx+1} response: {resp}"})

        # 최종 메시지를 생성
        final_response = self.generate_response(system_prompt, user_message, task, multi_agent_response=messages)
        print("Final Response:", final_response)
        return final_response
    

# 예시 사용법

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

multi_agent = LLM_Agent(model_name="gemini-2.5-flash", provider="genai", api_key=os.getenv("GENAI_API_KEY"))

agent_responses = {
    name: multi_agent.generate_response(multi_agent_system_prompts[name], user_prompts[name], multi_agent_tasks[name])
    for name in order
}
response_list = [agent_responses[name] for name in order]

multi_agent_responses = multi_agent.multi_agent_interaction(
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