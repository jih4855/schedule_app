from sqlalchemy import Column, Integer, String
from Fast_api.db.base_class import Base
from sqlalchemy import DateTime
from datetime import datetime
from sqlalchemy import DateTime
from datetime import datetime
from zoneinfo import ZoneInfo
from passlib.context import CryptContext

# KST 타임존 정의
KST = ZoneInfo('Asia/Seoul')
time_stamp = Column(DateTime, default=lambda: datetime.now(KST))

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    time_stamp = Column(DateTime, default=lambda: datetime.now(KST))  # 한국 시간으로 기본값 설정



    def verify_password(self, password: str) -> bool:
        pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
        """저장된 해시와 입력된 비밀번호를 비교"""
        return pwd_context.verify(password, self.hashed_password)
