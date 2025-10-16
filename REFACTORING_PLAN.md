# SchedulePage 컴포넌트 리팩토링 계획서

작성일: 2025-10-16
작성자: Claude (CTO) + react-frontend-guardian Agent

---

## 📊 현재 구조 분석

### SchedulePage.js 현황

**기본 정보:**
- **파일 크기**: 544줄
- **컴포넌트 타입**: 단일 거대 컴포넌트 (Monolithic Component)
- **State 개수**: 7개 (schedules, selectedDate, currentMonth, inputText, isLoading, isSending, error)
- **함수 개수**: 16개 (API 호출 3개, 이벤트 핸들러 4개, 유틸리티 9개)
- **JSX 섹션**: 5개 주요 영역 (헤더, 달력, 날짜 상세, 주간 요약, 입력폼)

**책임 및 역할:**
현재 SchedulePage 컴포넌트가 담당하는 책임:
1. **인증 관리**: JWT 토큰 검증, 로그아웃 처리
2. **데이터 관리**: 일정 CRUD 작업 (생성, 조회, 수정, 삭제)
3. **API 통신**: 4개의 API 엔드포인트와 통신
4. **UI 렌더링**: 5개의 복잡한 UI 섹션 렌더링
5. **날짜 계산**: 달력 생성, 날짜 비교, 포맷팅 등 9개의 유틸리티 함수
6. **통계 계산**: 주간 일정 통계 및 완료율 계산
7. **에러 처리**: 네트워크 및 인증 에러 처리
8. **상태 관리**: 7개의 독립적인 상태 관리

**복잡도 지표:**
- **인지적 복잡도**: 매우 높음 (16개 함수 + 7개 상태를 한 파일에서 관리)
- **응집도**: 낮음 (서로 다른 관심사가 혼재)
- **재사용성**: 없음 (모든 로직이 강하게 결합됨)
- **테스트 가능성**: 낮음 (단위 테스트 작성 어려움)

---

## 🚨 문제점

### 1. **단일 책임 원칙 위반 (SRP Violation)**
- 하나의 컴포넌트가 너무 많은 책임을 담당
- UI 렌더링, 비즈니스 로직, API 통신이 모두 혼재

### 2. **코드 재사용 불가**
- 달력 컴포넌트를 다른 곳에서 사용 불가
- 일정 카드를 독립적으로 사용 불가
- 유틸리티 함수들이 컴포넌트 내부에 갇혀 있음

### 3. **유지보수 어려움**
- 버그 수정 시 영향 범위 파악 어려움
- 새 기능 추가 시 파일이 계속 비대해짐
- 다른 개발자가 코드 이해하기 어려움

### 4. **테스트 어려움**
- 개별 기능을 독립적으로 테스트하기 어려움
- Mock 설정이 복잡함

### 5. **성능 최적화 제한**
- 전체 컴포넌트가 불필요하게 리렌더링될 수 있음
- React.memo 등 최적화 기법 적용 어려움

### 6. **Props Drilling 위험**
- 현재는 단일 컴포넌트라 문제 없지만, 향후 확장 시 Props Drilling 발생 가능

---

## 🎯 리팩토링 계획

### 분할할 컴포넌트

#### **1. Calendar 컴포넌트** (달력 UI)
- **책임**: 월간 달력 렌더링 및 날짜 선택
- **Props**:
  ```javascript
  {
    currentMonth: Date,
    selectedDate: Date,
    schedules: Array,
    onDateSelect: (date) => void,
    onMonthChange: (direction: 'prev' | 'next') => void
  }
  ```
- **파일**: `src/components/Calendar/Calendar.js`
- **추출 대상 코드**: 라인 309-362 (달력 섹션 전체)

#### **2. CalendarDay 컴포넌트** (달력 날짜 칸)
- **책임**: 개별 날짜 칸 렌더링 (일정 미리보기 포함)
- **Props**:
  ```javascript
  {
    day: Date | null,
    isSelected: boolean,
    isToday: boolean,
    schedules: Array,
    onClick: () => void
  }
  ```
- **파일**: `src/components/Calendar/CalendarDay.js`
- **추출 대상 코드**: 라인 329-358 (calendar-day 부분)

