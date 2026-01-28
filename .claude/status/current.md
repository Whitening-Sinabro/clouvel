# Clouvel 현재 상태

> **마지막 업데이트**: 2026-01-28 (v2.0.0 PyPI 배포 완료)

---

## 개발 환경

| 항목 | 값 |
|------|-----|
| **패키지 관리** | uv / uvx |
| **로컬 테스트** | `py -m pip install -e D:\clouvel` |
| **MCP 설정** | `PYTHONPATH=D:\clouvel\src` (로컬 소스 강제) |
| **MCP 리로드** | Claude Code 재시작 (프로세스 재시작 필요) |
| **Python** | 3.10+ |

---

## 지금 상태

| 항목              | 상태                              |
| ----------------- | --------------------------------- |
| **clouvel**       | v2.0.0 PyPI 배포 완료 |
| **아키텍처**      | ✅ Manager Worker API 전환 완료   |
| **문서 시스템**   | ✅ SSOT 완성 (ENTRYPOINTS + SIDE_EFFECTS + SMOKE_LOGS) |
| **MCP 표준화**    | ✅ 52개 도구 분석 완료 (9그룹, 12표준, 5폐기, 6통합) |
| **Knowledge Base**| ✅ 아키텍처 결정 기록 완료        |
| **라이선스 서버** | ✅ 동작 중 (Polar.sh + Worker API) |
| **결제**          | ✅ Polar.sh 연동 완료             |
| **보안**          | ✅ 민감 파일 커밋 차단 자동화     |
| **Product Hunt**  | 🚀 런칭 예약됨 (2026-01-28 15:00 VN) |

---

## 확인된 런타임 경로 (v1.9.0)

- **Manager**: `_wrap_manager()` → `call_manager_api()` → Dev mode? → 로컬 실행 | Non-dev → Worker API
- **Ship**: Dev mode → 직접 실행 | Non-dev → API 권한 체크 → 로컬 실행
- **License**: `license_free.py` stub (PyPI) | `license.py` (Pro/Dev)

## Top 3 Side Effects

1. **Network**: Worker API 호출 (`clouvel-api.workers.dev`, 30s timeout)
2. **File I/O**: `~/.clouvel/license.json` (라이선스 캐시)
3. **Process**: `git remote -v` (is_developer 체크, 5s timeout)

---

## 문서 시스템 (SSOT)

### 구조

```
docs/architecture/
├── ENTRYPOINTS.md          # 진입점 (CLI, MCP, Packaging)
├── SIDE_EFFECTS.md         # 외부 부작용 매트릭스
├── SMOKE_LOGS.md           # 실행 검증 기록
├── RUNTIME_PATHS.md        # 조건 분기 (AUTO-GEN)
├── MODULE_MAP.md           # 모듈 맵 (AUTO-GEN)
├── data_contracts.md       # API 스키마 (AUTO-GEN)
├── CALL_FLOWS/
│   ├── flow_index.md       # 인덱스
│   ├── flow_manager.md     # Manager 플로우
│   ├── flow_activate.md    # 라이선스 활성화
│   └── flow_webhook.md     # Worker API 통신
└── DECISION_LOG/
    └── ADR-0001-manager-execution.md  # RESOLVED

docs/mcp/
├── MCP_CATALOG.md          # 52개 도구 전체 카탈로그
├── MCP_GROUPS.md           # 9개 유사 그룹 분류
└── MCP_STANDARDIZATION_PLAN.md  # 표준화 계획 + 로드맵

scripts/
├── docs_extract.py         # AUTO-GEN 섹션 갱신
└── docs_check.py           # 문서 유효성 검증 (all PASS)
```

### 검증 명령

```bash
py -3 scripts/docs_check.py   # 문서 유효성 검증
py -3 scripts/docs_extract.py # AUTO-GEN 섹션 갱신
```

---

## 결론 (2026-01-26)

**v1.8.0 배포 - Manager Worker API 전환 완료**

- `_wrap_manager()`가 `call_manager_api()` 호출하도록 수정
- `_wrap_quick_perspectives()`도 Worker API 사용하도록 변경
- 로컬 `tools/manager/` 의존성 제거
- PyPI 설치 시 정상 동작 확인

**SSOT 문서 시스템 강화 완료**:
- ENTRYPOINTS.md - 진입점 문서 (Evidence 기반)
- SIDE_EFFECTS.md - 부작용 매트릭스 (6개 카테고리)
- SMOKE_LOGS.md - 실행 검증 기록 템플릿
- ADR-0001 업데이트 - RESOLVED 상태로 변경
- docs_extract.py - entrypoints, side_effects 추출 추가
- docs_check.py - 새 문서 검증 추가 (7개 체크 all PASS)

---

## 오늘 완료 (2026-01-28)

### Product Hunt 런칭 예약 ✅

**런칭 시간**: 2026-01-28 15:00 (베트남) / 00:01 PST

**완료 항목**:
- [x] 썸네일 이미지 수정 (비율 깨짐 해결)
- [x] Gallery 이미지 3장 (01, 02, 04)
- [x] 데모 영상 YouTube 업로드 (20초, 10배속)
- [x] Shoutouts 추가 (Claude, GitHub, Polar)
- [x] First comment 작성
- [x] 프로모 코드: LAUNCH70 (70% off)
- [x] Bootstrapped 선택
- [x] 100% 체크리스트 완료

**소셜 포스트 예약**:
| 플랫폼 | 시간 (VN) | 상태 |
|--------|----------|------|
| Twitter | 15:00 | ✅ 예약됨 |
| Threads | 15:30 | ✅ 예약됨 |
| Twitter 리마인더 | 20:00 | ✅ 예약됨 |

**Reddit 포스트 준비**:
- [x] `docs/marketing/reddit-posts-ph-launch.md` 작성 완료
- r/ClaudeAI, r/SideProject, r/IndieHackers 3개

**런칭 당일 할 일**:
- [ ] 댓글 1시간마다 확인 & 답변
- [ ] Reddit 포스트 발행 (링크 교체 후)

### v2.0 Proactive MCP 구현 완료 ✅

