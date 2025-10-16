# AI Schedule Manager

자연어 입력으로 일정을 관리할 수 있는 웹 애플리케이션입니다.

## 주요 기능

- **자연어 일정 입력**: "내일 오후 2시에 회의" 같은 자연어로 일정 등록
- **달력 뷰**: 월간 달력으로 일정 한눈에 확인
- **일정 관리**: 일정 추가, 수정, 삭제, 완료 체크
- **주간 요약**: 이번 주 일정 통계 및 완료율 확인
- **JWT 인증**: 안전한 사용자 인증 및 세션 관리

## 기술 스택

### Backend
- **FastAPI**: Python 기반 고성능 웹 프레임워크
- **SQLAlchemy**: ORM (데이터베이스: SQLite)
- **JWT**: 토큰 기반 인증
- **Google Gemini API**: 자연어 처리 (일정 파싱)

### Frontend
- **React 19**: 사용자 인터페이스
- **JavaScript**: 프로그래밍 언어
- **CSS**: 다크 모드 스타일링

## 설치 및 실행

### 1. 환경 설정

프로젝트 루트에 `.env` 파일 생성:

```bash
# JWT 설정
SECRET_KEY=your_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM 설정 (Google Gemini)
model_name=gemini-flash-lite-latest
provider=genai
api_key=your_google_api_key_here

# 배포 설정 (선택사항)
ENVIRONMENT=development
PRODUCTION_URL=
```

### 2. 백엔드 실행

```bash
# Python 가상환경 생성 및 활성화
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 서버 실행
uvicorn Fast_api.main:app --reload --host 0.0.0.0 --port 8000
```

백엔드 서버: http://localhost:8000

### 3. 프론트엔드 실행

```bash
cd react_ui

# 의존성 설치
npm install

# 개발 서버 실행
npm start
```

프론트엔드: http://localhost:3000

## 프로젝트 구조

```
AI-Multi-Agent-Toolkit/
├── Fast_api/              # 백엔드 (FastAPI)
│   ├── api/               # API 라우터
│   ├── auth/              # JWT 인증
│   ├── core/              # 설정
│   ├── db/                # 데이터베이스
│   ├── models/            # ORM 모델
│   ├── schemas/           # Pydantic 스키마
│   ├── services/          # 비즈니스 로직
│   └── main.py            # FastAPI 앱 진입점
│
└── react_ui/              # 프론트엔드 (React)
    ├── public/            # 정적 파일
    └── src/
        ├── components/    # React 컴포넌트
        │   ├── LoginForm.js
        │   ├── SignupForm.js
        │   └── SchedulePage.js
        └── App.js         # 메인 앱
```

## API 엔드포인트

### 인증
- `POST /api/signup` - 회원가입
- `POST /api/login` - 로그인
- `POST /api/logout` - 로그아웃
- `POST /api/refresh` - 토큰 갱신

### 일정
- `GET /api/schedules` - 일정 목록 조회
- `POST /api/schedules` - 일정 생성 (자연어 입력)
- `PUT /api/schedules/{id}` - 일정 수정
- `DELETE /api/schedules/{id}` - 일정 삭제

## 배포

### Cloudtype (추천)

1. GitHub 저장소 연동
2. `integrated-deploy` 브랜치 선택
3. 환경변수 설정 (.env 내용)
4. Start Command: `uvicorn Fast_api.main:app --host 0.0.0.0 --port 8000`

## 개발 환경

- Python 3.9+
- Node.js 16+
- npm 8+