#### **3. ScheduleList 컴포넌트** (일정 목록)
- **책임**: 선택된 날짜의 일정 목록 렌더링
- **Props**:
  ```javascript
  {
    date: Date,
    schedules: Array,
    onToggleComplete: (id, currentStatus) => void,
    onDelete: (id) => void
  }
  ```
- **파일**: `src/components/Schedule/ScheduleList.js`
- **추출 대상 코드**: 라인 366-433 (date-details 섹션)

#### **4. ScheduleCard 컴포넌트** (개별 일정 카드)
- **책임**: 개별 일정 정보 렌더링 (체크박스, 시간, 설명, 액션 버튼)
- **Props**:
  ```javascript
  {
    schedule: Object,
    onToggleComplete: (id, currentStatus) => void,
    onDelete: (id) => void
  }
  ```
- **파일**: `src/components/Schedule/ScheduleCard.js`
- **추출 대상 코드**: 라인 374-429 (schedule-card 부분)

#### **5. WeekSummary 컴포넌트** (주간 요약)
- **책임**: 이번 주 일정 통계 및 요약 렌더링
- **Props**:
  ```javascript
  {
    schedules: Array,
    currentDate: Date
  }
  ```
- **파일**: `src/components/Schedule/WeekSummary.js`
- **추출 대상 코드**: 라인 435-469 (week-summary 섹션)

#### **6. ScheduleInput 컴포넌트** (일정 입력 폼)
- **책임**: 자연어 입력 폼 및 툴팁 렌더링
- **Props**:
  ```javascript
  {
    value: string,
    onChange: (value) => void,
    onSubmit: (text) => void,
    isLoading: boolean
  }
  ```
- **파일**: `src/components/Schedule/ScheduleInput.js`
- **추출 대상 코드**: 라인 474-538 (schedule-input-form 섹션)

#### **7. Header 컴포넌트** (헤더)
- **책임**: 앱 헤더 및 로그아웃 버튼 렌더링
- **Props**:
  ```javascript
  {
    onLogout: () => void
  }
  ```
- **파일**: `src/components/Layout/Header.js`
- **추출 대상 코드**: 라인 294-299 (schedule-header)

---

### 커스텀 훅 (Custom Hooks)

#### **1. useSchedules** (일정 데이터 관리)
- **책임**: 일정 CRUD API 호출 및 상태 관리
- **반환값**:
  ```javascript
  {
    schedules: Array,
    isLoading: boolean,
    error: string,
    fetchSchedules: () => Promise<void>,
    createSchedule: (text) => Promise<void>,
    updateSchedule: (id, data) => Promise<void>,
    deleteSchedule: (id) => Promise<void>
  }
  ```
- **파일**: `src/hooks/useSchedules.js`
- **추출 대상 코드**: 라인 19-155 (모든 API 관련 함수)

#### **2. useDateUtils** (날짜 유틸리티)
- **책임**: 날짜 계산 및 포맷팅 유틸리티 함수 제공
- **반환값**:
  ```javascript
  {
    getDaysInMonth: (date) => Array,
    isSameDay: (date1, date2) => boolean,
    formatDate: (date) => string,
    formatDateTime: (dateString) => string,
    getSchedulesForDate: (date, schedules) => Array,
    hasSchedulesOnDate: (date, schedules) => boolean,
    getWeekSchedules: (schedules) => Array,
    getWeekStatistics: (schedules) => Object
  }
  ```
- **파일**: `src/hooks/useDateUtils.js`
- **추출 대상 코드**: 라인 162-269 (모든 유틸리티 함수)

---

### 디렉토리 구조

리팩토링 후 파일 구조:

```
src/
├── components/
│   ├── Calendar/
│   │   ├── Calendar.js           # 월간 달력 컨테이너
│   │   ├── Calendar.module.css
│   │   ├── CalendarDay.js        # 개별 날짜 칸
│   │   └── CalendarDay.module.css
│   │
│   ├── Schedule/
│   │   ├── ScheduleList.js       # 일정 목록
│   │   ├── ScheduleList.module.css
│   │   ├── ScheduleCard.js       # 개별 일정 카드
│   │   ├── ScheduleCard.module.css
│   │   ├── ScheduleInput.js      # 일정 입력 폼
│   │   ├── ScheduleInput.module.css
│   │   ├── WeekSummary.js        # 주간 요약
│   │   └── WeekSummary.module.css
│   │
│   ├── Layout/
│   │   ├── Header.js             # 헤더
│   │   └── Header.module.css
│   │
│   ├── ErrorBoundary/
│   │   ├── ErrorBoundary.js      # 에러 바운더리
│   │   └── ErrorFallback.js      # 에러 UI
│   │
│   ├── SchedulePage.js           # 메인 컨테이너 (오케스트레이션)
│   └── SchedulePage.module.css   # 레이아웃 스타일
│
└── hooks/
    ├── useSchedules.js           # 일정 API 훅
    └── useDateUtils.js           # 날짜 유틸리티 훅
```