**목표**: Claude Code Hooks 연동으로 자동 PRD 체크 및 드리프트 감지

**완료 항목**:

| 항목 | 설명 | 티어 |
|------|------|------|
| `can_code --silent` | 훅용 PRD 체크 (exit code만) | Free |
| `drift_check --silent` | 컨텍스트 드리프트 감지 | Pro |
| `pattern_watch` | 에러 패턴 감시 | Pro |
| `auto_remind` | 진행 리마인드 | Pro |
| `setup --proactive [free|pro]` | 훅 자동 설정 | Free |

**생성 파일**:
- `src/clouvel/tools/proactive.py` - 프로액티브 도구 (drift_check, pattern_watch, auto_remind)
- `tests/test_proactive.py` - 25개 테스트 (all pass)
- `docs/HOOKS.md` - Claude Code Hooks 연동 가이드

**수정 파일**:
- `src/clouvel/tools/setup.py` - `proactive` 파라미터 추가
- `src/clouvel/server.py` - CLI 명령어 + Tool 정의 추가
- `src/clouvel/tools/__init__.py` - export 추가

**훅 설정 예시** (`.claude/settings.local.json`):
```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "clouvel can_code --path ./docs --silent"
      }]
    }]
  }
}
```

**티어 전략**:
- Free: 자동 PRD 체크만 (코드 작성 전 차단)
- Pro: 드리프트 감지, 패턴 감시, 진행 리마인드 추가

**커밋**:
- `56d89b8` feat(v2.0): proactive MCP - drift_check, pattern_watch, auto_remind
- `47e6bc4` fix: remove emojis for Windows cp949 encoding
- `de62b24` feat: clouvel setup --proactive [free|pro] command

### v2.0.0 PyPI 배포 완료 ✅

**배포 시간**: 2026-01-28 ~13:00 (VN)

**버전**: `clouvel==2.0.0`

**배포 확인**:
```bash
uvx clouvel@2.0.0 status  # License status 확인
uvx clouvel@2.0.0 can_code --path ./docs --silent  # Exit 0 (PASS)
uvx clouvel@2.0.0 drift_check --path . --silent  # OK:NO_GOALS
```

**테스트 결과**:
- **1395 passed, 10 skipped** (40초)
- Skipped: ChromaDB 선택적 의존성 3개 + 이전 Shovel 테스트 7개

**Windows cp949 인코딩 수정**:
- `proactive.py`에서 모든 이모지 제거
- `[OK]`, `[WARN]`, `[ERROR]`, `[Pro]` 텍스트 형식으로 변경

**최종 커밋**:
- `26ac47f` feat(v2.0.0): Proactive MCP release + Windows cp949 fix
- `2206d07` chore: update current.md to v2.0.0 deployed status

### Pro 훅 활성화 ✅

**파일**: `.claude/settings.local.json`

```json
{
  "hooks": {
    "PreToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{
        "type": "command",
        "command": "clouvel can_code --path ./docs --silent"
      }]
    }],
    "PostToolUse": [{
      "matcher": ".*",
      "hooks": [{
        "type": "command",
        "command": "clouvel drift_check --path . --silent"
      }]
    }]
  }
}
```

**동작**:
- Edit/Write 전: PRD 체크 (BLOCK/PASS)
- 모든 도구 후: 드리프트 감지 (OK/WARN/DRIFT)

---

## 오늘 요약 (2026-01-28)

| 시간 | 작업 | 결과 |
|------|------|------|
| 오전 | Product Hunt 런칭 예약 | 15:00 VN 예약 완료 |
| 오전 | 썸네일/Gallery/소셜 포스트 | 전부 준비 완료 |
| 오후 | v2.0 Proactive MCP 구현 | proactive.py + 25 tests |
| 오후 | Windows cp949 이모지 수정 | 모든 이모지 제거 |
| 오후 | v2.0.0 PyPI 배포 | 배포 + uvx 테스트 완료 |
| 오후 | Pro 훅 활성화 | settings.local.json 업데이트 |

**GitHub 커밋 (오늘)**:
1. `56d89b8` - v2.0 proactive MCP 구현
2. `47e6bc4` - Windows 이모지 수정
3. `de62b24` - setup --proactive 명령어
4. `26ac47f` - v2.0.0 릴리즈
5. `2206d07` - current.md 업데이트

---

## 이전 완료 (2026-01-27)

### pytest coverage 52% 달성 ✅

**목표**: 49% → 50%
**결과**: **52%** (목표 초과 달성)

| 항목 | Before | After |
|------|--------|-------|
| 커버리지 | 49% | **52%** |
| 테스트 수 | ~1306 | **1341** |
| 테스트 파일 | - | +31개 |

**추가된 테스트 파일**:
- `test_api_client.py` - API 클라이언트 (dynamic meeting, import errors)
- `test_architecture.py` - 아키텍처 도구 (KB, grep, sync)
- `test_context.py` - 컨텍스트 복구
- `test_db_*.py` - DB 모듈 (errors, rules, migrate, vectors)
- `test_hooks.py` - 훅 시스템
- `test_rules_tools.py` - 규칙 도구
- 외 21개 모듈 테스트

**커밋**:
- `92cef73` test: increase coverage from 49% to 52%
- `162c066` feat: comprehensive tests + architecture docs + MCP catalog

---

### 8역할 C-Level 마스터 분석 ✅

**생성 파일**:
- `CLOUVEL_STATUS.md` - 현재 상태 종합
- `CLOUVEL_ACTION_PLAN.md` - P0/P1/P2 액션 플랜

**주요 발견**:
- PRD vs 구현 갭: 5개 기능 PRD 미반영
- 테스트 커버리지: 4개 파일만 (P0 개선 필요)
- Manager 충돌: ✅ RESOLVED (v1.8.0 Worker API)

**CLAUDE.md 업데이트**:
- Manager 충돌 해결됨으로 변경
- Compounding Rules 4개 추가
- v1.9 도구 통합 안내 추가

**다음 P0 액션**:
1. test_knowledge.py 작성 (20+ 테스트)
2. test_ship.py 작성 (15+ 테스트)
3. Reddit r/ClaudeAI 포스트 업로드

---

