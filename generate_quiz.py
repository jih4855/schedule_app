from module.llm_agent import LLM_Agent
import dotenv
from module.audio_tool import Audio
from module.text_tool import Text_tool
import os
import json

def main():
    print("오디오 에이전트 시작...")

    # --- 1. 오디오 파일 다운로드 및 텍스트 변환 ---
    print("\n1단계: 오디오 다운로드 및 변환")

    # Audio 인스턴스 생성
    text_output = "test_text"
    source_file = "source_test"

    audio_processor = Audio(
        text_output=text_output,
        source_file=source_file
    )

    urls = [
        "https://youtu.be/KSC8CQCMuvk?si=TtSPawZJPeKClfTe"  # 여기에 실제 YouTube URL을 넣으세요.
    ]

    try:
        # 오디오 다운로드
        audio_processor.download_youtube_audio(urls=urls)

        # 텍스트 변환
        result = audio_processor.transcribe_audio(
            whisper_model="small"
)
        print(f"변환 완료: {result}")

    except Exception as e:
        print(f"오디오 처리 오류: {e}")
        return

    # --- 2. 텍스트 청크 분할 및 멀티 에이전트 처리 ---
    print("\n2단계: LLM 에이전트 처리")

    # 폴더 존재 확인
    text_folder = text_output
    if not os.path.exists(text_folder):
        print(f"오류: {text_folder} 폴더가 없습니다.")
        return

    # json 파일 찾기 및 정렬
    json_files = sorted([
        os.path.join(text_folder, f)
        for f in os.listdir(text_folder)
        if f.endswith('.json')
    ])

    if not json_files:
        print(f"{text_folder} 폴더에 JSON 파일이 없습니다.")
        return

    print(f"발견된 JSON 파일: {len(json_files)}개")

    dotenv.load_dotenv()
    # LLM 에이전트 생성 (변수명 변경!)
    llm_agent = LLM_Agent(model_name="gemini-2.5-flash", provider="genai", api_key=os.getenv("GENAI_API_KEY"))

    # 에이전트 정의
    agent_user_prompt = {
        "agent1": "주어진 텍스트에서 기출문제 출제에 활용할 수 있는 핵심 개념과 용어를 추출하세요. 각 개념과 용어는 명확하고 구체적으로 추출하되, 시험 문제로 만들 수 있는 중요한 내용들을 중심으로 선별하세요.(중요: 키워드 중심으로 추출하고, 너무 일반적이거나 사소한 내용은 제외하세요.) 다음 JSON 형식으로 정확히 생성하세요: {'concepts_and_terms': ['개념1', '개념2', ...]} 중요: 반드시 RAW DATA 내에서 추출하세요.",

        "agent2": "앞서 추출된 개념과 용어에 해당하는 내용을 바탕으로 4지선다 객관식 문제를 생성하세요. 각 문제는 실제 기출문제 수준의 난이도와 형식을 갖춰야 합니다. 다음 JSON 형식으로 정확히 생성하세요: [{'question': '문제 내용', 'options': ['선택지1', '선택지2', '선택지3', '선택지4'], 'answer': '정답', 'explanation': '상세한 해설'}]. 중요: 반드시 RAW DATA 내에서 추출하세요.",

        "agent3": """
        agent2가 생성한 문제들을 검토하고, 다음 사항들을 확인 및 수정하세요:
        1. 오타 및 문법 오류 수정
        2. 논리적 오류 및 모호한 표현 수정
        3. 원본데이터가 잘못되었다고 의심되는 경우 검토가 필요한 문제 목록 작성
        최종 결과를 JSON 형식으로 출력하세요.
        중요: 모든 문자열에 큰따옴표(")만 사용하고, JSON 외 다른 텍스트는 절대 포함하지 
        마세요.
        중요: 반드시 RAW DATA 내에서 추출하세요.

        {"concepts_and_terms": ["개념1", "개념2"], "questions": [{"question": "문제내용",
        "options": ["선택1", "선택2", "선택3", "선택4"], "answer": "정답", "explanation":
        "해설내용"}],"검토가 필요한 문제 목록(이유를 상세히 기재):": ["문제1", "문제2"], "오타 및 수정사항": ["수정1(원표기)", "수정2(원표기)"]}
        """
    }

    agent_system_prompt = {
        "agent1": "당신은 교육 전문가입니다. 주어진 텍스트에서 중요한 개념과 용어를 추출하는 역할을 합니다.",
        "agent2": "당신은 시험 문제 출제 전문가입니다. 주어진 개념과 용어를 바탕으로 객관식 시험 문제를 출제하는 역할을 합니다.",
        "agent3": "당신은 교정 전문가입니다. 주어진 텍스트의 오타, 문법, 논리적 오류를 검토하고 수정하는 역할을 합니다."
    }

    order = ["agent1", "agent2", "agent3"]

    # 텍스트 도구 생성
    text_tool = Text_tool(chunk_size=2000, overlap=200, max_length= 100)
    all_chunks = []

    # 모든 JSON 파일 읽고 청크 분할
    for json_file in json_files:
        try:
            print(f"읽는 중: {json_file}")
            with open(json_file, 'r', encoding='utf-8') as file:
                json_content = json.load(file)

            chunks = text_tool.split_text_with_overlap(json_content.get("text", ""))
            all_chunks.extend(chunks)
            print(f"{len(chunks)}개 청크 생성")

        except Exception as e:
            print(f"파일 읽기 오류 ({json_file}): {e}")
            continue

    if not all_chunks:
        print("처리할 청크가 없습니다.")
        return

    print(f"\n총 {len(all_chunks)}개 청크 처리 시작")

    # 각 청크에 대해 에이전트 순차 실행
    for i, chunk in enumerate(all_chunks):
        print(f"\n=== 청크 {i+1}/{len(all_chunks)} 처리 중 ===")
              # 청크 내용 확인 (추가!)
        print(f"청크 내용 (처음 200자): {chunk[:200]}...")
        print(f"청크 길이: {len(chunk)}")

        try:
            # 순차적으로 에이전트 실행 (멀티 에이전트 방식)
            agent_responses = {}
            current_input = chunk
            
            for agent_name in order:
                print(f"{agent_name} 실행 중...")
                response = llm_agent(
                    agent_system_prompt[agent_name],
                    agent_user_prompt[agent_name],
                    task = current_input
                ) 
                agent_responses[agent_name] = response
                current_input = response  # 다음 에이전트의 입력으로 사용
                print(f"=== {agent_name} 응답 (일부) ===")
                print(response)
                print(f"{agent_name} 완료")

            # agent3의 응답을 최종 결과로 사용 및 저장
            final_output = agent_responses["agent3"]
            print(f"\n=== 최종 결과 (청크 {i+1}) ===")
            print(final_output[:500] + "..." if len(str(final_output)) > 500 else final_output)

            # 파일 저장
            output_filename = f"final_output_chunk_{i+1}"
            save_foldername = "final_outputs_test"

            text_tool.save_result_json(final_output, output_filename, save_foldername)

        except Exception as e:
            print(f"청크 {i+1} 처리 오류: {e}")
            continue

    print("\n모든 처리 완료!")

if __name__ == "__main__":
    main()