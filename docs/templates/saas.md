# SaaS 템플릿

> 결제 기능이 있는 SaaS MVP

---

## 자동 감지 조건

다음 중 하나라도 있으면 `saas`로 감지:

- `pages/pricing` 또는 `app/pricing` 폴더
- `stripe.ts`, `checkout` 파일
- 의존성: `stripe`, `@stripe/stripe-js`, `polar-sh`, `paddle`

---

## PRD 질문 가이드

| 순서 | 섹션         | 질문                         | 예시                                               |
| ---- | ------------ | ---------------------------- | -------------------------------------------------- |
| 1    | summary      | 이 SaaS가 해결하려는 문제는? | 랜딩 페이지 만들기가 어려움                        |
| 2    | target       | 주요 타겟 사용자는?          | 1인 창업자, 소규모 팀                              |
| 3    | features     | 핵심 기능 3-5개              | 드래그앤드롭 빌더, 템플릿, 커스텀 도메인           |
| 4    | pricing      | 가격 구조는?                 | Free $0, Pro $15/월                                |
| 5    | payment      | 결제 방식은?                 | Stripe 구독, 연/월 결제                            |
| 6    | side_effects | 기존 사용자/결제에 영향?     | 기존 요금제 영향, 데이터 마이그레이션, 결제 플로우 |
| 7    | out_of_scope | 제외할 기능                  | 팀 기능, 모바일 앱                                 |

---

## PRD 예시

````markdown
# PageBuilder SaaS PRD

## 1. 프로젝트 개요

### 1.1 목적

코딩 없이 랜딩 페이지를 만들 수 있는 SaaS

### 1.2 타겟 사용자

- 1인 창업자
- 마케터
- 비개발자

### 1.3 성공 지표

| 지표      | 목표 (3개월) |
| --------- | ------------ |
| 가입자    | 500+         |
| 유료 전환 | 50+          |
| MRR       | $500+        |

---

## 2. 기능 요구사항

### 2.1 핵심 기능 (Must Have)

1. **드래그앤드롭 빌더**: 블록 기반 편집
2. **템플릿**: 10개 이상 시작 템플릿
3. **퍼블리시**: 서브도메인 배포

### 2.2 부가 기능 (Nice to Have)

1. **커스텀 도메인**: Pro 전용
2. **분석**: 페이지뷰 통계

### 2.3 제외 범위 (v1)

- 팀 협업 기능
- 모바일 앱
- A/B 테스트

---

## 3. 가격 정책

### 3.1 티어 구성

| 티어 | 가격   | 기능                         |
| ---- | ------ | ---------------------------- |
| Free | $0     | 3개 페이지, 서브도메인       |
| Pro  | $15/월 | 무제한 페이지, 커스텀 도메인 |
| Team | $49/월 | 협업, 분석, 우선 지원        |

### 3.2 결제 방식

- 결제 처리: Stripe
- 월간/연간 (연간 20% 할인)
- 14일 환불 보장

---

## 4. 기술 스펙

### 4.1 기술 스택

- Frontend: Next.js + TypeScript
- Backend: Next.js API Routes
- Database: Supabase (PostgreSQL)
- Auth: Supabase Auth
- Payment: Stripe
- 배포: Vercel

### 4.2 주요 API

| Method | Path                | 설명                      |
| ------ | ------------------- | ------------------------- |
| POST   | `/api/checkout`     | Stripe Checkout 세션 생성 |
| POST   | `/api/webhook`      | Stripe Webhook 처리       |
| GET    | `/api/subscription` | 구독 상태 조회            |

### 4.3 DB 스키마

```sql
-- users (Supabase Auth 확장)
CREATE TABLE profiles (
  id UUID REFERENCES auth.users PRIMARY KEY,
  plan TEXT DEFAULT 'free',
  stripe_customer_id TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- pages
CREATE TABLE pages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES profiles(id),
  title TEXT,
  content JSONB,
  published BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT NOW()
);
```
````

```

---

## 체크리스트

- [ ] 가격 정책이 명확한가?
- [ ] Free tier가 있는가?
- [ ] Stripe Webhook이 구현되었는가?
- [ ] 구독 상태별 기능 제한이 있는가?
- [ ] 환불 정책이 있는가?
- [ ] 이용약관/개인정보처리방침이 있는가?
```
