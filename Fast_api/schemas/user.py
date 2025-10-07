from pydantic import BaseModel, ConfigDict
from pydantic import EmailStr, field_validator
import re

# Fast_api/api/login.py에서 가져온 코드입니다.
class LoginRequest(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: EmailStr  # 이메일 형식 자동 검증
    password: str
    

    @field_validator('username')
    @classmethod
    def validate_username(cls, v):
        if len(v) < 3:
            raise ValueError('사용자명은 최소 3글자 이상이어야 합니다')
        if len(v) > 50:
            raise ValueError('사용자명은 50글자를 초과할 수 없습니다')
        return v
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('비밀번호는 최소 8글자 이상이어야 합니다')
        if not re.search(r'[A-Za-z]', v):
            raise ValueError('비밀번호에는 영문자가 포함되어야 합니다')
        if not re.search(r'\d', v):
            raise ValueError('비밀번호에는 숫자가 포함되어야 합니다')
        return v
    
class UserSchema(BaseModel):
    id: int
    username: str
    email: str

    # from_attributes 옵션을 사용하여 모델을 구성합니다.
    model_config = ConfigDict(from_attributes=True)

