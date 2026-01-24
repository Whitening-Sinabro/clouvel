# Reddit Post Drafts

> Created: 2026-01-24
> Target: Week 2 - First community posts

---

## 1. r/ClaudeAI

**Title**: I built an MCP server that blocks Claude from coding until you write a spec

**Body**:

Hey r/ClaudeAI!

I kept running into the same problem: I'd ask Claude to "build login" and it would skip password reset, forget social auth, and ignore half my requirements. Every time I asked, I got different code.

So I built **Clouvel** - an MCP server that adds a PRD gate to Claude.

**How it works:**
- You ask Claude to code something
- Clouvel checks if a PRD (spec) exists
- No spec? Coding blocked. Write the spec first.
- Spec exists? Coding allowed.

```
You: "Build login"
Claude: ❌ BLOCKED - No PRD found

You: *writes requirements*
Claude: ✅ PASS - Coding allowed
```

**Demo**: [GIF showing BLOCK → PASS flow]

The idea is simple: same spec → same output. No more "AI lottery."

It's free and open source. Pro version adds 8 C-Level manager personas (PM, CTO, QA, etc.) that review your code.

**GitHub**: https://github.com/Whitening-Sinabro/clouvel
**Docs**: https://whitening-sinabro.github.io/clouvel/

Would love feedback from this community. Anyone else frustrated with inconsistent AI code output?

---

## 2. r/SideProject

**Title**: I built a "spec gate" for AI coding after wasting hours debugging AI-generated code

**Body**:

Hey everyone!

**The problem**: As a solo dev, I use AI coding assistants constantly. But I noticed a pattern - AI would "interpret" my vague requests and build something 80% right. Then I'd spend hours debugging the 20%.

**The pattern**:
- "Build login" → skips password reset
- "Add dashboard" → different layout every time
- "Create API" → inconsistent error handling

**My solution**: I built Clouvel, an MCP server that blocks AI from coding until you write a spec (PRD).

It sounds annoying, but it actually saves time. Writing a 10-minute spec means:
- AI knows exactly what to build
- Consistent output every time
- No more "what was I thinking?" moments

**Quick start:**
```bash
pip install clouvel
clouvel install
# That's it
```

It's free and MIT licensed. I also have a Pro version with "manager" personas that review code (like having a virtual PM and CTO).

**GitHub**: https://github.com/Whitening-Sinabro/clouvel

Anyone else building tools to make AI coding more predictable? Would love to hear your approaches.

---

## 3. r/IndieHackers (or r/SaaS)

**Title**: From 0 subscribers to pivoting to English market - my AI dev tool journey

**Body**:

Hey indie hackers!

Quick story: I built Clouvel, a PRD-first gate for AI coding. Launched targeting Korean developers. Result: 0 paying users.

**What went wrong**: The Claude Code / MCP ecosystem is almost entirely English-speaking. I was marketing in Korean to an audience that doesn't exist.

**The pivot**: Spent a week converting everything to English - docs, error messages, landing page. Now targeting solo devs and indie hackers globally.

**What Clouvel does**:
Blocks AI from coding until you write a spec. Sounds simple, but it solves the "AI lottery" problem where you get different code every time you ask.

```
Before: "Build login" → AI guesses requirements
After: "Build login" → AI reads your PRD, builds exactly what you specified
```

**Business model**:
- Free: Core PRD gate (open source)
- Pro ($9.99/mo): 8 "manager" personas review your code

**Current stats**:
- GitHub stars: [X]
- Users: [X]
- Revenue: $0 (just pivoted)

**Lessons learned**:
1. Check if your target market exists before building
2. English-first for dev tools (unless you have a specific regional advantage)
3. MCP ecosystem is small but growing fast

Would love feedback on the positioning. Does "PRD-first AI coding" resonate?

**Links**:
- GitHub: https://github.com/Whitening-Sinabro/clouvel
- Landing: https://whitening-sinabro.github.io/clouvel/

---

## Posting Strategy

| Subreddit | Best Time (PST) | Day | Notes |
|-----------|-----------------|-----|-------|
| r/ClaudeAI | 9-11 AM | Tue-Thu | Technical audience, focus on MCP |
| r/SideProject | 8-10 AM | Mon-Wed | Show progress, ask for feedback |
| r/IndieHackers | 7-9 AM | Tue-Thu | Story-driven, business angle |

### Tips
- Don't post to all 3 on the same day
- Engage with comments within first 2 hours
- Cross-post success to X with #BuildInPublic

---

## Checklist

- [ ] Post to r/ClaudeAI (most relevant)
- [ ] Wait 2-3 days, post to r/SideProject
- [ ] Wait 2-3 days, post to r/IndieHackers
- [ ] Update stats in posts with real numbers
- [ ] Replace [GIF] with actual demo.gif link
