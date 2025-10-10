# in: app/core/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # .env 파일에서 읽어올 변수들을 타입 힌트와 함께 선언합니다.
    # Pydantic이 자동으로 값을 읽어와 타입이 맞는지 검증까지 해줍니다.
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    model_name: str = ""
    provider: str = ""
    api_key: str = ""

    # Pydantic V2의 설정 방식:
    # model_config에 SettingsConfigDict를 사용하여 설정을 전달합니다.
    model_config = SettingsConfigDict(
        env_file="./.env",
        env_file_encoding="utf-8",
        extra="allow"  # .env 파일의 추가 필드 허용
    )

# 다른 파일에서 쉽게 가져다 쓸 수 있도록 settings 객체를 생성합니다.
settings = Settings()