### v3.2: MCP 런타임 디버그 + 로컬 소스 강제 ✅

**문제**: `project_path` 기반 DEV 모드 감지가 MCP에서 작동 안 함
- 직접 Python 테스트: `is_developer("D:/clouvel")` → `True` ✅
- MCP 호출: `search_knowledge(project_path="D:\\clouvel")` → Pro 라이센스 필요 ❌

**원인**: MCP 서버가 설치본(`site-packages`)을 사용, 로컬 소스 아님

**해결**:
1. `debug_runtime` 도구 추가 (`server.py`)
   - `sys.executable`, `clouvel.__file__`, `is_developer()` 출력
   - MCP 런타임 환경 즉시 진단 가능
2. MCP 설정에 `PYTHONPATH` 추가
   ```bash
   claude mcp remove clouvel -s user
   claude mcp add clouvel -s user --env PYTHONPATH="D:\clouvel\src" -- py -m clouvel.server
   ```

**변경 파일**:
- `src/clouvel/server.py` - `debug_runtime` 도구 + 핸들러 추가

**다음 단계**: Claude Code 재시작 후 `debug_runtime` 호출하여 확인

---

### Phase 3: Sideeffect 검사 + 안전장치 (v3.1) ✅

**check_sync 도구 구현**
- `architecture.py`에 `check_sync()` 함수 추가
- license.py ↔ license_free.py 함수 시그니처 동기화 검증
- messages/en.py ↔ ko.py 메시지 키 동기화 검증
- server.py에 도구 등록 완료

**ship 상업용 안전장치**
- `_run_safety_checks()`: ship 전 안전 검사
- 시크릿 파일 탐지 (`.env`, `*.key`, `*.pem` 등)
- 시크릿 내용 패턴 탐지 (API key, password 등)
- .env.example 존재 확인
- git 추적 시크릿 → BLOCK

**Manager context 분석 강화**
- PRD/Spec 관련 패턴 추가
- Ship/Deploy 관련 패턴 추가
- 코드 품질 패턴 추가 (refactor, duplicate)

**변경 파일**:
- `src/clouvel/tools/architecture.py` - check_sync 추가
- `src/clouvel/tools/__init__.py` - export 추가
- `src/clouvel/server.py` - 도구 등록
- `src/clouvel/tools/ship_pro.py` - 안전장치 추가
- `src/clouvel/tools/manager/utils.py` - context 분석 강화

### Phase 2: PRD Diff + 영향 분석 (v3.1) ✅

**PRD 버전 관리**
- `_backup_prd()`: 이전 PRD를 `.claude/prd_history/PRD_{timestamp}.md`에 백업
- 변경 이력 추적 가능

**PRD Diff 계산**
- `_calculate_prd_diff()`: difflib로 변경 내용 분석
- 추가/삭제 라인 수, 변경된 섹션, 키워드 추출

**영향 분석**
- `_analyze_prd_impact()`: 변경된 키워드로 영향받는 파일 검색
- 테스트 파일 영향 경고
- Critical 섹션 (API, Schema, Security) 변경 경고

**save_prd 통합**
- 결과에 diff 요약 포함: `+N -M lines`
- 영향받는 파일 수 표시: `N files may need updates`

**변경 파일**: `src/clouvel/tools/start.py`

### Phase 1: 유료화 강화 (v3.1) ✅

**Ship COMPLETION_REPORT 자동 생성**
- `_generate_completion_report()` 함수 추가
- ship PASS 시 프로젝트 루트에 `COMPLETION_REPORT.md` 생성
- AC 기준 PASS 근거 테이블 포함

**Pro 유도 메시지 삽입 (3개 포인트)**
- `can_code` WARN 시: "ship auto-generates evidence & completion report"
- `save_prd` 후: "Track PRD changes & impact analysis with ship"
- `plan` 후: "ship auto-generates PASS evidence & completion report"

**변경 파일**:
- `src/clouvel/tools/ship_pro.py` - COMPLETION_REPORT 생성
- `src/clouvel/messages/en.py` - Pro 유도 메시지
- `src/clouvel/tools/start.py` - save_prd Pro 유도
- `src/clouvel/tools/planning.py` - plan Pro 유도

### 환경 정리 (PM+CTO 리뷰) ✅

**Phase 1: .env.example 생성**
- 12개 환경 변수 문서화
- 용도별 그룹핑 (Dev/API/License/Pro/Team)

**Phase 2: DEV 모드 변수 통합**
- `CLOUVEL_DEV_MODE` → `CLOUVEL_DEV` 통합
- `content_api.py`, `shovel.py` 수정
- 단일 변수로 일관성 확보

**Phase 3: pyproject.toml 수정**
- classifier에 Python 3.10, 3.13 추가
- 실제 지원 버전 명시 (3.10~3.13)

**Phase 4: CLAUDE.md 환경 섹션 추가**
- 개발 모드 설정 방법
- 환경 변수 목록 테이블
- 필수 파일 목록

### 랜딩페이지 카피 수정 (Solo Dev 타겟) ✅

**C-Level 동적 회의 결과 반영**:

| 섹션 | EN Before | EN After | KO After |
|------|-----------|----------|----------|
| Hero title | "AI that asks tough questions." | "No spec, no code." | "스펙 없이? 코딩 금지." |
| Hero subtitle | "8 AI managers help you think..." | "Skip the spec, enter debugging hell." | "스펙 건너뛰면 디버깅 지옥행." |
| Hero desc | "Not another AI that gives easy answers." | "You're building alone. Make every hour count." | "혼자 개발하니까. 매 시간이 소중하니까." |
| Problem 3 title | "Results vary every time, debugging explodes" | "You forget what you decided last week" | "지난주에 뭘 결정했는지 까먹음" |
| Problem 3 desc | "Same prompt, different results..." | "No record of decisions. Repeat the same debates." | "결정 기록 없음. 같은 논쟁 반복." |

**회의 결정 사항**:
- 타겟: Solo dev only (Team lead 문구 제거)
- "Vibe coding" 표현 제거 → 더 직접적인 메시지
- Problem 3 오버프라미스 제거: "same prompt, different results" → "결정 기록 없음" (Knowledge Base 기능과 연결)

