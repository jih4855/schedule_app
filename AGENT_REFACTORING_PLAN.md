# Agent 세분화 계획서 (Refactoring Plan)

> **작성일**: 2025-10-22
> **적용 전략**: 시나리오 2 - 중간 세분화 (균형 접근)
> **목표**: 전문성 강화 + 유지 가능한 복잡도

---

## 📊 현재 상태 분석

### 기존 Agent 구성 (4개)

| Agent | 크기 | 주요 책임 | 상태 |
|-------|------|----------|------|
| `react-frontend-guardian` | 26KB | React 컴포넌트 + API 검증 + 리팩토링 + 코딩 원칙 | 🔴 **과부하** |
| `fastapi-backend-guardian` | 11KB | FastAPI 엔드포인트 + 스키마 + 미들웨어 + 인증 | 🟡 **다소 과부하** |
| `deployment-validator` | 14KB | 배포 검증 (9가지 영역) | 🟢 **적절** |
| `frontend-css-specialist` | 6.2KB | CSS/스타일링만 | 🟢 **최적** |

### 문제점

#### 1. react-frontend-guardian 과부하 (26KB)
**현재 7가지 책임:**
1. React 컴포넌트 작성
2. API 통합 검증
3. API 스펙 보호
4. 코딩 원칙 적용 (SRP, DRY, 관심사 분리 등 7개 원칙)
5. 리팩토링 제안
6. 컴포넌트 분리
7. 에러 처리

**문제:**
- 하나의 Agent가 너무 많은 역할
- 코딩 원칙 섹션이 상세 예시로 방대함 (713줄 추가)
- 작업 흐름 복잡 (API 체크 → 코딩 원칙 체크 → 작성 → 리팩토링)

#### 2. fastapi-backend-guardian 다소 과부하
**현재 5가지 책임:**
1. API 엔드포인트 구현
2. Pydantic 스키마 정의
3. 미들웨어 설정
4. 비즈니스 로직
5. 인증/인가 시스템

**문제:**
- 인증/인가는 별도 Agent로 분리 가능
- 비즈니스 로직과 API 라우팅 분리 가능

#### 3. 책임 공백 영역
- **테스트 코드**: 어느 Agent도 담당 안 함
- **DB 스키마 설계**: fastapi-backend-guardian 금지 영역이지만 전담 Agent 없음
- **폼 검증 로직**: 프론트/백엔드 경계 모호
- **에러 처리 패턴**: 통합 전략 부재

---

## 🎯 시나리오 2: 중간 세분화 (추천)

### 목표
- 전문성 강화
- 유지 가능한 복잡도
- 명확한 책임 분리

### 최종 구성: 4개 → 11개

---

## 📋 세부 실행 계획

### Phase 1: 필수 Agent 추가 (즉시 실행) 🔴

#### 1.1 `test-writer` 생성

**파일**: `.claude/agents/test-writer.md`

**책임:**
- React 컴포넌트 테스트 (Jest + React Testing Library)
- FastAPI 엔드포인트 테스트 (pytest)
- 통합 테스트
- Mock 데이터 생성
- 테스트 커버리지 분석

**핵심 기능:**
```markdown
- 컴포넌트 렌더링 테스트
- 사용자 이벤트 시뮬레이션
- API 모킹 (MSW)
- E2E 테스트 (Playwright/Cypress)
- 스냅샷 테스트
```

**금지 영역:**
- 프로덕션 코드 수정
- 테스트 외 로직 구현

**측정 지표:**
- 테스트 커버리지 80% 이상
- 모든 critical path 테스트
- Edge case 커버

---

#### 1.2 `db-schema-designer` 생성

**파일**: `.claude/agents/db-schema-designer.md`

**책임:**
- SQLAlchemy 모델 설계
- 테이블 관계 정의 (1:N, M:N)
- 인덱스 최적화
- 제약 조건 설정 (Unique, FK, Check)
- 마이그레이션 스크립트 생성

**핵심 기능:**
```markdown
- ERD 분석 및 테이블 설계
- 정규화 적용 (3NF)
- 성능 최적화 (인덱스 전략)
- 데이터 타입 선택
- 마이그레이션 전략
```

**금지 영역:**
- API 엔드포인트 구현
- 비즈니스 로직 작성
- 프론트엔드 코드

**설계 원칙:**
- ACID 준수
- 정규화 우선, 필요 시 역정규화
- 인덱스는 쿼리 패턴 기반

---

### Phase 2: react-frontend-guardian 분할 (1주 이내) 🟡

#### 2.1 `react-component-builder` 생성

**파일**: `.claude/agents/react-component-builder.md`

**책임:**
- React 컴포넌트 작성 (함수형 컴포넌트)
- Props 정의 및 타입 검증
- 컴포넌트 컴포지션
- 코딩 원칙 적용 (SRP, DRY, 관심사 분리)

