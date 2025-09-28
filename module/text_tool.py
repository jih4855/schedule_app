import os
import re
import json

class Text_tool:
    def __init__(self, chunk_size=1000, overlap=0, max_length=None):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_length = max_length


    def split_text_with_overlap(self, text: str) -> list[str]:
        """
        텍스트를 겹침을 포함해서 청크로 분할
        """
        chunks = []
        start = 0

        while start < len(text):
            # 현재 청크의 끝 위치 계산
            end = start + self.chunk_size

            # 텍스트가 남아있으면
            if end < len(text):
                # 문장 경계에서 자르기 (더 자연스럽게)
                # 마지막 문장 끝 찾기
                last_period = text.rfind('.', start, end)
                last_question = text.rfind('?', start, end)
                last_exclamation = text.rfind('!', start, end)

                # 가장 뒤에 있는 문장 끝 찾기
                sentence_end = max(last_period, last_question, last_exclamation)

                if sentence_end > start:
                    end = sentence_end + 1  # 문장부호 포함

            chunk = text[start:end]
            chunks.append(chunk.strip())

            # 다음 청크 시작점 (겹침 고려)
            if end >= len(text):
                break
            
            start = end - self.overlap
        return chunks

    def safe_filename(self, filename: str) -> str:
        """파일명을 안전하게 변환"""
        # 특수문자 제거 및 공백을 언더스코어로 변경
        safe_name = re.sub(r'[<>:"/\\|?*]', '', filename)
        safe_name = re.sub(r'[\'",.]', '', safe_name)
        safe_name = re.sub(r'\s+', '_', safe_name)

        # 길이 제한
        if len(safe_name) > self.max_length:
            safe_name = safe_name[:self.max_length]

        return safe_name


    def save_result_json(self, final_output, output_filename: str, save_foldername: str):
        """결과를 JSON 또는 텍스트 파일로 저장"""
        safe_output_filename = self.safe_filename(output_filename)
        safe_save_foldername = self.safe_filename(save_foldername)
        if not os.path.exists(safe_save_foldername):
            os.makedirs(safe_save_foldername, exist_ok=True)

        try:
            # JSON 형태인지 확인하고 저장
            if isinstance(final_output, str):
                try:
                    #'''json ... ``` 형태의 JSON 추출 시도
                    import re
                    json_match = re.search(r'```json\s*(.*?)\s*```', final_output, re.DOTALL)
                    if json_match:
                        json_str = json_match.group(1)
                    else:
                        json_str = final_output  # 전체 문자열을 JSON으로 시도
                    json_data = json.loads(json_str)
                    filepath = os.path.join(safe_save_foldername, f"{safe_output_filename}.json")
                    with open(filepath, 'w', encoding='utf-8') as outfile:
                        json.dump(json_data, outfile, ensure_ascii=False, indent=2)
                    print(f"✅ JSON 저장 완료: {filepath}")
                    return
                except json.JSONDecodeError:
                    pass

            # JSON이 아니거나 파싱 실패 시 객체 그대로 저장
            if isinstance(final_output, (dict, list)):
                filepath = os.path.join(safe_save_foldername, f"{safe_output_filename}.json")
                with open(filepath, 'w', encoding='utf-8') as outfile:
                    json.dump(final_output, outfile, ensure_ascii=False, indent=2)
                print(f"✅ JSON 저장 완료: {filepath}")
            else:
                # 텍스트로 저장
                filepath = os.path.join(safe_save_foldername, f"{safe_output_filename}.txt")
                with open(filepath, 'w', encoding='utf-8') as outfile:
                    outfile.write(str(final_output))
                print(f"✅ 텍스트 저장 완료: {filepath}")

        except Exception as e:
            print(f"❌ 저장 오류: {e}")