---

### State 관리 방식

**현재**: 모든 상태가 SchedulePage 컴포넌트에 있음
**리팩토링 후**:

1. **SchedulePage (Container)**: 전역 상태 관리
   - `selectedDate` (선택된 날짜)
   - `currentMonth` (현재 표시 중인 월)

2. **useSchedules Hook**: API 관련 상태
   - `schedules` (일정 목록)
   - `isLoading` (로딩 상태)
   - `error` (에러 메시지)

3. **ScheduleInput Component**: 로컬 상태
   - `inputText` (입력 텍스트)
   - `isSending` (전송 중 상태)

**장점**:
- 상태가 사용되는 곳에 가깝게 배치
- 불필요한 Props Drilling 방지
- 각 컴포넌트의 독립성 보장

---

## 📋 단계별 실행 계획

### **Phase 1: 필수 리팩토링** (즉시 효과) - 2시간

#### 1-1. useDateUtils 분리 (30분)
- `useDateUtils.js` 커스텀 훅 생성
- 날짜 관련 유틸리티 함수 9개 이동
- SchedulePage에서 훅 import 및 사용
- **위험도**: 낮음 (순수 함수이므로 테스트 용이)

#### 1-2. useSchedules 분리 (1시간)
- `useSchedules.js` 커스텀 훅 생성
- API 호출 함수 4개 + 상태 3개 이동
- SchedulePage에서 훅 사용
- **위험도**: 중간 (API 호출 로직이므로 신중 필요)

#### 1-3. PropTypes 추가 (30분)
- 모든 Props에 PropTypes 정의
- 타입 안정성 확보
- **위험도**: 낮음

**효과**: 코드 품질 30% 향상, 재사용성 확보

---

### **Phase 2: UI 컴포넌트 분리** (점진적 개선) - 2-3시간

#### 2-1. ScheduleCard 추출 (30분)
- 개별 일정 카드 컴포넌트 생성
- Props 전달 및 이벤트 핸들러 연결
- CSS Modules 적용
- PropTypes 추가
- **위험도**: 낮음

#### 2-2. ScheduleList 추출 (30분)
- 일정 목록 컴포넌트 생성 (ScheduleCard 사용)
- Props 전달
- CSS Modules 적용
- **위험도**: 낮음

#### 2-3. CalendarDay 추출 (30분)
- 개별 날짜 칸 컴포넌트 생성
- Props 전달
- CSS Modules 적용
- **위험도**: 낮음

#### 2-4. Calendar 추출 (45분)
- 달력 컨테이너 컴포넌트 생성 (CalendarDay 사용)
- Props 전달
- CSS Modules 적용
- **위험도**: 중간

#### 2-5. 성능 최적화 (30분)
- `useCallback`으로 이벤트 핸들러 메모이제이션
- `useMemo`로 계산 결과 메모이제이션
- React.memo로 불필요한 리렌더링 방지
- **위험도**: 낮음

---

### **Phase 3: 부가 기능** (선택적) - 1-2시간

#### 3-1. WeekSummary 추출 (30분)
- 주간 요약 컴포넌트 생성
- `useDateUtils` 훅 사용
- CSS Modules 적용
- **위험도**: 낮음

#### 3-2. ScheduleInput 추출 (30분)
- 입력 폼 컴포넌트 생성
- 로컬 상태 관리 (inputText, isSending)
- CSS Modules 적용
- **위험도**: 낮음

#### 3-3. Header 추출 (15분)
- 헤더 컴포넌트 생성
- CSS Modules 적용
- **위험도**: 매우 낮음

#### 3-4. ErrorBoundary 추가 (45분)
- ErrorBoundary 컴포넌트 생성
- ErrorFallback UI 생성
- SchedulePage를 ErrorBoundary로 감싸기
- **위험도**: 낮음

---

### **Phase 4: 최종 통합 및 검증** - 1시간