**파일 변경**:
- `docs/landing/i18n/en.json` - Hero + Problem 섹션
- `docs/landing/i18n/ko.json` - Hero + Problem 섹션
- `docs/landing/index.html` - Hero + Problem 섹션 (하드코딩 텍스트)
- `docs/landing/index-ko.html` - Hero + Problem 섹션 (기본 텍스트/fallback)

### Knowledge Base 개발자 모드 수정 ✅

**문제**: 개발자 환경에서 Knowledge Base 도구 사용 불가 (Pro 라이센스 필요 메시지)

**원인**: `tools/knowledge.py`에 `is_developer()` 체크 누락

**수정**:
- `_is_dev_mode()` 함수 추가
- `_IS_DEVELOPER`, `_CAN_USE_KB` 플래그 추가
- 모든 함수에서 `_HAS_KNOWLEDGE_DB` → `_CAN_USE_KB` 변경
- 개발자 모드면 Knowledge Base 전체 접근 가능

**테스트**:
```python
_IS_DEVELOPER: True
_HAS_KNOWLEDGE_DB: True
_CAN_USE_KB: True
record_decision: {'status': 'recorded', 'decision_id': '42'} ✅
```

**파일 변경**:
- `src/clouvel/tools/knowledge.py`

**주의**: MCP 서버 재시작 필요 (코드 변경 반영)

---

## 이전 완료 (2026-01-26)

### v1.9.0 - MCP 표준화 전체 구현 ✅

**Phase 1: Deprecation Warnings** ✅
- `tools/core.py` - `scan_docs`, `analyze_docs`, `init_docs` deprecation warning
- `tools/verify.py` - `verify`, `gate`, `handoff` deprecation warning
- `tools/docs.py` - `get_prd_template`, `get_prd_guide` deprecation warning
- `tools/rules.py` - `init_rules` deprecation warning
- `tools/hooks.py` - `hook_design`, `hook_verify` deprecation warning

**Phase 2: Option Extensions** ✅
- `tools/start.py` - `--template`, `--layout`, `--guide`, `--init` 옵션 추가
- `tools/setup.py` - `--rules`, `--hook`, `--hook_trigger` 옵션 추가
- `server.py` - Tool 정의 + 핸들러 업데이트

**Developer Mode Fix** ✅
- `api_client.py:66-72` - `call_manager_api()`에 `is_developer()` 체크 추가
- 개발자 모드에서 Worker API 우회 → 로컬 manager 모듈 사용
- `_dev_mode_response()` - 로컬 manager 호출 + `dev_mode: True` 반환
- 테스트: `is_developer(): True`, `dev_mode: True`, `error: None` ✅

**Phase 3: Deprecation Plan (v2.0 제거 예정)**
| 도구 | 대체 | Migration Path |
|------|------|----------------|
| `scan_docs` | `can_code` | `can_code(path)` |
| `analyze_docs` | `can_code` | `can_code(path)` |
| `verify` | `ship` | `ship(path, steps=["lint", "test"])` |
| `gate` | `ship` | `ship(path, steps=steps, auto_fix=fix)` |
| `handoff` | `record_decision` + `update_progress` | 조합 사용 |
| `get_prd_template` | `start` | `start(path, template="web-app")` |
| `get_prd_guide` | `start` | `start(path, guide=True)` |
| `init_docs` | `start` | `start(path, init=True)` |
| `init_rules` | `setup_cli` | `setup_cli(path, rules="web")` |
| `hook_design` | `setup_cli` | `setup_cli(path, hook="design")` |
| `hook_verify` | `setup_cli` | `setup_cli(path, hook="verify")` |

### MCP 도구 표준화 완료 ✅

**생성 파일**:
- `docs/mcp/MCP_CATALOG.md` - 52개 도구 전체 카탈로그
- `docs/mcp/MCP_GROUPS.md` - 9개 유사 그룹 분류
- `docs/mcp/MCP_STANDARDIZATION_PLAN.md` - 표준화 계획

**분석 결과**:
| Action | Count | 대상 |
|--------|-------|------|
| **Standard** | 12 | `can_code`, `start`, `ship`, `manager`, `setup_cli` 등 |
| **Keep** | 18 | 용도가 명확히 다른 도구 |
| **Merge** | 6 | `get_prd_template` → `start --template` 등 |
| **Deprecate** | 5 | `scan_docs`, `analyze_docs`, `verify`, `gate`, `handoff` |

**유사 판정 기준** (5개 중 3개 이상 일치):
1. Purpose - 해결하는 문제
2. Interface - IO 스키마
3. Side Effects - Network/FS/ENV/Process
4. Runtime Context - Local/Worker, Sync/Async
5. Dependencies - API 키/스토리지

### v1.8.0 배포 - Manager Worker API 전환 ✅

**변경 내용**:
- `server.py:1193-1225`: `_wrap_manager()` → `call_manager_api()` 호출
- `server.py:1275-1305`: `_wrap_quick_perspectives()` → Worker API 사용
- 제거된 import: `manager`, `quick_perspectives`, `generate_meeting_sync`
- 추가된 import: `from .api_client import call_manager_api`

**근거**: ADR-0001 (Manager 실행 아키텍처 결정)

### 문서 시스템 구축 ✅

**디렉토리 구조**:
```
docs/architecture/
├── CALL_FLOWS/
│   ├── flow_index.md
│   ├── flow_manager.md
│   ├── flow_activate.md
│   └── flow_webhook.md
├── DECISION_LOG/
│   └── ADR-0001-manager-execution.md
├── DATA_CONTRACTS.md
├── MODULE_MAP.md
└── RUNTIME_PATHS.md
```

**자동화 스크립트**:
- `scripts/docs_extract.py` - 코드에서 AUTO-GEN 섹션 자동 생성
- `scripts/docs_check.py` - 문서 유효성 검증

### 이전: 아키텍처 분석 및 기록 📋

**문제**: manager 도구 충돌로 다른 작업 불가

**근본 원인 분석**:
1. Import 규칙 미정의 → 두 곳에서 같은 함수 정의
2. 아키텍처 결정 미기록 → 왜 이렇게 되었는지 알 수 없음
3. 규칙이 부정형 → 역효과 발생

