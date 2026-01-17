# Clouvel 현재 상태

> **마지막 업데이트**: 2026-01-17

---

## 지금 상태

- **PyPI**: v0.5.0 ✅
- **도구 수**: 18개 (v0.5.0 기준), 23개 (v0.8.0 완료 시)
- **단계**: 자동 배포 시스템 가동 중
- **블로커**: 없음

---

## 배포 시스템

```
releases/
├── v0.5.0.toml  (1/17) ✅ 배포 완료
├── v0.6.0.toml  (1/20) 자동 대기
├── v0.7.0.toml  (1/23) 자동 대기
└── v0.8.0.toml  (1/26) 자동 대기 (마지막 공개)

pyproject.toml → dev (개발용)
scheduled-release.yml → 날짜별 자동 배포
```

---

## 오늘 완료 (2026-01-17)

- [x] v0.5.0 PyPI 배포
- [x] 버전별 배포 시스템 구축 (releases/*.toml)
- [x] scheduled-release.yml 자동화
- [x] PYPI_API_TOKEN 시크릿 설정
- [x] 로드맵 정리 (ROADMAP.md 통합, INTERNAL 삭제)

---

## 자동 배포 스케줄

| 버전 | 날짜 | 도구 | 상태 |
|------|------|------|------|
| v0.5.0 | 1/17 | Rules + Verify | ✅ 완료 |
| v0.6.0 | 1/20 | Planning | 자동 |
| v0.7.0 | 1/23 | Agents | 자동 |
| v0.8.0 | 1/26 | Hooks | 자동 (마지막) |

---

## 개발 우선순위

```
✅ Clouvel 먼저 (v0.8.0까지)
   → 23개 도구 완성
   → Free 버전 확정

⏳ Pro 개발 (v1.0+)
   → 에러 학습, 컨텍스트 유지
   → Shovel-setup 점진적 흡수

✅ 개인화 먼저 (Free → Pro)
⏳ 팀 기능 나중 (Team)
```

---

## 다음 할 일

- [ ] v0.6.0~v0.8.0 자동 배포 모니터링
- [ ] Pro 기능 설계 시작 (2월)
- [ ] 랜딩페이지 Pro 섹션 업데이트

---

## 주의사항

- 개발 중 pyproject.toml 버전은 "dev" 유지
- 배포는 releases/*.toml 파일로 관리
- 수동 배포: GitHub Actions > scheduled-release > Run workflow
