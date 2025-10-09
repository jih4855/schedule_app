from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from core.config import settings
from datetime import datetime
import zoneinfo
from db.session import get_db
from sqlalchemy.orm import Session

def verify_token(token: str):
    """
    JWT 토큰을 검증하고, 유효한 경우 토큰의 페이로드를 반환합니다.
    
    Args:
        token (str): 검증할 JWT 토큰 문자열.

    """

    try:
        #JWT 토큰 디코딩
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing subject",
                headers={"WWW-Authenticate": "Bearer"},
            )
        #토큰 만료 시간 검증
        exp_time = payload.get("exp")
        if exp_time is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰 만료 시간이 없습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )

        current_time = datetime.now(tz=zoneinfo.ZoneInfo("UTC"))

        if datetime.fromtimestamp(exp_time, tz=zoneinfo.ZoneInfo("UTC")) < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="토큰이 만료되었습니다.",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 토큰입니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

security = HTTPBearer()

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    JWT 토큰을 검증하고 현재 사용자를 반환하는 의존성 함수.

    Args:
        credentials: HTTPBearer로부터 추출된 인증 자격 증명
        db: 데이터베이스 세션

    Returns:
        User: 인증된 사용자 객체
    """
    from models.user import User

    token = credentials.credentials
    payload = verify_token(token)
    username = payload.get("sub")

    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="사용자를 찾을 수 없습니다.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user