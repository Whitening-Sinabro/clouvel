# Clouvel 현재 상태

> **마지막 업데이트**: 2026-01-16

---

## 지금 상태

- **버전**: v0.3.5 → v0.4.0 준비 중
- **단계**: CLI 온보딩 기능 추가 완료
- **블로커**: 없음

---

## 완료 목록

- [x] ROADMAP_INTERNAL.md에 글로벌 확장 조건 추가
- [x] ROADMAP_INTERNAL.md에 v0.4.0 디자인 가이드 섹션 추가
- [x] **Analytics 기능 추가** (2026-01-16)
  - `get_analytics` 도구 추가
- [x] **CLI 온보딩 기능 추가** (2026-01-16)
  - `init_clouvel` MCP 도구 - 플랫폼별 맞춤 안내 (desktop/vscode/cli)
  - `setup_cli` MCP 도구 - CLI 환경 자동 설정 (hooks, CLAUDE.md, pre-commit)
  - `clouvel init` CLI 명령어 - 인터랙티브 설정
  - 강제 수준 선택: remind(경고) / strict(커밋차단) / full(전부)

---

## 현재 도구 목록 (12개)

| 도구 | 설명 | 신규 |
|------|------|------|
| `can_code` | 코딩 가능 여부 확인 (핵심) | |
| `scan_docs` | docs 폴더 스캔 | |
| `analyze_docs` | 필수 문서 분석 | |
| `init_docs` | docs 폴더 초기화 | |
| `get_prd_template` | PRD 템플릿 생성 | |
| `write_prd_section` | PRD 섹션별 가이드 | |
| `get_prd_guide` | PRD 작성법 | |
| `get_verify_checklist` | 검증 체크리스트 | |
| `get_setup_guide` | 설치 가이드 | |
| `get_analytics` | 사용량 통계 | |
| `init_clouvel` | 온보딩 (플랫폼 선택) | ⭐ |
| `setup_cli` | CLI 환경 설정 | ⭐ |

---

## 다음 할 일

v0.4.0 버전 릴리스:
- [ ] 버전 번호 업데이트 (pyproject.toml)
- [ ] README 업데이트 (새 기능 설명)
- [ ] 테스트 (clouvel init 실행 확인)
- [ ] PyPI 배포

v0.5.0 (컨텍스트 유지):
- [ ] `save_context` 구현
- [ ] `restore_context` 구현
- [ ] `get_handoff` 구현

---

## 주의사항

- 내부 프로젝트 작업 시 PM+CTO 듀얼 관점 적용
- 비전공자 친화적 원칙 유지
- CLI 강제는 Hooks + pre-commit 조합으로 구현
