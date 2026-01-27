# Clouvel 액션 플랜

> **생성일**: 2026-01-27
> **분석 기준**: 8역할 C-Level 동적회의
> **담당**: PM + CTO 통합 관점

---

## P0: 이번 주 (Critical)

### 1. 테스트 커버리지 확보 (QA)

**왜 중요한가**: 현재 4개 테스트 파일만 존재. 회귀 버그 위험 높음.

```bash
# 생성할 테스트 파일
tests/test_knowledge.py  # 20+ 테스트
tests/test_ship.py       # 15+ 테스트
tests/test_start.py      # 10+ 테스트
```

**완료 기준**:
- [x] test_knowledge.py: record_decision, search_knowledge, get_context 테스트 ✅
- [x] test_ship.py: ship, quick_ship, full_ship 테스트 ✅
- [x] pytest 전체 통과 ✅ (234 passed, 7 skipped)

### 2. PRD 동기화 (PM)

**왜 중요한가**: v1.9 변경사항이 PRD에 미반영. 문서 신뢰도 저하.

```markdown
# docs/PRD.md에 추가할 내용

## v1.9 Tool Consolidation (2026-01-27)
- [ ] `debug_runtime` 도구 추가
- [ ] Deprecation warnings 11개 도구
- [ ] `start --template/--guide/--init` 통합
- [ ] `setup_cli --rules/--hook` 통합
```

**완료 기준**:
- [x] PRD v1.9 섹션 추가 ✅
- [x] 구현된 5개 기능 PRD 반영 ✅
- [x] 체크리스트 전부 [x] 가능한 상태 ✅

### 3. Reddit 포스트 (CMO)

**왜 중요한가**: 커뮤니티 노출 시급. Product Hunt 전 웜업 필요.

```markdown
# r/ClaudeAI 포스트

제목: "I built an MCP server that blocks AI coding until you write a spec"

내용: .claude/planning/reddit-posts.md 참조
```

**완료 기준**:
- [ ] r/ClaudeAI 포스트 업로드
- [ ] 댓글 모니터링 (24시간)

---

## P1: 2주 내 (High Priority)

### 4. CI 문서 검증 (CTO)

**왜 중요한가**: 문서 동기화가 수동. 자동화 필요.

```yaml
# .github/workflows/ci.yml 추가

- name: Validate Documentation
  run: python scripts/docs_check.py
```

**완료 기준**:
- [x] docs_check.py CI 연동 ✅
- [x] PR에서 문서 검증 실패 시 블록 ✅

### 5. `review` 도구 설계 (PM)

**왜 중요한가**: 검증 워크플로우 불완전. handoff → verify → review → gate 중 review 누락.

```python
# 설계 초안

async def review(
    path: str,
    scope: str = "feature",  # file | feature | full
    managers: list[str] = None  # 특정 매니저만
) -> list[TextContent]:
    """매니저들의 코드 리뷰

    1. 변경된 파일 목록 수집 (git diff)
    2. 각 매니저 관점에서 리뷰
    3. 문제 발견 시 수정 제안
    """
```

**완료 기준**:
- [x] review 도구 API 설계 완료 ✅
- [x] PRD v1.10 섹션 추가 ✅

### 6. Product Hunt 준비 (CMO)

**왜 중요한가**: 초기 사용자 획득의 핵심 채널.

```markdown
# 준비 체크리스트

- [x] 제품 페이지 초안 작성 ✅ (docs/marketing/product-hunt-checklist.md)
- [x] 데모 GIF ✅ (docs/landing/assets/demo.gif)
- [ ] 스크린샷 3장 준비 (can_code, manager, ship)
- [x] 메이커 코멘트 준비 ✅
- [ ] 로고 240x240 PNG
- [ ] 런칭 날짜 확정 (2월 중)
```

**완료 기준**:
- [ ] Product Hunt 제출 가능 상태 (로고 + 스크린샷 필요)
- [ ] 런칭 날짜 확정

### 7. Compounding Rules (Error Manager)

