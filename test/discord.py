
#모듈 경로 설정
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from module.text_tool import Text_tool
import requests

class TestDiscord:
    def __init__(self, base_url, message):
        self.base_url = base_url
        self.message = message
        self.chunk = Text_tool(chunk_size=1900, overlap=0)

    def send_message(self):

        chunks = self.chunk.split_text_with_overlap(self.message)
        for i, chunk in enumerate(chunks):
            payload = {"content": chunk}
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.base_url, json=payload, headers=headers)

        if response.status_code == 204:
            print(f"Message chunk {i} sent successfully.")
        else:
            print(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    webhook_url = "your_discord_webhook_url"
    message = "Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!Hello, Discord!"
    discord_test = TestDiscord(webhook_url, message)
    discord_test.send_message()