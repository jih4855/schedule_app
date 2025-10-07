"""
피어 투 피어 멀티에이전트 시스템
에이전트들이 초기 라우팅 오류를 감지하고 서로에게 쿼리를 핸드오프할 수 있는 시스템
"""

import os
import sys
import json
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

try:
    from module.llm_agent import LLM_Agent
    from module.audio_tool import Audio
    from module.discord import Send_to_discord
except ImportError as e:
    print(f"모듈 임포트 오류: {e}")
    print("기본 모의 클래스를 사용합니다.")

    class LLM_Agent:
        def __init__(self, **kwargs):
            pass
        def __call__(self, system_prompt, user_message, **kwargs):
            return f"[Mock] {user_message}에 대한 응답"

    class Audio:
        pass

    class Send_to_discord:
        def __init__(self, base_url=""):
            pass

class AgentDomain(Enum):
    """에이전트 도메인 정의"""
    TEXT_ANALYSIS = "text_analysis"
    AUDIO_PROCESSING = "audio_processing"
    COMMUNICATION = "communication"
    GENERAL = "general"
    UNKNOWN = "unknown"

class HandoffDecision(Enum):
    """핸드오프 결정 타입"""
    HANDLE_MYSELF = "handle_myself"
    HANDOFF_TO_PEER = "handoff_to_peer"
    NEEDS_COLLABORATION = "needs_collaboration"