**왜 중요한가**: 과거 실수 반복 방지.

```markdown
# CLAUDE.md 추가할 규칙

## 과거 실수에서 배운 규칙

### Stub 파일 동기화 (2026-01-25)
- **트리거**: license.py, license_free.py, messages/*.py 수정 시
- **체크**: 반환값 구조, 함수 시그니처 일치 확인
- **도구**: `check_sync(path)` 실행

### PyPI 배포 전 테스트 (2026-01-25)
- **트리거**: version bump 후 배포 전
- **체크**: `uvx clouvel@latest license_status` 실행
- **기대**: tier_info 정상 반환

### Import 규칙 (2026-01-26)
- **트리거**: server.py에서 tools import 추가 시
- **체크**: tools/__init__.py에서만 import
- **금지**: tools/manager/core.py 직접 import
```

**완료 기준**:
- [x] CLAUDE.md에 4개 규칙 추가 ✅ (Compounding Rules 섹션)
- [x] Knowledge Base에 기록 ✅ (#38, #39, #40)

---

## P2: 1개월 내 (Medium Priority)

### 8. pytest 커버리지 (CTO)

```bash
# pytest-cov 설정
pip install pytest-cov
pytest --cov=src/clouvel --cov-report=html
```

**목표**: 50% 이상 커버리지

### 9. 기능별 GIF (CDO)

```
docs/landing/assets/
├── demo.gif (현재)
├── can_code.gif (신규)
├── manager.gif (신규)
├── knowledge.gif (신규)
└── ship.gif (신규)
```

### 10. Team 티어 계획 (CFO)

```markdown
# Team 티어 설계

- 가격: $129/mo (10석)
- 기능:
  - 팀 협업 도구
  - 공유 Knowledge Base
  - 팀 규칙 동기화
- 출시: Q2 2026
```

### 11. KB 암호화 (CSO)

```python
# 기본 암호화 활성화 검토

# 현재: CLOUVEL_KB_KEY 환경변수 있을 때만
# 제안: 첫 실행 시 자동 키 생성

def init_knowledge(path: str):
    if not os.getenv("CLOUVEL_KB_KEY"):
        key = Fernet.generate_key()
        # ~/.clouvel/.kb_key에 저장
```

---

## 진행 추적

| 주차 | P0 | P1 | P2 | 비고 |
|------|----|----|----|----|
| Week 1 | 3/3 | 0/4 | 0/4 | 테스트 집중 |
| Week 2 | - | 2/4 | 0/4 | CI, review |
| Week 3 | - | 4/4 | 1/4 | PH 준비 |
| Week 4 | - | - | 4/4 | 마무리 |

---

## 검증 체크리스트

### P0 완료 조건
- [x] pytest 전체 통과 ✅ (234 passed)
- [x] PRD v1.9 섹션 추가됨 ✅
- [ ] Reddit 포스트 업로드됨 (대기 중)

### P1 완료 조건
- [x] CI에서 docs_check.py 실행됨 ✅
- [x] review 도구 API 설계 완료 ✅ (PRD v1.10)
- [ ] Product Hunt 제출 가능 상태
- [x] CLAUDE.md에 Compounding Rules 추가됨 ✅

### P2 완료 조건
- [ ] 테스트 커버리지 50% 이상
- [ ] 기능별 GIF 4개 추가됨
- [ ] Team 티어 설계 문서 완료
- [ ] KB 암호화 기본 활성화 검토 완료

---

## 담당자 배정

| 역할 | 담당 | P0 | P1 | P2 |
|------|------|----|----|----|
| PM | Product | 1 | 1 | 0 |
| CTO | Tech | 0 | 1 | 1 |
| QA | Quality | 1 | 0 | 0 |
| CMO | Marketing | 1 | 1 | 0 |
| CFO | Finance | 0 | 0 | 1 |
| CSO | Security | 0 | 0 | 1 |
| CDO | Design | 0 | 0 | 1 |
| Error | Errors | 0 | 1 | 0 |
