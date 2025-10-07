"""
향상된 피어 투 피어 멀티에이전트 시스템
더 정교한 핸드오프 메커니즘과 실제 시나리오 테스트
"""

import os
import sys
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum
import random

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

class AgentDomain(Enum):
    """에이전트 도메인"""
    TEXT_ANALYSIS = "text_analysis"
    AUDIO_PROCESSING = "audio_processing"
    COMMUNICATION = "communication"
    DATA_ANALYSIS = "data_analysis"
    GENERAL = "general"

class ConfidenceLevel(Enum):
    """확신도 레벨"""
    VERY_HIGH = "very_high"  # 0.8+
    HIGH = "high"           # 0.6-0.8
    MEDIUM = "medium"       # 0.4-0.6
    LOW = "low"            # 0.2-0.4
    VERY_LOW = "very_low"  # 0.0-0.2

class EnhancedPeerAgent:
    """향상된 피어 에이전트"""

    def __init__(self, agent_id: str, domain: AgentDomain, specialties: List[str] = None):
        self.agent_id = agent_id
        self.domain = domain
        self.specialties = specialties or []
        self.handoff_count = 0
        self.success_count = 0
        self.collaboration_count = 0

        # 도메인별 고도화된 키워드와 가중치
        self.domain_analysis = {
            AgentDomain.TEXT_ANALYSIS: {
                "primary_keywords": ["번역", "요약", "분석", "텍스트", "문서", "언어", "문법"],
                "secondary_keywords": ["글", "문장", "단어", "해석", "작성", "편집"],
                "negative_keywords": ["음성", "오디오", "숫자", "계산", "차트"],
                "weight": 1.0
            },
            AgentDomain.AUDIO_PROCESSING: {
                "primary_keywords": ["음성", "오디오", "소리", "듣기", "녹음", "변환", "인식"],
                "secondary_keywords": ["voice", "sound", "audio", "speech", "wav", "mp3"],
                "negative_keywords": ["텍스트", "문서", "글자", "읽기"],
                "weight": 1.0
            },
            AgentDomain.COMMUNICATION: {
                "primary_keywords": ["메시지", "전송", "보내기", "디스코드", "알림", "통신"],
                "secondary_keywords": ["discord", "send", "message", "notify", "email"],
                "negative_keywords": ["분석", "변환", "계산"],
                "weight": 1.0
            },
            AgentDomain.DATA_ANALYSIS: {
                "primary_keywords": ["데이터", "분석", "통계", "차트", "그래프", "수치"],
                "secondary_keywords": ["계산", "비교", "패턴", "트렌드", "예측"],
                "negative_keywords": ["음성", "메시지", "번역"],
                "weight": 1.0
            },
            AgentDomain.GENERAL: {
                "primary_keywords": ["질문", "도움", "설명", "일반", "기본"],
                "secondary_keywords": ["무엇", "어떻게", "왜", "언제", "어디서"],
                "negative_keywords": [],
                "weight": 0.5  # 일반 도메인은 낮은 가중치
            }
        }

    def advanced_domain_analysis(self, query: str) -> Tuple[AgentDomain, float, str]:
        """향상된 도메인 분석"""

        query_lower = query.lower()
        domain_scores = {}
        analysis_details = []

        for domain, analysis in self.domain_analysis.items():
            score = 0
            matched_keywords = []

            # Primary keywords (높은 가중치)
            for keyword in analysis["primary_keywords"]:
                if keyword in query_lower:
                    score += 2.0 * analysis["weight"]
                    matched_keywords.append(f"주요:{keyword}")

            # Secondary keywords (중간 가중치)
            for keyword in analysis["secondary_keywords"]:
                if keyword in query_lower:
                    score += 1.0 * analysis["weight"]
                    matched_keywords.append(f"보조:{keyword}")

            # Negative keywords (감점)
            for keyword in analysis["negative_keywords"]:
                if keyword in query_lower:
                    score -= 1.0
                    matched_keywords.append(f"제외:{keyword}")

            # 점수 정규화
            max_possible = len(analysis["primary_keywords"]) * 2 + len(analysis["secondary_keywords"]) * 1
            if max_possible > 0:
                normalized_score = max(0, score) / max_possible
                domain_scores[domain] = normalized_score

                if matched_keywords:
                    analysis_details.append(f"{domain.value}: {normalized_score:.2f} ({', '.join(matched_keywords)})")

        if not domain_scores:
            return AgentDomain.GENERAL, 0.1, "키워드 매칭 없음"

        best_domain = max(domain_scores.keys(), key=lambda d: domain_scores[d])
        confidence = domain_scores[best_domain]

        details = " | ".join(analysis_details) if analysis_details else "분석 불가"
        return best_domain, confidence, details

    def get_confidence_level(self, confidence: float) -> ConfidenceLevel:
        """확신도를 레벨로 변환"""
        if confidence >= 0.8:
            return ConfidenceLevel.VERY_HIGH
        elif confidence >= 0.6:
            return ConfidenceLevel.HIGH
        elif confidence >= 0.4:
            return ConfidenceLevel.MEDIUM
        elif confidence >= 0.2:
            return ConfidenceLevel.LOW
        else:
            return ConfidenceLevel.VERY_LOW

    def should_handoff(self, analyzed_domain: AgentDomain, confidence: float) -> Tuple[bool, str]:
        """향상된 핸드오프 결정 로직"""

        confidence_level = self.get_confidence_level(confidence)

        # 자신의 도메인과 정확히 일치
        if analyzed_domain == self.domain:
            if confidence_level in [ConfidenceLevel.VERY_HIGH, ConfidenceLevel.HIGH]:
                return False, f"내 전문 분야 ({confidence_level.value})"
            elif confidence_level == ConfidenceLevel.MEDIUM:
                return False, f"적당한 확신으로 처리 가능 ({confidence_level.value})"
            else:
                return True, f"확신도 부족으로 협업 필요 ({confidence_level.value})"

        # 다른 도메인
        else:
            if confidence_level in [ConfidenceLevel.VERY_HIGH, ConfidenceLevel.HIGH]:
                return True, f"다른 전문가 필요 ({analyzed_domain.value}, {confidence_level.value})"
            elif confidence_level == ConfidenceLevel.MEDIUM:
                # 일반 에이전트인 경우는 처리, 전문 에이전트는 핸드오프
                if self.domain == AgentDomain.GENERAL:
                    return False, f"일반 에이전트로 처리 ({confidence_level.value})"
                else:
                    return True, f"다른 전문가가 더 적합 ({analyzed_domain.value})"
            else:
                return False, f"불분명하여 직접 시도 ({confidence_level.value})"

    def find_best_peer_advanced(self, target_domain: AgentDomain,
                              peer_registry: Dict[str, 'EnhancedPeerAgent']) -> Optional[Tuple[str, float]]:
        """향상된 피어 찾기 (성능 지표 고려)"""

        candidates = []

        for agent_id, agent in peer_registry.items():
            if agent_id == self.agent_id:
                continue

            # 도메인 일치도
            if agent.domain == target_domain:
                # 성능 지표 계산 (성공률)
                success_rate = (agent.success_count / max(1, agent.success_count + agent.handoff_count)) * 100
                candidates.append((agent_id, success_rate, "정확한 도메인"))
            elif agent.domain == AgentDomain.GENERAL:
                # 일반 에이전트는 fallback
                success_rate = (agent.success_count / max(1, agent.success_count + agent.handoff_count)) * 100
                candidates.append((agent_id, success_rate * 0.5, "일반 에이전트"))

        if candidates:
            # 성능이 가장 좋은 에이전트 선택
            best_candidate = max(candidates, key=lambda x: x[1])
            return best_candidate[0], best_candidate[1]

        return None, 0

    def execute_query_enhanced(self, query: str, peer_registry: Dict[str, 'EnhancedPeerAgent'],
                             handoff_count: int = 0, max_handoffs: int = 3) -> Dict[str, Any]:
        """향상된 쿼리 실행"""

        print(f"\n🔍 [{self.agent_id}] ({self.domain.value}) 분석 시작...")

        if handoff_count >= max_handoffs:
            return {
                "status": "error",
                "message": f"최대 핸드오프 횟수 초과 ({max_handoffs})",
                "agent_id": self.agent_id,
                "handoff_chain": [self.agent_id]
            }

        # 1. 고급 도메인 분석
        analyzed_domain, confidence, details = self.advanced_domain_analysis(query)
        print(f"   📊 분석: {analyzed_domain.value} (확신도: {confidence:.3f})")
        print(f"   🔎 세부사항: {details}")

        # 2. 핸드오프 결정
        should_handoff, reason = self.should_handoff(analyzed_domain, confidence)
        print(f"   🎯 결정: {'핸드오프' if should_handoff else '직접 처리'} - {reason}")

        # 3. 핸드오프 실행
        if should_handoff and analyzed_domain != AgentDomain.GENERAL:
            best_peer, peer_score = self.find_best_peer_advanced(analyzed_domain, peer_registry)

            if best_peer:
                print(f"   🚀 핸드오프: {best_peer} (성능 점수: {peer_score:.1f})")
                self.handoff_count += 1

                target_agent = peer_registry[best_peer]
                result = target_agent.execute_query_enhanced(
                    query, peer_registry, handoff_count + 1, max_handoffs
                )

                # 핸드오프 체인 업데이트
                if "handoff_chain" in result:
                    result["handoff_chain"] = [self.agent_id] + result["handoff_chain"]
                else:
                    result["handoff_chain"] = [self.agent_id, best_peer]

                return result
            else:
                print(f"   ⚠️ 적절한 피어 없음. 직접 처리합니다.")

        # 4. 직접 처리
        return self._process_query_enhanced(query, confidence, handoff_count)

    def _process_query_enhanced(self, query: str, confidence: float, handoff_count: int) -> Dict[str, Any]:
        """향상된 쿼리 처리"""

        print(f"   ⚡ 직접 처리 중... (확신도: {confidence:.3f})")

        try:
            # 도메인별 전문 응답 시뮬레이션
            responses = {
                AgentDomain.TEXT_ANALYSIS: f"[텍스트 분석 전문가] '{query}'에 대한 언어학적 분석을 수행했습니다.",
                AgentDomain.AUDIO_PROCESSING: f"[오디오 처리 전문가] '{query}'에 대한 음성 처리 작업을 완료했습니다.",
                AgentDomain.COMMUNICATION: f"[통신 전문가] '{query}'에 대한 메시지 전송 작업을 준비했습니다.",
                AgentDomain.DATA_ANALYSIS: f"[데이터 분석 전문가] '{query}'에 대한 통계적 분석을 실시했습니다.",
                AgentDomain.GENERAL: f"[일반 어시스턴트] '{query}'에 대한 범용적인 답변을 제공합니다."
            }

            response = responses.get(self.domain, f"[{self.agent_id}] 쿼리를 처리했습니다: {query}")

            # 성공률 계산 (확신도 기반)
            success_probability = confidence * 0.8 + 0.2  # 최소 20% 성공 확률
            is_success = random.random() < success_probability

            if is_success:
                self.success_count += 1
                status = "success"
                print(f"   ✅ 처리 성공!")
            else:
                status = "partial_success"
                response += " (부분적 성공)"
                print(f"   ⚠️ 부분적 성공")

            return {
                "status": status,
                "response": response,
                "agent_id": self.agent_id,
                "domain": self.domain.value,
                "confidence": confidence,
                "handoff_count": handoff_count,
                "handoff_chain": [self.agent_id]
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"처리 중 오류: {str(e)}",
                "agent_id": self.agent_id,
                "handoff_count": handoff_count,
                "handoff_chain": [self.agent_id]
            }

