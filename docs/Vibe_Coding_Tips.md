# 바이브 코딩 실전 팁

> **출처**: 커뮤니티 베스트 프랙티스 모음
> **Last Updated**: 2026-01-14

---

## 🎨 Typography (뻔한 폰트 방지)

> **출처**: aicoffeechat (226❤️)
> **문제**: AI는 학습 데이터의 통계적 패턴 → 뻔한 결과

### 프롬프트에 추가

```markdown
<use_interesting_fonts>
❌ 사용 금지: Inter, Roboto, Open Sans, Lato, 시스템 기본 폰트

✅ 대신 사용:
- 기능성/개발: JetBrains Mono, Fira Code, Space Grotesk
- 감성/고급: Playfair Display, Crimson Pro
- 기하학/모던: DM Sans family, Source Sans 3
- 브루탈리스트: Bricolage Grotesque, Newsreader

해상도별 고려: 픽셀 밀도에 따라 폰트 크기/가중치 조정
소스: Google Fonts 사용
</use_interesting_fonts>
```

### 적용 시점

| 상황 | Typography 지정 |
|------|----------------|
| 랜딩 페이지 | ✅ 필수 |
| 대시보드 UI | ✅ 권장 |
| 카드뉴스/SNS | ✅ 필수 |
| 내부 도구 | △ 선택 |
| CLI | ❌ 불필요 |

---

## 🔢 토큰 관리 (Claude Max)

> **출처**: passionit._
> **경험**: Claude Max x20 사용

### 교훈

```
"압도적인 토큰 앞에 굴복하라"
→ 토큰 많아도 완료 기준 명확히!
```

### 팁
- 토큰 무제한이라도 작업 범위 명확히
- 한 세션에서 너무 많은 것 하지 않기
- 완료 조건 사전 정의

---

## ⚡ n8n 자동화

> **출처**: do_do_i_do
> **시간**: 2시간 만에 구축

### 워크플로우 예시

```
Execute → HTTP Request (Google API) → Split Out → HTTP Requests → JavaScript
```

### 활용
- 떡상 쇼츠 자동 수집
- API 연동 자동화
- 반복 작업 제거

---

## 🎯 PM 관점 (20년차)

> **철학**: 제품 50% + 비즈니스 50%

### 항상 질문

```
제품: 고객 문제? 검증됨? MVP 필수?
비즈니스: 수익 모델? 경쟁사? 가격? GTM?
```

### 바이브 코딩 역할

```
나: 고객, PRD, 우선순위, 전략, 검증
AI: 구현, 테스트, 디버깅, 문서화
```

---

## 📚 출처

- [aicoffeechat](https://threads.net/@aicoffeechat) - Typography
- [qjc.ai](https://threads.net/@qjc.ai) - 검증 프로토콜
- [Boris Cherny](https://howborisusesclaudecode.com/) - 워크플로우