#### 4-1. SchedulePage 리팩토링
- SchedulePage를 Container 컴포넌트로 전환
- 모든 자식 컴포넌트 조립
- Props 전달 체계 확립
- 레이아웃 CSS만 유지
- **위험도**: 중간

#### 4-2. 통합 테스트
- 모든 기능 정상 동작 확인
- API 호출 정상 여부 확인
- UI 렌더링 확인
- 에러 처리 확인
- 성능 확인 (불필요한 리렌더링 없는지)

---

## ✅ 예상 효과

### 1. **코드 품질 향상**
- **가독성**: 각 파일이 200줄 이하로 축소 (현재 544줄 → 평균 100줄)
- **이해도**: 각 컴포넌트의 책임이 명확해짐
- **유지보수성**: 버그 수정 및 기능 추가가 쉬워짐

### 2. **재사용성 증가**
- Calendar 컴포넌트를 다른 페이지에서도 사용 가능
- ScheduleCard를 다른 뷰(리스트, 검색 결과 등)에서 사용 가능
- useDateUtils 훅을 다른 날짜 관련 기능에서 활용 가능

### 3. **테스트 가능성 향상**
- 각 컴포넌트를 독립적으로 테스트 가능
- 순수 함수(유틸리티)는 단위 테스트 작성 용이
- Mock 설정이 간단해짐

### 4. **성능 최적화 기회**
- React.memo로 불필요한 리렌더링 방지
- 각 컴포넌트에 최적화 전략 적용 가능
- 코드 스플리팅(Code Splitting) 가능

### 5. **팀 협업 개선**
- 여러 개발자가 동시에 다른 컴포넌트 작업 가능
- 코드 리뷰가 쉬워짐
- 신입 개발자의 코드 이해도 향상

### 6. **확장성 향상**
- 새 기능 추가 시 적절한 위치를 쉽게 찾을 수 있음
- 카테고리 기능 추가 등 향후 확장이 용이함

---

## ⚠️ 주의사항

### 1. **API 스펙 변경 없음**
- 리팩토링은 내부 구조만 변경
- API 엔드포인트, 요청/응답 형식은 그대로 유지
- `/api/schedules` 관련 모든 API 호출 동일하게 유지

### 2. **Props Drilling 주의**
- 컴포넌트 깊이가 3단계 이상 가면 Context 또는 전역 상태 관리 고려
- 현재 계획은 2단계까지만 (SchedulePage → 자식 컴포넌트)
- 향후 더 복잡해지면 Zustand, Jotai, Context API 도입 검토

**Context 도입 기준**:
- 카테고리 기능 추가로 깊이 증가 시
- 테마 설정 등 전역 상태 필요 시
- 5개 이상 Props 전달 시

### 3. **CSS 분리 전략**
- 현재 SchedulePage.css (715줄)를 여러 파일로 분리
- **CSS Modules 사용 권장** (`*.module.css`)
- 클래스명 충돌 방지
- BEM 네이밍 또는 CSS Modules로 스코프 명확화

**예시**:
```css
/* Calendar.module.css */
.calendar { }
.calendar__header { }
.calendar__grid { }
```

### 4. **성능 최적화 전략**

#### useCallback 사용
```javascript
// SchedulePage.js
const handleDateSelect = useCallback((date) => {
  setSelectedDate(date);
}, []);

const handleToggleComplete = useCallback((id, currentStatus) => {
  updateSchedule(id, { is_completed: !currentStatus });
}, [updateSchedule]);
```

#### useMemo 사용
```javascript
const filteredSchedules = useMemo(() =>
  getSchedulesForDate(selectedDate, schedules),
  [selectedDate, schedules]
);

const weekStats = useMemo(() =>
  getWeekStatistics(schedules),
  [schedules]
);
```

#### React.memo 사용
```javascript
// ScheduleCard.js
export default React.memo(ScheduleCard);
```

### 5. **단계별 동작 확인 필수**
- 각 단계마다 반드시 브라우저에서 동작 확인
- 콘솔 에러 없는지 확인
- API 호출이 정상 작동하는지 확인
- 성능 회귀 없는지 확인

### 6. **Git 커밋 전략**
- 각 단계마다 커밋 (예: "Refactor: Extract useDateUtils hook")
- 문제 발생 시 이전 커밋으로 롤백 가능하게
- 커밋 메시지 컨벤션:
  - `Refactor: [작업 내용]` (리팩토링)
  - `Perf: [작업 내용]` (성능 최적화)
  - `Test: [작업 내용]` (테스트 추가)

