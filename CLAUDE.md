# Clouvel

> PRD 없으면 코딩 없다.

---

## 개요

Clouvel은 바이브코딩 프로세스를 강제하는 MCP 서버입니다.

문서 없이 코딩 시작? 차단됩니다.

---

## 기본 사용법

```bash
# 설치
pip install clouvel

# Claude Code에서 사용
claude --mcp clouvel
```

---

## 핵심 도구

| 도구           | 설명                   |
| -------------- | ---------------------- |
| `can_code`     | 코딩 가능 여부 검사    |
| `get_progress` | 진행 상황 확인         |
| `get_goal`     | 프로젝트 목표 리마인드 |

---

## Pro 버전

더 강력한 기능이 필요하다면 [Clouvel Pro](https://whitening-sinabro.github.io/clouvel/)를 확인하세요.

- Shovel 워크플로우 자동 설치
- Gate 시스템 (lint → test → build)
- Context 관리 도구
- 검증 프로토콜

---

## 링크

- [GitHub](https://github.com/Whitening-Sinabro/clouvel)
- [Landing Page](https://whitening-sinabro.github.io/clouvel/)

---

## 🔒 보안 규칙 (MUST CHECK)

> **커밋 전 반드시 확인. 위반 시 커밋 금지.**

### 절대 커밋 금지 파일

| 카테고리 | 패턴                                              | 이유          |
| -------- | ------------------------------------------------- | ------------- |
| 마케팅   | `*MARKETING*`, `*STRATEGY*`, `*마케팅*`, `*전략*` | 비즈니스 기밀 |
| 가격     | `*pricing*`, `*PRICING*`, `*가격*`                | 비즈니스 기밀 |
| Pro 코드 | `server_pro.py`, `license.py`, `tools/team.py`    | 유료 기능     |
| 시크릿   | `*.key`, `*.secret`, `license*.json`              | 보안          |

### 커밋 전 체크리스트

```bash
# 반드시 실행
git diff --cached --name-only | grep -iE "(marketing|strategy|pricing|pro|license|secret|key)"
```

**결과가 있으면 커밋 금지!**

### 실수로 커밋했다면

```bash
# 히스토리에서 완전 삭제
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch <파일경로>" \
  --prune-empty --tag-name-filter cat -- --all

# 원격에 강제 푸시
git push origin main --force
```

### Claude 규칙

- Write/Edit 전에 파일명이 위 패턴과 일치하면 **작업 거부**
- 의심스러우면 사용자에게 먼저 확인
- `.gitignore` 확인 후 추적 여부 검증

## Clouvel 규칙 (자동 생성)

> 이 규칙은 Clouvel이 자동으로 추가했습니다.

### 필수 준수 사항

1. **코드 작성 전 문서 체크**: Edit/Write 도구 사용 전 반드시 `can_code` 도구를 먼저 호출
2. **can_code 실패 시 코딩 금지**: 필수 문서가 없으면 PRD 작성부터
3. **PRD가 법**: docs/PRD.md에 없는 기능은 구현하지 않음