**Knowledge Base 기록 완료** (11개 결정, 10개 위치):

| ID | 카테고리 | 내용 | 상태 |
|----|----------|------|------|
| #30 | architecture | server.py Import 규칙 | 🔒 LOCKED |
| #31 | architecture | Pro 기능 패턴 (ship 표준) | 🔒 LOCKED |
| #32 | architecture | Manager 충돌 | ✅ RESOLVED (v1.8.0) |
| #33 | architecture | 라이센스 모듈 구조 | 🔒 LOCKED |
| #34 | architecture | Trial 관리 (API 우선) | 🔒 LOCKED |
| #35 | architecture | Optional 의존성 | 🔒 LOCKED |
| #36 | architecture | 개발자 감지 | 🔒 LOCKED |
| #37 | architecture | 파일 구조 규칙 | 🔒 LOCKED |
| #38 | design | 긍정적 프레이밍 원칙 | 🔒 LOCKED |
| #39 | process | 기록 트리거 | 🔒 LOCKED |
| #40 | process | 코드 추가 전 확인 | 🔒 LOCKED |

---

## 다음 할 일

### P0: MCP 서버 재시작 후 확인 (v3.2) ✅
- [x] `debug_runtime(project_path="D:\\clouvel")` 호출
- [x] `clouvel.__file__` = `D:\clouvel\src\clouvel\...` 확인
- [x] `is_developer` = `True` 확인
- [x] `search_knowledge(query="architecture", project_path="D:\\clouvel")` 테스트
- [x] Knowledge Base 도구 정상 작동 확인

### P0: 테스트 커버리지 확보 ✅
- [x] test_knowledge.py 작성 (35 테스트)
- [x] test_ship.py 작성 (23 테스트)
- [x] 전체 테스트 통과: **234 passed, 7 skipped**

### P0: PRD v1.9 동기화 ✅
- [x] docs/PRD.md에 v1.9 도구 통합 섹션 추가
- [x] v3.1 런타임 안전장치 섹션 추가
- [x] v3.2 MCP 런타임 디버그 섹션 추가
- [x] 테스트 커버리지 강화 섹션 추가

### P0: Product Hunt 런칭 당일 (2026-01-28 15:00 VN)
- [ ] 소셜 포스트 발행 (Twitter 15:00, Threads 15:30, Twitter 20:00)
- [ ] 댓글 1시간마다 확인 & 답변
- [ ] r/ClaudeAI 포스트
- [ ] r/SideProject 포스트 (업데이트)
- [ ] r/IndieHackers 포스트

### P1: 완료 (2026-01-27)
- [x] CI 문서 검증 ✅ (.github/workflows/ci.yml에 docs_check.py 추가)
- [x] review 도구 API 설계 ✅ (docs/PRD.md v1.10 섹션)
- [x] Compounding Rules ✅ (CLAUDE.md에 4개 규칙)
- [x] Product Hunt 준비 ✅ (2026-01-28 런칭 예약 완료)

### P1: 완료 ✅

- [x] `python scripts/docs_check.py` 실행 (all PASS)
- [x] SSOT 문서 시스템 구축 완료
- [x] ADR-0001 RESOLVED 상태로 업데이트
- [x] MCP 도구 표준화 (52개 → 9그룹 → 표준화 계획)

### P1: Gate 통합 (다음 단계)

- [ ] `docs_check.py`를 ship 도구에 연동
- [ ] pre-commit hook에 문서 검증 추가
- [ ] CI에 docs_check.py 실행 추가
- [x] MCP Deprecation Warnings (v1.9): 11개 도구 ✅
- [x] MCP Option Extensions (v1.9): `start --template/--guide/--init`, `setup_cli --rules/--hook` ✅

### P2: Smoke Test 자동화 (선택)

- [ ] `scripts/smoke_test.py` 생성
- [ ] SMOKE_LOGS.md AUTO-GEN 섹션 자동 채우기

---

## 이전 완료 (2026-01-25)

### v1.6.6 배포 ✅ (Locked Decisions 완성)

**신규 기능**: Decision Lock 시스템 완성

| 도구 | 설명 |
|------|------|
| `record_decision(locked=True)` | 결정 잠금 (컨텍스트 드리프트 방지) |
| `unlock_decision(id, reason)` | 잠긴 결정 해제 (사유 필수) |
| `list_locked_decisions()` | 잠긴 결정 목록 조회 |
| can_code 🔒 표시 | 잠긴 결정은 `🔒 LOCKED` 배지로 표시 |

**테스트 통과** (2026-01-25 22:00):
- record → list → unlock → verify 전체 플로우 ✅
- 커밋: c81c3e4, PyPI 배포 완료, GitHub push 완료

### v1.6.4-5 배포 ✅ (File Tracking 강화)

**P0-P3 구현 완료**:

| 우선순위 | 내용 | 상태 |
|----------|------|------|
| P0 | pre-commit hook에 file tracking 체크 | ✅ |
| P1 | 경고에 복붙 가능 명령어 포함 | ✅ |
| P2 | CLAUDE.md에 record_file 규칙 | ✅ |
| P3 | can_code(mode="post") 후검증 | ✅ |

### v1.6.3 배포 ✅

**해결된 문제**: `license_status`가 "Unknown" 표시 → tier_info 정상 반환

| 항목 | 내용 |
|------|------|
| **커밋 1** | 697f16d - license_common + record_file |
| **커밋 2** | 4b54b3a - version bump |
| **PyPI** | v1.6.3 배포 완료 |
| **테스트** | uvx 환경 테스트 통과 |

### 변경 파일

| 파일 | 설명 |
|------|------|
| `license_common.py` | 공통 라이선스 로직 (신규) |
| `license_free.py` | common 모듈 사용하도록 수정 |
| `server.py` | record_file, list_files 추가 |
| `tools/tracking.py` | 파일 추적 도구 (신규) |
| `messages/en.py` | i18n 메시지 (신규) |
| `test_record_file.py` | 테스트 100개 (신규) |

### 제외된 파일 (보안)