**핵심 기능:**
```markdown
- 순수 프레젠테이션 컴포넌트 작성
- 컨테이너 컴포넌트 작성
- Props drilling 방지
- 커스텀 훅 생성
- Early return 패턴
- 일관된 네이밍 규칙
```

**코딩 원칙 체크리스트:**
- [ ] 컴포넌트 200줄 이하
- [ ] 단일 책임 원칙
- [ ] 중복 코드 제거
- [ ] 5개 이상 useState 시 커스텀 훅

**금지 영역:**
- API 호출 로직 (→ react-api-integrator)
- 리팩토링 (→ react-refactoring-specialist)
- CSS 수정 (→ frontend-css-specialist)

---

#### 2.2 `react-api-integrator` 생성

**파일**: `.claude/agents/react-api-integrator.md`

**책임:**
- API 호출 로직 구현
- API 스펙 검증
- 에러 처리 (try-catch, 상태 코드)
- 인증 토큰 관리
- API 응답 데이터 변환

**핵심 기능:**
```markdown
- fetch/axios 호출 구현
- API 스펙과 프론트엔드 코드 일치 검증
- 에러 경계 설정
- 로딩 상태 관리
- 재시도 로직
- 타임아웃 설정
```

**API 검증 프로세스:**
1. 백엔드 API 스펙 확인 (엔드포인트, 메서드, 파라미터)
2. 프론트엔드 요청 형식 검증
3. 응답 데이터 구조 검증
4. 타입 불일치 확인

**금지 영역:**
- 백엔드 API 수정
- UI 컴포넌트 작성
- 비즈니스 로직 구현

---

#### 2.3 `react-refactoring-specialist` 생성

**파일**: `.claude/agents/react-refactoring-specialist.md`

**책임:**
- 기존 컴포넌트 리팩토링
- 코드 품질 분석
- 컴포넌트 분리 제안
- 성능 최적화 (useMemo, useCallback)
- 코딩 원칙 적용 검증

**핵심 기능:**
```markdown
- 대형 컴포넌트 분리 (300줄 초과 시)
- 중복 코드 추출 (DRY)
- Props drilling 해결 (Context API)
- 커스텀 훅 추출
- 유틸 함수 분리
```

**리팩토링 기준:**
- 300줄 초과: 즉시 분리 필수
- 200-300줄: 분리 강력 권장
- 5개 이상 useState: 커스텀 훅 검토
- 같은 로직 3회 반복: 함수/훅 추출

**리팩토링 제안 템플릿:**
```
## 리팩토링 필요 감지
- 파일: [파일명]
- 라인 수: [XXX줄]
- 문제점: [구체적 내용]

## 분리 제안:
1. [새 파일명] - [책임] (~XX줄)
2. [새 파일명] - [책임] (~XX줄)

## 기대 효과:
- 가독성, 재사용성, 테스트 용이성, 유지보수성
```

**금지 영역:**
- 새 컴포넌트 작성 (→ react-component-builder)
- API 로직 변경 (→ react-api-integrator)

---

### Phase 3: Backend 세분화 (2주 이내) 🟢

#### 3.1 `fastapi-api-builder` 생성

**파일**: `.claude/agents/fastapi-api-builder.md`

**책임:**
- FastAPI 라우터 구현
- Pydantic 스키마 정의
- API 엔드포인트 작성
- 요청/응답 검증
- 비즈니스 로직 구현

**핵심 기능:**
```markdown
- RESTful API 설계
- CRUD 엔드포인트 구현
- 경로 파라미터, 쿼리 파라미터 처리
- 요청 바디 검증 (Pydantic)
- 응답 모델 정의
- 상태 코드 설정
```

**API 설계 원칙:**
- RESTful 규칙 준수
- 명확한 경로 네이밍 (`/api/users`, `/api/posts`)
- HTTP 메서드 적절히 사용 (GET, POST, PUT, DELETE)
- 일관된 응답 형식

**금지 영역:**
- 인증/인가 로직 (→ fastapi-security-specialist)
- DB 스키마 변경 (→ db-schema-designer)
- 배포 설정 (→ deployment-validator)

---

#### 3.2 `fastapi-security-specialist` 생성

**파일**: `.claude/agents/fastapi-security-specialist.md`

**책임:**
- JWT 인증 구현
- OAuth2 설정
- 미들웨어 구성 (CORS, Rate Limiting)
- 권한 관리 (Role-based Access Control)
- 보안 헤더 설정

**핵심 기능:**
```markdown
- JWT 토큰 생성/검증
- Refresh Token 관리
- 비밀번호 해싱 (bcrypt)
- CORS 설정
- Rate Limiting (SlowAPI)
- HTTPS 강제
- SQL Injection 방지
- XSS 방지
```

