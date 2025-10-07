from jose import jwt, JWTError
from fastapi import HTTPException, status
from core.config import settings
from datetime import datetime
import zoneinfo

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

def extract_token_from_header(authorization: str):
    """
    Authorization 헤더에서 Bearer 토큰을 추출합니다.
    
    Args:
        authorization (str): Authorization 헤더 문자열.

    Returns:
        str: 추출된 토큰 문자열.
    """
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Bearer 토큰이 아닙니다",
                    headers={"WWW-Authenticate": "Bearer"},
                )
            return token
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="잘못된 Authorization 헤더 형식입니다",
            headers={"WWW-Authenticate": "Bearer"},
        )