- `.claude/planning/*` (마케팅/내부 전략)
- `docs/marketing/`
- `docs/PRD.md`, `CLAUDE.md`

---

## v1.5 계획 (2026-01-25 추가)

> **모토 이행**: "기록을 잃지 않는다"
> 상세: `docs/PRD.md` v1.5 섹션 참조

### 발견된 문제 (7개)

| # | 문제 | 카테고리 |
|---|------|----------|
| 1 | 파일 생성 자동 추적 없음 | 기록 |
| 2 | current.md 자동 업데이트 없음 | 기록 |
| 3 | DoD 체크 강제 없음 | can_code |
| 4 | 테스트 존재 확인 없음 | can_code |
| 5 | Manager context 분석이 얕음 | manager |
| 6 | Clouvel/MCP 토픽 없음 | manager |
| 7 | 동적 피드백이 generic | manager |

### 구현 순서

| Phase | 항목 | 상태 |
|-------|------|------|
| 1 | can_code 강화 (테스트/DoD 체크) | ✅ 완료 (2026-01-25) |
| 2 | pre-commit hook 강화 | ✅ 완료 (2026-01-25) |
| 3 | Manager 토픽 확장 | ✅ 완료 (2026-01-25) |
| 4 | Manager context 분석 개선 | ✅ 완료 (2026-01-25) |
| 5 | record_file 도구 | ✅ 완료 (2026-01-25) |

### Phase 1 완료 내용

**A2: DoD 패턴 추가** (`core.py:61-67`)
- `## DoD`, `## Definition of Done`, `## 완료 정의` 패턴 추가
- `## Criteria`, `## 기준` 패턴 추가

**A1: 테스트 메시지 개선** (`messages/en.py:70-71`)
- 테스트 없을 때 경고: `No Tests (⚠️ write tests before marking complete)`

### Phase 2 완료 내용

**A3: pre-commit hook 강화** (`server.py`, `setup.py`)
- `clouvel setup --hooks` 명령 추가
- PRD 체크 + 기록 파일 체크 + 보안 체크
- `files/created.md` 없으면 커밋 차단
- `status/current.md` 없으면 커밋 차단

### Phase 3 완료 내용

**B1: 토픽 확장** (`utils.py`, `data/__init__.py`)
- topic_keywords에 4개 토픽 추가: `mcp`, `internal`, `tracking`, `maintenance`
- CONTEXT_GROUPS에 매니저 매핑 추가
- 테스트: "Clouvel 기능 개선" → `['mcp', 'internal']` ✓

### Phase 4 완료 내용 (LLM 주의력 최적화 적용)

**B2: Context 분석 강화** (`utils.py`)
- 키워드 매칭 + 패턴 감지 결합
- 문제 패턴: "없다", "안 됨", "느려", "취약" → error/performance/security
- 요청 패턴: "추가", "구현", "수정", "테스트" → feature/maintenance

**B3: 동적 피드백 개선** (`formatter.py`)
- XML 구조화: `<critical_summary>`, `<situation_analysis>`, `<meeting_notes>`
- Bookending: critical issues를 처음과 끝에 반복 (U-shaped attention)
- 압축된 instruction: 장황한 템플릿 → 핵심 규칙만

### Phase 5 완료 내용

**A4: record_file 도구** (`tracking.py`)
- `record_file(path, file_path, purpose, deletable, session)` - 파일 생성 기록
- `list_files(path)` - 기록된 파일 목록 조회
- `.claude/files/created.md`에 자동 추가
- 중복 체크 포함

---

## 오늘 완료 (2026-01-24)

### 동적 회의 4회 진행 📋

> 상세 기록: `.claude/planning/meetings/2026-01-24-decisions.md`

#### 회의 1: 팀 라이선스 아키텍처
- [x] Worker KV 유지 (Supabase 추가 안 함)
- [x] MVP: Phase 1만 (rate limiting, team license validation)
- [x] 연기: PostgreSQL, 대시보드, Linear/Jira

#### 회의 2: 가격 책정
- [x] Personal Pro: $9.99/mo
- [x] Team 10: $129/mo ($12.9/user)
- [x] 프리미엄 근거: 주니어 성장 메트릭 (lock-in)
- [x] LAUNCH70: 70% off → $38.7/10석

#### 회의 3-4: Knowledge Base 설계
- [x] 저장소: SQLite (`~/.clouvel/knowledge.db`)
- [x] 50MB 제한, 40MB 아카이브 트리거
- [x] 5개 테이블 + FTS5 스키마 설계
- [x] 4개 신규 도구 API 설계
- [x] 8주 로드맵 수립

### 마케팅 런칭 🚀

- [x] **Twitter 쓰레드** 7개 올림 (@ShovelMaker91)
- [x] **Threads 포스트** 3개 올림 (@sinabrocoding)
- [x] **Reddit 워밍업** 시작 - r/ClaudeAI, r/SideProject 답글 각 1개
- [x] **LAUNCH70 쿠폰** 생성 (70% off, 50개 한정, Polar.sh)
- [x] **Demo GIF** GitHub Pages 배포 완료

### 마케팅 자동화 설정

- [x] Typefully 가입
- [x] Make.com 가입
- [x] Week 1 콘텐츠 예약 (월/화/수)
- [x] 2주치 콘텐츠 초안 작성 (`.claude/planning/content-drafts.md`)
- [x] 마케팅 일정표 작성 (`.claude/planning/marketing-schedule.md`)
- [x] Reddit 포스트 초안 v3 (`.claude/planning/reddit-posts.md`)

### 테스트 라이선스 발급

- [x] Worker API로 테스트 라이선스 발급 확인
- [x] 내 테스트 키: `TEST-0BM6-E8N6-L0V9` (Personal, 30일)
- [x] 배포용 Personal 키 5개 (14일 만료)
- [x] 배포용 Team 키 2개 (1/30 만료)
  - `TEST-E737-2CG1-I188`
  - `TEST-04Q2-5DY5-MSTH`

### 이전 완료 (v1.3.11~13)

- [x] manager 동적 회의록 생성 (Claude API 연동)
- [x] Windows cp949 인코딩 수정
- [x] manager import 조건부 처리 (Free 버전 호환)
- [x] PyPI 배포 성공 (v1.3.13)

