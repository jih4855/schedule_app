import os
import sys
import json
import re
# Ensure module import path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.llm_agent import Multi_modal_agent
import dotenv
dotenv.load_dotenv()

def extract_json_from_response(response_text):
    """응답에서 JSON 부분만 추출하여 파싱"""
    try:
        # JSON 블록 찾기 (```json ... ``` 형태)
        json_match = re.search(r'```json\s*(.*?)\s*```', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # 중괄호로 시작하는 JSON 찾기
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
            else:
                return None, "JSON 형태를 찾을 수 없습니다."

        # JSON 파싱
        parsed_json = json.loads(json_str)
        return parsed_json, None

    except json.JSONDecodeError as e:
        return None, f"JSON 파싱 오류: {e}"
    except Exception as e:
        return None, f"예상치 못한 오류: {e}"

model_name = 'gemma3:12b'  # 사용할 모델명을 입력하세요
system_prompt = '''당신은 영수증 분석 전문가입니다.
영수증을 보고 다음 JSON 형태로 정확히 반환해주세요:
{
  "store_name": "매장명",
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "items": [
    {"name": "상품명", "price": 가격, "quantity": 수량}
  ],
  "subtotal": 소계,
  "tax": 세금,
  "total": 총액,
  "payment_method": "결제방법"
}'''

user_prompt = '다음 영수증의 세부내역을 위의 JSON 형태로 정확히 반환해주세요. JSON만 반환하고 다른 설명은 추가하지 마세요.'
image_path = "image.png"
provider = 'ollama'  # 현재 사용가능한 provier는 "ollama", "openai","genai(gemini)"입니다


agent = Multi_modal_agent(model_name, provider, api_key=None)
response = agent(system_prompt, user_prompt, image_path=image_path, task=None)

print("=== 원본 응답 ===")
print(response)
print("\n" + "="*50)

# JSON 파싱 시도
parsed_data, error = extract_json_from_response(response)
with open("parsed_receipt.json", "w", encoding="utf-8") as f:
    if parsed_data:
        json.dump(parsed_data, f, ensure_ascii=False, indent=2)
    else:
        f.write(response)  # 파싱 실패 시 원본 텍스트 저장

if parsed_data:
    print("=== 파싱된 JSON ===")
    print(json.dumps(parsed_data, ensure_ascii=False, indent=2))

    print("\n=== 사용 예시 ===")
    print(f"매장명: {parsed_data.get('store_name', 'N/A')}")
    print(f"총액: {parsed_data.get('total', 'N/A')}원")
    print(f"상품 개수: {len(parsed_data.get('items', []))}")
else:
    print(f"=== JSON 파싱 실패 ===")
    print(f"오류: {error}")
    print("원본 텍스트 그대로 사용하세요.")