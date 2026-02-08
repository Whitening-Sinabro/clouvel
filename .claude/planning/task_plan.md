# Task Plan: 영어권 피벗 + 6주 로드맵

> 생성일: 2026-01-24
> 기반: C-Level 동적 회의 결과

---

## 배경

- **문제**: 한국 타겟 마케팅 → 구독자 0명
- **원인**: Claude Code/MCP 생태계가 영어권 중심
- **결정**: 한국 마케팅 중단, 영어권 올인

---

## 6주 목표

| 시점 | 목표 |
|------|------|
| **2주차** | GitHub 프로젝트 완전 정비 완료 |
| **4주차** | 무료 사용자 100명 확보 |
| **6주차** | Show HN 포스팅 + 유료 전환 의향자 10명 |

---

## Phase 1: GitHub 프로젝트 정비 (Week 1-2)

### 1.1 README.md 영문 재작성

| # | 작업 | 파일 | 상태 |
|---|------|------|------|
| 1.1.1 | Hero 섹션 - 한 줄 설명 + 배지 | README.md | [ ] |
| 1.1.2 | 데모 GIF 추가 (can_code 차단 장면) | README.md | [ ] |
| 1.1.3 | Quick Start (3줄 설치) | README.md | [ ] |
| 1.1.4 | Features 섹션 (Free vs Pro 명확히) | README.md | [ ] |
| 1.1.5 | 실제 사용 예시 (Before/After) | README.md | [ ] |

#### README 구조
```markdown
# Clouvel

> No spec, no code. PRD-First gate for AI coding.

[![PyPI](https://img.shields.io/pypi/v/clouvel)](https://pypi.org/project/clouvel/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

![Demo GIF](docs/demo.gif)

## Quick Start

\`\`\`bash
pip install clouvel
claude mcp add clouvel -- clouvel serve
claude  # can_code check runs automatically
\`\`\`

## Why Clouvel?

**Before**: "Build login" → AI guesses, skips password reset, social login
**After**: AI reads PRD → implements exactly what you specified

## Features

### Free
- PRD enforcement (can_code)
- Project onboarding (start)
- Progress tracking

### Pro ($9.99/mo)
- 8 C-Level managers
- One-click Ship
- Error Learning

## Documentation

[Full docs →](https://whitening-sinabro.github.io/clouvel/)
```

### 1.2 Contributing Guide

| # | 작업 | 파일 | 상태 |
|---|------|------|------|
| 1.2.1 | CONTRIBUTING.md 생성 | CONTRIBUTING.md | [ ] |
| 1.2.2 | CODE_OF_CONDUCT.md 생성 | CODE_OF_CONDUCT.md | [ ] |
| 1.2.3 | Issue 템플릿 추가 | .github/ISSUE_TEMPLATE/ | [ ] |
| 1.2.4 | PR 템플릿 추가 | .github/PULL_REQUEST_TEMPLATE.md | [ ] |

### 1.3 커뮤니티 채널 개설

| # | 작업 | 상태 |
|---|------|------|
| 1.3.1 | GitHub Discussions 활성화 | [ ] |
| 1.3.2 | Discord 서버 생성 (선택) | [ ] |

### 1.4 기술 점검

| # | 작업 | 상태 |
|---|------|------|
| 1.4.1 | 에러 메시지 영어 확인 | [ ] |
| 1.4.2 | CLI 출력 영어 확인 | [ ] |
| 1.4.3 | 로그 메시지 영어 확인 | [ ] |

---

## Phase 2: 커뮤니티 활동 (Week 3-4)

### 2.1 Reddit 활동

| # | 작업 | 채널 | 상태 |
|---|------|------|------|
| 2.1.1 | r/ClaudeAI 가입 + 소개 글 | Reddit | [ ] |
| 2.1.2 | r/SideProject 소개 글 | Reddit | [ ] |
| 2.1.3 | r/IndieHackers 활동 | Reddit | [ ] |

#### Reddit 글 구조
```
Title: I built a PRD gate for AI coding - no spec, no code

Hey everyone! Solo dev here.

**Problem I had**: AI keeps skipping requirements. I say "build login" and it forgets password reset, social auth, etc.

**Solution**: Clouvel - an MCP server that blocks coding until you write a spec.

Demo: [GIF]

It's free and open source: github.com/...

Would love feedback!
```

### 2.2 X (Twitter) 활동

