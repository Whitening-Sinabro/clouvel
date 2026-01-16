# Lemon Squeezy 세팅 가이드 (2026년 1월 기준)

> **상태**: 대기 (나중에 진행)
> **작성일**: 2026-01-17

---

## 0. 2026년 변경사항 요약 (Stripe 인수 후)

| 항목 | 이전 | 2026년 현재 |
|------|------|-------------|
| **Payout Fee (US)** | 0.5% + $2.50 | **무료** (Stripe payout) |
| **Payout Fee (국제)** | 3% + $2.50 | **1%** (Stripe payout) |
| **Platform Fee** | 5% + $0.50 | 동일 |
| **언어 지원** | 영어 중심 | **34개 언어 자동 감지** |
| **Webhook** | 수동 테스트 | **시뮬레이션 기능 추가** |
| **보안** | 기본 | **2FA 지원** |
| **환불** | 전체만 | **부분 환불 가능** |

---

## 1. 계정 및 Store 설정

### 1-1. Store Settings → General

| 설정 | 값 |
|------|-----|
| **Store name** | `Clouvel` |
| **Store subdomain** | `clouvel` → clouvel.lemonsqueezy.com |
| **Currency** | `USD` |
| **Tax-inclusive pricing** | `OFF` |
| **2FA** | `ON` |

### 1-2. Payouts

- **Stripe Payout 사용** (국민은행 이미 연결됨)
- Payout fee: 1% (한국)

---

## 2. Product 설정

### 기본 정보

| 필드 | 값 |
|------|-----|
| **Name** | `Clouvel Pro` |
| **Slug** | `clouvel-pro` |
| **Tax Category** | `Software` |

### Description (120-160자 권장)

```
PRD 없으면 코딩 없다. 바이브코딩 프로세스를 강제하는 MCP 서버. Shovel 통합, Gate/Verify 자동화. 1회 결제, 평생 사용.
```

---

## 3. Variants (3개 플랜)

### Variant 1: Personal

| 필드 | 값 |
|------|-----|
| **Name** | `Personal` |
| **Description** | `개인 개발자. 1 디바이스.` |
| **Price** | `$29` |
| **Payment type** | `One-time` |
| **License length** | `Unlimited` ✅ |
| **Activation limit** | `1` |

### Variant 2: Team (추천)

| 필드 | 값 |
|------|-----|
| **Name** | `Team` |
| **Description** | `소규모 팀. 10 디바이스.` |
| **Price** | `$79` |
| **Payment type** | `One-time` |
| **Featured** | `ON` ✅ |
| **License length** | `Unlimited` |
| **Activation limit** | `10` |

### Variant 3: Enterprise

| 필드 | 값 |
|------|-----|
| **Name** | `Enterprise` |
| **Description** | `대규모 팀. 무제한 디바이스.` |
| **Price** | `$199` |
| **Payment type** | `One-time` |
| **License length** | `Unlimited` |
| **Activation limit** | `Unlimited` |

---

## 4. License Key 설정 (모든 Variant)

| 설정 | 값 |
|------|-----|
| **Generate license keys** | `ON` ✅ |
| **License key length** | `16` (기본값) |
| **License length** | `Unlimited` ⚠️ (16 Years 아님!) |

---

## 5. Files (업로드 필요)

```
clouvel-pro-v1.x.x.zip
├── .claude/
│   ├── commands/
│   ├── templates/
│   ├── settings.json
│   └── CLAUDE.md
├── README.md
├── LICENSE.txt
└── CHANGELOG.md
```

---

## 6. Checkout 설정

| 설정 | 값 |
|------|-----|
| **Success URL** | `https://jinhyeokpark28.github.io/clouvel/success?license_key={license_key}` |

---

## 7. 랜딩페이지 연결 (나중에)

`docs/landing/index.html`의 `href="#"` → 실제 Lemon Squeezy URL로 교체

```html
<!-- Personal -->
<a href="https://clouvel.lemonsqueezy.com/buy/XXXXXXXX">구매하기</a>

<!-- Team -->
<a href="https://clouvel.lemonsqueezy.com/buy/YYYYYYYY">구매하기</a>

<!-- Enterprise -->
<a href="https://clouvel.lemonsqueezy.com/buy/ZZZZZZZZ">구매하기</a>
```

---

## 8. 수수료 계산

**$29 Personal 판매 시:**
```
판매가:          $29.00
Platform fee:    -$1.45 (5%)
Transaction fee: -$0.50
Net:             $27.05
Payout fee (KR): -$0.27 (1%)
────────────────────────
실수령:          $26.78
```

---

## 9. 체크리스트

```
□ Store 생성 (clouvel.lemonsqueezy.com)
□ Stripe Payout 연결 (국민은행)
□ Product "Clouvel Pro" 생성
□ Tax Category = "Software"
□ 3개 Variant 생성
   □ Personal: $29, 1 activation, unlimited length
   □ Team: $79, 10 activations, Featured
   □ Enterprise: $199, unlimited activations
□ ZIP 파일 업로드
□ Checkout redirect URL 설정
□ Store 활성화 요청
□ 랜딩페이지 구매 버튼 URL 연결
□ Test Mode에서 테스트 구매
□ Live Mode 전환
```

---

## Sources

- [Lemon Squeezy Docs](https://docs.lemonsqueezy.com/help)
- [Getting Started Guide](https://docs.lemonsqueezy.com/guides/getting-started)
- [Fees Documentation](https://docs.lemonsqueezy.com/help/getting-started/fees)
- [Tax Categories](https://docs.lemonsqueezy.com/help/products/tax-categories)
- [Stripe Acquires Lemon Squeezy](https://www.lemonsqueezy.com/blog/stripe-acquires-lemon-squeezy)
