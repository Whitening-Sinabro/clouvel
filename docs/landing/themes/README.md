# Clouvel Landing Page Themes

> 상황별 레이아웃 테마 시스템

---

## 상황별 레이아웃 매핑

| 상황          | 테마        | 레퍼런스      | 특징                  |
| ------------- | ----------- | ------------- | --------------------- |
| 기본          | `default`   | Hybrid (현재) | 현재 + 개선, 안정적   |
| 개발자 타겟   | `developer` | Warp          | 터미널/AI 코딩 느낌   |
| 일반 사용자   | `friendly`  | Raycast + Arc | 친근, 깔끔            |
| 프리미엄 느낌 | `premium`   | Linear        | 다크 + 프로페셔널     |
| 미니멀 강조   | `minimal`   | Vercel + xmcp | 극 미니멀             |
| 차별화        | `creative`  | Cloudflare    | 오렌지 + 크리에이티브 |

---

## 파일 구조

```
themes/
├── README.md           # 이 문서
├── default.css         # 기본 테마 (Option 10: Hybrid)
├── developer.css       # 개발자 테마 (Option 4: Warp)
├── premium.css         # 프리미엄 테마 (Option 1: Linear)
├── minimal.css         # 미니멀 테마 (Option 3/9: Vercel/xmcp)
├── friendly.css        # 친근한 테마 (Option 2/7: Raycast/Arc)
└── creative.css        # 크리에이티브 테마 (Option 5: Cloudflare)
```

---

## 사용법

### 1. 수동 테마 전환

URL 파라미터로 테마 지정:

```
https://example.com/?theme=developer
https://example.com/?theme=premium
```

### 2. JavaScript API

```javascript
// 테마 변경
const switcher = new ThemeSwitcher();
switcher.applyTheme("developer");

// 다크 모드 토글
switcher.toggleDarkMode();

// 현재 테마 확인
console.log(switcher.currentTheme);
```

### 3. 직접 CSS 링크

```html
<link rel="stylesheet" href="themes/developer.css" />
```

---

## 테마 특성

### Default (기본)

- **모드**: 라이트/다크 지원
- **색상**: 파란색 액센트 (#0EA5E9)
- **폰트**: Space Grotesk
- **용도**: 범용, 현재 디자인 유지

### Developer (개발자)

- **모드**: 다크 고정
- **색상**: 터미널 그린 (#00D4AA)
- **폰트**: JetBrains Mono (코드), Inter (본문)
- **용도**: CLI 도구, 개발자 타겟 제품
- **특징**: 터미널 UI, 타이핑 애니메이션, 그라데이션 보더

### Premium (프리미엄)

- **모드**: 다크 고정
- **색상**: 퍼플 그라데이션 (#7C3AED → #A855F7)
- **폰트**: Inter
- **용도**: 고급 SaaS, 프로페셔널 제품
- **특징**: 글로우 효과, 그라데이션 텍스트, 2x2 그리드

### Minimal (미니멀)

- **모드**: 라이트/다크 지원
- **색상**: 흑백 + 포인트 1색
- **폰트**: Inter (SF Pro 스타일)
- **용도**: 심플한 도구, 원페이저
- **특징**: 최대 여백, 큰 타이포, 요소 최소화

### Friendly (친근)

- **모드**: 라이트/다크 지원
- **색상**: 블루 (#3B82F6)
- **폰트**: Inter
- **용도**: 일반 사용자, B2C 제품
- **특징**: 둥근 모서리, 소프트 그림자, 제품 스크린샷 강조

### Creative (크리에이티브)

- **모드**: 다크 고정
- **색상**: 오렌지 그라데이션 (#F6821F)
- **폰트**: Space Grotesk
- **용도**: 차별화 필요 시, 마케팅 캠페인
- **특징**: 대담한 타이포, 일러스트 활용, 볼드 버튼

---

## CSS 변수

모든 테마는 공통 CSS 변수 구조를 사용합니다:

```css
:root {
  /* 배경 */
  --color-bg-primary: #fff;
  --color-bg-secondary: #f8fafc;
  --color-bg-tertiary: #f1f5f9;

  /* 텍스트 */
  --color-text-primary: #0f172a;
  --color-text-secondary: #64748b;
  --color-text-muted: #94a3b8;

  /* 액센트 */
  --color-accent: #0ea5e9;
  --color-accent-dark: #0284c7;
  --color-accent-light: rgba(14, 165, 233, 0.1);

  /* 보더 */
  --color-border: #e2e8f0;

  /* 상태 */
  --color-success: #10b981;
  --color-warning: #f59e0b;
  --color-error: #ef4444;
}
```

---

## 다크 모드

`[data-theme="dark"]` 셀렉터로 다크 모드 스타일 정의:

```css
[data-theme="dark"] {
  --color-bg-primary: #0f172a;
  --color-text-primary: #ffffff;
  /* ... */
}
```

**참고**: `developer`, `premium`, `creative` 테마는 다크 모드 고정입니다.

---

## 추가 계획

- [ ] 테마별 전용 컴포넌트 스타일
- [ ] A/B 테스트 통합
- [ ] 사용자 선호도 분석
- [ ] 시즌별 테마 (할로윈, 크리스마스 등)
