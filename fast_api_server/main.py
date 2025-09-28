# main.py
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from module.llm_agent import LLM_Agent
from pydantic import BaseModel

# 이 변수 이름이 반드시 'app' 이어야 합니다!
app = FastAPI() 

# ⭐️ 2. 허용할 출처 목록을 만듭니다. (개발 중에는 "*"로 모든 주소를 허용)
origins = [
    "http://localhost:3000",  # CRA 기본 포트
    "http://localhost:3001",  # 포트 충돌 시 대체
    "http://localhost:3002",  # 또 다른 대체 포트
    # "https://my-cool-app.com"  # 배포 주소 (추후 활성화)
]

# ⭐️ 3. 앱에 CORS 미들웨어를 추가합니다. (이 코드는 반드시 @app.post 보다 위에 있어야 합니다!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins, # 위에서 정의한 출처 목록
    allow_credentials=True,
    allow_methods=["*"], # 모든 HTTP 메소드 허용
    allow_headers=["*"], # 모든 HTTP 헤더 허용
)


@app.get("/")
def read_root():
    return {"message": "AI Toolkit API에 오신 것을 환영합니다!"}

# ... (이하 생략) ...

class LLM_loader(BaseModel):
    system_prompt: str
    user_message: str
# 3. LLM 에이전트를 호출할 '문'을 만듭니다.
@app.post("/generate")
def generate_text(llm_loader: LLM_loader):
    # 이미 완벽하게 만들어두신 LLM_Agent를 그대로 사용합니다.
    agent = LLM_Agent(model_name="gemma3n", provider="ollama")
    response = agent(system_prompt=llm_loader.system_prompt, user_message=llm_loader.user_message)
    return {"response": response}


class multiAgent_loader(BaseModel):
    system_prompt: str
    user_message: str
    task: str
    agents: list[dict]  # 동적 에이전트 리스트로 변경

@app.post("/multi_agent")
def multi_agent_text(multi_agent_loader: multiAgent_loader):
    agent = LLM_Agent(model_name="gemma3n", provider="ollama")

    # 동적 에이전트 처리
    agent_responses = []  # 순서 유지 리스트 [{name, response}]
    response_list = []    # 최종 집계용 순수 문자열 리스트

    for i, agent_data in enumerate(multi_agent_loader.agents):
        if agent_data.get('name') and agent_data.get('role') and agent_data.get('task'):
            response = agent(
                system_prompt=agent_data['role'],
                user_message=multi_agent_loader.user_message,
                task=agent_data['task']
            )
            agent_responses.append({"name": agent_data['name'], "response": response})
            response_list.append(response)

    # 마스터 AI가 모든 에이전트 응답을 종합 (존재하지 않는 multi_agent_interaction 대신 aggregate_responses 사용)
    final_response = agent.aggregate_responses(
        system_prompt=multi_agent_loader.system_prompt,
        user_message=multi_agent_loader.user_message,
        task=multi_agent_loader.task,
        responses=response_list
    )

    # 응답 포맷을 /run_dynamic_multi_agent 와 동일한 구조로 통일
    return {
        "individual_responses": agent_responses,  # [{name, response}, ...]
        "final_response": final_response,
        "count": len(agent_responses)
    }

# fastapi_server/main.py

from typing import List # ⭐️ 1. Python의 List 타입을 가져옵니다.
from pydantic import BaseModel
# ... (기존 import 및 app 설정은 동일)

# ⭐️ 2. 개별 에이전트 1명의 '설계도'를 만듭니다.
class AgentConfig(BaseModel):
    name: str
    role: str
    task: str

# ⭐️ 3. 메인 요청의 '설계도'를 수정합니다.
class DynamicMultiAgentRequest(BaseModel):
    system_prompt: str
    user_message: str
    task: str
    agents: List[AgentConfig] # <- 이제 에이전트 설정을 '리스트'로 받습니다!

# ⭐️ 4. 새로운 동적 API 엔드포인트를 만듭니다.
@app.post("/run_dynamic_multi_agent")
def run_dynamic_multi_agent(request: DynamicMultiAgentRequest):
    agent_runner = LLM_Agent(model_name="gemma3n", provider="ollama")
    agent_responses = []  # [{name, response}]
    response_list = []

    # ⭐️ 5. 리스트로 받은 에이전트들을 반복문으로 처리합니다!
    for agent_config in request.agents:
        response = agent_runner(
            system_prompt=agent_config.role,
            user_message=request.user_message,
            task=agent_config.task
        )
        agent_responses.append({"name": agent_config.name, "response": response})
        response_list.append(response)
    
    # 최종 종합 에이전트 실행
    final_response = agent_runner.aggregate_responses(
        system_prompt=request.system_prompt,
        user_message=request.user_message,
        task=request.task,
        responses=response_list
    )

    # 프론트엔드에 결과를 돌려줍니다.
    return {
        "individual_responses": agent_responses,
        "final_response": final_response,
        "count": len(agent_responses)
    }