class PeerAgent:
    """피어 투 피어 시스템의 개별 에이전트"""

    def __init__(self, agent_id: str, domain: AgentDomain, llm_agent: LLM_Agent,
                 specialized_tool: Any = None, max_handoffs: int = 3):
        self.agent_id = agent_id
        self.domain = domain
        self.llm_agent = llm_agent
        self.specialized_tool = specialized_tool
        self.max_handoffs = max_handoffs
        self.handoff_history = []

        # 도메인별 전문성 설명
        self.domain_descriptions = {
            AgentDomain.TEXT_ANALYSIS: "텍스트 분석, 언어 처리, 번역, 요약, 감정 분석 등",
            AgentDomain.AUDIO_PROCESSING: "음성 인식, 오디오 변환, 음성 합성, 오디오 분석 등",
            AgentDomain.COMMUNICATION: "메시지 전송, 알림, 외부 시스템 통신 등",
            AgentDomain.GENERAL: "일반적인 질문 답변, 추론, 계산 등"
        }

    def analyze_query_domain(self, query: str) -> Tuple[AgentDomain, float]:
        """쿼리의 도메인을 분석하고 확신도를 반환"""

        domain_analysis_prompt = f"""
        다음 쿼리를 분석하여 어느 도메인에 속하는지 판단하세요:

        쿼리: "{query}"

        도메인 옵션:
        1. text_analysis: 텍스트 분석, 언어 처리, 번역, 요약, 감정 분석
        2. audio_processing: 음성 인식, 오디오 변환, 음성 합성, 오디오 분석
        3. communication: 메시지 전송, 알림, 외부 시스템 통신
        4. general: 일반적인 질문 답변, 추론, 계산
        5. unknown: 위 범주에 해당하지 않음

        응답 형식:
        {{
            "domain": "도메인명",
            "confidence": 0.85,
            "reasoning": "판단 근거"
        }}

        반드시 JSON 형식으로만 응답하세요.
        """

        try:
            response = self.llm_agent(
                system_prompt="당신은 쿼리 도메인 분류 전문가입니다. JSON 형식으로만 응답하세요.",
                user_message=domain_analysis_prompt
            )

            # JSON 파싱 시도
            result = json.loads(response.strip())
            domain_str = result.get("domain", "unknown")
            confidence = float(result.get("confidence", 0.5))

            # 문자열을 AgentDomain enum으로 변환
            try:
                domain = AgentDomain(domain_str)
            except ValueError:
                domain = AgentDomain.UNKNOWN

            return domain, confidence

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            print(f"도메인 분석 오류: {e}")
            return AgentDomain.UNKNOWN, 0.3

    def should_handoff(self, query: str, analyzed_domain: AgentDomain, confidence: float) -> HandoffDecision:
        """핸드오프 여부를 결정"""

        # 자신의 도메인과 정확히 일치하고 확신도가 높으면 직접 처리
        if analyzed_domain == self.domain and confidence > 0.7:
            return HandoffDecision.HANDLE_MYSELF

        # 일반 도메인이고 자신이 일반 에이전트가 아니면서 확신도가 낮으면 핸드오프
        if analyzed_domain == AgentDomain.GENERAL and self.domain != AgentDomain.GENERAL and confidence < 0.8:
            return HandoffDecision.HANDOFF_TO_PEER

        # 다른 도메인이고 확신도가 높으면 핸드오프
        if analyzed_domain != self.domain and analyzed_domain != AgentDomain.UNKNOWN and confidence > 0.6:
            return HandoffDecision.HANDOFF_TO_PEER

        # 확신도가 낮으면 협업 필요
        if confidence < 0.5:
            return HandoffDecision.NEEDS_COLLABORATION

        # 기본적으로 직접 처리
        return HandoffDecision.HANDLE_MYSELF

    def find_best_peer(self, target_domain: AgentDomain, peer_registry: Dict[str, 'PeerAgent']) -> Optional[str]:
        """타겟 도메인에 가장 적합한 피어 에이전트 찾기"""

        # 정확히 일치하는 도메인의 에이전트 찾기
        for agent_id, agent in peer_registry.items():
            if agent_id != self.agent_id and agent.domain == target_domain:
                return agent_id

        # 일반 도메인 에이전트 찾기 (fallback)
        for agent_id, agent in peer_registry.items():
            if agent_id != self.agent_id and agent.domain == AgentDomain.GENERAL:
                return agent_id

        return None

    def execute_query(self, query: str, peer_registry: Dict[str, 'PeerAgent'],
                     handoff_count: int = 0) -> Dict[str, Any]:
        """쿼리 실행 (핸드오프 로직 포함)"""

        print(f"\n🤖 Agent {self.agent_id} ({self.domain.value}) 처리 중...")

        # 핸드오프 횟수 제한
        if handoff_count >= self.max_handoffs:
            return {
                "status": "error",
                "message": f"최대 핸드오프 횟수({self.max_handoffs}) 초과",
                "agent_id": self.agent_id,
                "handoff_count": handoff_count
            }

        # 1. 쿼리 도메인 분석
        analyzed_domain, confidence = self.analyze_query_domain(query)
        print(f"   📊 도메인 분석: {analyzed_domain.value} (확신도: {confidence:.2f})")

        # 2. 핸드오프 결정
        decision = self.should_handoff(query, analyzed_domain, confidence)
        print(f"   🎯 결정: {decision.value}")

        # 3. 결정에 따른 행동
        if decision == HandoffDecision.HANDLE_MYSELF:
            return self._handle_query_myself(query, handoff_count)

        elif decision == HandoffDecision.HANDOFF_TO_PEER:
            target_agent_id = self.find_best_peer(analyzed_domain, peer_registry)
            if target_agent_id:
                print(f"   🔄 핸드오프: {target_agent_id}로 전달")
                target_agent = peer_registry[target_agent_id]
                return target_agent.execute_query(query, peer_registry, handoff_count + 1)
            else:
                print(f"   ⚠️ 적절한 피어를 찾지 못함. 직접 처리합니다.")
                return self._handle_query_myself(query, handoff_count)

        elif decision == HandoffDecision.NEEDS_COLLABORATION:
            return self._handle_with_collaboration(query, peer_registry, handoff_count)

        else:
            return self._handle_query_myself(query, handoff_count)

    def _handle_query_myself(self, query: str, handoff_count: int) -> Dict[str, Any]:
        """쿼리를 직접 처리"""

        try:
            # 도메인별 시스템 프롬프트 설정
            system_prompt = f"""
            당신은 {self.domain_descriptions.get(self.domain, '일반적인')} 전문 AI 에이전트입니다.
            주어진 쿼리에 대해 최고의 전문성을 발휘하여 답변하세요.
            """

            # 전문 도구가 있는 경우 활용
            if self.specialized_tool:
                if self.domain == AgentDomain.AUDIO_PROCESSING:
                    # 오디오 관련 작업인지 확인
                    if any(keyword in query.lower() for keyword in ['음성', '오디오', '소리', 'audio', 'voice', 'sound']):
                        # 오디오 도구 사용 안내
                        response = f"오디오 전문 에이전트입니다. 다음 기능을 사용할 수 있습니다:\n"
                        response += "- 텍스트를 음성으로 변환 (TTS)\n"
                        response += "- 음성을 텍스트로 변환 (STT)\n"
                        response += "구체적인 파일 경로나 텍스트를 제공하시면 처리해드립니다.\n"
                        response += f"\n일반 답변: {self.llm_agent(system_prompt, query)}"
                    else:
                        response = self.llm_agent(system_prompt, query)
                elif self.domain == AgentDomain.COMMUNICATION:
                    # 통신 관련 작업인지 확인
                    if any(keyword in query.lower() for keyword in ['디스코드', 'discord', '메시지', '전송', 'send']):
                        response = f"통신 전문 에이전트입니다. 디스코드 메시지 전송 기능을 사용할 수 있습니다.\n"
                        response += f"\n일반 답변: {self.llm_agent(system_prompt, query)}"
                    else:
                        response = self.llm_agent(system_prompt, query)
                else:
                    response = self.llm_agent(system_prompt, query)
            else:
                response = self.llm_agent(system_prompt, query)

            return {
                "status": "success",
                "response": response,
                "agent_id": self.agent_id,
                "domain": self.domain.value,
                "handoff_count": handoff_count,
                "processing_type": "direct"
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"쿼리 처리 중 오류: {str(e)}",
                "agent_id": self.agent_id,
                "handoff_count": handoff_count
            }

    def _handle_with_collaboration(self, query: str, peer_registry: Dict[str, 'PeerAgent'],
                                 handoff_count: int) -> Dict[str, Any]:
        """여러 에이전트와 협업하여 처리"""

        print(f"   🤝 협업 모드: 여러 에이전트 의견 수집")

        try:
            responses = []

            # 자신의 응답
            my_response = self._handle_query_myself(query, handoff_count)
            responses.append(f"Agent {self.agent_id}: {my_response['response']}")

            # 다른 에이전트들의 응답 (최대 2개)
            other_agents = [agent for agent_id, agent in peer_registry.items()
                          if agent_id != self.agent_id][:2]

            for agent in other_agents:
                try:
                    peer_response = agent._handle_query_myself(query, handoff_count)
                    responses.append(f"Agent {agent.agent_id}: {peer_response['response']}")
                except:
                    continue

            # 응답 통합
            integration_prompt = f"""
            다음은 여러 전문 에이전트들의 의견입니다:

            {chr(10).join(responses)}

            이 의견들을 종합하여 최종적으로 통합된 답변을 제공하세요.
            각 에이전트의 전문성을 고려하여 가장 정확하고 완전한 답변을 만드세요.
            """

            final_response = self.llm_agent(
                system_prompt="당신은 여러 전문가의 의견을 통합하는 메타 에이전트입니다.",
                user_message=integration_prompt
            )

            return {
                "status": "success",
                "response": final_response,
                "agent_id": self.agent_id,
                "domain": self.domain.value,
                "handoff_count": handoff_count,
                "processing_type": "collaboration",
                "participating_agents": [self.agent_id] + [agent.agent_id for agent in other_agents]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"협업 처리 중 오류: {str(e)}",
                "agent_id": self.agent_id,
                "handoff_count": handoff_count
            }

