import json
import sqlite3


class MemoryManager:
    def __init__(self, db_path = "memory.db", session_id=None, messages=None):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.session_id = session_id
        self.messages = messages if messages is not None else []

    def create_table(self):
        """
        'conversations' 테이블이 없으면 새로 생성합니다.
        - session_id: 각 대화 세션을 구분하는 고유 ID
        - history: 대화 기록 전체를 JSON 텍스트 형태로 저장
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                session_id TEXT PRIMARY KEY,
                history TEXT
            )
        ''')
        self.conn.commit()
    
    def get_history(self, session_id):
        """
        특정 세션의 대화 기록을 가져옵니다.
        Args:
            session_id (str): 대화 세션의 고유 ID
        Returns:
            list: 대화 기록을 담은 리스트
        """
        self.cursor.execute("SELECT history FROM conversations WHERE session_id = ?", (session_id,))
        result = self.cursor.fetchone()

        if result:
            return json.loads(result[0])
        else:
            return []

    def save_history(self, session_id, messages):
        """
        대화 기록을 저장합니다.
        Args:
            messages(list): 대화 기록
        """
        history_json = json.dumps(messages, ensure_ascii=False)
        self.cursor.execute('''
            INSERT OR REPLACE INTO conversations (session_id, history)
            VALUES (?, ?)
            ''', (session_id, history_json))
        self.conn.commit()
        
    def close(self):
        """
        데이터베이스 연결을 닫습니다.
        """
        self.conn.close()