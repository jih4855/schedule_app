from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schemas.user import UserCreate, UserSchema
from services.user_service import get_user_by, create_user
from passlib.context import CryptContext
from db.session import get_db


router = APIRouter()

@router.post("/signup", response_model=UserSchema)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    user_info = get_user_by(db, email=user.email)
    user_email = user_info.email if user_info else None

    if user_email == user.email:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        new_user = create_user(db, user=user)
    except Exception as e:
        raise HTTPException(status_code=400, detail="중복된 사용자 이름입니다.")
    return new_user
