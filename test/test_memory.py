
# #모듈 경로 설정
# import sys
# import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# from module.llm_agent import LLM_Agent



# llm=LLM_Agent(model_name = "gemma3n", provider='ollama', api_key=None, session_id="test1", max_history=10)
# response=llm(system_prompt="You are a helpful assistant.", user_message="안녕?", memory=True) #memory=True로 설정하여 기억력 활성화
# print(response)
# print(type(response))

# response=llm(system_prompt="You are a helpful assistant.", user_message="우리 대화내역 알려줘", memory=True) #memory=True로 설정하여 기억력 활성화

# print(response)
# print(type(response))



# from module.llm_agent import LLM_Agent

# system_prompt = "You are a helpful assistant."
# agent1_user_prompt = "리눅스에 대해서 설명해주세요."
# agent2_user_prompt = "앞선 답변을 읽고 내용을 보충해 주세요"
# #복수의 에이전트의 프롬프트를 정의합니다.
# multi_agent = LLM_Agent(model_name="gemma3n", provider="ollama")
# agent1 = multi_agent(system_prompt, agent1_user_prompt, task=None)
# agent2 = multi_agent(system_prompt, agent2_user_prompt, task=None, multi_agent_response=agent1)#agent1의 답변을 이어 받아, agent2의 프롬프트에 포함시킵니다.
# print("Agent 1 Response:", agent1)
# print("Agent 2 Response:", agent2)


import os
import sys
# Ensure module import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.discord import Send_to_discord
from module.llm_agent import LLM_Agent
            
model_name = 'gemma3:12b' #사용할 모델명을 입력하세요
system_prompt = '당신은 유능한 비서입니다. 이용자에게 도움이 되는 답변을 제공합니다.'
user_prompt = '프랑스의 수도는 어디인가요?'
provider = 'ollama'  #현재 사용가능한 provier는 "ollama", "openai","genai(gemini)"입니다

agent = LLM_Agent(model_name, provider, api_key=None)
response = agent(system_prompt, user_prompt, task=None)

discord = Send_to_discord(base_url="your_discord_webhook_url") #청크 사이즈 및 겹침 크기 설정
discord.send_message(response)
        