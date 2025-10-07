# 🛡️ AI-Multi-Agent-Toolkit 보안 체크리스트

> **현재 보안 점수: 6.5/10** (개발 단계 - 배포 전 개선 필요)

## 🔴 긴급 (배포 전 필수)

### 📝 입력값 검증
- [ㅇ] 사용자명 길이 제한 (3-50자)
- [ ㅇ] 사용자명 특수문자 필터링 (`^[a-zA-Z0-9_]+$`)
- [ ㅇ] 이메일 형식 검증 (EmailStr 사용)
- [ㅇ ] 비밀번호 강도 검증 (대소문자, 숫자, 특수문자 포함)
- [ ㅇ] 비밀번호 길이 제한 (8-128자)
- [ ㅇ] SQL 인젝션 방어 확인 ✅ (SQLAlchemy ORM으로 이미 방어됨)

### 🔐 파일 권한 및 민감정보
- [ ] `.env` 파일 권한 600으로 설정 (`chmod 600 Fast_api/.env`)
- [ ] 데이터베이스 파일 권한 600으로 설정 (`chmod 600 Fast_api/my_pipeline_service.db`)
- [ ] `.gitignore`에 `.env` 파일 포함 확인 ✅ (이미 포함됨)
- [ ] 프로덕션용 SECRET_KEY 새로 생성 (현재: 개발용)

### 🔑 JWT 보안
- [x] SECRET_KEY 충분한 길이 확인 ✅ (64자 - 양호)
- [ ] 프로덕션 환경용 새 SECRET_KEY 생성 (현재: temp_secret_key - 변경 필요)
- [x] 토큰 만료 시간 검토 (현재: 30분 - 적절함)
- [x] JWT 알고리즘 보안성 확인 ✅ (HS256 - 안전함)
- [x] JWT 헤더 자동 생성 확인 ✅ (typ: JWT, alg: HS256)
- [ ] 프론트엔드 전체 API 래퍼 구현 (토큰 자동 포함)

## 🟡 중요 (1개월 내)

### 🌐 API 보안
- [ ] CORS 설정 제한 (현재: 모든 메소드/헤더 허용)
- [ ] Rate Limiting 구현 (로그인 시도 제한: 5회/분)
- [ ] HTTPS 강제 적용
- [ ] 보안 헤더 추가 (HSTS, CSP, X-Frame-Options)

### ⚠️ 에러 처리
- [ ] 민감한 정보 노출 방지
- [ ] 사용자 열거 공격 방지 (이메일 존재 여부 숨김)
- [ ] 일관된 에러 메시지 정책
- [ ] 보안 이벤트 로깅 시스템 구축

### 🔄 세션 관리
- [ ] JWT 토큰 무효화 기능 (블랙리스트)
- [ ] 로그아웃 API 구현
- [ ] 토큰 갱신 로직 구현
- [ ] 동시 로그인 세션 제한

## 🟢 권장 (장기 개선)

### 🗃️ 데이터베이스
- [ ] SQLite → PostgreSQL/MySQL 이전
- [ ] 데이터베이스 연결 풀링 구현
- [ ] 정기 백업 및 복구 계획 수립
- [ ] 데이터 암호화 (저장 시/전송 시)

### 📊 모니터링 및 로깅
- [ ] 보안 이벤트 로깅 시스템
- [ ] 의심스러운 활동 탐지 알림
- [ ] 정기 보안 감사 프로세스
- [ ] 성능 모니터링 및 이상 탐지

### 🔒 고급 보안
- [ ] 2단계 인증 (2FA) 구현
- [ ] 계정 잠금 정책 (실패 시도 후)
- [ ] 비밀번호 히스토리 관리
- [ ] 정기 비밀번호 변경 정책

---

## 📝 최근 구현 현황 (2025-10-03)

### ✅ 완료된 항목
- **JWT 인증 시스템**: 로그인/회원가입 API 구현 완료
- **토큰 구조 이해**: 헤더 자동생성, 페이로드(sub, exp) 확인
- **보안 설정**: CORS 미들웨어 적용, 비밀번호 해싱(bcrypt)

### 🔄 진행 중
- **프론트엔드 JWT 통합**: API 래퍼 클래스 설계 완료, 구현 대기
- **토큰 관리 전략**: localStorage vs sessionStorage vs HTTP-only 쿠키 검토

### ⚠️ 주요 보안 이슈
1. **SECRET_KEY**: 현재 `temp_secret_key` 사용 중 - 즉시 변경 필요
2. **API 래퍼**: 모든 요청에 자동 Authorization 헤더 포함 필요
3. **토큰 만료 처리**: 401 에러 시 자동 로그아웃 로직 필요

---

## 💻 구현 코드 예제

