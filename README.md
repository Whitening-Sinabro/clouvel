# Clouvel

> **PRD 없으면 코딩 없다.**

바이브코딩 프로세스를 강제하는 MCP 서버.
문서 없이 코딩 시작? 차단됩니다.

---

## v1.3.9 (2026-01-23)

- **Pro 배포 인프라**: S3 기반 Pro 모듈 자동 다운로드
- **activate 개선**: 라이선스 활성화 시 Pro 자동 설치
- **에러 처리 강화**: 네트워크 재시도, 지수 백오프

## v1.3.8 (2026-01-23)

- **manager 개선**: relevance score 기반 질문 필터링 (삼천포 방지)
- **크리티컬 체크**: 각 매니저별 누락 사항/보안 이슈 자동 검출
- **승인 상태**: BLOCKED / NEEDS_REVISION / APPROVED 표시

## v1.3.7 (2026-01-22)

- **Antigravity 지원**: Google Antigravity 연동 가이드 추가
- **Pro 안정화**: 도구 안정성 개선

## v1.3.6 (2026-01-22)

- **FAQ 페이지**: 자주 묻는 질문 문서 추가
- **안정화**: gitignore 정리, 도구 안정성 개선

## v1.3.5 (2026-01-22)

- **PyPI 수정**: license_free.py stub 추가 (배포 오류 수정)

## v1.3.4 (2026-01-22)

- **템플릿 8종**: web-app, api, cli, chrome-ext, discord-bot, landing-page, saas, generic
- **start 개선**: 프로젝트 타입 자동 감지 + 대화형 PRD 가이드
- **save_prd**: PRD 저장 도구 추가
- **버전 체크**: PyPI 최신 버전 알림 (24시간 캐싱)

---

## 설치

```bash
pip install clouvel
```

---

## Claude Code 연동

`claude_desktop_config.json`에 추가:

```json
{
  "mcpServers": {
    "clouvel": {
      "command": "uvx",
      "args": ["clouvel"]
    }
  }
}
```

---

## 도구 목록 (23개)

### Core (4개)

| 도구           | 설명                       |
| -------------- | -------------------------- |
| `can_code`     | 코딩 가능? PRD 있어야 허용 |
| `scan_docs`    | docs 폴더 파일 목록        |
| `analyze_docs` | 필수 문서 체크             |
| `init_docs`    | docs 폴더 + 템플릿 생성    |

**예시: can_code**

```
You: "로그인 기능 만들어줘"
Claude: can_code 호출...

❌ 코딩 차단
- PRD.md 없음
- Architecture.md 없음
💡 먼저 PRD를 작성하세요.
```

---

### Docs (6개)

| 도구                   | 설명                 |
| ---------------------- | -------------------- |
| `get_prd_template`     | PRD 템플릿 생성      |
| `write_prd_section`    | PRD 섹션별 가이드    |
| `get_prd_guide`        | PRD 작성 전체 가이드 |
| `get_verify_checklist` | 검증 체크리스트      |
| `get_setup_guide`      | 플랫폼별 설정 가이드 |
| `get_analytics`        | 사용량 통계          |

**예시: get_analytics**

```
📊 최근 7일 사용 통계
- can_code: 23회
- gate: 8회
- Gate 통과율: 85%
```

---

### Setup (2개)

| 도구           | 설명                 |
| -------------- | -------------------- |
| `init_clouvel` | 온보딩 (플랫폼 선택) |
| `setup_cli`    | CLI 환경 설정        |

**예시: setup_cli**

```
You: "strict 모드로 설정해줘"

⚙️ CLI 설정 완료
- CLAUDE.md 생성됨
- pre-commit 훅 설치됨
- PRD 없으면 커밋 차단
```

---

### Rules - v0.5 (3개)

| 도구         | 설명                  |
| ------------ | --------------------- |
| `init_rules` | 규칙 파일 생성        |
| `get_rule`   | 파일별 적용 규칙 조회 |
| `add_rule`   | 새 규칙 추가          |

