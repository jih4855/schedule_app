import sys
import os
# Add Fast_api directory to Python path for module imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Any, Optional
import logging
from api import signup, login, schedule
from auth.jwt_handle import get_current_user
from models.user import User

app = FastAPI()
logging.basicConfig(level=logging.INFO)

# CORS 설정 추가
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React 앱 주소
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root(current_user: User = Depends(get_current_user)):
    return {
        "message": "Hello World",
        "user": current_user.username,
        "email": current_user.email
    }

app.include_router(signup.router, prefix="/api", tags=["signup"])
app.include_router(login.router, prefix="/api", tags=["login"])
app.include_router(schedule.router, prefix="/api", tags=["schedules"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)