
#모듈 경로 설정
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.text_tool import Text_tool
import requests

class Send_to_discord:
    def __init__(self, base_url:str, chunk_size:int=1900, overlap:int=0):
        self.base_url = base_url
        self.chunk = Text_tool(chunk_size=chunk_size, overlap=overlap)

    def send_message(self, message:str):

        chunks = self.chunk.split_text_with_overlap(message)
        for i, chunk in enumerate(chunks):
            payload = {"content": chunk}
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.base_url, json=payload, headers=headers)

        if response.status_code == 204:
            print(f"Message chunk {i} sent successfully.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")