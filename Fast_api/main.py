import sys
import os
# Add Fast_api directory to Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Dict, Any, Optional
import logging
from Fast_api.api import signup, login, schedule
from Fast_api.auth.jwt_handle import get_current_user
from Fast_api.models.user import User

# 환경 변수로 개발/프로덕션 모드 구분
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
IS_PRODUCTION = ENVIRONMENT == "production"

# 프로덕션에서는 문서 비활성화
app = FastAPI(
    docs_url="/docs" if not IS_PRODUCTION else None,
    redoc_url="/redoc" if not IS_PRODUCTION else None,
    openapi_url="/openapi.json" if not IS_PRODUCTION else None
)
logging.basicConfig(level=logging.INFO)

# 데이터베이스 초기화 (테이블 자동 생성)
from Fast_api.db.session import engine
from Fast_api.db.base_class import Base
from Fast_api.models import user
from Fast_api.models import schedule as schedule_model  # 이름 충돌 방지

Base.metadata.create_all(bind=engine)
logging.info("Database tables initialized")

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

# React 정적 파일 서빙 (반드시 API 라우터 설정 후에 추가)
# 현재 파일 기준 상위 디렉토리의 react_ui/build 경로를 절대 경로로 계산
STATIC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "react_ui", "build")
app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)