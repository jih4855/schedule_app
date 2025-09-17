import os
import re

class Text_tool:
    def __init__(self, chunk_size=1000, overlap=0, max_length=None):
        self.chunk_size = chunk_size
        self.overlap = overlap
        self.max_length = max_length

    
    def split_text_with_overlap(self, text):
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

    def safe_filename(self, filename):
        """파일명을 안전하게 변환"""
        # 특수문자 제거 및 공백을 언더스코어로 변경
        safe_name = re.sub(r'[<>:"/\\|?*]', '', filename)
        safe_name = re.sub(r'[\'",.]', '', safe_name)
        safe_name = re.sub(r'\s+', '_', safe_name)

        # 길이 제한
        if len(safe_name) > self.max_length:
            safe_name = safe_name[:self.max_length]

        return safe_name

  #음성파일을 텍스트로 변환하고 저장할 폴더 생성하기
    def make_a_folder(self, filename):
        safe_filename = self.safe_filename(filename)
        self.result_folder = safe_filename
        if not os.path.exists(self.result_folder):
            os.makedirs(self.result_folder)
            print(f"Folder '{self.result_folder}' created successfully.")
        else:
            print(f"Folder '{self.result_folder}' already exists.")