---

## 이전 완료 (2026-01-22)

### v1.3.4 신규 기능

#### 템플릿 확장 (8개 카테고리, 16개 파일)

- [x] web-app (lite, standard, detailed) - 기존
- [x] api (lite, standard) - 신규
- [x] cli (lite, standard) - 신규
- [x] chrome-ext (lite, standard) - 신규
- [x] discord-bot (lite, standard) - 신규
- [x] landing-page (lite, standard) - 신규
- [x] saas (lite, standard) - 신규
- [x] generic (standard) - 기존

#### start 도구 개선 (Free)

- [x] 프로젝트 타입 자동 감지
  - 파일 패턴 분석 (manifest.json → chrome-ext)
  - 의존성 분석 (discord.js → discord-bot, stripe → saas)
- [x] 대화형 PRD 작성 가이드
  - 타입별 5-6개 질문 세트
  - Claude가 질문 → 사용자 답변 수집
- [x] save_prd 도구 추가 (PRD 저장)

#### 버전 체크 기능

- [x] PyPI API로 최신 버전 조회
- [x] 24시간 캐싱 (~/.clouvel/version_cache.json)
- [x] 첫 도구 호출 시 체크 (어떤 도구든)
- [x] 업데이트 있으면 배너 1회 표시

### 파일 변경

- [x] `src/clouvel/tools/start.py` - 타입 감지 + PRD 가이드
- [x] `src/clouvel/tools/docs.py` - TEMPLATES 확장
- [x] `src/clouvel/version_check.py` - 신규
- [x] `src/clouvel/server.py` - save_prd 등록, 버전 체크 연동
- [x] `src/clouvel/templates/*` - 14개 신규 템플릿 파일

---

## 완료된 기능

### Free (clouvel)

- [x] can_code - 문서 강제
- [x] start - 프로젝트 온보딩 + 타입 감지 + PRD 가이드
- [x] save_prd - PRD 저장
- [x] get_progress - 진행 상황
- [x] get_goal - 목표 리마인드
- [x] 템플릿 8종 (web-app, api, cli, chrome-ext, discord-bot, landing-page, saas, generic)
- [x] 버전 체크 (PyPI 최신 버전 알림)

### Pro - $49 (Early Bird)

- [x] manager - 8명 C-Level 매니저 협업 피드백
- [x] ship - 원클릭 테스트→검증→증거 생성
- [x] activate_license - Lemon Squeezy 연동
- [x] recover_context - 컨텍스트 복구
- [x] 기타 Pro 도구들

### Team - $149 (Early Bird)

- [x] 팀 협업 도구 (invite, members, settings 등)
- [x] 팀 규칙 동기화
- [x] 프로젝트 컨텍스트 공유

---

## 이전 완료 (2026-01-21)

### v1.2.0 ~ v1.3.3

- [x] /start 도구 기본 구현
- [x] /manager 도구 (8명 매니저)
- [x] /ship 도구 (lint → test → build)
- [x] clouvel install 명령
- [x] 보안 hook (민감 파일 차단)

---

## 로드맵

> **📄 5개년 로드맵**: `docs/roadmap/` 폴더 참조

### Q1 2026 목표

| 항목   | 목표 | 현재   |
| ------ | ---- | ------ |
| 템플릿 | 10개 | 8개 ✅ |
| 가입자 | 200  | -      |
| MAU    | 50   | -      |

### 다음 단계

**v1.4 - 템플릿 완성 + MCP 확장**

- [ ] 템플릿 2개 추가 (블로그/CMS, E-commerce)
- [ ] Windsurf/Continue.dev 가이드
- [ ] Cursor 디렉토리 제출

**v1.5 - 다른 LLM 지원 (조건부)**

- [ ] LangChain Tool 패키지
- 전환 조건: 유료 15건+ 또는 요청 5건+

---

## 가격 전략

| 단계         | Personal | Team     | 시점           |
| ------------ | -------- | -------- | -------------- |
| Early Bird   | **$49**  | **$149** | ~ Feb 15, 2026 |
| After Launch | $79      | $249     | Feb 16~        |

---

## ✅ 완료: i18n 랜딩페이지

> **완료 시점**: 2026-01-24

### 완료 항목

- [x] `docs/landing/i18n/en.json` - 영문 번역 전체
- [x] `docs/landing/i18n/ko.json` - 한글 번역 전체
- [x] `docs/landing/i18n.js` - 언어 전환 스크립트
- [x] `index.html` - `<html lang="en">` 변경
- [x] `index.html` - i18n.js 스크립트 추가
- [x] `index.html` - 언어 토글 버튼 추가 (nav)
- [x] `index.html` - nav 링크 data-i18n 속성 추가
- [x] Hero 섹션 data-i18n 추가
- [x] Works with 섹션 data-i18n 추가
- [x] PRD 설명 섹션 data-i18n 추가
- [x] Problem 섹션 data-i18n 추가
- [x] How it works 섹션 data-i18n 추가
- [x] Demo 섹션 data-i18n 추가
- [x] Features 섹션 data-i18n 추가
- [x] Getting Started 섹션 data-i18n 추가
- [x] Pricing 섹션 data-i18n 추가
- [x] FAQ 섹션 data-i18n 추가
- [x] Contact 섹션 data-i18n 추가
- [x] Footer data-i18n 추가
- [x] 모바일 메뉴 data-i18n 추가

### 테스트 방법

```
# 영문
file:///D:/Clouvel/docs/landing/index.html?lang=en

# 한글
file:///D:/Clouvel/docs/landing/index.html?lang=ko
```

### 컨텍스트

- **목표**: 국제 indie hackers 타겟 영문 랜딩
- **결정**: 별도 영문 페이지 대신 i18n 단일 페이지
- **Threads/X**: Build in Public, 팀 리드 타겟
- **로드맵**: 18개월 후 $120K ARR, 10K 사용자

---

## 다음 할 일

### ✅ Manager v2: Augmentation 모델 (2026-01-24)

**핵심 변경**: 답변형 → 질문형 전환

