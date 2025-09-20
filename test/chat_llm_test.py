
#모듈 경로 설정
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.llm_agent import LLM_Agent



import dotenv
import os
dotenv.load_dotenv()

# LLM_Agent 인스턴스 생성
llm = LLM_Agent(model_name="gemini-2.5-flash", provider="genai", api_key=os.getenv("GENAI_API_KEY"), session_id="test_memory", max_history=10)

# 대화 루프 예시
while True:
    user_input = input("You: ")
    response = llm(system_prompt="You are a helpful assistant.", user_message=user_input, memory=True)
    print("Assistant:", response)

    if user_input.lower() in ['exit', 'quit']:
        break