class EnhancedPeerToPeerSystem:
    """향상된 피어 투 피어 시스템"""

    def __init__(self):
        self.agents: Dict[str, EnhancedPeerAgent] = {}
        self.query_log = []
        self.performance_stats = {}

    def register_agent(self, agent: EnhancedPeerAgent):
        """에이전트 등록"""
        self.agents[agent.agent_id] = agent
        self.performance_stats[agent.agent_id] = {
            "queries_handled": 0,
            "handoffs_made": 0,
            "success_rate": 0.0
        }
        print(f"✅ 에이전트 등록: {agent.agent_id} ({agent.domain.value})")

    def route_query_enhanced(self, query: str, preferred_agent: str = None) -> Dict[str, Any]:
        """향상된 쿼리 라우팅"""

        print(f"\n🎯 새로운 쿼리: '{query}'")

        # 시작 에이전트 선택
        if preferred_agent and preferred_agent in self.agents:
            start_agent = self.agents[preferred_agent]
            print(f"   👤 지정된 시작 에이전트: {preferred_agent}")
        else:
            # 의도적으로 부정확한 초기 라우팅
            start_agent = self._deliberately_wrong_route(query)
            print(f"   🎲 (의도적으로 잘못된) 자동 라우팅: {start_agent.agent_id}")

        # 쿼리 실행
        result = start_agent.execute_query_enhanced(query, self.agents)

        # 성능 통계 업데이트
        self._update_performance_stats(result)

        # 로그 저장
        self.query_log.append({
            "query": query,
            "result": result,
            "timestamp": len(self.query_log) + 1
        })

        return result

    def _deliberately_wrong_route(self, query: str) -> EnhancedPeerAgent:
        """의도적으로 잘못된 초기 라우팅 (피어 투 피어 복구 테스트용)"""

        agents_list = list(self.agents.values())
        query_lower = query.lower()

        # 키워드와 반대되는 에이전트 선택
        if "음성" in query_lower or "오디오" in query_lower:
            # 오디오 쿼리를 텍스트 에이전트에게
            for agent in agents_list:
                if agent.domain == AgentDomain.TEXT_ANALYSIS:
                    return agent

        if "번역" in query_lower or "텍스트" in query_lower:
            # 텍스트 쿼리를 오디오 에이전트에게
            for agent in agents_list:
                if agent.domain == AgentDomain.AUDIO_PROCESSING:
                    return agent

        if "데이터" in query_lower or "분석" in query_lower:
            # 데이터 쿼리를 통신 에이전트에게
            for agent in agents_list:
                if agent.domain == AgentDomain.COMMUNICATION:
                    return agent

        # 기본값: 첫 번째 에이전트
        return agents_list[0]

    def _update_performance_stats(self, result: Dict[str, Any]):
        """성능 통계 업데이트"""

        if "handoff_chain" in result:
            for agent_id in result["handoff_chain"]:
                if agent_id in self.performance_stats:
                    self.performance_stats[agent_id]["queries_handled"] += 1

        final_agent = result.get("agent_id")
        if final_agent and final_agent in self.performance_stats:
            if result.get("status") == "success":
                # 성공률 업데이트 로직
                stats = self.performance_stats[final_agent]
                total = stats["queries_handled"]
                if total > 0:
                    stats["success_rate"] = (stats["success_rate"] * (total - 1) + 1.0) / total

    def get_comprehensive_report(self) -> Dict[str, Any]:
        """종합 보고서"""

        # 핸드오프 분석
        handoff_stats = {
            "total_queries": len(self.query_log),
            "successful_handoffs": 0,
            "average_handoff_chain_length": 0,
            "most_active_agent": None
        }

        handoff_counts = {}
        chain_lengths = []

        for log in self.query_log:
            result = log["result"]
            if "handoff_chain" in result:
                chain_length = len(result["handoff_chain"])
                chain_lengths.append(chain_length)

                if chain_length > 1:
                    handoff_stats["successful_handoffs"] += 1

                for agent_id in result["handoff_chain"]:
                    handoff_counts[agent_id] = handoff_counts.get(agent_id, 0) + 1

        if chain_lengths:
            handoff_stats["average_handoff_chain_length"] = sum(chain_lengths) / len(chain_lengths)

        if handoff_counts:
            handoff_stats["most_active_agent"] = max(handoff_counts.keys(), key=lambda k: handoff_counts[k])

        return {
            "handoff_statistics": handoff_stats,
            "agent_performance": self.performance_stats,
            "recent_queries": self.query_log[-5:] if self.query_log else [],
            "agent_handoff_counts": handoff_counts
        }