**보안 체크리스트:**
- [ ] 비밀번호 평문 저장 금지
- [ ] JWT Secret 환경변수 관리
- [ ] CORS 화이트리스트 설정
- [ ] Rate Limiting 적용
- [ ] SQL Injection 방어
- [ ] 민감 정보 로깅 금지

**금지 영역:**
- API 엔드포인트 구현 (→ fastapi-api-builder)
- DB 스키마 변경 (→ db-schema-designer)

---

### Phase 4: Cross-cutting Concerns (필요 시) ⚪

#### 4.1 `form-validation-specialist` (선택)

**파일**: `.claude/agents/form-validation-specialist.md`

**책임:**
- 프론트엔드 폼 검증 (클라이언트)
- 백엔드 검증 로직 (서버)
- 검증 규칙 통합
- 에러 메시지 표준화

**검증 영역:**
- 이메일 형식
- 비밀번호 강도
- 필수 필드
- 길이 제한
- 정규식 패턴

---

#### 4.2 `error-handling-specialist` (선택)

**파일**: `.claude/agents/error-handling-specialist.md`

**책임:**
- 프론트엔드 에러 경계 (Error Boundary)
- 백엔드 HTTPException 패턴
- 로깅 전략
- 사용자 친화적 에러 메시지

**에러 처리 계층:**
1. UI 레벨 (사용자 메시지)
2. 컴포넌트 레벨 (Error Boundary)
3. API 레벨 (상태 코드)
4. 서버 레벨 (로깅)

---

#### 4.3 `accessibility-specialist` (선택)

**파일**: `.claude/agents/accessibility-specialist.md`

**책임:**
- ARIA 속성 추가
- 키보드 내비게이션
- 스크린 리더 호환성
- 색상 대비 검증 (WCAG 2.1 AA)

---

#### 4.4 `performance-optimizer` (선택)

**파일**: `.claude/agents/performance-optimizer.md`

**책임:**
- React 렌더링 최적화
- FastAPI 쿼리 최적화
- 번들 크기 최적화
- 이미지 최적화 (WebP, lazy loading)

---

## 📐 최종 Agent 구성도

```
프로젝트 Agent 구조 (11개)

Frontend 영역 (3개)
├── react-component-builder       - 컴포넌트 작성 + 코딩 원칙
├── react-api-integrator          - API 통합 + 스펙 검증
└── react-refactoring-specialist  - 리팩토링 + 품질 개선

Backend 영역 (2개)
├── fastapi-api-builder           - API 엔드포인트 + 스키마
└── fastapi-security-specialist   - 인증/인가 + 보안

Database 영역 (1개)
└── db-schema-designer            - 스키마 설계 + 마이그레이션

Testing 영역 (1개)
└── test-writer                   - 테스트 코드 (프론트 + 백)

Styling 영역 (1개)
└── frontend-css-specialist       - CSS/스타일링

Deployment 영역 (1개)
└── deployment-validator          - 배포 전 검증

Cross-cutting 영역 (2개, 선택)
├── form-validation-specialist    - 폼 검증 (프론트 + 백)
└── error-handling-specialist     - 에러 처리 통합
```

---

## ⚙️ Agent 간 협업 시나리오

### 시나리오 1: 새 기능 추가 (사용자 프로필)

**작업 흐름:**
```
1. db-schema-designer
   → users 테이블에 profile 필드 추가 (avatar_url, bio)

2. fastapi-api-builder
   → GET /api/users/profile, PUT /api/users/profile 구현

3. fastapi-security-specialist
   → 인증된 사용자만 자신의 프로필 수정 가능 (권한 체크)

4. react-component-builder
   → ProfileCard, ProfileEditForm 컴포넌트 작성

5. react-api-integrator
   → API 호출 로직 구현 (getUserProfile, updateUserProfile)

6. frontend-css-specialist
   → 프로필 카드 스타일링

7. test-writer
   → 프로필 CRUD 테스트 작성 (프론트 + 백)

8. deployment-validator
   → 배포 전 검증 (import 경로, 빌드 파일 등)
```

---

### 시나리오 2: 기존 컴포넌트 리팩토링

**작업 흐름:**
```
1. react-refactoring-specialist
   → SchedulePage.js (543줄) 분석
   → 분리 계획 수립 (9개 파일)

2. react-component-builder
   → MonthCalendar, ScheduleList 등 새 컴포넌트 작성

3. react-api-integrator
   → useSchedules 커스텀 훅 생성 (API 로직 분리)

4. test-writer
   → 분리된 각 컴포넌트 테스트 작성

5. deployment-validator
   → 빌드 성공 여부 확인
```

---

## 📊 트레이드오프 분석

