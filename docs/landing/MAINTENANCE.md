# Landing Page 유지보수 계획

> 테마/레이아웃 시스템 유지보수 가이드

---

## 유지보수 범위

> **결정: 랜딩페이지와 Clouvel MCP 서버는 분리 유지보수**

### C-Level 회의록 (2026-01-23)

**👔 PM**: 유지보수 범위 최종 결정합니다. 랜딩페이지만 할지, Clouvel MCP 서버까지 포함할지. 현재 `docs/landing/`에 독립적으로 있고, MCP 서버는 `src/clouvel/`에 Python 패키지로 있어요.

**🛠️ CTO**: **분리**가 맞아요. 이유는 세 가지:

1. **배포 주기 다름** - 랜딩은 마케팅 이벤트에 맞춰 자주 변경, MCP는 버전 릴리스 주기
2. **기술 스택 다름** - 랜딩은 HTML/CSS/JS, MCP는 Python
3. **책임 분리** - 랜딩 깨져도 MCP 동작에 영향 없어야 함

**🧪 QA**: CTO 동의해요. 테스트도 분리해야 해요. 랜딩은 시각적 회귀 테스트 (Playwright), MCP는 pytest. 섞으면 CI 복잡해지고 실패 원인 추적 어려워요.

**🔥 ERROR**: 운영 관점에서도 분리 맞아요. 장애 격리 원칙이에요. 랜딩 CDN 터져도 MCP 서버는 정상 동작해야 하고, 반대도 마찬가지.

**📢 CMO**: 마케팅 관점 추가하면, 랜딩은 빠른 실험이 필요해요. A/B 테스트, 테마 변경, 카피 수정 등. MCP 배포 기다릴 수 없어요.

**👔 PM**: 만장일치네요. 정리하면:

- **랜딩페이지**: `docs/landing/` - 이 문서로 관리
- **Clouvel MCP**: `src/clouvel/` - 별도 CONTRIBUTING.md로 관리
- **공통 브랜딩**: 색상/로고는 동기화 유지

---

### 최종 결정 요약

| 항목   | 랜딩페이지               | Clouvel MCP     |
| ------ | ------------------------ | --------------- |
| 위치   | `docs/landing/`          | `src/clouvel/`  |
| 문서   | MAINTENANCE.md (이 문서) | CONTRIBUTING.md |
| 테스트 | Playwright (시각적)      | pytest          |
| 배포   | GitHub Pages             | PyPI            |
| 주기   | 수시 (마케팅 연동)       | 버전 릴리스     |

---

## 파일 구조

```
docs/landing/
├── index.html              # 메인 페이지
├── styles.css              # 기본 스타일
├── index.js                # 기존 기능 (탭, 폼 등)
├── layouts.js              # 레이아웃 템플릿 (Hero 영역)
├── theme-switcher.js       # 테마 전환 로직
├── themes/
│   ├── default.css         # 기본 테마
│   ├── developer.css       # 개발자 테마
│   ├── premium.css         # 프리미엄 테마
│   ├── minimal.css         # 미니멀 테마
│   ├── friendly.css        # 친근한 테마
│   └── creative.css        # 크리에이티브 테마
└── MAINTENANCE.md          # 이 문서
```

---

## 1. 테마 추가 방법

### Step 1: CSS 파일 생성

```bash
# themes/새테마.css 생성
cp themes/default.css themes/새테마.css
```

### Step 2: CSS 변수 수정

```css
/* themes/새테마.css */
:root {
  --color-bg-primary: #신규색상;
  --color-accent: #액센트색상;
  /* ... */
}

/* Tailwind 오버라이드 필수 */
.bg-warm-white {
  background-color: #신규색상 !important;
}
.bg-accent {
  background-color: #액센트색상 !important;
}
/* ... */
```

### Step 3: theme-switcher.js에 등록

```javascript
const THEMES = {
  // ... 기존 테마들
  새테마: {
    name: "새테마",
    description: "테마 설명",
    file: "themes/새테마.css",
    darkMode: true, // 다크모드 토글 지원 여부
  },
};
```

### Step 4: layouts.js에 레이아웃 추가 (선택)

```javascript
const LAYOUTS = {
  // ... 기존 레이아웃들
  새테마: {
    hero: `
      <section class="hero-새테마">
        <!-- Hero HTML -->
      </section>
    `,
  },
};
```

---

## 2. 테마 수정 체크리스트

테마 수정 시 반드시 확인할 항목:

### 색상 변경 시

- [ ] `:root` CSS 변수 수정
- [ ] Tailwind 오버라이드 클래스 수정 (`.bg-warm-white`, `.text-accent` 등)
- [ ] 다크모드 오버라이드 수정 (`[data-theme="dark"]`)
- [ ] CTA 버튼 pulse 애니메이션 색상 수정

### 레이아웃 변경 시

- [ ] `layouts.js`의 해당 테마 HTML 수정
- [ ] 새 CSS 클래스 추가 시 테마 CSS에도 스타일 추가
- [ ] 모바일 반응형 확인

### 공통

- [ ] 크롬, 파이어폭스, 사파리 테스트
- [ ] 모바일 (iOS/Android) 테스트
- [ ] 다크모드 토글 동작 확인
- [ ] 테마 전환 후 원래 테마로 복귀 확인

---

## 3. 테스트 절차

### 로컬 테스트

```bash
# 간단한 로컬 서버 실행
cd docs/landing
python -m http.server 8000

# 브라우저에서 확인
open http://localhost:8000
```

### 테스트 시나리오

1. **테마 전환 테스트**
   - Default → Developer → Premium → Minimal → Friendly → Creative → Default
   - 각 전환 시 색상 + 레이아웃 모두 변경 확인

