"""
pytest 설정 및 공통 fixture 정의
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext

# 테스트용 환경 변수 설정 (import 전에 먼저 설정)
os.environ["SECRET_KEY"] = "test_secret_key_for_testing_only_12345678901234567890"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"
os.environ["REFRESH_TOKEN_EXPIRE_DAYS"] = "7"
os.environ["ENVIRONMENT"] = "testing"
os.environ["model_name"] = "test-model"
os.environ["provider"] = "test-provider"
os.environ["api_key"] = "test-api-key"

# 이제 app import (환경 변수 설정 후)
from Fast_api.main import app
from Fast_api.db.base_class import Base
from Fast_api.db.session import get_db
from Fast_api.models.user import User
from Fast_api.models.schedule import Schedule

# Rate Limiting 비활성화 (테스트 환경)
# SlowAPI의 limiter를 완전히 제거
from unittest.mock import Mock
app.state.limiter = Mock()
app.state.limiter.limit = lambda *args, **kwargs: lambda func: func

# 테스트용 인메모리 SQLite 데이터베이스
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


@pytest.fixture(scope="function")
def db_session():
    """
    각 테스트마다 새로운 데이터베이스 세션을 생성하고 테스트 후 정리
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db_session):
    """
    TestClient 생성 및 데이터베이스 의존성 오버라이드
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """
    테스트용 사용자 생성
    """
    hashed_password = pwd_context.hash("testpassword123")
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=hashed_password
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """
    인증된 사용자의 JWT 토큰 헤더 생성
    """
    response = client.post(
        "/api/login",
        json={"username": "testuser", "password": "testpassword123"}
    )
    assert response.status_code == 200
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