| # | 작업 | 해시태그 | 상태 |
|---|------|----------|------|
| 2.2.1 | 계정 영문 프로필로 변경 | - | [ ] |
| 2.2.2 | 첫 소개 쓰레드 | #MCP #ClaudeCode #BuildInPublic | [ ] |
| 2.2.3 | 주 2회 Build in Public 포스트 | #BuildInPublic | [ ] |

### 2.3 사용자 피드백 수집

| # | 작업 | 상태 |
|---|------|------|
| 2.3.1 | GitHub Issues로 피드백 수집 | [ ] |
| 2.3.2 | 주요 피드백 정리 | [ ] |
| 2.3.3 | 피드백 기반 개선 | [ ] |

---

## Phase 3: 확산 (Week 5-6)

### 3.1 Show HN 준비

| # | 작업 | 조건 | 상태 |
|---|------|------|------|
| 3.1.1 | 사용자 50명 확보 확인 | 필수 | [ ] |
| 3.1.2 | Show HN 글 작성 | 3.1.1 완료 후 | [ ] |
| 3.1.3 | 포스팅 타이밍 결정 (화-목 오전) | - | [ ] |
| 3.1.4 | Show HN 포스팅 | - | [ ] |

#### Show HN 글 구조
```
Show HN: Clouvel – PRD gate for AI coding (no spec, no code)

Hi HN!

I'm a solo dev who got tired of AI skipping requirements.
"Build login" → no password reset, no social auth.

So I built Clouvel, an MCP server that blocks coding until you write a spec.

- Free and open source
- Works with Claude Code, Desktop, VS Code
- 8 project templates included

Demo: [link]
GitHub: [link]

Feedback welcome!
```

### 3.2 Product Hunt 준비

| # | 작업 | 상태 |
|---|------|------|
| 3.2.1 | PH 프로필 영문 업데이트 | [ ] |
| 3.2.2 | 스크린샷/GIF 준비 | [ ] |
| 3.2.3 | 런칭 날짜 결정 | [ ] |

### 3.3 유료 전환 파악

| # | 작업 | 상태 |
|---|------|------|
| 3.3.1 | 활성 사용자 중 Pro 관심자 파악 | [ ] |
| 3.3.2 | 1:1 피드백 요청 | [ ] |
| 3.3.3 | Pro 기능 개선점 정리 | [ ] |

---

## 성공 지표

| 지표 | Week 2 | Week 4 | Week 6 |
|------|--------|--------|--------|
| GitHub Stars | 30+ | 100+ | 300+ |
| 무료 사용자 | 20+ | 100+ | 200+ |
| WAU | 10+ | 50+ | 100+ |
| Pro 관심자 | - | - | 10+ |

---

## 주간 체크포인트

### Week 1
- [ ] README.md 재작성 완료
- [ ] 데모 GIF 생성
- [ ] Contributing guide 추가

### Week 2
- [ ] GitHub Discussions 활성화
- [ ] 에러 메시지 영어 확인
- [ ] 첫 Reddit 포스트

### Week 3
- [ ] r/ClaudeAI, r/SideProject 포스팅
- [ ] X 소개 쓰레드
- [ ] 사용자 피드백 수집 시작

### Week 4
- [ ] 100명 사용자 확보
- [ ] 주요 피드백 반영
- [ ] Show HN 글 초안

### Week 5
- [ ] Show HN 포스팅
- [ ] 반응 모니터링
- [ ] Product Hunt 준비

### Week 6
- [ ] 유료 전환 의향자 파악
- [ ] 6주 결과 리뷰
- [ ] 다음 단계 계획

---

## ⚠️ 주의사항

- ❌ NEVER: 한국 마케팅에 시간 투자
- ❌ NEVER: 준비 안 된 상태로 Show HN
- ❌ NEVER: 사용자 없이 Product Hunt
- ✅ ALWAYS: 영어권 개발자 관점으로 검토
- ✅ ALWAYS: 커뮤니티 활동 전 코드/문서 품질 확보
- ✅ ALWAYS: 피드백 기반 개선

---

## 첫 번째 액션

**지금 바로 시작**: README.md 영문 재작성

```bash
# 데모 GIF 녹화 준비
# 1. can_code 차단 장면
# 2. PRD 작성 후 통과 장면
# 3. manager 피드백 장면 (Pro)
```

---

> 💡 진행 상황 업데이트: `update_progress` 도구 호출
