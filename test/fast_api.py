from jose import jwt
from datetime import datetime, timedelta
import zoneinfo

# 임시 시크릿 키 및 알고리즘, 만료 시간 정의
SECRET_KEY = "temp_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# 임시 사용자 정보
username = "testuser"

expire_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
expire_time = datetime.now(tz=zoneinfo.ZoneInfo("UTC")) + expire_delta

access_token = jwt.encode(
    {
        "sub": username,
        "exp": int(expire_time.timestamp())
    },
    SECRET_KEY,
    algorithm=ALGORITHM,
)

print(access_token)
