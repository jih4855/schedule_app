from sqlalchemy.orm import Session
from passlib.context import CryptContext
from Fast_api.models.user import User
from Fast_api.schemas.user import UserCreate, UserSchema

# bcrypt 대신 pbkdf2_sha256 사용 (Python 내장 라이브러리 기반으로 안정적)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

def get_user_by(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def create_user(db: Session, user: UserCreate):
    # pbkdf2_sha256은 길이 제한이 없으므로 바로 해싱
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user