#모듈 경로 설정
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.text_tool import Text_tool

chunk_test = Text_tool(chunk_size=100, overlap=10)
text = """Whisper는 범용 음성 인식 모델입니다. 다양한 오디오 데이터셋으로 학습되었으며, 다중 작업 모델로서 다국어 음성 인식, 음성 번역, 언어 식별을 수행할 수 있습니다. 이 접근 방식은 억양, 배경 소음, 기술 용어에 대한 강인성을 높이기 위해 설계되었습니다. 모델은 웹에서 수집한 3000시간의 라벨링된 오디오 데이터를 사용하여 지도 학습 방식으로 학습되었습니다. 아키텍처는 원시 오디오 파형을 처리하기 위해 컨볼루션 프론트엔드를 사용하는 수정된 트랜스포머 모델입니다. Whisper는 CPU에서 실행 가능한 소형 모델부터 GPU가 필요한 대형 모델까지 여러 크기로 제공됩니다. 이 모델은 오픈 소스로 공개되어 있으며, 파이썬 라이브러리나 커맨드라인 인터페이스를 통해 사용할 수 있습니다. Whisper는 전사 서비스, 음성 비서, 언어 식별 등 다양한 잠재적 응용 분야를 가지고 있습니다. 또한 음성 인식 작업을 수행하는 연구자와 개발자에게도 유용합니다."""



chunks = chunk_test.split_text_with_overlap(text)
# for i, chunk in enumerate(chunks):
#     print(f"Chunk {i+1}:\n{chunk}\n")

# print(f"Total chunks created: {len(chunks)}")

print(type(chunks))
print(type(chunks[0]))

print(chunks)
print(chunks[0])