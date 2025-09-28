import os
import sys
import logging
from typing import List, Dict, Any, Optional

# 프로젝트 모듈 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# 프로젝트의 실제 모듈들을 임포트
from module.audio_tool import Audio
from module.llm_agent import LLM_Agent, Multi_modal_agent
from module.discord import Send_to_discord

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Multi-Agent Toolkit API",
    description="워크플로우 기반의 멀티모달 AI 에이전트 오케스트레이션 시스템",
    version="2.0.0"
)

# CORS 설정
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

# === Pydantic 모델 정의 ===

class WorkflowStep(BaseModel):
    step: int = Field(..., description="실행 순서")
    module: str = Field(..., description="실행할 모듈 이름 (Audio, LLM_Agent, Multi_modal_agent, Discord)")
    action: str = Field(..., description="실행할 메서드 이름")
    params: Dict[str, Any] = Field(default_factory=dict, description="메서드에 전달할 파라미터")
    init_params: Dict[str, Any] = Field(default_factory=dict, description="모듈 초기화 파라미터")

class WorkflowRequest(BaseModel):
    workflow: List[WorkflowStep] = Field(..., description="실행할 워크플로우 단계들")

class WorkflowResponse(BaseModel):
    status: str
    step_outputs: Dict[int, Any] = {}
    final_result: Any = None
    error_message: Optional[str] = None

# === 워크플로우 오케스트레이터 클래스 ===

class WorkflowOrchestrator:
    def __init__(self, workflow_steps: List[WorkflowStep]):
        self.steps = sorted(workflow_steps, key=lambda x: x.step)
        self.step_outputs = {}

        # 🔥 핵심! 문자열 모듈명을 실제 클래스로 매핑하는 딕셔너리
        self.module_map = {
            "Audio": Audio,
            "LLM_Agent": LLM_Agent,
            "Multi_modal_agent": Multi_modal_agent,
            "Discord": Send_to_discord,
        }

    def execute(self) -> Dict:
        """워크플로우를 순차적으로 실행하고 결과를 반환"""
        try:
            for step in self.steps:
                logger.info(f"--- 단계 {step.step} 실행: {step.module}.{step.action} ---")

                # 이전 단계 출력을 참조하는 파라미터들을 실제 값으로 교체
                resolved_params = self._resolve_params(step.params)

                # 1. 모듈 클래스 찾기
                module_class = self.module_map.get(step.module)
                if not module_class:
                    raise ValueError(f"모듈 '{step.module}'을 찾을 수 없습니다. 사용 가능한 모듈: {list(self.module_map.keys())}")

                # 2. 모듈 인스턴스 생성 (초기화 파라미터 포함)
                try:
                    if step.init_params:
                        module_instance = module_class(**step.init_params)
                    else:
                        module_instance = module_class()
                except TypeError as e:
                    logger.error(f"모듈 {step.module} 초기화 실패: {e}")
                    # 파라미터 없이 재시도
                    module_instance = module_class()

                # 3. 메서드 찾기 및 실행
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

