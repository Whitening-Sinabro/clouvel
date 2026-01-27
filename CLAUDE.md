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

## 환경 설정

### 개발 모드 (개발자 전용)

```bash
# 방법 1: 환경 변수 (권장)
export CLOUVEL_DEV=1

# 방법 2: git remote 자동 감지
# clouvel 저장소 내에서 실행 시 자동 활성화
```

**개발 모드 활성화 시**:
- 라이선스 체크 우회
- Pro 기능 전체 접근
- Worker API 우회 → 로컬 실행

### 환경 변수 목록

| 변수 | 용도 | 기본값 |
|------|------|--------|
| `CLOUVEL_DEV` | 개발 모드 | - |
| `CLOUVEL_LICENSE` | 라이선스 키 | - |
| `ANTHROPIC_API_KEY` | 동적 회의 | - (없으면 static mode) |
| `CLOUVEL_KB_KEY` | KB 암호화 | - (선택) |

### 필수 파일

| 파일 | 용도 | Git 추적 |
|------|------|----------|
| `.env` | 로컬 설정 | ❌ (.gitignore) |
| `.env.example` | 템플릿 | ✅ |

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

---

## 🚨 사이드이펙트 체크 규칙 (MUST)

> 계획 변경 시 반드시 영향 범위를 확인하라.

### 동기화 필수 파일 쌍

| Primary 파일 | Stub/Free 파일 | 동기화 항목 |
|-------------|---------------|------------|
| `license.py` | `license_free.py` | 함수 시그니처, 반환값 구조 |
| `server.py` | `server_pro.py` | Tool 정의, handler 매핑 |
| `messages/en.py` | `messages/ko.py` | 메시지 키, 포맷 변수 |

### 변경 전 체크리스트

1. **Stub 파일 확인**: Primary 파일 수정 시 Stub 파일도 동일 인터페이스 유지
2. **반환값 구조**: 함수 반환값에 새 필드 추가 시 Stub도 동일하게 추가
3. **테스트 실행**: 변경 후 반드시 `pytest tests/` 실행
4. **uvx 환경 테스트**: PyPI 배포 시 Stub만 사용됨을 인지

### 과거 실수 사례

| 날짜 | 문제 | 원인 | 예방책 |
|-----|------|-----|-------|
| 2026-01-25 | license_status가 "Unknown" 표시 | license_free.py에 tier_info 반환 누락 | Stub 파일 동기화 체크 |
| 2026-01-25 | uvx에서 anthropic 못찾음 | optional dependency 미지정 | pyproject.toml 확인 |
| 2026-01-26 | manager 도구 충돌 | tools/__init__.py와 tools/manager/core.py 둘 다 manager 정의 | Import 규칙 준수 |

---

## 🏗️ 아키텍처 규칙 (LOCKED)

> **Knowledge Base에 기록됨. 변경 시 unlock 필요.**
> `search_knowledge("architecture")` 로 전체 결정 조회 가능.

### Import 규칙 (🔒 LOCKED #30)

```
server.py
  └─ from .tools import xxx  ✅ (tools/__init__.py에서만)
  └─ from .tools.manager import xxx  ❌ (직접 import 금지)
```

- `server.py`는 `tools/__init__.py`에서만 import
- `tools/xxx/` 폴더에서 직접 import 금지
- `tools/__init__.py`가 단일 진입점

### Pro 기능 패턴 (🔒 LOCKED #31)

```
tools/xxx.py (진입점)
  → call_xxx_api() (권한 체크)
  → tools/xxx_pro.py (실행)
```

**표준 예시**: `ship.py` 참조
- API로 Trial/License만 체크
- 실제 로직은 `xxx_pro.py`에서 로컬 실행
- 오프라인 시 graceful degradation

### 파일 구조 (🔒 LOCKED #37)

| 패턴 | 용도 | 예시 |
|------|------|------|
| `tools/xxx.py` | 진입점 (조합) | `ship.py` |
| `tools/xxx_pro.py` | Pro 구현 | `ship_pro.py` |
| `tools/xxx/` | 복잡한 내부 모듈 | `manager/` (내부용) |

### ✅ Manager 충돌 해결됨 (#32 - RESOLVED, v1.8.0)

| 위치 | 역할 | 현재 상태 |
|------|------|----------|
| `server.py` | `call_manager_api()` 호출 | ✅ Worker API 사용 |
| `tools/manager/` | 로컬 모듈 (DEV 모드) | ✅ DEV 시에만 사용 |

**해결**: Worker API 전환 완료 (2026-01-26)
- Non-dev: Worker API 호출
- Dev: 로컬 manager 모듈 사용

### 라이센스 모듈 (🔒 LOCKED #33)

| 파일 | 역할 |
|------|------|
| `license_common.py` | 공통 로직 (is_developer, get_machine_id 등) |
| `license.py` | Pro 버전 (API 검증) |
| `license_free.py` | Free 스텁 (PyPI 배포용) |