### 1. 입력값 검증 강화
```python
# Fast_api/schemas/user.py
from pydantic import BaseModel, EmailStr, Field, validator
import re

class UserCreate(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=50,
        pattern="^[a-zA-Z0-9_]+$"
    )
    email: EmailStr  # 자동 이메일 형식 검증
    password: str = Field(min_length=8, max_length=128)

    @validator('password')
    def validate_password_strength(cls, v):
        pattern = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]"
        if not re.search(pattern, v):
            raise ValueError(
                '비밀번호는 대소문자, 숫자, 특수문자를 포함해야 합니다'
            )
        return v

class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    password: str = Field(min_length=1, max_length=128)
```

### 2. CORS 설정 제한
```python
# Fast_api/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # 개발 환경
        "https://yourdomain.com"  # 프로덕션 환경
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # 필요한 메소드만
    allow_headers=["Content-Type", "Authorization"],  # 필요한 헤더만
)
```

### 3. Rate Limiting 구현
```python
# Fast_api/main.py
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Fast_api/api/login.py
from slowapi import Limiter

@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")  # 분당 5회 로그인 시도 제한
def login_for_access_token(
    request: Request,  # Rate limiting을 위해 필요
    login_request: LoginRequest,
    db=Depends(get_db)
):
    # 로그인 로직...
```

### 4. 보안 헤더 추가
```python
# Fast_api/main.py
from fastapi.middleware.security import SecurityHeaders

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response
```

### 5. 프론트엔드 JWT API 래퍼 (권장 구현)
```javascript
// react_ui/src/utils/apiClient.js
class APIClient {
  constructor() {
    this.baseURL = 'http://localhost:8000/api';
    this.token = localStorage.getItem('token');
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const config = {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...(this.token && { 'Authorization': `Bearer ${this.token}` }),
        ...options.headers,
      },
    };

    const response = await fetch(url, config);

    // 401 에러 시 자동 로그아웃
    if (response.status === 401) {
      this.logout();
      throw new Error('Unauthorized');
    }

    return response.json();
  }

  setToken(token) {
    this.token = token;
    localStorage.setItem('token', token);
  }

  logout() {
    this.token = null;
    localStorage.removeItem('token');
    window.location.href = '/login';
  }
}

export const apiClient = new APIClient();

// 사용 예시:
// const loginData = await apiClient.request('/login', {
//   method: 'POST',
//   body: JSON.stringify({username, password})
// });
// apiClient.setToken(loginData.access_token);
```

### 6. 파일 권한 수정 스크립트
```bash
#!/bin/bash
# scripts/secure_files.sh

echo "파일 권한 보안 설정 중..."

# .env 파일 권한 설정 (소유자만 읽기/쓰기)
chmod 600 Fast_api/.env
echo "✅ .env 파일 권한 설정 완료"

# 데이터베이스 파일 권한 설정
chmod 600 Fast_api/*.db
echo "✅ 데이터베이스 파일 권한 설정 완료"

# 권한 확인
echo "📋 현재 파일 권한:"
ls -la Fast_api/.env Fast_api/*.db

echo "🔒 보안 설정 완료!"
```

---

## 🚀 배포 전 최종 점검

### 필수 확인사항
1. **환경 변수**: 프로덕션용 SECRET_KEY 설정
2. **HTTPS**: SSL/TLS 인증서 적용
3. **방화벽**: 필요한 포트만 개방 (80, 443)
4. **모니터링**: 로그 수집 및 알림 시스템 구성
5. **백업**: 데이터베이스 정기 백업 설정

### 테스트 명령어
```bash
# SQL 인젝션 테스트
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"username": "admin'\'' OR '\''1'\''='\''1", "password": "test"}'

# Rate Limiting 테스트
for i in {1..10}; do
  curl -X POST "http://localhost:8000/api/login" \
    -H "Content-Type: application/json" \
    -d '{"username": "test", "password": "wrong"}' &
done
```

---

## 📞 문제 발생 시 대응

### 보안 사고 대응 절차
1. **즉시 조치**: 영향받은 서비스 격리
2. **로그 분석**: 공격 벡터 및 범위 파악
3. **패치 적용**: 취약점 즉시 수정
4. **모니터링 강화**: 추가 공격 시도 감시
5. **사후 검토**: 보안 정책 개선

### 긴급 연락처
- **개발팀**: [연락처 입력]
- **보안팀**: [연락처 입력]
- **인프라팀**: [연락처 입력]

---

> **마지막 업데이트**: 2025-10-03
> **다음 점검 예정**: 프로덕션 배포 전
> **담당자**: 개발팀

**⚠️ 이 체크리스트는 배포 전에 반드시 완료해야 할 보안 요구사항입니다!**