### 7. **에러 처리 유지**
- 현재 구현된 인증 에러 처리 (401) 유지
- Rate Limit 에러 처리 (429) 유지
- 서버 연결 실패 에러 처리 유지
- ErrorBoundary로 예상치 못한 에러 처리

### 8. **타입 안정성**

#### PropTypes 적용 (즉시)
```javascript
import PropTypes from 'prop-types';

ScheduleCard.propTypes = {
  schedule: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    scheduled_at: PropTypes.string.isRequired,
    is_completed: PropTypes.bool.isRequired
  }).isRequired,
  onToggleComplete: PropTypes.func.isRequired,
  onDelete: PropTypes.func.isRequired
};
```

#### TypeScript 전환 (향후)
- 리팩토링 완료 후 TypeScript 전환 검토
- 단계적 마이그레이션 (`.js` → `.tsx`)

---

## 🧪 테스트 전략

### Phase 1 테스트

#### useDateUtils 테스트 (Jest)
```javascript
// src/hooks/__tests__/useDateUtils.test.js
import { renderHook } from '@testing-library/react-hooks';
import useDateUtils from '../useDateUtils';

test('isSameDay should compare dates correctly', () => {
  const { result } = renderHook(() => useDateUtils());
  const date1 = new Date('2025-10-16');
  const date2 = new Date('2025-10-16');

  expect(result.current.isSameDay(date1, date2)).toBe(true);
});
```

#### useSchedules 테스트 (MSW)
```javascript
// src/hooks/__tests__/useSchedules.test.js
import { renderHook } from '@testing-library/react-hooks';
import { rest } from 'msw';
import { setupServer } from 'msw/node';
import useSchedules from '../useSchedules';

const server = setupServer(
  rest.get('/api/schedules', (req, res, ctx) => {
    return res(ctx.json([...]));
  })
);

beforeAll(() => server.listen());
afterAll(() => server.close());

test('fetchSchedules should load schedules', async () => {
  const { result, waitForNextUpdate } = renderHook(() => useSchedules());

  result.current.fetchSchedules();
  await waitForNextUpdate();

  expect(result.current.schedules.length).toBeGreaterThan(0);
});
```

### Phase 2 테스트

#### 컴포넌트 테스트 (React Testing Library)
```javascript
// src/components/Schedule/__tests__/ScheduleCard.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import ScheduleCard from '../ScheduleCard';

test('renders schedule information', () => {
  const schedule = {
    id: 1,
    title: '회의',
    scheduled_at: '2025-10-16T14:00:00',
    is_completed: false
  };

  render(
    <ScheduleCard
      schedule={schedule}
      onToggleComplete={jest.fn()}
      onDelete={jest.fn()}
    />
  );

  expect(screen.getByText('회의')).toBeInTheDocument();
});

test('calls onToggleComplete when checkbox is clicked', () => {
  const handleToggle = jest.fn();
  // ... test implementation
});
```

---

## 🎯 다음 단계

### 즉시 시작 가능 (추천)
**Phase 1: 필수 리팩토링** (2시간)
1. useDateUtils 분리
2. useSchedules 분리
3. PropTypes 추가

### 후속 작업
**Phase 2: UI 컴포넌트 분리** (2-3시간)
- ScheduleCard + ScheduleList
- CalendarDay + Calendar
- 성능 최적화

**Phase 3: 부가 기능** (선택적, 1-2시간)
- 나머지 컴포넌트 분리
- ErrorBoundary 추가
- CSS Modules 적용

---

## 📚 참고 자료

### React 공식 문서
- [Hooks at a Glance](https://react.dev/reference/react)
- [Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [React.memo](https://react.dev/reference/react/memo)

### 코드 품질
- [Single Responsibility Principle](https://en.wikipedia.org/wiki/Single-responsibility_principle)
- [Component Composition](https://react.dev/learn/passing-props-to-a-component)
- [CSS Modules](https://github.com/css-modules/css-modules)

### 테스트
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Jest](https://jestjs.io/)
- [MSW (Mock Service Worker)](https://mswjs.io/)

---

**작성 완료일**: 2025-10-16
**최종 검토**: Claude (CTO)