def run_enhanced_demo():
    """향상된 데모 실행"""

    print("🚀 향상된 피어 투 피어 멀티에이전트 시스템")
    print("=" * 60)

    # 시스템 생성
    system = EnhancedPeerToPeerSystem()

    # 전문 에이전트들 생성
    agents = [
        EnhancedPeerAgent("text_master", AgentDomain.TEXT_ANALYSIS, ["번역", "요약", "편집"]),
        EnhancedPeerAgent("audio_wizard", AgentDomain.AUDIO_PROCESSING, ["음성인식", "변환", "분석"]),
        EnhancedPeerAgent("comm_specialist", AgentDomain.COMMUNICATION, ["메시징", "알림", "전송"]),
        EnhancedPeerAgent("data_scientist", AgentDomain.DATA_ANALYSIS, ["통계", "시각화", "예측"]),
        EnhancedPeerAgent("general_helper", AgentDomain.GENERAL, ["질답", "도움", "설명"])
    ]

    for agent in agents:
        system.register_agent(agent)

    print(f"\n📋 등록된 에이전트: {len(agents)}개")

    # 다양한 핸드오프 시나리오 테스트
    test_scenarios = [
        {
            "query": "이 영어 PDF 문서를 한국어로 번역해주세요",
            "expected_domain": AgentDomain.TEXT_ANALYSIS,
            "description": "텍스트 번역 작업"
        },
        {
            "query": "녹음된 음성 파일에서 텍스트를 추출하고 요약해주세요",
            "expected_domain": AgentDomain.AUDIO_PROCESSING,
            "description": "오디오-텍스트 변환 + 후처리"
        },
        {
            "query": "팀 채널에 프로젝트 완료 알림을 보내주세요",
            "expected_domain": AgentDomain.COMMUNICATION,
            "description": "메시지 전송 작업"
        },
        {
            "query": "매출 데이터를 분석하고 트렌드 차트를 만들어주세요",
            "expected_domain": AgentDomain.DATA_ANALYSIS,
            "description": "데이터 분석 및 시각화"
        },
        {
            "query": "복잡한 다중 모달 AI 시스템을 설계해주세요",
            "expected_domain": AgentDomain.GENERAL,
            "description": "복합적 요청 (협업 필요)"
        }
    ]

    # 각 시나리오 테스트
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{'='*15} 시나리오 {i} {'='*15}")
        print(f"설명: {scenario['description']}")
        print(f"예상 도메인: {scenario['expected_domain'].value}")

        result = system.route_query_enhanced(scenario["query"])

        print(f"\n📊 실행 결과:")
        print(f"   상태: {result['status']}")
        print(f"   최종 처리자: {result.get('agent_id', 'N/A')}")
        print(f"   핸드오프 체인: {' → '.join(result.get('handoff_chain', []))}")
        print(f"   확신도: {result.get('confidence', 0):.3f}")

        if result.get('status') == 'success':
            print(f"   ✅ 성공적으로 처리됨")
        else:
            print(f"   ⚠️ 부분적 성공 또는 오류")

    # 종합 보고서
    print(f"\n{'='*20} 시스템 분석 보고서 {'='*20}")
    report = system.get_comprehensive_report()

    handoff_stats = report["handoff_statistics"]
    print(f"\n🔄 핸드오프 통계:")
    print(f"   총 쿼리 수: {handoff_stats['total_queries']}")
    print(f"   성공적 핸드오프: {handoff_stats['successful_handoffs']}")
    print(f"   평균 체인 길이: {handoff_stats['average_handoff_chain_length']:.2f}")
    print(f"   가장 활발한 에이전트: {handoff_stats['most_active_agent']}")

    print(f"\n👥 에이전트 활동도:")
    for agent_id, count in report["agent_handoff_counts"].items():
        print(f"   {agent_id}: {count}회 참여")

    print(f"\n✅ 향상된 피어 투 피어 패턴 데모 완료!")
    print(f"💡 핵심 개선사항:")
    print(f"   🎯 정교한 도메인 분석 (키워드 가중치, 제외 키워드)")
    print(f"   📊 성능 기반 피어 선택")
    print(f"   🔄 의도적 잘못 라우팅으로 복구 능력 테스트")
    print(f"   📈 상세한 성능 추적 및 분석")

if __name__ == "__main__":
    run_enhanced_demo()