
#모듈 경로 설정
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.llm_agent import LLM_Agent



llm=LLM_Agent(model_name = "gemma3n", provider='ollama', api_key=None, session_id="test1", max_history=10)
response=llm.generate_response(system_prompt="You are a helpful assistant.", user_message="님 이름이 머임?", memory=False)
print(response)
print(type(response))