@app.get("/examples")
def get_workflow_examples():
    """워크플로우 사용 예제들을 반환"""
    return {
        "workflow_examples": {
            "simple_llm": {
                "name": "기본 LLM 호출",
                "description": "단일 LLM 에이전트 호출 예제",
                "workflow": {
                    "workflow": [
                        {
                            "step": 1,
                            "module": "LLM_Agent",
                            "action": "__call__",
                            "init_params": {"model_name": "gemma3n", "provider": "ollama"},
                            "params": {
                                "system_prompt": "당신은 도움이 되는 AI 어시스턴트입니다.",
                                "user_message": "파이썬에서 리스트와 튜플의 차이점을 설명해주세요."
                            }
                        }
                    ]
                }
            },
            "multi_agent_discussion": {
                "name": "멀티 에이전트 토론",
                "description": "여러 전문가 에이전트가 토론하고 최종 결론을 도출",
                "workflow": {
                    "workflow": [
                        {
                            "step": 1,
                            "module": "LLM_Agent",
                            "action": "__call__",
                            "init_params": {"model_name": "gemma3n", "provider": "ollama"},
                            "params": {
                                "system_prompt": "당신은 데이터 사이언티스트입니다.",
                                "user_message": "머신러닝과 딥러닝의 차이점은 무엇인가요?",
                                "task": "데이터 사이언스 관점에서 설명하세요."
                            }
                        },
                        {
                            "step": 2,
                            "module": "LLM_Agent",
                            "action": "__call__",
                            "init_params": {"model_name": "gemma3n", "provider": "ollama"},
                            "params": {
                                "system_prompt": "당신은 소프트웨어 엔지니어입니다.",
                                "user_message": "머신러닝과 딥러닝의 차이점은 무엇인가요?",
                                "task": "구현 관점에서 설명하세요."
                            }
                        },
                        {
                            "step": 3,
                            "module": "LLM_Agent",
                            "action": "aggregate_responses",
                            "init_params": {"model_name": "gemma3n", "provider": "ollama"},
                            "params": {
                                "system_prompt": "당신은 종합 분석 전문가입니다.",
                                "user_message": "머신러닝과 딥러닝의 차이점은 무엇인가요?",
                                "task": "전문가들의 의견을 종합하여 완전한 답변을 제공하세요.",
                                "responses": ["step_output_1", "step_output_2"]
                            }
                        }
                    ]
                }
            },
            "audio_to_text_analysis": {
                "name": "오디오 → 텍스트 → 분석 파이프라인",
                "description": "음성 파일을 텍스트로 변환하고 LLM으로 분석",
                "workflow": {
                    "workflow": [
                        {
                            "step": 1,
                            "module": "Audio",
                            "action": "transcribe_audio",
                            "init_params": {"text_output": "output", "source_file": "audio_files"},
                            "params": {
                                "whisper_model": "base"
                            }
                        },
                        {
                            "step": 2,
                            "module": "LLM_Agent",
                            "action": "__call__",
                            "init_params": {"model_name": "gemma3n", "provider": "ollama"},
                            "params": {
                                "system_prompt": "당신은 텍스트 분석 전문가입니다.",
                                "user_message": "step_output_1",
                                "task": "이 텍스트의 주요 내용과 감정을 분석해주세요."
                            }
                        }
                    ]
                }
            },
            "analysis_to_discord": {
                "name": "분석 결과를 Discord로 전송",
                "description": "LLM 분석 결과를 Discord 채널로 전송",
                "workflow": {
                    "workflow": [
                        {
                            "step": 1,
                            "module": "LLM_Agent",
                            "action": "__call__",
                            "init_params": {"model_name": "gemma3n", "provider": "ollama"},
                            "params": {
                                "system_prompt": "당신은 시장 분석 전문가입니다.",
                                "user_message": "오늘의 AI 기술 동향을 분석해주세요."
                            }
                        },
                        {
                            "step": 2,
                            "module": "Discord",
                            "action": "send_message",
                            "init_params": {"base_url": "YOUR_DISCORD_WEBHOOK_URL"},
                            "params": {
                                "message": "step_output_1"
                            }
                        }
                    ]
                }
            },
            "multimodal_workflow": {
                "name": "복합 멀티모달 워크플로우",
                "description": "오디오 → 텍스트 → 멀티에이전트 분석 → Discord 전송",
                "workflow": {
                    "workflow": [
                        {
                            "step": 1,
                            "module": "Audio",
                            "action": "transcribe_audio",
                            "init_params": {"text_output": "transcripts", "source_file": "meeting_audio"},
                            "params": {"whisper_model": "large-v3"}
                        },
                        {
                            "step": 2,
                            "module": "LLM_Agent",
                            "action": "__call__",
                            "init_params": {"model_name": "gemma3n", "provider": "ollama"},
                            "params": {
                                "system_prompt": "당신은 회의록 작성 전문가입니다.",
                                "user_message": "step_output_1",
                                "task": "이 회의 내용을 요약하고 주요 결정사항을 추출하세요."
                            }
                        },
                        {
                            "step": 3,
                            "module": "LLM_Agent",
                            "action": "__call__",
                            "init_params": {"model_name": "gemma3n", "provider": "ollama"},
                            "params": {
                                "system_prompt": "당신은 액션 아이템 추출 전문가입니다.",
                                "user_message": "step_output_1",
                                "task": "다음 단계로 해야 할 일들을 정리하세요."
                            }
                        },
                        {
                            "step": 4,
                            "module": "Discord",
                            "action": "send_message",
                            "init_params": {"base_url": "YOUR_DISCORD_WEBHOOK_URL"},
                            "params": {
                                "message": "📝 회의 요약:\n\nstep_output_2\n\n✅ 액션 아이템:\n\nstep_output_3"
                            }
                        }
                    ]
                }
            }
        },
        "usage_tips": [
            "워크플로우는 step 순서대로 실행됩니다.",
            "step_output_N을 사용해 이전 단계의 결과를 참조할 수 있습니다.",
            "init_params로 각 모듈의 초기화 설정을 지정합니다.",
            "params로 메서드에 전달할 파라미터를 설정합니다.",
            "/modules 엔드포인트에서 사용 가능한 모듈과 메서드를 확인할 수 있습니다."
        ]
    }

