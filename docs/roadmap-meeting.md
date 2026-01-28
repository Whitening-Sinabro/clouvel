# Meeting System Roadmap

> v2.1 회의 시뮬레이션 시스템

---

## 완료된 Phase

### Phase 1: 기본 연결 (v2.1) ✅

**목표**: meeting 도구로 자연스러운 회의록 생성

| 파일 | 역할 |
|------|------|
| `meeting.py` | MCP 도구 (meeting, meeting_topics) |
| `meeting_prompt.py` | 프롬프트 빌더 (PERSONAS + EXAMPLES 조합) |

**핵심 달성**:
- BYOK 불필요 - Claude가 직접 생성
- 토픽 자동 감지 (12개 토픽)
- 매니저 자동 선택
- Few-shot 예시 포함

---

### Phase 2: 피드백 루프 (v2.1) ✅

**목표**: 품질 측정 + A/B 테스팅으로 프롬프트 지속 개선

| 파일 | 역할 |
|------|------|
| `meeting_feedback.py` | 평가 수집, 통계, training data 추출 |
| `meeting_tuning.py` | A/B 테스팅, 프롬프트 버전 관리 |

**MCP 도구**:
- `rate_meeting` - 회의 품질 평가 (1-5점)
- `get_meeting_stats` - 통계 보기
- `export_training_data` - 고품질 회의록 추출
- `enable_ab_testing` / `disable_ab_testing` - A/B 테스팅
- `get_variant_performance` - 버전별 성능 비교
- `list_variants` - 사용 가능한 버전 목록

**프롬프트 버전**:
| 버전 | 이름 | 특징 |
|------|------|------|
| v1.0.0 | baseline | 풀 페르소나 + 예시 1개 |
| v1.1.0 | concise | 요약 페르소나, 질문 없음 |
| v1.2.0 | rich_examples | 예시 2개 |
| v1.3.0 | minimal | 최소 프롬프트 |

---

### Phase 3: KB 연동 고도화 (v2.1) ✅

**목표**: 프로젝트 컨텍스트 + 개인화

| 파일 | 역할 |
|------|------|
| `meeting_kb.py` | 풍부한 KB 컨텍스트, 프로젝트 패턴 분석 |
| `meeting_personalization.py` | 매니저 비중, 페르소나 커스터마이징 |

**MCP 도구**:
- `configure_meeting` - 매니저 비중, 언어, 형식 설정
- `add_persona_override` - 매니저 말투/질문 커스터마이징
- `get_meeting_config` - 현재 설정 확인
- `reset_meeting_config` - 설정 초기화

**KB 연동 강화**:
- 🔒 LOCKED 결정 → 제약사항으로 표시
- 📋 관련 결정 + reasoning 포함
- 📍 토픽 관련 코드 위치 포함
- 🎯 프로젝트 패턴 → 매니저 비중 자동 조절

---

## 예정된 Phase

### Phase 4: 품질 자동화 (v2.2) 📋

**목표**: 수동 평가 없이도 품질 측정 + 자동 개선

**구현 항목**:

| 항목 | 설명 | 우선순위 |
|------|------|----------|
| `meeting_quality.py` | 품질 자동 체크 로직 | P1 |
| 품질 기반 자동 평가 | rating 없어도 점수 산출 | P1 |
| 재생성 요청 로직 | 품질 낮으면 재시도 유도 | P2 |
| 자동 버전 선택 | 품질 기반 variant 가중치 조절 | P2 |
| EXAMPLES 자동 제안 | 고품질 회의록 → 학습 데이터 | P3 |

**품질 체크 항목**:
```python
{
    "has_all_managers": bool,      # 선택된 매니저 다 발언?
    "has_action_items": bool,      # 액션 아이템 있나?
    "has_warnings": bool,          # NEVER/ALWAYS 있나?
    "dialogue_natural": float,     # 대화 자연스러움 (0-1)
    "context_specific": float,     # 구체적 조언인가? (0-1)
    "total_score": int,            # 종합 점수 (0-100)
}
```

**트리거 조건**:
- 사용자 피드백: "회의록 품질이 들쭉날쭉하다"
- 데이터: rate_meeting 사용률 < 10%
- 요청: "자동으로 좋은 회의록만 보여줘"

---

## 전체 도구 목록 (v2.1)

| Phase | 도구 | 설명 |
|-------|------|------|
| 1 | `meeting` | 회의 시뮬레이션 |
| 1 | `meeting_topics` | 지원 토픽 목록 |
| 2 | `rate_meeting` | 회의 품질 평가 |
| 2 | `get_meeting_stats` | 통계 |
| 2 | `export_training_data` | 학습 데이터 추출 |
| 2 | `enable_ab_testing` | A/B 테스팅 시작 |
| 2 | `disable_ab_testing` | A/B 테스팅 종료 |
| 2 | `get_variant_performance` | 버전별 성능 |
| 2 | `list_variants` | 버전 목록 |
| 3 | `configure_meeting` | 프로젝트 설정 |
| 3 | `add_persona_override` | 페르소나 커스터마이징 |
| 3 | `get_meeting_config` | 설정 확인 |
| 3 | `reset_meeting_config` | 설정 초기화 |

**총 13개 새 MCP 도구** (모두 Free)

---

## 마케팅 포인트

### Before (기존 manager)
- "PRD 없으면 코딩 없다" → 차단/강제 느낌
- 플랜/액션아이템만 반환
- API 키 필요 (BYOK)

### After (새 meeting)
- **"30초 회의록"** → 도움 느낌
- 자연스러운 대화형 회의록
- API 불필요, Claude가 직접 생성
- 프로젝트별 맞춤 설정

---

## 다음 단계

1. [ ] 실제 테스트 - meeting 도구 돌려보기
2. [ ] 랜딩페이지 업데이트 - "회의록 자동 생성" 강조
3. [ ] PyPI 배포 - v2.1.0
4. [ ] 사용자 피드백 수집
5. [ ] Phase 4 검토 (피드백 기반)
