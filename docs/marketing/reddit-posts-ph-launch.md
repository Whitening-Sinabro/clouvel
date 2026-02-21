# Reddit Posts — Product Hunt Launch Day

> **사용 시점**: Product Hunt 런칭 후 2~4시간
> **링크 교체**: `[PH_LINK]` → Product Hunt URL

---

## 1. r/ClaudeAI (타겟 유저)

**Title:**
```
I built an MCP server that gives Claude Code a memory — it remembers what it broke and stops it from happening again
```

**Body:**
```
Hey everyone!

I kept hitting the same problem: Claude Code would introduce a bug, I'd fix it, and next session it would break the exact same thing. No memory between sessions = same mistakes on repeat.

So I built Clouvel — an MCP server that gives Claude Code persistent memory:

**What it does:**
- 🔴 Regression Memory — records every error pattern. Same bug tries to ship twice? Caught automatically.
- 🟡 8 AI Managers — before you code, a virtual CTO/QA/CSO review your plan and surface blind spots.
- 🟢 Ship with Proof — one command: lint → test → build → evidence file. "Works on my machine" becomes a signed report.

**How it works:**
```
pip install clouvel
```
That's it. 20 MCP tools load into Claude Code. 10 are completely free.

No account needed. No data leaves your machine. Everything runs locally.

**Stats:**
- 5,100+ monthly installs on PyPI
- 20 tools (10 free / 10 Pro)
- Open source: https://github.com/Whitening-Sinabro/clouvel

Just launched on Product Hunt today: [PH_LINK]

Would love feedback from this community — you're literally the target users! What problems do you hit with Claude Code that you wish were solved?
```

---

## 2. r/SideProject (인디 개발자)

**Title:**
```
Claude Code kept breaking the same thing every session. So I built a tool that gives it a memory.
```

**Body:**
```
The problem was stupid simple:

1. Tell Claude "build auth system"
2. It writes working code
3. Next session: "refactor the API"
4. Auth system breaks. The same way as last time.
5. Fix it. Again.

Claude Code has zero memory between sessions. Every session starts from scratch.

**The fix: Clouvel**

It's an MCP server (Claude Code plugin) that:
- **Remembers errors** across sessions — if the same pattern tries to recur, it warns you before the code ships
- **Reviews your plan** with 8 AI "managers" (CTO, QA, security, etc.) — catches blind spots before coding starts
- **Generates ship evidence** — lint/test/build results in one report

**Install:** `pip install clouvel`

10 tools free. No account. Runs 100% locally.

Open source: https://github.com/Whitening-Sinabro/clouvel
Launched on Product Hunt today: [PH_LINK]

Solo dev here — built this over 3 months because I was losing hours to repeated bugs. Would love your thoughts!
```

---

## 3. r/IndieHackers (비즈니스 관점)

**Title:**
```
Launching my MCP server on Product Hunt today — 5K monthly installs, $0 spent on marketing
```

**Body:**
```
Hey IH!

Launching Clouvel on Product Hunt today. It's an MCP server (plugin) for Claude Code that prevents repeated mistakes.

**The problem I'm solving:**
AI coding tools are fast but have no memory. Same bugs, same mistakes, every session. Developers waste hours re-fixing what AI already broke before.

**The solution:**
Clouvel gives Claude Code persistent memory — error patterns, decisions, and context survive across sessions.

**Numbers so far:**
- 5,100+ monthly PyPI installs (organic, $0 marketing spend)
- 20 tools (10 free / 10 Pro at $7.99/mo or $49/yr)
- Solo developer

**Tech stack:**
- Python MCP server
- Polar.sh for licensing
- Cloudflare Pages + GitHub Pages for landing
- SQLite for local knowledge base

**What worked:**
- Solving my own pain point (developers who use Claude Code daily)
- Free tier that's genuinely useful (10 tools, no limits)
- PyPI distribution = zero-friction install

**What's next:**
- Product Hunt launch (today!)
- First blog posts / content marketing
- Community building

PH link: [PH_LINK]
GitHub: https://github.com/Whitening-Sinabro/clouvel

Happy to answer questions about the build, pricing, or launch strategy!
```

---

## 포스팅 순서

| 순서 | 서브레딧 | PH 런칭 후 | 비고 |
|------|----------|-----------|------|
| 1 | r/ClaudeAI | +2h | 핵심 타겟 유저 |
| 2 | r/SideProject | +3h | 일반 개발자 |
| 3 | r/IndieHackers | +4h | 비즈니스/런칭 관점 |

---

## 주의사항

- `[PH_LINK]`를 실제 Product Hunt URL로 교체
- 각 서브레딧의 self-promotion 규칙 확인
- r/ClaudeAI는 유용한 정보 위주, PH 링크는 맨 아래에
- 모든 댓글에 성실하게 답변 (특히 처음 2시간)
- "upvote 해주세요" 절대 금지 — PH 규칙 위반