@app.get("/workflow-builder")
def get_workflow_builder_config():
    """웹 인터페이스용 워크플로우 빌더 설정을 반환"""
    return {
        "modules": {
            "Audio": {
                "name": "오디오 처리",
                "description": "음성 파일을 텍스트로 변환",
                "init_params": {
                    "text_output": {
                        "type": "string",
                        "description": "텍스트 출력 폴더명",
                        "default": "transcripts",
                        "required": False
                    },
                    "source_file": {
                        "type": "string",
                        "description": "오디오 파일이 있는 폴더명",
                        "default": "audio_files",
                        "required": False
                    }
                },
                "actions": {
                    "transcribe_audio": {
                        "name": "음성을 텍스트로 변환",
                        "params": {
                            "whisper_model": {
                                "type": "select",
                                "options": ["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
                                "default": "base",
                                "description": "Whisper 모델 크기 (클수록 정확하지만 느림)"
                            },
                            "audio_extensions": {
                                "type": "multiselect",
                                "options": ["mp3", "wav", "m4a", "flac", "aac", "ogg"],
                                "default": ["mp3", "wav", "m4a"],
                                "description": "처리할 오디오 파일 확장자"
                            }
                        }
                    }
                }
            },
            "LLM_Agent": {
                "name": "LLM 에이전트",
                "description": "다양한 LLM 모델로 텍스트 생성",
                "init_params": {
                    "model_name": {
                        "type": "string",
                        "description": "사용할 모델명",
                        "default": "gemma3n",
                        "required": True
                    },
                    "provider": {
                        "type": "select",
                        "options": ["ollama", "openai", "genai"],
                        "default": "ollama",
                        "description": "LLM 제공업체"
                    },
                    "api_key": {
                        "type": "password",
                        "description": "API 키 (OpenAI, Google AI 사용시 필요)",
                        "required": False
                    },
                    "session_id": {
                        "type": "string",
                        "description": "세션 ID (메모리 기능용)",
                        "default": "default_session",
                        "required": False
                    }
                },
                "actions": {
                    "__call__": {
                        "name": "텍스트 생성",
                        "params": {
                            "system_prompt": {
                                "type": "textarea",
                                "description": "시스템 프롬프트 (AI의 역할 정의)",
                                "required": True,
                                "placeholder": "당신은 도움이 되는 AI 어시스턴트입니다."
                            },
                            "user_message": {
                                "type": "textarea",
                                "description": "사용자 메시지 또는 이전 단계 결과 참조",
                                "required": True,
                                "placeholder": "질문을 입력하거나 step_output_1 같은 참조를 사용하세요"
                            },
                            "task": {
                                "type": "textarea",
                                "description": "구체적인 작업 설명 (선택사항)",
                                "required": False,
                                "placeholder": "예: 이 텍스트를 요약해주세요"
                            },
                            "memory": {
                                "type": "checkbox",
                                "description": "대화 기록 저장",
                                "default": False
                            }
                        }
                    },
                    "aggregate_responses": {
                        "name": "응답 종합",
                        "params": {
                            "system_prompt": {
                                "type": "textarea",
                                "description": "종합 분석을 위한 시스템 프롬프트",
                                "required": True,
                                "placeholder": "당신은 종합 분석 전문가입니다."
                            },
                            "user_message": {
                                "type": "textarea",
                                "description": "원래 질문",
                                "required": True
                            },
                            "task": {
                                "type": "textarea",
                                "description": "종합 분석 작업",
                                "required": True,
                                "placeholder": "전문가들의 의견을 종합하여 완전한 답변을 제공하세요"
                            },
                            "responses": {
                                "type": "array",
                                "description": "종합할 이전 단계들 (예: [\"step_output_1\", \"step_output_2\"])",
                                "required": True,
                                "placeholder": "[\"step_output_1\", \"step_output_2\"]"
                            }
                        }
                    }
                }
            },
            "Multi_modal_agent": {
                "name": "멀티모달 에이전트",
                "description": "이미지와 텍스트를 함께 처리",
                "init_params": {
                    "model_name": {
                        "type": "string",
                        "description": "멀티모달 모델명",
                        "default": "llava",
                        "required": True
                    },
                    "provider": {
                        "type": "select",
                        "options": ["ollama", "openai"],
                        "default": "ollama",
                        "description": "제공업체"
                    }
                },
                "actions": {
                    "__call__": {
                        "name": "멀티모달 분석",
                        "params": {
                            "system_prompt": {
                                "type": "textarea",
                                "description": "시스템 프롬프트",
                                "required": True
                            },
                            "user_message": {
                                "type": "textarea",
                                "description": "사용자 메시지",
                                "required": True
                            },
                            "image_path": {
                                "type": "string",
                                "description": "이미지 파일 경로",
                                "required": False
                            }
                        }
                    }
                }
            },
            "Discord": {
                "name": "Discord 전송",
                "description": "Discord 채널로 메시지 전송",
                "init_params": {
                    "base_url": {
                        "type": "url",
                        "description": "Discord 웹훅 URL",
                        "required": True,
                        "placeholder": "https://discord.com/api/webhooks/..."
                    },
                    "chunk_size": {
                        "type": "number",
                        "description": "메시지 분할 크기",
                        "default": 1900,
                        "min": 100,
                        "max": 2000
                    },
                    "overlap": {
                        "type": "number",
                        "description": "분할시 겹치는 글자 수",
                        "default": 0,
                        "min": 0,
                        "max": 200
                    }
                },
                "actions": {
                    "send_message": {
                        "name": "메시지 전송",
                        "params": {
                            "message": {
                                "type": "textarea",
                                "description": "전송할 메시지 또는 이전 단계 결과 참조",
                                "required": True,
                                "placeholder": "메시지 내용 또는 step_output_1"
                            }
                        }
                    }
                }
            }
        },
        "workflow_templates": [
            {
                "name": "간단한 질문답변",
                "description": "기본적인 LLM 질문답변",
                "steps": 1,
                "template": [
                    {
                        "module": "LLM_Agent",
                        "action": "__call__"
                    }
                ]
            },
            {
                "name": "멀티 에이전트 토론",
                "description": "여러 전문가가 토론하고 결론 도출",
                "steps": 3,
                "template": [
                    {
                        "module": "LLM_Agent",
                        "action": "__call__",
                        "role": "전문가 1"
                    },
                    {
                        "module": "LLM_Agent",
                        "action": "__call__",
                        "role": "전문가 2"
                    },
                    {
                        "module": "LLM_Agent",
                        "action": "aggregate_responses",
                        "role": "종합 분석가"
                    }
                ]
            },
            {
                "name": "오디오 분석 파이프라인",
                "description": "음성 → 텍스트 → 분석",
                "steps": 2,
                "template": [
                    {
                        "module": "Audio",
                        "action": "transcribe_audio"
                    },
                    {
                        "module": "LLM_Agent",
                        "action": "__call__"
                    }
                ]
            },
            {
                "name": "분석 후 Discord 알림",
                "description": "분석 결과를 Discord로 전송",
                "steps": 2,
                "template": [
                    {
                        "module": "LLM_Agent",
                        "action": "__call__"
                    },
                    {
                        "module": "Discord",
                        "action": "send_message"
                    }
                ]
            }
        ],
        "usage_guide": {
            "step_references": {
                "description": "이전 단계의 결과를 다음 단계에서 사용하려면 step_output_N 형태로 참조하세요",
                "examples": [
                    "step_output_1: 첫 번째 단계의 결과",
                    "step_output_2: 두 번째 단계의 결과"
                ]
            },
            "parameter_types": {
                "string": "일반 텍스트 입력",
                "textarea": "여러 줄 텍스트 입력",
                "select": "드롭다운 선택",
                "multiselect": "여러 옵션 선택",
                "checkbox": "체크박스 (true/false)",
                "number": "숫자 입력",
                "url": "URL 주소",
                "password": "비밀번호 입력",
                "array": "배열 형태의 데이터"
            }
        }
    }

class DynamicWorkflowRequest(BaseModel):
    name: str = Field(..., description="워크플로우 이름")
    description: str = Field(default="", description="워크플로우 설명")
    steps: List[Dict[str, Any]] = Field(..., description="동적으로 구성된 워크플로우 단계들")

@app.post("/build-workflow")
def build_dynamic_workflow(request: DynamicWorkflowRequest):
    """웹에서 구성한 동적 워크플로우를 실행 가능한 형태로 변환"""
    try:
        workflow_steps = []

        for i, step_config in enumerate(request.steps, 1):
            # 필수 필드 검증
            if 'module' not in step_config or 'action' not in step_config:
                raise HTTPException(
                    status_code=400,
                    detail=f"단계 {i}에 필수 필드 (module, action)가 누락되었습니다."
                )

            # init_params와 params 분리
            init_params = step_config.get('init_params', {})
            params = step_config.get('params', {})

            # 빈 문자열이나 None 값 제거
            init_params = {k: v for k, v in init_params.items() if v not in [None, "", []]}
            params = {k: v for k, v in params.items() if v not in [None, "", []]}

            workflow_step = WorkflowStep(
                step=i,
                module=step_config['module'],
                action=step_config['action'],
                init_params=init_params,
                params=params
            )
            workflow_steps.append(workflow_step)

        # 워크플로우 실행
        workflow_request = WorkflowRequest(workflow=workflow_steps)
        result = execute_workflow_endpoint(workflow_request)

        return {
            "workflow_info": {
                "name": request.name,
                "description": request.description,
                "total_steps": len(workflow_steps)
            },
            "execution_result": result
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"동적 워크플로우 빌드 실패: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"워크플로우 빌드 중 오류가 발생했습니다: {str(e)}"
        )

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

# === 호환성을 위한 기존 엔드포인트들 (래퍼) ===

class LegacyLLMRequest(BaseModel):
    system_prompt: str
    user_message: str

class LegacyMultiAgentRequest(BaseModel):
    system_prompt: str
    user_message: str
    task: str
    agents: List[dict]

class AgentConfig(BaseModel):
    name: str
    role: str
    task: str

class DynamicMultiAgentRequest(BaseModel):
    system_prompt: str
    user_message: str
    task: str
    agents: List[AgentConfig]

@app.post("/generate")
def generate_text_legacy(request: LegacyLLMRequest):
    """기존 /generate 엔드포인트와의 호환성을 위한 래퍼"""
    workflow = WorkflowRequest(workflow=[
        WorkflowStep(
            step=1,
            module="LLM_Agent",
            action="__call__",
            init_params={"model_name": "gemma3n", "provider": "ollama"},
            params={
                "system_prompt": request.system_prompt,
                "user_message": request.user_message
            }
        )
    ])

    result = execute_workflow_endpoint(workflow)

    if result.status == "success":
        return {"response": result.final_result}
    else:
        raise HTTPException(status_code=500, detail=result.error_message)

@app.post("/multi_agent")
def multi_agent_legacy(request: LegacyMultiAgentRequest):
    """기존 /multi_agent 엔드포인트와의 호환성을 위한 래퍼"""
    # 동적 에이전트들을 순차적으로 실행하는 워크플로우 생성
    workflow_steps = []

    # 개별 에이전트들 실행
    for i, agent_data in enumerate(request.agents, 1):
        if agent_data.get('name') and agent_data.get('role') and agent_data.get('task'):
            workflow_steps.append(WorkflowStep(
                step=i,
                module="LLM_Agent",
                action="__call__",
                init_params={"model_name": "gemma3n", "provider": "ollama"},
                params={
                    "system_prompt": agent_data['role'],
                    "user_message": request.user_message,
                    "task": agent_data['task']
                }
            ))

    # 마스터 에이전트가 모든 응답을 종합
    final_step = len(workflow_steps) + 1
    workflow_steps.append(WorkflowStep(
        step=final_step,
        module="LLM_Agent",
        action="aggregate_responses",
        init_params={"model_name": "gemma3n", "provider": "ollama"},
        params={
            "system_prompt": request.system_prompt,
            "user_message": request.user_message,
            "task": request.task,
            "responses": [f"step_output_{i}" for i in range(1, len(workflow_steps) + 1)]
        }
    ))

    workflow = WorkflowRequest(workflow=workflow_steps)
    result = execute_workflow_endpoint(workflow)

    if result.status == "success":
        # 기존 응답 포맷과 호환되도록 변환
        individual_responses = []
        for i, agent_data in enumerate(request.agents, 1):
            if agent_data.get('name') and i in result.step_outputs:
                individual_responses.append({
                    "name": agent_data['name'],
                    "response": result.step_outputs[i]
                })

        return {
            "individual_responses": individual_responses,
            "final_response": result.final_result,
            "count": len(individual_responses)
        }
    else:
        raise HTTPException(status_code=500, detail=result.error_message)

@app.post("/run_dynamic_multi_agent")
def run_dynamic_multi_agent_legacy(request: DynamicMultiAgentRequest):
    """기존 /run_dynamic_multi_agent 엔드포인트와의 호환성을 위한 래퍼"""
    # 에이전트들을 순차적으로 실행하는 워크플로우 생성
    workflow_steps = []

    # 개별 에이전트들 실행
    for i, agent_config in enumerate(request.agents, 1):
        workflow_steps.append(WorkflowStep(
            step=i,
            module="LLM_Agent",
            action="__call__",
            init_params={"model_name": "gemma3n", "provider": "ollama"},
            params={
                "system_prompt": agent_config.role,
                "user_message": request.user_message,
                "task": agent_config.task
            }
        ))

    # 마스터 에이전트가 모든 응답을 종합
    final_step = len(workflow_steps) + 1
    workflow_steps.append(WorkflowStep(
        step=final_step,
        module="LLM_Agent",
        action="aggregate_responses",
        init_params={"model_name": "gemma3n", "provider": "ollama"},
        params={
            "system_prompt": request.system_prompt,
            "user_message": request.user_message,
            "task": request.task,
            "responses": [f"step_output_{i}" for i in range(1, len(workflow_steps) + 1)]
        }
    ))

    workflow = WorkflowRequest(workflow=workflow_steps)
    result = execute_workflow_endpoint(workflow)

    if result.status == "success":
        # 기존 응답 포맷과 호환되도록 변환
        individual_responses = []
        for i, agent_config in enumerate(request.agents, 1):
            if i in result.step_outputs:
                individual_responses.append({
                    "name": agent_config.name,
                    "response": result.step_outputs[i]
                })

        return {
            "individual_responses": individual_responses,
            "final_response": result.final_result,
            "count": len(individual_responses)
        }
    else:
        raise HTTPException(status_code=500, detail=result.error_message)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)