class PeerToPeerSystem:
    """피어 투 피어 멀티에이전트 시스템"""

    def __init__(self):
        self.agents: Dict[str, PeerAgent] = {}
        self.query_history = []

    def register_agent(self, agent: PeerAgent):
        """에이전트 등록"""
        self.agents[agent.agent_id] = agent
        print(f"✅ Agent {agent.agent_id} ({agent.domain.value}) 등록됨")

    def route_query(self, query: str, preferred_agent_id: str = None) -> Dict[str, Any]:
        """쿼리 라우팅 (초기 에이전트 선택)"""

        print(f"\n🎯 쿼리 라우팅: '{query}'")

        # 선호하는 에이전트가 지정된 경우
        if preferred_agent_id and preferred_agent_id in self.agents:
            start_agent = self.agents[preferred_agent_id]
            print(f"   👆 지정된 에이전트: {preferred_agent_id}")
        else:
            # 간단한 키워드 기반 초기 라우팅 (의도적으로 불완전하게)
            start_agent = self._simple_route(query)
            print(f"   🎲 자동 라우팅: {start_agent.agent_id}")

        # 선택된 에이전트에서 실행 시작
        result = start_agent.execute_query(query, self.agents)

        # 기록 저장
        self.query_history.append({
            "query": query,
            "start_agent": start_agent.agent_id,
            "result": result
        })

        return result

    def _simple_route(self, query: str) -> PeerAgent:
        """간단한 키워드 기반 초기 라우팅 (의도적으로 부정확할 수 있음)"""

        query_lower = query.lower()

        # 키워드 기반 라우팅 (부정확할 수 있음)
        if any(keyword in query_lower for keyword in ['음성', '오디오', 'audio', 'voice']):
            for agent in self.agents.values():
                if agent.domain == AgentDomain.AUDIO_PROCESSING:
                    return agent

        if any(keyword in query_lower for keyword in ['디스코드', 'discord', '메시지', '전송']):
            for agent in self.agents.values():
                if agent.domain == AgentDomain.COMMUNICATION:
                    return agent

        if any(keyword in query_lower for keyword in ['번역', '분석', '요약', '텍스트']):
            for agent in self.agents.values():
                if agent.domain == AgentDomain.TEXT_ANALYSIS:
                    return agent

        # 기본값: 첫 번째 에이전트 (의도적으로 부정확할 수 있음)
        return list(self.agents.values())[0]

    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 조회"""
        return {
            "registered_agents": {
                agent_id: {
                    "domain": agent.domain.value,
                    "has_specialized_tool": agent.specialized_tool is not None
                }
                for agent_id, agent in self.agents.items()
            },
            "query_count": len(self.query_history),
            "recent_queries": self.query_history[-5:] if self.query_history else []
        }

def create_sample_peer_system():
    """샘플 피어 투 피어 시스템 생성"""

    # 피어 투 피어 시스템 초기화
    p2p_system = PeerToPeerSystem()

    # LLM 에이전트들 초기화
    llm_config = {
        "model_name": "gemma3n",  # 또는 사용 가능한 모델
        "provider": "ollama"
    }

    # 에이전트 생성 및 등록

    # 1. 텍스트 분석 전문 에이전트
    text_agent = PeerAgent(
        agent_id="text_specialist",
        domain=AgentDomain.TEXT_ANALYSIS,
        llm_agent=LLM_Agent(**llm_config, session_id="text_session")
    )
    p2p_system.register_agent(text_agent)

    # 2. 오디오 처리 전문 에이전트
    audio_agent = PeerAgent(
        agent_id="audio_specialist",
        domain=AgentDomain.AUDIO_PROCESSING,
        llm_agent=LLM_Agent(**llm_config, session_id="audio_session"),
        specialized_tool=Audio()
    )
    p2p_system.register_agent(audio_agent)

    # 3. 통신 전문 에이전트
    try:
        comm_tool = Send_to_discord("https://discord.com/api/webhooks/test")  # 테스트용 URL
    except:
        comm_tool = None  # Discord 도구 없이 실행

    comm_agent = PeerAgent(
        agent_id="communication_specialist",
        domain=AgentDomain.COMMUNICATION,
        llm_agent=LLM_Agent(**llm_config, session_id="comm_session"),
        specialized_tool=comm_tool
    )
    p2p_system.register_agent(comm_agent)

    # 4. 일반 목적 에이전트
    general_agent = PeerAgent(
        agent_id="general_assistant",
        domain=AgentDomain.GENERAL,
        llm_agent=LLM_Agent(**llm_config, session_id="general_session")
    )
    p2p_system.register_agent(general_agent)

    return p2p_system

# 테스트 함수들
def test_peer_to_peer_system():
    """피어 투 피어 시스템 테스트"""

    print("=" * 60)
    print("🚀 피어 투 피어 멀티에이전트 시스템 테스트")
    print("=" * 60)

    # 시스템 생성
    p2p_system = create_sample_peer_system()

    # 테스트 쿼리들 (의도적으로 잘못 라우팅될 수 있는 쿼리들 포함)
    test_queries = [
        "파이썬 코드를 한국어로 번역해주세요",  # 텍스트 분석이지만 다른 에이전트가 받을 수 있음
        "이 음성 파일을 텍스트로 변환해주세요",  # 오디오 처리
        "디스코드에 메시지를 보내고 싶어요",  # 통신
        "1+1은 무엇인가요?",  # 일반적인 질문
        "사진을 분석해주세요",  # 모호한 요청 (협업 필요)
    ]

    # 각 쿼리 테스트
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*20} 테스트 {i} {'='*20}")
        print(f"쿼리: {query}")

        result = p2p_system.route_query(query)

        print(f"\n📊 결과:")
        print(f"   상태: {result['status']}")
        if result['status'] == 'success':
            print(f"   처리 에이전트: {result['agent_id']}")
            print(f"   도메인: {result['domain']}")
            print(f"   핸드오프 횟수: {result['handoff_count']}")
            print(f"   처리 방식: {result['processing_type']}")
            print(f"   응답: {result['response'][:200]}...")
        else:
            print(f"   오류: {result['message']}")

    # 시스템 상태 출력
    print(f"\n{'='*20} 시스템 상태 {'='*20}")
    status = p2p_system.get_system_status()
    print(f"등록된 에이전트: {len(status['registered_agents'])}")
    print(f"처리된 쿼리: {status['query_count']}")

def test_handoff_scenarios():
    """특정 핸드오프 시나리오 테스트"""

    print("\n" + "=" * 60)
    print("🔄 핸드오프 시나리오 테스트")
    print("=" * 60)

    p2p_system = create_sample_peer_system()

    # 의도적으로 잘못된 에이전트에 라우팅하여 핸드오프 테스트
    test_scenarios = [
        {
            "query": "음성 인식 기술에 대해 설명해주세요",
            "wrong_agent": "text_specialist",  # 텍스트 에이전트에게 오디오 질문
            "expected_handoff": "audio_specialist"
        },
        {
            "query": "이 문서를 요약해주세요",
            "wrong_agent": "audio_specialist",  # 오디오 에이전트에게 텍스트 질문
            "expected_handoff": "text_specialist"
        }
    ]

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n--- 시나리오 {i} ---")
        print(f"쿼리: {scenario['query']}")
        print(f"잘못 라우팅된 에이전트: {scenario['wrong_agent']}")
        print(f"예상 핸드오프 대상: {scenario['expected_handoff']}")

        result = p2p_system.route_query(scenario['query'], scenario['wrong_agent'])

        print(f"실제 결과:")
        print(f"   최종 처리 에이전트: {result.get('agent_id', 'N/A')}")
        print(f"   핸드오프 횟수: {result.get('handoff_count', 0)}")
        print(f"   상태: {result['status']}")

if __name__ == "__main__":
    # 기본 테스트 실행
    test_peer_to_peer_system()

    # 핸드오프 시나리오 테스트
    test_handoff_scenarios()

    print(f"\n{'='*60}")
    print("✅ 모든 테스트 완료!")
    print("💡 피어 투 피어 패턴이 성공적으로 구현되었습니다.")
    print("🔄 에이전트들이 자동으로 적절한 피어에게 쿼리를 핸드오프합니다.")