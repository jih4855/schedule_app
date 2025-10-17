# 테스트 가이드

## 설치

```bash
pip install pytest pytest-asyncio httpx
```

## 실행

```bash
# 전체 테스트 실행
pytest

# 특정 파일만 실행
pytest tests/test_auth.py

# 특정 테스트만 실행
pytest tests/test_auth.py::TestLogin::test_login_success

# 상세 출력
pytest -v

# 커버리지 확인 (설치 필요: pip install pytest-cov)
pytest --cov=Fast_api --cov-report=html
```

## 테스트 구조

```
tests/
├── __init__.py
├── conftest.py              # 공통 fixture 정의
├── test_auth.py             # 인증 테스트
├── test_schedule.py         # 일정 CRUD 테스트
└── test_security.py         # 보안 테스트
```

## 주요 Fixture

### `db_session`
- 각 테스트마다 새로운 데이터베이스 세션 생성
- 테스트 후 자동 정리

### `client`
- FastAPI TestClient 생성
- 데이터베이스 의존성 오버라이드

### `test_user`
- 테스트용 사용자 자동 생성
- username: testuser
- password: testpassword123

### `auth_headers`
- 인증된 사용자의 JWT 토큰 헤더
- 보호된 엔드포인트 테스트에 사용

## 테스트 커버리지

### 인증 (test_auth.py)
- ✅ 회원가입 (정상, 중복 이메일, 중복 사용자명)
- ✅ 로그인 (정상, 잘못된 비밀번호, 존재하지 않는 사용자)
- ✅ 타이밍 공격 방어
- ✅ JWT 토큰 검증
- ✅ Refresh Token 갱신
- ✅ 로그아웃
- ✅ Rate Limiting

### 일정 (test_schedule.py)
- ✅ CRUD 전체 (생성, 조회, 수정, 삭제)
- ✅ 권한 검증 (다른 사용자 일정 접근 불가)
- ✅ 자연어 파싱
- ✅ 프롬프트 인젝션 방어
- ✅ 입력 검증 (길이 제한)

### 보안 (test_security.py)
- ✅ Path Traversal 방어
- ✅ SQL Injection 방어
- ✅ XSS 방어
- ✅ CSRF 방어 (SameSite 쿠키)
- ✅ Rate Limiting 우회 방지

## 주의사항

### 1. LLM API 호출 테스트
`test_schedule.py`의 자연어 파싱 테스트는 실제 LLM API를 호출합니다.
프로덕션에서는 Mock으로 대체해야 합니다.

```python
# Mock 예시 (pytest-mock 설치 필요)
@pytest.mark.asyncio
async def test_parse_with_mock(client, auth_headers, mocker):
    mock_llm = mocker.patch('Fast_api.services.llm_schedule_parser.parse_natural_language_to_schedules')
    mock_llm.return_value = [
        ScheduleCreate(title="회의", scheduled_at=datetime.now())
    ]
    # 테스트 진행...
```

### 2. Rate Limiting 테스트
Rate Limiting 테스트는 실제로 요청을 여러 번 보내므로 느릴 수 있습니다.

### 3. 타이밍 공격 테스트
타이밍 공격 방어 테스트는 시스템 부하에 따라 실패할 수 있습니다.
CI/CD 환경에서는 스킵하는 것을 권장합니다.

```python
@pytest.mark.skip(reason="CI 환경에서 불안정")
def test_timing_attack_defense(self, client, test_user):
    # ...
```

## 개선 사항

### 구현 필요한 테스트
1. **DB 마이그레이션 테스트**
2. **성능 테스트** (부하 테스트, 병목 구간)
3. **통합 테스트** (전체 플로우 E2E)
4. **Mock 기반 LLM 테스트**

### 테스트 커버리지 목표
- 현재: 0%
- 목표: 80% 이상

```bash
# 커버리지 확인
pytest --cov=Fast_api --cov-report=term-missing
```
