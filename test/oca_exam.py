import os
import sys
# Ensure module import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.llm_agent import LLM_Agent
import dotenv

dotenv.load_dotenv()

# --- 1. LLM 클라이언트 및 에이전트 역할 정의 ---

# LLM 에이전트 인스턴스는 하나만 생성해서 모두가 공유합니다.
llm_client = LLM_Agent(
    model_name="gemma3n", 
    provider="ollama", 
    api_key=None
)

# 토론에 참여할 에이전트들의 페르소나(시스템 프롬프트) 정의
agents = {
    "시장 분석가": "당신은 시장 트렌드와 고객 요구를 날카롭게 파악하는 전문가입니다. 데이터 기반의 현실적인 분석을 제시합니다.",
    "제품 디자이너": "당신은 사용자 경험(UX)을 최우선으로 생각하는 창의적인 제품 디자이너입니다. 혁신적이고 아름다운 디자인을 제안합니다.",
    "기술 엔지니어": "당신은 구현 가능성과 기술적 한계를 냉정하게 판단하는 현실주의 엔지니어입니다. 안정성과 확장성을 중요하게 생각합니다."
}

# 토론 순서 정의
discussion_order = ["시장 분석가", "제품 디자이너", "기술 엔지니어"]

# --- 2. '사회자(Orchestrator)' 로직 구현 ---

# 모든 대화가 기록될 '공유 대화 기록' 리스트
chat_history = []
max_turns = 3 # 총 3번의 턴(라운드) 동안 토론을 진행

# 토론 주제
topic = "20대를 위한 혁신적인 금융 앱 신규 기능 아이디어 회의"
print(f"===== 토론 시작: {topic} =====\n")
chat_history.append(f"사회자: '{topic}'에 대한 회의를 시작하겠습니다.")


# 정해진 턴 만큼 토론을 반복
for turn in range(max_turns * len(agents)):
    # 이번 턴에 발언할 에이전트를 순서대로 선택
    agent_name = discussion_order[turn % len(agents)]
    agent_system_prompt = agents[agent_name]

    print(f"--- [턴 {turn+1}] {agent_name}의 발언 차례 ---")

    # << 여기가 핵심 >>
    # 이전까지의 '모든 대화 기록'을 현재 에이전트의 입력으로 전달합니다.
    current_context = "\n".join(chat_history)
    
    prompt = f"""
    아래는 현재까지의 회의록입니다. 이 내용을 바탕으로 당신의 의견을 제시하세요.
    
    <회의록>
    {current_context}
    </회의록>
    
    이제 '{agent_name}'로서 당신의 의견을 말해주세요.
    """

    # 사용자님의 LLM_Agent를 호출하여 발언 생성
    new_statement = llm_client(
        system_prompt=agent_system_prompt,
        user_message=prompt
    )
    
    # 생성된 발언을 에이전트 이름과 함께 форматирование
    formatted_statement = f"{agent_name}: {new_statement}"
    print(formatted_statement, "\n")
    
    # 현재 발언을 '공유 대화 기록'에 추가하여 다음 에이전트가 볼 수 있게 함
    chat_history.append(formatted_statement)

print("===== 토론 종료 =====")

# --- 3. 최종 회의록을 바탕으로 결론 도출 ---

# 최종적으로 쌓인 전체 대화 기록을 요약 에이전트에게 전달
final_summary = llm_client(
    system_prompt="당신은 회의 내용을 정리하고 실행 계획을 도출하는 유능한 프로젝트 매니저입니다.",
    user_message=f"""
    다음은 전체 회의록입니다. 이 내용을 바탕으로 최종 결론과 다음 단계(Action Items)를 정리해주세요.
    
    <전체 회의록>
    {"\n".join(chat_history)}
    </전체 회의록>
    """
)

print("\n\n===== 최종 결론 및 실행 계획 =====")
print(final_summary)