from fastapi import APIRouter, HTTPException, Request, Response
from Fast_api.schemas.user import LoginRequest
from Fast_api.db.session import get_db
from fastapi import Depends
from Fast_api.auth.jwt_handle import create_refresh_token, create_access_token, verify_refresh_token
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
async def login_for_access_token(
    request: Request,
    login_request: LoginRequest,
    response: Response,
    db=Depends(get_db)
):
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

    # Access Token 생성
    access_token = create_access_token(user.username)

    # Refresh Token 생성 및 HttpOnly 쿠키 설정
    refresh_token = create_refresh_token(user.username)

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,  # JavaScript 접근 차단 (XSS 방어)
        secure=True if settings.ENVIRONMENT == "production" else False,  # HTTPS에서만 전송 (개발: False, 프로덕션: True)
        samesite="lax",  # CSRF 방어
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,  # 초 단위
    )

    # Access Token 반환
    return TokenResponse(access_token=access_token, token_type="bearer")


@router.post("/refresh", response_model=TokenResponse)
@limiter.limit("30/minute;200/hour;1000/day")
async def refresh_access_token(request: Request):
    """
    Refresh Token을 사용하여 새로운 Access Token을 발급합니다.

    Args:
        request (Request): FastAPI Request 객체 (쿠키 접근용)

    Returns:
        TokenResponse: 새로 발급된 Access Token

    Raises:
        HTTPException: Refresh Token이 없거나 유효하지 않은 경우
    """
    # 쿠키에서 refresh_token 읽기
    refresh_token = request.cookies.get("refresh_token")

    # refresh_token이 없으면 401 에러
    if not refresh_token:
        raise HTTPException(
            status_code=401,
            detail="Refresh token이 없습니다."
        )

    # refresh_token 검증
    username = verify_refresh_token(refresh_token)

    # 새 Access Token 생성
    new_access_token = create_access_token(username)

    # 응답 반환
    return TokenResponse(access_token=new_access_token, token_type="bearer")


@router.post("/logout")
async def logout(response: Response):
    """
    로그아웃: Refresh Token 쿠키를 제거합니다.

    Args:
        response (Response): FastAPI Response 객체

    Returns:
        dict: 로그아웃 성공 메시지
    """
    # Refresh Token 쿠키 삭제
    response.delete_cookie(
        key="refresh_token",
        httponly=True,
        secure=True if settings.ENVIRONMENT == "production" else False,  # 개발: False, 프로덕션: True
        samesite="lax"
    )

    return {"message": "로그아웃 성공"}