**규칙**: 반환값 구조 동일 유지 필수

### Optional 의존성 (🔒 LOCKED #35)

| 패키지 | 용도 | 필수 여부 |
|--------|------|----------|
| `requests` | API 클라이언트 | 런타임 (fallback 있음) |
| `anthropic` | Dynamic meeting | 런타임 (fallback 있음) |

서버 시작 시 필수 아님. 사용 시점에 import + fallback 처리.

---

## 📝 기록 규칙 (LOCKED)

> **긍정적 프레이밍**: "하지 마라" 대신 "이렇게 해라"

### 기록 트리거 (🔒 LOCKED #39)

| 상황 | 행동 |
|------|------|
| 아키텍처 변경 | `record_decision(category="architecture", locked=True)` |
| 새 파일 생성 | `record_location(name, repo, path)` |
| 설계 결정 | `record_decision(category="design")` + reasoning 필수 |
| 프로세스 변경 | `record_decision(category="process")` |

### 코드 추가 전 확인 (🔒 LOCKED #40)

새 함수/모듈 작성 전:
1. `search_knowledge("함수명 또는 기능")` - 기존 결정 확인
2. `Grep` - 기존 코드에 같은 역할 있는지 확인
3. 있으면 **수정**, 없으면 **추가**

### 규칙 작성 원칙 (🔒 LOCKED #38)

| 부정적 (피하기) | 긍정적 (사용) |
|----------------|--------------|
| "중복 정의 금지" | "각 함수는 하나의 위치에서만 export" |
| "직접 import 금지" | "server.py는 tools/__init__.py에서 import" |
| "기록 안 하면 안 됨" | "아키텍처 변경 시 record_decision 호출" |

**연구 근거**: Wegner (1987) - 부정형 지시는 역효과. Anthropic/OpenAI 공식 문서 - 긍정적 프레이밍 권장.

---

## 📋 Compounding Rules (과거 실수에서 배운 규칙)

> **추가일**: 2026-01-27
> **목적**: 같은 실수 반복 방지

### Rule 1: Stub 파일 동기화 (2026-01-25)

**트리거**: `license.py`, `license_free.py`, `messages/*.py` 수정 시

**체크리스트**:
1. 반환값 구조 일치 확인
2. 함수 시그니처 일치 확인
3. `check_sync(path)` 실행하여 자동 검증

**사고 사례**: `license_status`가 "Unknown" 표시 - `tier_info` 반환 누락

### Rule 2: PyPI 배포 전 테스트 (2026-01-25)

**트리거**: version bump 후 배포 전

**체크리스트**:
1. `pip install -e .` 로컬 테스트
2. `uvx clouvel@latest license_status` 실행
3. tier_info 정상 반환 확인
4. optional deps 없이도 기본 기능 동작 확인

**사고 사례**: uvx에서 `anthropic` import 실패 - optional dependency 미지정

### Rule 3: Import 규칙 준수 (2026-01-26)

**트리거**: `server.py`에서 tools import 추가 시

**체크리스트**:
1. `from .tools import xxx` 형태만 사용
2. `from .tools.xxx import yyy` 형태 금지
3. `check_imports(path)` 실행하여 자동 검증

**사고 사례**: Manager 도구 충돌 - 두 곳에서 같은 함수 정의

### Rule 4: 테스트 후 검증 (2026-01-25)

**트리거**: 기능 구현 완료 후

**체크리스트**:
1. `pytest tests/` 통과
2. MCP 도구 수동 호출 테스트 (실제 환경)
3. uvx 환경에서 테스트 (PyPI 배포 시뮬레이션)

**원칙**: pytest 통과 ≠ 완료. 실제 MCP 환경 테스트 필수.

---

## 🔄 v1.9 도구 통합 안내

> **추가일**: 2026-01-27
> **목적**: Deprecated 도구 대체 방법 안내

### 대체 매핑

| Deprecated | 대체 | 예시 |
|------------|------|------|
| `scan_docs` | `can_code` | `can_code(path)` |
| `analyze_docs` | `can_code` | `can_code(path)` |
| `verify` | `ship` | `ship(path, steps=["lint", "test"])` |
| `gate` | `ship` | `ship(path, steps=steps, auto_fix=fix)` |
| `get_prd_template` | `start` | `start(path, template="web-app")` |
| `get_prd_guide` | `start` | `start(path, guide=True)` |
| `init_docs` | `start` | `start(path, init=True)` |
| `init_rules` | `setup_cli` | `setup_cli(path, rules="web")` |
| `hook_design` | `setup_cli` | `setup_cli(path, hook="design")` |
| `hook_verify` | `setup_cli` | `setup_cli(path, hook="verify")` |
| `handoff` | `record_decision` + `update_progress` | 조합 사용 |

### v2.0 제거 예정

위 deprecated 도구들은 v2.0에서 완전 제거 예정.
현재는 deprecation warning만 표시되며 기능은 정상 동작.
