"""
피어 투 피어 멀티에이전트 시스템 데모
의존성 없이 실행 가능한 간단한 버전
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
    print("✅ LLM_Agent 모듈 임포트 성공")
except ImportError as e:
    print(f"❌ LLM_Agent 모듈 임포트 실패: {e}")
    print("💡 기본 모의 클래스를 사용합니다.")

    class LLM_Agent:
        def __init__(self, model_name="mock", provider="ollama", session_id="test"):
            self.model_name = model_name
            self.provider = provider
            self.session_id = session_id

        def __call__(self, system_prompt, user_message, **kwargs):
            return f"[Mock Response] 모의 LLM 응답: {user_message[:50]}에 대한 답변"

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

class SimplePeerAgent:
    """간단한 피어 에이전트 (데모용)"""

    def __init__(self, agent_id: str, domain: AgentDomain, max_handoffs: int = 2):
        self.agent_id = agent_id
        self.domain = domain
        self.max_handoffs = max_handoffs

        # 간단한 LLM 에이전트 (모의 또는 실제)
        self.llm_agent = LLM_Agent(
            model_name="gemma2:9b",
            provider="ollama",
            session_id=f"{agent_id}_session"
        )

        # 도메인별 키워드 (간단한 분류용)
        self.domain_keywords = {
            AgentDomain.TEXT_ANALYSIS: ["번역", "요약", "분석", "텍스트", "문서", "글"],
            AgentDomain.AUDIO_PROCESSING: ["음성", "오디오", "소리", "듣기", "audio", "voice", "sound"],
            AgentDomain.COMMUNICATION: ["메시지", "전송", "보내기", "디스코드", "discord", "알림"],
            AgentDomain.GENERAL: ["계산", "질문", "일반", "도움", "설명"]
        }

    def analyze_query_domain(self, query: str) -> Tuple[AgentDomain, float]:
        """키워드 기반 간단한 도메인 분석"""

        query_lower = query.lower()
        domain_scores = {}

        # 각 도메인별 키워드 매칭 점수 계산
        for domain, keywords in self.domain_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                domain_scores[domain] = score / len(keywords)

        if not domain_scores:
            return AgentDomain.UNKNOWN, 0.3

        # 가장 높은 점수의 도메인 반환
        best_domain = max(domain_scores.keys(), key=lambda d: domain_scores[d])
        confidence = min(domain_scores[best_domain] * 2, 1.0)  # 최대 1.0으로 제한

        return best_domain, confidence

    def should_handoff(self, query: str, analyzed_domain: AgentDomain, confidence: float) -> HandoffDecision:
        """핸드오프 여부 결정"""

        print(f"   🤔 분석 결과: {analyzed_domain.value} (확신도: {confidence:.2f})")
        print(f"   🏠 내 전문 도메인: {self.domain.value}")

        # 자신의 도메인과 일치하고 확신도가 높으면 직접 처리
        if analyzed_domain == self.domain and confidence > 0.5:
            print(f"   ✅ 내 전문 분야입니다. 직접 처리하겠습니다.")
            return HandoffDecision.HANDLE_MYSELF

        # 다른 도메인이고 확신도가 높으면 핸드오프
        if analyzed_domain != self.domain and analyzed_domain != AgentDomain.UNKNOWN and confidence > 0.3:
            print(f"   🔄 다른 전문가가 더 적합합니다. 핸드오프하겠습니다.")
            return HandoffDecision.HANDOFF_TO_PEER

        # 확신도가 낮으면 협업
        if confidence < 0.3:
            print(f"   🤝 불분명한 요청입니다. 협업이 필요합니다.")
            return HandoffDecision.NEEDS_COLLABORATION

        # 기본적으로 직접 처리
        print(f"   🎯 확신은 없지만 직접 처리해보겠습니다.")
        return HandoffDecision.HANDLE_MYSELF

    def find_best_peer(self, target_domain: AgentDomain, peer_registry: Dict[str, 'SimplePeerAgent']) -> Optional[str]:
        """최적의 피어 찾기"""

        # 정확히 일치하는 도메인 찾기
        for agent_id, agent in peer_registry.items():
            if agent_id != self.agent_id and agent.domain == target_domain:
                return agent_id

        # 일반 에이전트 찾기 (fallback)
        for agent_id, agent in peer_registry.items():
            if agent_id != self.agent_id and agent.domain == AgentDomain.GENERAL:
                return agent_id

        return None

    def execute_query(self, query: str, peer_registry: Dict[str, 'SimplePeerAgent'],
                     handoff_count: int = 0) -> Dict[str, Any]:
        """쿼리 실행 (핸드오프 포함)"""

        print(f"\n🤖 [{self.agent_id}] ({self.domain.value}) 처리 시작...")

        # 최대 핸드오프 횟수 체크
        if handoff_count >= self.max_handoffs:
            return {
                "status": "error",
                "message": f"최대 핸드오프 횟수 초과 ({self.max_handoffs})",
                "agent_id": self.agent_id,
                "handoff_count": handoff_count
            }

        # 1. 도메인 분석
        analyzed_domain, confidence = self.analyze_query_domain(query)

        # 2. 핸드오프 결정
        decision = self.should_handoff(query, analyzed_domain, confidence)

        # 3. 결정에 따른 행동
        if decision == HandoffDecision.HANDOFF_TO_PEER:
            target_agent_id = self.find_best_peer(analyzed_domain, peer_registry)
            if target_agent_id:
                print(f"   📤 핸드오프: {target_agent_id}에게 전달합니다.")
                target_agent = peer_registry[target_agent_id]
                return target_agent.execute_query(query, peer_registry, handoff_count + 1)
            else:
                print(f"   ⚠️ 적절한 피어를 찾지 못했습니다. 직접 처리합니다.")

        elif decision == HandoffDecision.NEEDS_COLLABORATION:
            return self._handle_with_collaboration(query, peer_registry, handoff_count)

        # 직접 처리
        return self._handle_query_myself(query, handoff_count)

    def _handle_query_myself(self, query: str, handoff_count: int) -> Dict[str, Any]:
        """직접 처리"""

        print(f"   ⚡ 직접 처리 중...")

        try:
            # 도메인별 전문 프롬프트
            domain_prompts = {
                AgentDomain.TEXT_ANALYSIS: "당신은 텍스트 분석 전문가입니다. 번역, 요약, 분석을 전문으로 합니다.",
                AgentDomain.AUDIO_PROCESSING: "당신은 오디오 처리 전문가입니다. 음성 인식, 변환을 전문으로 합니다.",
                AgentDomain.COMMUNICATION: "당신은 통신 전문가입니다. 메시지 전송, 알림을 전문으로 합니다.",
                AgentDomain.GENERAL: "당신은 범용 AI 어시스턴트입니다. 다양한 질문에 답변합니다."
            }

            system_prompt = domain_prompts.get(self.domain, "당신은 도움이 되는 AI 어시스턴트입니다.")
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
                "message": f"처리 중 오류: {str(e)}",
                "agent_id": self.agent_id,
                "handoff_count": handoff_count
            }

    def _handle_with_collaboration(self, query: str, peer_registry: Dict[str, 'SimplePeerAgent'],
                                 handoff_count: int) -> Dict[str, Any]:
        """협업 처리"""

        print(f"   🤝 협업 모드 활성화...")

        try:
            responses = []

            # 자신의 응답
            my_result = self._handle_query_myself(query, handoff_count)
            responses.append(f"[{self.agent_id}]: {my_result.get('response', '응답 없음')}")

            # 다른 에이전트 1-2개의 의견 수집
            other_agents = [agent for agent_id, agent in peer_registry.items()
                          if agent_id != self.agent_id][:2]

            for agent in other_agents:
                try:
                    peer_result = agent._handle_query_myself(query, handoff_count)
                    responses.append(f"[{agent.agent_id}]: {peer_result.get('response', '응답 없음')}")
                except:
                    continue

            # 응답 통합
            integration_prompt = f"""
            여러 전문가의 의견:

            {chr(10).join(responses)}

            위 의견들을 종합하여 최종 답변을 제공하세요.
            """

            final_response = self.llm_agent(
                "당신은 여러 전문가 의견을 통합하는 메타 어시스턴트입니다.",
                integration_prompt
            )

            return {
                "status": "success",
                "response": final_response,
                "agent_id": self.agent_id,
                "domain": self.domain.value,
                "handoff_count": handoff_count,
                "processing_type": "collaboration",
                "collaborators": [agent.agent_id for agent in other_agents]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"협업 처리 중 오류: {str(e)}",
                "agent_id": self.agent_id,
                "handoff_count": handoff_count
            }

class SimplePeerToPeerSystem:
    """간단한 피어 투 피어 시스템"""

    def __init__(self):
        self.agents: Dict[str, SimplePeerAgent] = {}
        self.query_log = []

    def register_agent(self, agent: SimplePeerAgent):
        """에이전트 등록"""
        self.agents[agent.agent_id] = agent
        print(f"✅ 에이전트 등록: {agent.agent_id} ({agent.domain.value})")

    def route_query(self, query: str, start_agent_id: str = None) -> Dict[str, Any]:
        """쿼리 라우팅"""

        print(f"\n🎯 새로운 쿼리: '{query}'")

        # 시작 에이전트 선택
        if start_agent_id and start_agent_id in self.agents:
            start_agent = self.agents[start_agent_id]
            print(f"   👤 지정된 시작 에이전트: {start_agent_id}")
        else:
            # 간단한 키워드 기반 초기 라우팅 (의도적으로 부정확할 수 있음)
            start_agent = self._simple_initial_route(query)
            print(f"   🎲 자동 선택된 시작 에이전트: {start_agent.agent_id}")

        # 쿼리 실행
        result = start_agent.execute_query(query, self.agents)

        # 로그 저장
        self.query_log.append({
            "query": query,
            "start_agent": start_agent.agent_id,
            "final_agent": result.get("agent_id"),
            "handoff_count": result.get("handoff_count", 0),
            "status": result.get("status")
        })

        return result

    def _simple_initial_route(self, query: str) -> SimplePeerAgent:
        """간단한 초기 라우팅 (의도적으로 부정확할 수 있음)"""

        query_lower = query.lower()

        # 키워드 기반 간단 라우팅
        if "음성" in query_lower or "오디오" in query_lower:
            for agent in self.agents.values():
                if agent.domain == AgentDomain.AUDIO_PROCESSING:
                    return agent

        if "메시지" in query_lower or "디스코드" in query_lower:
            for agent in self.agents.values():
                if agent.domain == AgentDomain.COMMUNICATION:
                    return agent

        # 기본값: 첫 번째 에이전트 (의도적으로 틀릴 수 있음)
        return list(self.agents.values())[0]

    def get_system_summary(self) -> Dict[str, Any]:
        """시스템 요약"""
        return {
            "agents": {
                agent_id: agent.domain.value
                for agent_id, agent in self.agents.items()
            },
            "total_queries": len(self.query_log),
            "recent_queries": self.query_log[-3:] if self.query_log else []
        }

def run_demo():
    """데모 실행"""

    print("🚀 피어 투 피어 멀티에이전트 시스템 데모")
    print("=" * 50)

    # 시스템 생성
    p2p_system = SimplePeerToPeerSystem()

    # 에이전트들 생성 및 등록
    agents = [
        SimplePeerAgent("text_expert", AgentDomain.TEXT_ANALYSIS),
        SimplePeerAgent("audio_expert", AgentDomain.AUDIO_PROCESSING),
        SimplePeerAgent("comm_expert", AgentDomain.COMMUNICATION),
        SimplePeerAgent("general_helper", AgentDomain.GENERAL)
    ]

    for agent in agents:
        p2p_system.register_agent(agent)

    print(f"\n📋 등록된 에이전트: {len(agents)}개")

    # 테스트 쿼리들
    test_queries = [
        "이 영어 문서를 한국어로 번역해주세요",  # 텍스트 분석
        "음성 파일을 텍스트로 변환하고 싶어요",  # 오디오 처리
        "디스코드에 알림 메시지를 보내주세요",  # 통신
        "2+2는 얼마인가요?",  # 일반 질문
        "복잡한 데이터 분석을 도와주세요"  # 모호한 요청 (협업 필요)
    ]

    # 각 쿼리 테스트
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*15} 테스트 {i} {'='*15}")

        # 의도적으로 잘못된 에이전트부터 시작 (첫 번째 에이전트)
        result = p2p_system.route_query(query, "text_expert")

        print(f"\n📊 최종 결과:")
        print(f"   상태: {result['status']}")
        if result['status'] == 'success':
            print(f"   최종 처리 에이전트: {result['agent_id']}")
            print(f"   핸드오프 횟수: {result['handoff_count']}")
            print(f"   처리 방식: {result.get('processing_type', 'unknown')}")
            print(f"   응답 미리보기: {result['response'][:100]}...")
        else:
            print(f"   오류: {result.get('message', 'Unknown error')}")

    # 시스템 요약
    print(f"\n{'='*20} 시스템 요약 {'='*20}")
    summary = p2p_system.get_system_summary()
    print(f"처리된 쿼리 수: {summary['total_queries']}")
    print("\n최근 쿼리 로그:")
    for log in summary['recent_queries']:
        print(f"  • '{log['query'][:30]}...' | "
              f"{log['start_agent']} → {log['final_agent']} | "
              f"핸드오프: {log['handoff_count']}회")

    print(f"\n✅ 데모 완료!")
    print(f"💡 피어 투 피어 패턴의 핵심 특징:")
    print(f"   🔄 자동 핸드오프: 에이전트가 자신의 전문 영역이 아닌 쿼리를 감지하면 적절한 피어에게 전달")
    print(f"   🤝 협업 메커니즘: 모호한 요청에 대해 여러 에이전트가 협력하여 응답")
    print(f"   🛡️ 복구 능력: 초기 라우팅 오류에서 자동 복구")

if __name__ == "__main__":
    run_demo()