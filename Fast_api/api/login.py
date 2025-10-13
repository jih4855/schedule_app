from fastapi import APIRouter, HTTPException, Request
from Fast_api.schemas.user import LoginRequest
from Fast_api.db.session import get_db
from fastapi import Depends
from jose import jwt
from Fast_api.models.user import User
from datetime import datetime, timedelta
import zoneinfo
from Fast_api.core.config import settings
from pydantic import BaseModel
from passlib.context import CryptContext
from slowapi import Limiter
from slowapi.util import get_remote_address
import asyncio

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

limiter = Limiter(key_func=get_remote_address)

router = APIRouter()


class TokenResponse(BaseModel):
    access_token: str
    token_type: str

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute;30/hour;100/day")
async def login_for_access_token(request: Request, login_request: LoginRequest, db=Depends(get_db)):
    """
    사용자의 로그인 요청을 처리하고, 인증 정보가 올바르면 JWT 액세스 토큰을 반환합니다.

    Args:
        login_request (LoginRequest): 사용자명과 비밀번호가 포함된 로그인 요청.
        db (Session): 데이터베이스 세션 의존성.

    Returns:
        dict: 액세스 토큰과 토큰 타입을 포함하는 딕셔너리.
    """
    # 사용자 조회 (SQLite는 빠르므로 동기로 유지)
    user = db.query(User).filter(User.username == login_request.username).first()

    # 타이밍 공격 방지: 항상 비밀번호 검증 수행
    # 비밀번호 해싱은 CPU-intensive 작업이므로 비동기 처리
    loop = asyncio.get_event_loop()

    if user:
        # user.verify_password() 메서드를 별도 스레드에서 실행 (User 모델에 정의됨)
        password_valid = await loop.run_in_executor(
            None,
            user.verify_password,  # User.verify_password(password) 실행
            login_request.password
        )
    else:
        # 사용자가 없어도 더미 해시 검증으로 동일한 시간 소요
        await loop.run_in_executor(
            None,
            pwd_context.verify,
            login_request.password,
            "$pbkdf2-sha256$29000$N2bMWQtBaA0hRAihlBJiLA$1t8iyB2A.WF/Z5JZv.lfCIhXXN8SjSNLW3pn.ljxF6g"
        )
        password_valid = False

    # 사용자 정보 또는 비밀번호가 올바르지 않은 경우 예외 발생
    if not password_valid:
        raise HTTPException(status_code=401, detail="사용자명 또는 비밀번호를 확인하세요.")

    # JWT 생성 (빠르므로 동기로 유지)
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