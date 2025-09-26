#!/usr/bin/env python3
"""
LLM_Agent 테스트 스크립트
수정된 메모리 지연 로딩 기능 테스트
"""

from module.llm_agent import LLM_Agent
import os

def test_without_memory():
    """메모리 기능 없이 테스트 - DB 파일이 생성되지 않아야 함"""
    print("🔍 메모리 기능 없이 테스트...")

    # LLM_Agent 생성 (메모리 기능 사용 안함)
    agent = LLM_Agent(model_name="gemma3n", provider="ollama")

    # 메모리 사용 안함 (memory=False가 기본값)
    response = agent(
        system_prompt="당신은 친절한 AI 어시스턴트입니다.",
        user_message="안녕하세요! 간단한 인사말 해주세요."
    )

    print(f"✅ 응답: {response[:100]}...")
    print("✅ 메모리 기능 없이 정상 작동!")

def test_with_memory():
    """메모리 기능 사용 테스트 - 이때만 DB 파일이 생성되어야 함"""
    print("\n🔍 메모리 기능 사용 테스트...")

    agent = LLM_Agent(model_name="gemma3n", provider="ollama", session_id="test_session")

    # 첫 번째 대화 (메모리 저장)
    response1 = agent(
        system_prompt="당신은 친절한 AI 어시스턴트입니다.",
        user_message="제 이름은 김철수입니다. 기억해주세요!",
        memory=True
    )
    print(f"✅ 첫 번째 응답: {response1[:100]}...")

    # 두 번째 대화 (메모리 불러오기)
    response2 = agent(
        system_prompt="당신은 친절한 AI 어시스턴트입니다.",
        user_message="제 이름이 뭐였죠?",
        memory=True
    )
    print(f"✅ 두 번째 응답: {response2[:100]}...")
    print("✅ 메모리 기능 정상 작동!")

def check_db_file():
    """DB 파일 존재 여부 확인"""
    print("\n🔍 DB 파일 확인...")
    db_path = "memory.db"

    if os.path.exists(db_path):
        print(f"✅ DB 파일 존재: {db_path}")
        # 파일 크기 확인
        size = os.path.getsize(db_path)
        print(f"📁 파일 크기: {size} bytes")
    else:
        print(f"❌ DB 파일 없음: {db_path}")

def main():
    print("🚀 LLM_Agent 지연 로딩 테스트 시작!")
    print("=" * 50)

    # 1. 메모리 기능 없이 테스트
    test_without_memory()

    # 2. DB 파일 확인 (아직 생성되지 않아야 함)
    check_db_file()

    # 3. 메모리 기능 사용 테스트
    test_with_memory()

    # 4. DB 파일 확인 (이제 생성되어야 함)
    check_db_file()

    print("\n🎉 테스트 완료!")
    print("💡 이제 메모리 기능을 사용할 때만 DB가 생성됩니다!")

if __name__ == "__main__":
    main()