2. **다크모드 테스트**
   - Default, Minimal, Friendly에서 다크모드 토글 확인
   - Developer, Premium, Creative는 다크모드 고정 확인

3. **새로고침 테스트**
   - 테마 선택 후 새로고침 → 선택 유지 확인 (localStorage)

4. **반응형 테스트**
   - 데스크톱 (1920px, 1440px, 1024px)
   - 태블릿 (768px)
   - 모바일 (375px, 320px)

---

## 4. 버전 관리

### 버전 넘버링

```
v{major}.{minor}.{patch}

예: v1.2.3
- major: 전체 구조 변경, 호환성 깨짐
- minor: 새 테마/레이아웃 추가
- patch: 버그 수정, 색상 미세 조정
```

### 변경 기록

| 버전   | 날짜       | 변경 내용                                          |
| ------ | ---------- | -------------------------------------------------- |
| v1.1.0 | 2026-01-23 | 유지보수 범위 결정 (분리), 에러 핸들링 가이드 추가 |
| v1.0.0 | 2026-01-23 | 6개 테마 + 레이아웃 시스템 초기 릴리스             |

---

## 5. 주기적 유지보수

### 월간 (Monthly)

- [ ] 외부 CDN 링크 유효성 확인 (Tailwind, Google Fonts)
- [ ] GitHub Pages 배포 상태 확인
- [ ] 브라우저 호환성 이슈 체크 (caniuse.com)

### 분기별 (Quarterly)

- [ ] 디자인 트렌드 리뷰 → 테마 업데이트 검토
- [ ] 사용자 피드백 수집 → 개선점 반영
- [ ] 성능 측정 (Lighthouse)
  - Performance: 90+
  - Accessibility: 90+
  - Best Practices: 90+
  - SEO: 90+

### 연간 (Yearly)

- [ ] 전체 테마 리뷰 → 구식 테마 제거/교체
- [ ] 새로운 레퍼런스 사이트 조사 → 신규 테마 추가

---

## 6. 트러블슈팅

### 테마가 적용되지 않음

```javascript
// 콘솔에서 확인
console.log(window.themeSwitcher.currentTheme);
console.log(document.getElementById("theme-stylesheet").href);
```

**원인:**

1. CSS 파일 경로 오류 → `themes/` 폴더 확인
2. Tailwind !important 누락 → 오버라이드 클래스 확인
3. 캐시 문제 → 강력 새로고침 (Cmd+Shift+R)

### 레이아웃이 전환되지 않음

```javascript
// 콘솔에서 확인
console.log(window.layoutManager.currentLayout);
console.log(window.layoutManager.originalContent);
```

**원인:**

1. layouts.js 로드 순서 → theme-switcher.js보다 먼저 로드
2. Hero 섹션 셀렉터 불일치 → `section.pt-32.pb-12` 확인
3. originalContent 저장 실패 → 페이지 로드 타이밍

### localStorage 문제

```javascript
// 저장된 설정 확인
localStorage.getItem("clouvel-theme");
localStorage.getItem("clouvel-mode");

// 초기화
localStorage.removeItem("clouvel-theme");
localStorage.removeItem("clouvel-mode");
```

### localStorage Fallback (권장 구현)

```javascript
// theme-switcher.js에 추가 권장
function getSavedTheme() {
  try {
    return localStorage.getItem("clouvel-theme");
  } catch (e) {
    console.warn("localStorage 접근 실패, 기본 테마 사용");
    return null;
  }
}

function saveTheme(theme) {
  try {
    localStorage.setItem("clouvel-theme", theme);
  } catch (e) {
    console.warn("localStorage 저장 실패");
  }
}
```

### CDN 장애 대비

```html
<!-- Tailwind CDN 실패 시 로컬 폴백 (선택) -->
<script>
  if (!window.tailwind) {
    document.write('<link rel="stylesheet" href="fallback/tailwind.min.css">');
  }
</script>
```

---

## 7. 향후 계획

### 단기 (1-2개월)

- [ ] A/B 테스트 통합 (어떤 테마가 전환율 높은지)
- [ ] 테마별 전용 Pricing 섹션 레이아웃
- [ ] 애니메이션 강화 (GSAP 또는 Framer Motion)

### 중기 (3-6개월)

- [ ] 사용자 커스텀 테마 저장 기능
- [ ] 테마 미리보기 모달
- [ ] 시즌 테마 (할로윈, 크리스마스)

### 장기 (6개월+)

- [ ] React/Vue 컴포넌트 버전
- [ ] 테마 마켓플레이스 (커뮤니티 테마)
- [ ] 다국어 지원 시 테마별 폰트 최적화

---

## 8. 담당자 & 연락처

| 역할        | 담당 | 연락처        |
| ----------- | ---- | ------------- |
| 메인테이너  | -    | GitHub Issues |
| 디자인 리뷰 | -    | -             |
| QA          | -    | -             |

---

## 부록: Tailwind 오버라이드 클래스 목록

테마 CSS에서 반드시 오버라이드해야 하는 클래스:

```css
/* 배경 */
.bg-warm-white
.bg-white
.bg-slate-50
.bg-slate-100
.bg-slate-800
.bg-dark-slate

/* 텍스트 */
.text-dark-slate
.text-slate-600
.text-slate-500
.text-slate-400
.text-accent
.accent-text

/* 보더 */
.border-slate-200
.border-slate-200\/50

/* 액센트 */
.bg-accent
.hover\:bg-accent-dark:hover

/* 상태 색상 */
.text-emerald-400, .text-emerald-500, .text-emerald-600
.bg-emerald-50, .bg-emerald-600
.border-emerald-200
.text-red-400, .text-red-500
.text-yellow-400, .text-yellow-500

/* Nav */
nav.fixed

/* 애니메이션 */
.cta-pulse
```