**예시: get_rule**

```
You: "auth.ts 수정하려는데 규칙 뭐야?"

📜 auth.ts 적용 규칙
NEVER:
- 비밀번호 평문 저장
- JWT 시크릿 하드코딩
ALWAYS:
- bcrypt로 해싱
```

---

### Verify - v0.5 (3개)

| 도구      | 설명                       |
| --------- | -------------------------- |
| `verify`  | Context Bias 제거 검증     |
| `gate`    | lint → test → build 자동화 |
| `handoff` | 의도 기록 (다음 세션용)    |

**예시: gate**

```
You: "gate 돌려줘"

🚦 Gate 실행
1. Lint... ✅
2. Test... ✅ (12/12)
3. Build.. ✅
🎉 Gate PASS - 커밋 가능!
```

**예시: handoff**

```
You: "로그인 기능 끝났어"

📋 핸드오프 저장됨
- 기능: 로그인
- 결정: JWT 선택
- 주의: refresh token 미구현
- 다음: 회원가입
```

---

### Planning - v0.6 (4개)

| 도구              | 설명               |
| ----------------- | ------------------ |
| `init_planning`   | 작업 목표 설정     |
| `save_finding`    | 조사 결과 저장     |
| `refresh_goals`   | 목표 리마인드      |
| `update_progress` | 진행 상황 업데이트 |

**예시: refresh_goals**

```
You: "지금 뭐하고 있었지?"

🎯 현재 목표
작업: 결제 시스템

✅ Stripe 연동
🔄 웹훅 처리 (진행 중)
⬚ 영수증 발송

진행률: 33%
```

---

### Agents - v0.7 (2개)

| 도구              | 설명               |
| ----------------- | ------------------ |
| `spawn_explore`   | 코드베이스 탐색    |
| `spawn_librarian` | 외부 문서/API 조사 |

**예시: spawn_explore**

```
You: "인증 로직 어디있어?"

🔍 탐색 결과
- src/lib/auth.ts (메인)
- src/middleware/auth.ts
- src/api/auth/route.ts
```

**예시: spawn_librarian**

```
You: "Next.js 15 바뀐거 조사해줘"

📚 조사 결과
- async/await 서버 컴포넌트 기본
- 새 캐싱 전략
- Turbopack 안정화
출처: Next.js 공식 문서
```

---

### Hooks - v0.8 (2개)

| 도구          | 설명              |
| ------------- | ----------------- |
| `hook_design` | 코딩 전 자동 체크 |
| `hook_verify` | 코딩 후 자동 검증 |

**예시: hook_verify**

```
You: "커밋 전에 자동으로 검사하게 해줘"

🪝 검증 훅 생성됨
트리거: pre_commit
단계: lint, test
실패 시: 커밋 차단
```

---

## Pro 버전

더 강력한 기능이 필요하다면 **Clouvel Pro**를 확인하세요.

### Pro 기능

- **Manager**: 8명 C-Level 매니저 피드백 (PM, CTO, QA, CDO, CMO, CFO, CSO, Error)
- **Ship**: 원클릭 테스트→검증→증거 생성
- **Error Learning**: 에러 패턴 학습 + NEVER/ALWAYS 규칙 자동 생성
- **Shovel 워크플로우** 자동 설치

### Pro 활성화

```bash
# 1. 설치
pip install clouvel

# 2. 라이선스 활성화
clouvel activate <LICENSE_KEY>

# 자동으로 Pro 모듈 9개 다운로드 & 설치됨
```

**[Clouvel Pro 구매하기](https://clouvel.lemonsqueezy.com)**

---

## 링크

- [GitHub](https://github.com/Whitening-Sinabro/clouvel)
- [Landing Page](https://whitening-sinabro.github.io/clouvel/)
- [Issues](https://github.com/Whitening-Sinabro/clouvel/issues)

---

## 라이선스

MIT
