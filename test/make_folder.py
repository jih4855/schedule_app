#상위 경로에서 임포트
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.text_tool import Text_tool


make_folder = Text_tool(max_length=50)
make_folder.make_a_folder("This is a test folder name: with special characters!@#$%^&*()")
print(f"Result folder name: {make_folder.result_folder}")
#결과 폴더명 출력