| Before | After |
|--------|-------|
| "OAuth 쓰세요" | "유저가 소셜 로그인 선호하나요?" |
| 매니저가 결정 | 개발자가 결정 (매니저는 관점 제시) |
| Action Items | Decisions for YOU |

**구현 내용:**
- 8명 매니저 각각 4개 카테고리 probing questions 추가
- 시스템 프롬프트에 "AUGMENTATION, NOT AUTOMATION" 철학 명시
- 출력 형식: "Decisions for YOU", "Key Questions to Answer" 섹션

**파일 변경:**
- `src/clouvel/tools/manager/prompts/personas.py` - probing_questions 추가
- `src/clouvel/tools/manager/prompts/templates.py` - 질문 중심 템플릿

### ✅ Knowledge Base 연동 강화 (2026-01-24)

**Manager가 과거 결정을 참조:**
- `_get_kb_context()` - 관련 과거 결정 조회
- 토픽 기반 검색 + 최근 결정 포함
- 매니저 프롬프트에 자동 주입

**파일 변경:**
- `src/clouvel/tools/manager/core.py` - `_get_kb_context()` 추가
- `src/clouvel/tools/manager/generator/conversation.py` - KB 컨텍스트 전달

### ✅ Quick Perspectives 도구 추가 (2026-01-24)

**코딩 전 빠른 관점 체크:**
- `quick_perspectives(context)` - 3-4명 매니저가 핵심 질문 제시
- 토픽 기반 자동 매니저 선택 (auth → CSO 포함, UI → CDO 포함)
- 매니저당 2개 probing questions
- KB에서 관련 과거 결정 참조

**출력 예시:**
```
## 💡 Quick Perspectives

_Before building: **Adding user authentication with JWT tokens**_

**👔 PM**:
  - Is this MVP scope or post-launch?
  - What's the ONE thing this feature must do?

**🔒 CSO**:
  - How do you verify the user is who they claim?
  - How do you verify they're allowed to do this action?

💡 _Related past decision: auth Use JWT with refresh token..._
```

**파일 변경:**
- `src/clouvel/tools/manager/core.py` - `quick_perspectives()` 함수 추가
- `src/clouvel/tools/manager/__init__.py` - export 추가
- `src/clouvel/server.py` - Tool 정의 및 핸들러 추가

---

### ✅ Knowledge Base 구현 완료 (8주 → 1일)

| 주차 | 목표 | 상태 |
|------|------|------|
| 1-2 | SQLite 기반 구축 | ✅ 완료 |
| 3-4 | 도구 통합 (record_decision, record_location) | ✅ 완료 |
| 5-6 | 자동화 (회의 후 자동 기록) | ✅ 완료 |
| 7-8 | FTS5 검색 + CLI | ✅ FTS5 완료, CLI 미정 |

**v1.4 Knowledge Base MVP 완료** (2026-01-24)
- `~/.clouvel/knowledge.db` SQLite 저장소
- 5개 테이블: projects, meetings, decisions, locations, events
- FTS5 전문 검색 지원 (category 포함)
- 6개 신규 도구: record_decision, record_location, search_knowledge, get_context, init_knowledge, rebuild_index
- **세션 시작 자동 컨텍스트 로딩**: can_code 호출 시 최근 결정/위치 표시
- **50MB 제한 + 자동 아카이브**: 40MB 초과 시 30일 이상 데이터 아카이브
- **API 키 fallback**: ANTHROPIC_API_KEY 없어도 manager 동작 (static mode)
- **회의 자동 기록**: manager 호출 시 결정사항 자동 추출 및 KB 저장
- **SQLite 암호화**: `CLOUVEL_KB_KEY` 환경변수로 선택적 Fernet 암호화

### 랜딩페이지 수정
- [x] "context preserved" → "Progress Tracking" + "Smart recovery coming soon" 변경 완료

---

- [x] **i18n 완료** ✅
- [x] **글로벌 런칭 Phase 1 완료** ✅
  - [x] hreflang 태그 추가 (SEO)
  - [x] Flash 방지 인라인 스크립트
  - [x] SUPPORTED_LANGS 유효성 검증
  - [x] localStorage 에러 핸들링
- [x] **GA4 언어별 전환율 추적 완료** ✅
  - [x] GA4 ID: G-17L1X6CZ4W
  - [x] trackCTA 함수 (CTA 클릭 추적)
  - [x] language_switch 이벤트 (언어 변경 추적)
- [x] **Solo-first 랜딩페이지 전환** ✅
  - [x] Hero 섹션: Solo devs & indie hackers 타겟팅
  - [x] Team 5/Team 10 플랜 숨김 → "Coming Soon"
  - [x] Personal Pro에 "추천" 배지 이동
  - [x] Enterprise 섹션 → "Need team features? Let us know"
  - [x] i18n 파일 업데이트 (en.json, ko.json)
  - [x] 영어 페이지(index-en.html) 동기화
- [x] **Week 1-2: GitHub 프로젝트 정비** ✅
  - [x] README.md 영문 재작성
  - [x] Demo GIF 생성 (docs/assets/demo.gif)
  - [x] CONTRIBUTING.md 확인 (영문 완료)
  - [x] CODE_OF_CONDUCT.md 확인 (영문 완료)
  - [x] Issue 템플릿 3개 확인 (bug, feature, question)
  - [x] PR 템플릿 확인
  - [x] GitHub Discussions 활성화
  - [x] 에러 메시지 영어 전환 (errors.py, planning.py)
  - [x] Reddit 포스트 초안 작성 (.claude/planning/reddit-posts.md)
- [ ] **Week 3: 커뮤니티 활동 시작**
  - [ ] r/ClaudeAI 포스팅
  - [ ] r/SideProject 포스팅
  - [ ] X/Threads 소개 쓰레드
- [ ] i18n 테스트 (`?lang=en` / `?lang=ko` / `?lang=jp` → fallback)
- [ ] Product Hunt 재런칭 준비 (Phase 3)
- [ ] Windows CI 추가 (GitHub Actions)
- [ ] 템플릿 2개 추가 (블로그/CMS, E-commerce)
- [ ] Cursor 디렉토리 제출
