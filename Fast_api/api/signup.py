import asyncio
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from Fast_api.schemas.user import UserCreate, UserSchema
from Fast_api.services.user_service import get_user_by, create_user
from passlib.context import CryptContext
from Fast_api.db.session import get_db


router = APIRouter()

@router.post("/signup", response_model=UserSchema)
async def signup(user: UserCreate, db: Session = Depends(get_db)):
    user_info = get_user_by(db, email=user.email)
    user_email = user_info.email if user_info else None

    if user_email == user.email:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        loop = asyncio.get_event_loop()
        new_user = await loop.run_in_executor(
            None,
            create_user,
            db,
            user
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="중복된 사용자 이름입니다.")
    return new_user
