import os
import sys
import logging
from typing import Dict, Any, Optional, List
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware

# 프로젝트의 실제 모듈들을 임포트
from module.audio_tool import Audio
from module.llm_agent import LLM_Agent, Multi_modal_agent
from module.discord import Send_to_discord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Multi-Agent Toolkit API",
    description="워크플로우 기반의 멀티모달 AI 에이전트 오케스트레이션 시스템",
    version="2.0.0"
)

# CORS 설정 (필요에 따라 조정)
origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic 모델 정의

class WorkflowStep(BaseModel):
    step: int = Field(..., description="실행 순서")
    module: str = Field(..., description="실행할 모듈 이름")
    action: str = Field(..., description="실행할 메서드 이름")
    params: Dict[str, Any] = Field(default_factory=dict, description="메서드에 전달할 파라미터")
    init_params : Dict[str, Any] = Field(default_factory=dict, description="모듈 초기화 파라미터")

class WorkflowResponse(BaseModel):
    status: str
    step_outputs: Dict[int, Any] = {}
    final_result: Any = None
    error_message: Optional[str] = None

class WorkflowRequest(BaseModel):
    workflow: List[WorkflowStep] = Field(..., description="실행할 워크플로우 단계 리스트")


# === 워크플로우 오케스트레이터 클래스 ===
class WorkflowOrchestrator:
    def __init__(self, workflow: List[WorkflowStep]):
        self.steps = sorted(workflow, key=lambda x: x.step)
        self.step_outputs = {}

        self.module_map = {
            "LLM_Agent": LLM_Agent,
            "Multi_modal_agent": Multi_modal_agent,
            "Audio": Audio,
            "Send_to_discord": Send_to_discord,
        }

    def execute(self) -> Dict:
        """워크플로우 단계들을 순차적으로 실행"""
        try:
            for step in self.steps:
                logger.info(f'---단계 {step.step} 실행: {step.module}.{step.action}---')

                resolved_params = self._resolve_params(step.params)
                
                #1. 모듈 클래스 찾기
                module_class = self.module_map.get(step.module)
                if not module_class:
                    raise ValueError(f'모듈 "{step.module}"을 찾을 수 없습니다. 사용 가능한 모듈: {list(self.module_map.keys())}')
                

                #2. 모듈 인스턴스 생성(초기화 파라미터 포함)

                try:
                    if step.init_params:
                        module_instance = module_class(**step.init_params)
                    else:
                        if step.module == "LLM_Agent":
                            module_instance = module_class(model_name="gemma3n", provider = "ollama")
                        elif step.module == "Multi_modal_agent":
                            module_instance = module_class(model_name="gemma3:4b", provider="ollama")
                        elif step.module == "Discord":
                            raise ValueError(f"Discord 모듈은 base_url이 필수입니다. init_params에 base_url을 설정하세요.")
                        else:
                            module_instance = module_class()
                except TypeError as e:
                    logger.error(f'모듈 "{step.module}" 초기화에 실패했습니다: {e}')
                    if step.module =="LLM_Agent":
                        module_instance = module_class(model_name="gemma3n", provider="ollama")
                    elif step.module == "Multi_modal_agent":
                        module_instance = module_class(model_name="gemma3:4b", provider="ollama")
                    else:
                        raise ValueError(f'모듈 "{step.module}" 초기화에 필요한 파라미터가 누락되었습니다: {e}')

                #3. 모듈 액션 메서드 찾기
                action_method = getattr(module_instance, step.action, None)
                if not action_method:
                    available_methods = [method for method in dir(module_instance)
                                         if not method.startswith('_') and callable(getattr(module_instance, method))]
                    raise ValueError(f"액션 '{step.action}'을 모듈 '{step.module}'에서 찾을 수 없습니다. "
                                f"사용 가능한 메서드: {available_methods}")
                
                # 4. 메서드 실행
                if resolved_params:
                    output = action_method(**resolved_params)
                else:
                    output = action_method()

                # 5. 결과 저장
                self.step_outputs[step.step] = output
                logger.info(f"단계 {step.step} 완료. 출력: {str(output)[:100]}...")

            return {
                "status": "success",
                "step_outputs": self.step_outputs,
                "final_result": self.step_outputs.get(len(self.steps)) if self.steps else None
            }

        except Exception as e:
            logger.error(f"워크플로우 실행 중 오류 발생: {e}")
            return {
                "status": "error",
                "error_message": str(e),
                "step_outputs": self.step_outputs
            }

    def _resolve_params(self, params: Dict) -> Dict:
        """파라미터에서 이전 단계 참조를 실제 값으로 교체"""
        resolved = {}
        for key, value in params.items():
            if isinstance(value, str) and value.startswith("step_output_"):
                try:
                    # "step_output_1" -> 1
                    source_step_num = int(value.split('_')[-1])
                    if source_step_num in self.step_outputs:
                        resolved[key] = self.step_outputs[source_step_num]
                    else:
                        raise ValueError(f"단계 {source_step_num}의 출력을 찾을 수 없습니다.")
                except (ValueError, IndexError):
                    logger.warning(f"잘못된 참조 형식: {value}. 원본 값을 사용합니다.")
                    resolved[key] = value
            else:
                resolved[key] = value
        return resolved

