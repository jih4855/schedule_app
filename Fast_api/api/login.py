from fastapi import APIRouter, HTTPException
from schemas.user import LoginRequest
from db.session import get_db
from fastapi import Depends
from jose import jwt
from models.user import User
from datetime import datetime, timedelta
import zoneinfo
from core.config import settings
from pydantic import BaseModel




router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=TokenResponse)
def login_for_access_token(login_request: LoginRequest, db=Depends(get_db)):
    """
    사용자의 로그인 요청을 처리하고, 인증 정보가 올바르면 JWT 액세스 토큰을 반환합니다.

    Args:
        login_request (LoginRequest): 사용자명과 비밀번호가 포함된 로그인 요청.
        db (Session): 데이터베이스 세션 의존성.

    Returns:
        dict: 액세스 토큰과 토큰 타입을 포함하는 딕셔너리.
    """
    # 사용자 조회
    user = db.query(User).filter(User.username == login_request.username).first()
    
    # 사용자 정보 또는 비밀번호가 올바르지 않은 경우 예외 발생
    if not user or not user.verify_password(login_request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    expire_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire_time = datetime.now(tz=zoneinfo.ZoneInfo("UTC")) + expire_delta

    access_token = jwt.encode(
        {
            "sub": user.username,
            "exp": int(expire_time.timestamp())  # Unix 타임스탬프로 변환
        },
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    # 액세스 토큰 반환
    return TokenResponse(access_token=access_token, token_type="bearer")