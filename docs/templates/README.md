# Clouvel 템플릿 가이드

> 프로젝트 타입별 PRD 작성 가이드

---

## 템플릿 목록

| 템플릿                          | 설명                      | 자동 감지                     |
| ------------------------------- | ------------------------- | ----------------------------- |
| [web-app](web-app.md)           | React/Vue/Svelte 등 웹 앱 | `src/App.tsx`, `pages/`       |
| [api](api.md)                   | REST API 서버             | `server.py`, FastAPI/Express  |
| [cli](cli.md)                   | 커맨드라인 도구           | `bin/`, `cli.py`, Click/Typer |
| [chrome-ext](chrome-ext.md)     | Chrome 확장프로그램       | `manifest.json`               |
| [discord-bot](discord-bot.md)   | 디스코드 봇               | discord.js/discord.py         |
| [landing-page](landing-page.md) | 마케팅 랜딩 페이지        | `index.html` (단독)           |
| [saas](saas.md)                 | SaaS MVP                  | Stripe/결제 연동              |
| [generic](generic.md)           | 범용 템플릿               | 기본값                        |

---

## 사용법

### 1. 프로젝트 시작

```
You: "새 프로젝트 시작할게"
Claude: start 도구 호출...

🚀 프로젝트 온보딩
프로젝트 타입: web-app (자동 감지)
```

### 2. 타입 수동 지정

```
You: "chrome-ext로 시작해줘"
Claude: start 도구 호출 (project_type="chrome-ext")
```

### 3. PRD 대화형 작성

각 템플릿은 타입에 맞는 질문을 제공합니다:

```
Claude: "이 확장프로그램이 해결하려는 문제는 무엇인가요?"
You: "유튜브 광고 스킵이 번거로움"

Claude: "핵심 기능 3가지를 알려주세요"
You: "1. 광고 자동 스킵 2. 스폰서 구간 건너뛰기 3. 통계 표시"
```

---

## 템플릿 선택 가이드

### 뭘 만들지 모르겠다면?

```
┌─────────────────────────────────────────┐
│  웹사이트/앱을 만든다                    │
│  ├─ 결제 기능 있다 → saas               │
│  ├─ 마케팅 페이지만 → landing-page      │
│  └─ 그 외 → web-app                     │
├─────────────────────────────────────────┤
│  서버/백엔드를 만든다                    │
│  └─ → api                               │
├─────────────────────────────────────────┤
│  도구를 만든다                           │
│  ├─ 터미널에서 실행 → cli               │
│  ├─ 브라우저 확장 → chrome-ext          │
│  └─ 디스코드 봇 → discord-bot           │
├─────────────────────────────────────────┤
│  잘 모르겠다 → generic                   │
└─────────────────────────────────────────┘
```

---

## PRD 필수 섹션

모든 템플릿에 공통:

| 섹션         | 설명          | 필수 |
| ------------ | ------------- | ---- |
| summary      | 프로젝트 목적 | ✅   |
| target       | 타겟 사용자   | ✅   |
| features     | 핵심 기능     | ✅   |
| out_of_scope | 제외 범위     | ✅   |

템플릿별 추가 섹션은 각 문서 참조.

---

## 관련 도구

| 도구               | 설명                         |
| ------------------ | ---------------------------- |
| `start`            | 프로젝트 온보딩 + PRD 가이드 |
| `save_prd`         | PRD 저장                     |
| `can_code`         | PRD 유무 체크                |
| `get_prd_template` | PRD 템플릿 생성              |
