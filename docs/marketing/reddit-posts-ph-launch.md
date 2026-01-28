# Reddit Posts - Product Hunt Launch Day

> **사용 시점**: Product Hunt 런칭 후 (2026-01-28 15:00 VN ~)
> **링크 교체 필요**: `[링크]` → Product Hunt URL

---

## 1. r/ClaudeAI

**Title:**
```
I built an MCP server that blocks Claude from coding until you write a PRD
```

**Body:**
```
Hey everyone!

I kept running into this problem: I'd tell Claude "build a login system" and it would skip password reset, rate limiting, error handling...

It's not Claude's fault - it compresses requirements to give you something fast.

So I built Clouvel - an MCP server that enforces PRD-first development:

- No PRD → BLOCKED (can't write code)
- Incomplete PRD → WARNING (shows what's missing)
- Complete PRD → PASS (start coding)

It also has 8 AI "managers" (PM, CTO, QA, CSO, etc.) that ask tough questions before you build - like "Is this MVP scope?" or "How do you handle token expiry?"

**Install:**
```
pip install clouvel
```

Works with Claude Code and Claude Desktop.

Free & open source: https://github.com/Whitening-Sinabro/clouvel

Just launched on Product Hunt today: [링크]

Would love feedback from this community since you all actually use Claude daily!
```

---

## 2. r/SideProject

**Title:**
```
I got mass frustrated with AI writing "almost right" code, so I built a tool that blocks coding until you write a spec
```

**Body:**
```
Every time I asked AI to build something, it would "compress" my requirements:

"Build login" → No password reset
"Add payments" → No error handling
"Create API" → No rate limiting

Then I'd spend hours debugging code that was 80% right but 100% broken.

**The fix:** Don't let AI code without a spec.

I built Clouvel - it's a simple gate:
- No documentation? Coding blocked.
- Missing sections? Warning shown.
- Complete PRD? Start building.

It also has 8 AI "managers" that review your plan and ask questions like:
- "Is this MVP scope or post-launch?"
- "What happens with empty input?"
- "How do you verify the user is who they claim?"

**The result:** Same input = same output. No more "that's not what I meant."

Free & open source. Just launched on Product Hunt:
[링크]

GitHub: https://github.com/Whitening-Sinabro/clouvel

Solo dev here - would love your feedback!
```

---

## 3. r/IndieHackers

**Title:**
```
Launched my first product on Product Hunt today - a "PRD gate" for AI coding
```

**Body:**
```
Hey IH!

Launched Clouvel on Product Hunt today. It's an MCP server that blocks AI from coding until your PRD is ready.

**The problem I was solving:**

When you tell Claude/Cursor "build X", it compresses your requirements. You get code that's 80% right but missing critical pieces. Then you debug for hours.

**The solution:**

A simple gate - no docs, no code. Plus 8 AI "managers" (PM, CTO, QA, etc.) that ask tough questions before you build.

**Tech stack:**
- Python (MCP server)
- Polar.sh for licensing
- GitHub Pages for landing

**Pricing:**
- Free: Core features (PRD gate)
- Pro: $9.99/mo (AI managers, verification tools)

**Launch day stats:** [will update]

Would appreciate any support on PH: [링크]

Happy to answer questions about the build or launch process!
```

---

## 포스팅 순서

| 순서 | 서브레딧 | 시간 (VN) | 비고 |
|------|----------|----------|------|
| 1 | r/ClaudeAI | 15:30 | 타겟 유저 |
| 2 | r/SideProject | 16:00 | 일반 개발자 |
| 3 | r/IndieHackers | 17:00 | 비즈니스 관점 |

---

## 주의사항

- Product Hunt 링크는 런칭 후 복사해서 교체
- 각 서브레딧 규칙 확인 (self-promotion 제한 있을 수 있음)
- 댓글에 성실히 답변하기