### 장점 (세분화)
- ✅ **명확한 책임**: 각 Agent가 1가지 일만
- ✅ **전문성 증가**: 깊이 있는 전문 지식
- ✅ **재사용성**: 다른 프로젝트에도 활용
- ✅ **테스트 용이**: Agent별 독립 테스트
- ✅ **확장성**: 새 Agent 추가 쉬움
- ✅ **유지보수**: 문제 발생 시 해당 Agent만 수정

### 단점 (세분화)
- ⚠️ **복잡도 증가**: Agent 수 증가 (4개 → 11개)
- ⚠️ **조율 부담**: CTO(Claude)의 라우팅 복잡
- ⚠️ **오버헤드**: 여러 Agent 호출 시간
- ⚠️ **의존성 관리**: Agent 간 작업 순서 조율
- ⚠️ **학습 곡선**: 어떤 Agent를 언제 쓸지 학습 필요

---

## 🎯 실행 우선순위

### 🔴 Priority 1: 즉시 필요 (다음 작업 시 문제)
1. **test-writer** - 테스트 코드 작성 필요
2. **db-schema-designer** - DB 스키마 변경 필요

### 🟡 Priority 2: 1주 이내 (과부하 해소)
3. **react-refactoring-specialist** - 리팩토링 작업 분리
4. **react-component-builder** - 컴포넌트 작성 전담
5. **react-api-integrator** - API 통합 전담

### 🟢 Priority 3: 2주 이내 (전문성 강화)
6. **fastapi-api-builder** - API 엔드포인트 전담
7. **fastapi-security-specialist** - 보안 전담

### ⚪ Priority 4: 필요 시 (선택적)
8. **form-validation-specialist**
9. **error-handling-specialist**
10. **accessibility-specialist**
11. **performance-optimizer**

---

## 📝 실행 체크리스트

### Phase 1 체크리스트
- [ ] `test-writer.md` 작성
- [ ] `db-schema-designer.md` 작성
- [ ] CLAUDE.md에 새 Agent 라우팅 규칙 추가
- [ ] 테스트로 Agent 동작 검증

### Phase 2 체크리스트
- [ ] `react-component-builder.md` 작성
- [ ] `react-api-integrator.md` 작성
- [ ] `react-refactoring-specialist.md` 작성
- [ ] `react-frontend-guardian.md` 아카이브 또는 삭제
- [ ] 기존 프로젝트 코드로 테스트

### Phase 3 체크리스트
- [ ] `fastapi-api-builder.md` 작성
- [ ] `fastapi-security-specialist.md` 작성
- [ ] `fastapi-backend-guardian.md` 아카이브 또는 삭제
- [ ] 기존 백엔드 코드로 테스트

### Phase 4 체크리스트
- [ ] 필요한 선택적 Agent 결정
- [ ] 각 Agent 파일 작성
- [ ] 통합 테스트

---

## 🔄 마이그레이션 전략

### 기존 Agent 처리 방법

**옵션 1: 아카이브 (권장)**
```bash
mv .claude/agents/react-frontend-guardian.md \
   .claude/agents/_archived/react-frontend-guardian.md
```

**옵션 2: 삭제**
```bash
rm .claude/agents/react-frontend-guardian.md
```

**옵션 3: 점진적 전환 (안전)**
- 새 Agent 생성 → 테스트 → 기존 Agent 비활성화

---

## 📚 참고 자료

### Agent 설계 원칙
- 단일 책임 원칙 (SRP)
- 도메인 경계 명확화
- 읽기/쓰기 권한 분리
- CTO 조율 중심

### 기존 Agent 분석 문서
- `AGENT_WORKING_PRINCIPLES.md` - Agent 작업 원칙
- `react-frontend-guardian.md` - 기존 프론트엔드 Agent
- `fastapi-backend-guardian.md` - 기존 백엔드 Agent

---

## 📅 예상 일정

| Phase | 기간 | 작업 내용 |
|-------|------|----------|
| **Phase 1** | 1일 | test-writer, db-schema-designer 생성 |
| **Phase 2** | 3일 | React Agent 3개 분리 |
| **Phase 3** | 2일 | Backend Agent 2개 분리 |
| **Phase 4** | 필요 시 | 선택적 Agent 추가 |
| **테스트** | 2일 | 통합 테스트 및 검증 |
| **문서화** | 1일 | Agent 사용 가이드 작성 |
| **총계** | **~2주** | 전체 완료 |

---

## ✅ 성공 기준

1. **각 Agent가 200줄 이하의 명확한 책임**
2. **Agent 간 의존성 최소화**
3. **실제 프로젝트에서 정상 작동**
4. **CTO(Claude) 라우팅 복잡도 관리 가능**
5. **개발자 생산성 향상 (측정 지표: 작업 시간 20% 단축)**

---

**문서 버전**: 1.0
**다음 리뷰 일정**: Agent 생성 완료 후
**담당**: CTO (Claude)
