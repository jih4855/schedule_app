"""
인증 관련 테스트 (JWT, 로그인, 회원가입)
"""
import pytest
from fastapi.testclient import TestClient
import time


class TestSignup:
    """회원가입 테스트"""

    def test_signup_success(self, client):
        """정상적인 회원가입"""
        response = client.post(
            "/api/signup",
            json={
                "username": "newuser",
                "email": "newuser@example.com",
                "password": "securepassword123"
            }
        )
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "newuser@example.com"
        assert "hashed_password" not in data  # 비밀번호는 응답에 포함 안 됨

    def test_signup_duplicate_email(self, client, test_user):
        """중복 이메일로 회원가입 시도"""
        response = client.post(
            "/api/signup",
            json={
                "username": "anotheruser",
                "email": "test@example.com",  # 이미 존재하는 이메일
                "password": "password123"
            }
        )
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_signup_duplicate_username(self, client, test_user):
        """중복 사용자명으로 회원가입 시도"""
        response = client.post(
            "/api/signup",
            json={
                "username": "testuser",  # 이미 존재하는 사용자명
                "email": "newemail@example.com",
                "password": "password123"
            }
        )
        assert response.status_code == 400


class TestLogin:
    """로그인 테스트"""

    def test_login_success(self, client, test_user):
        """정상적인 로그인"""
        response = client.post(
            "/api/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Refresh Token이 쿠키로 설정되었는지 확인
        assert "refresh_token" in response.cookies

    def test_login_wrong_password(self, client, test_user):
        """잘못된 비밀번호로 로그인"""
        response = client.post(
            "/api/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        assert response.status_code == 401
        assert "사용자명 또는 비밀번호를 확인하세요" in response.json()["detail"]

    def test_login_nonexistent_user(self, client):
        """존재하지 않는 사용자로 로그인"""
        response = client.post(
            "/api/login",
            json={"username": "nonexistent", "password": "password123"}
        )
        assert response.status_code == 401

    def test_timing_attack_defense(self, client, test_user):
        """
        타이밍 공격 방어 검증
        존재하는 사용자와 존재하지 않는 사용자의 응답 시간이 비슷해야 함
        """
        # 존재하는 사용자
        start1 = time.time()
        response1 = client.post(
            "/api/login",
            json={"username": "testuser", "password": "wrongpassword"}
        )
        time1 = time.time() - start1

        # 존재하지 않는 사용자
        start2 = time.time()
        response2 = client.post(
            "/api/login",
            json={"username": "nonexistent", "password": "wrongpassword"}
        )
        time2 = time.time() - start2

        # 두 응답 모두 401
        assert response1.status_code == 401
        assert response2.status_code == 401

        # 응답 시간 차이가 0.1초 이내 (타이밍 공격 방어 확인)
        time_diff = abs(time1 - time2)
        assert time_diff < 0.1, f"Time difference too large: {time_diff}s"


class TestJWT:
    """JWT 토큰 관련 테스트"""

    def test_access_protected_endpoint_with_valid_token(self, client, auth_headers):
        """유효한 토큰으로 보호된 엔드포인트 접근"""
        response = client.get("/api/schedules", headers=auth_headers)
        assert response.status_code == 200

    def test_access_protected_endpoint_without_token(self, client):
        """토큰 없이 보호된 엔드포인트 접근"""
        response = client.get("/api/schedules")
        assert response.status_code == 403  # FastAPI HTTPBearer가 403 반환

    def test_access_protected_endpoint_with_invalid_token(self, client):
        """잘못된 토큰으로 보호된 엔드포인트 접근"""
        response = client.get(
            "/api/schedules",
            headers={"Authorization": "Bearer invalid_token_here"}
        )
        assert response.status_code == 401

    def test_refresh_token_endpoint(self, client, test_user):
        """Refresh Token으로 새 Access Token 발급"""
        # 먼저 로그인
        login_response = client.post(
            "/api/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        assert login_response.status_code == 200

        # Refresh Token으로 새 토큰 발급
        refresh_response = client.post("/api/refresh")
        assert refresh_response.status_code == 200
        data = refresh_response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_without_cookie(self, client):
        """Refresh Token 쿠키 없이 갱신 시도"""
        response = client.post("/api/refresh")
        assert response.status_code == 401
        assert "Refresh token이 없습니다" in response.json()["detail"]


class TestLogout:
    """로그아웃 테스트"""

    def test_logout_success(self, client, test_user):
        """정상적인 로그아웃"""
        # 먼저 로그인
        login_response = client.post(
            "/api/login",
            json={"username": "testuser", "password": "testpassword123"}
        )
        assert login_response.status_code == 200

        # 로그아웃
        logout_response = client.post("/api/logout")
        assert logout_response.status_code == 200
        assert "로그아웃 성공" in logout_response.json()["message"]

        # Refresh Token 쿠키가 삭제되었는지 확인
        # (TestClient는 쿠키 삭제를 명시적으로 확인하기 어려움)


class TestRateLimiting:
    """Rate Limiting 테스트"""

    def test_login_rate_limiting(self, client, test_user):
        """
        로그인 Rate Limiting 검증
        분당 10회 제한 (login.py @limiter.limit("10/minute"))
        """
        # 11번 로그인 시도
        for i in range(11):
            response = client.post(
                "/api/login",
                json={"username": "testuser", "password": "wrongpassword"}
            )
            if i < 10:
                assert response.status_code == 401  # 로그인 실패
            else:
                # 11번째 시도는 Rate Limit 걸림
                assert response.status_code == 429
                data = response.json()
                assert "요청 제한 초과" in data["error"]
                assert "retry_after_seconds" in data