# === API 엔드포인트 ===

@app.get("/")
def read_root():
    return {
        "message": "🚀 AI Multi-Agent Toolkit - 워크플로우 오케스트레이션 API에 오신 것을 환영합니다!",
        "version": "2.0.0",
        "features": [
            "워크플로우 기반 멀티모달 AI 파이프라인",
            "동적 모듈 오케스트레이션",
            "단계별 결과 연결",
            "확장 가능한 모듈 아키텍처"
        ],
        "endpoints": {
            "/execute_workflow": "워크플로우 실행",
            "/docs": "API 문서",
            "/modules": "사용 가능한 모듈 목록"
        }
    }

@app.get("/modules")
def get_available_modules():
    """사용 가능한 모듈과 메서드 목록을 반환"""
    modules_info = {}

    # 임시 인스턴스를 만들어서 사용 가능한 메서드 추출
    module_map = {
        "Audio": Audio,
        "LLM_Agent": LLM_Agent,
        "Multi_modal_agent": Multi_modal_agent,
        "Discord": Send_to_discord,
    }

    for module_name, module_class in module_map.items():
        try:
            instance = module_class()
            methods = [method for method in dir(instance)
                      if not method.startswith('_') and callable(getattr(instance, method))]
            modules_info[module_name] = {
                "description": instance.__class__.__doc__ or f"{module_name} 모듈",
                "methods": methods
            }
        except Exception as e:
            modules_info[module_name] = {
                "description": f"{module_name} 모듈 (초기화 파라미터 필요할 수 있음)",
                "error": str(e)
            }

    return {"available_modules": modules_info}


@app.post("/execute_workflow", response_model=WorkflowResponse)
def execute_workflow_endpoint(request: WorkflowRequest):
    """
    🎯 메인 워크플로우 실행 엔드포인트

    JSON으로 정의된 워크플로우를 순차적으로 실행하고 결과를 반환합니다.

    예시 워크플로우:
    ```json
    {
        "workflow": [
            {
                "step": 1,
                "module": "LLM_Agent",
                "action": "__call__",
                "init_params": {"model_name": "gemma3n", "provider": "ollama"},
                "params": {
                    "system_prompt": "당신은 도움이 되는 AI 어시스턴트입니다.",
                    "user_message": "안녕하세요!"
                }
            }
        ]
    }
    ```
    """
    if not request.workflow:
        raise HTTPException(status_code=400, detail="워크플로우가 비어있습니다.")

    try:
        # 워크플로우 오케스트레이터 생성 및 실행
        orchestrator = WorkflowOrchestrator(request.workflow)
        result = orchestrator.execute()

        return WorkflowResponse(**result)

    except Exception as e:
        logger.error(f"워크플로우 실행 실패: {e}")
        raise HTTPException(status_code=500, detail=f"워크플로우 실행 중 오류가 발생했습니다: {str(e)}")