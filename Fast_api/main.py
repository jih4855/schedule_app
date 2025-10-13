import sys
import os
# Add Fast_api directory to Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
logging.basicConfig(level=logging.INFO)

# 데이터베이스 초기화 (API import 전에 먼저 실행)
from Fast_api.db.session import engine, SQLALCHEMY_DATABASE_URL
from Fast_api.db.base_class import Base
from Fast_api.models import user
from Fast_api.models import schedule as schedule_model  # 이름 충돌 방지

logging.info(f"Database URL: {SQLALCHEMY_DATABASE_URL}")
Base.metadata.create_all(bind=engine)
logging.info("Database tables initialized")

# DB 파일 존재 확인
import os
db_path = SQLALCHEMY_DATABASE_URL.replace("sqlite:///", "")
logging.info(f"Database file exists: {os.path.exists(db_path)}, path: {db_path}")

# 이제 API 모듈 import (DB가 준비된 후)
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
from Fast_api.api import signup, login, schedule
from Fast_api.auth.jwt_handle import get_current_user
from Fast_api.models.user import User
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# 환경 변수로 개발/프로덕션 모드 구분
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# SlowAPI Rate Limiter 초기화
limiter = Limiter(key_func=get_remote_address)

# Rate Limit 커스텀 에러 핸들러
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Rate Limit 초과 시 단계별로 다른 메시지를 반환합니다.

    Args:
        request: FastAPI Request 객체
        exc: RateLimitExceeded 예외

    Returns:
        JSONResponse: 429 상태 코드와 함께 에러 메시지
    """
    # Rate Limit 정보 파싱
    detail_str = str(exc.detail) if hasattr(exc, 'detail') else ""

    # 기본값
    retry_after = 60
    message = "너무 많은 요청을 보냈습니다. 잠시 후 다시 시도해주세요."
    detail = "요청 제한을 초과했습니다."

    # 단계별 메시지 설정
    if "minute" in detail_str.lower() or "/minute" in detail_str:
        retry_after = 60
        message = "1분 이내에 너무 많은 요청을 보냈습니다. 1분 후 다시 시도해주세요."
        detail = "분당 요청 제한을 초과했습니다."
    elif "hour" in detail_str.lower() or "/hour" in detail_str:
        retry_after = 3600
        message = "1시간 이내에 너무 많은 요청을 보냈습니다. 1시간 후 다시 시도해주세요."
        detail = "시간당 요청 제한을 초과했습니다."
    elif "day" in detail_str.lower() or "/day" in detail_str:
        retry_after = 86400
        message = "오늘 요청 가능 횟수를 모두 사용했습니다. 내일 다시 시도해주세요."
        detail = "일일 요청 제한을 초과했습니다."

    return JSONResponse(
        status_code=429,
        headers={
            "Retry-After": str(retry_after)
        },
        content={
            "error": "요청 제한 초과",
            "message": message,
            "detail": detail,
            "retry_after_seconds": retry_after
        }
    )

# 프로덕션에서는 문서 비활성화 (기본값: 비활성화)
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None
)

# SlowAPI 설정 추가
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://localhost:3000", os.getenv("PRODUCTION_URL", "")],  # 통합 서버 및 개발 서버
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

# @app.get("/")
# async def root(current_user: User = Depends(get_current_user)):
#     return {
#         "message": "Hello World",
#         "user": current_user.username,
#         "email": current_user.email
#     }

app.include_router(signup.router, prefix="/api", tags=["signup"])
app.include_router(login.router, prefix="/api", tags=["login"])
app.include_router(schedule.router, prefix="/api", tags=["schedules"])

# 헬스체크 엔드포인트
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# React 정적 파일 서빙
# 현재 파일 기준 상위 디렉토리의 react_ui/build 경로를 절대 경로로 계산
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "react_ui", "build")
logging.info(f"STATIC_DIR: {STATIC_DIR}")
logging.info(f"STATIC_DIR exists: {os.path.exists(STATIC_DIR)}")

static_files_dir = os.path.join(STATIC_DIR, "static")
logging.info(f"Static files directory: {static_files_dir}")
logging.info(f"Static files directory exists: {os.path.exists(static_files_dir)}")

if os.path.exists(static_files_dir):
    app.mount("/static", StaticFiles(directory=static_files_dir), name="static")
    logging.info("Static files mounted successfully")
else:
    logging.error(f"Static files directory not found: {static_files_dir}")

# API 라우트가 아닌 모든 요청을 React 앱으로 전달 (SPA 라우팅)
@app.get("/{full_path:path}")
async def serve_react_app(full_path: str):
    from fastapi.responses import FileResponse

    # API 경로와 static 경로는 이미 위에서 처리됨
    # 파일이 존재하면 해당 파일 반환
    file_path = os.path.join(STATIC_DIR, full_path)
    if os.path.isfile(file_path):
        return FileResponse(file_path)

    # 파일이 없으면 index.html 반환 (React Router용)
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)