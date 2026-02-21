# Product Hunt Launch — Clouvel v5.0

> **목표 런칭일**: 2026-02-24 (화) or 2026-02-25 (수)
> **최적 시간**: 00:01 PST (한국 17:01 / 베트남 14:01)
> **상태**: 준비 중

---

## 1. Basic Info

| Item | Content |
|------|---------|
| Product Name | Clouvel |
| Tagline (60 chars) | Stop Claude Code from breaking your code. It remembers. |
| Website | https://clouvels.com/ |
| GitHub | https://github.com/Whitening-Sinabro/clouvel |
| Topics | Developer Tools, AI, Open Source, Productivity |
| Pricing | Free (10 tools) / Pro $7.99/mo or $49/yr |

---

## 2. Description (240 chars max)

```
Claude Code is fast. But it forgets what it broke yesterday and breaks it again today.

Clouvel remembers every error, warns before repeats, and ships with proof. 20 MCP tools — 10 free. pip install clouvel.
```

---

## 3. First Comment (Maker's Comment)

```
Hey Product Hunt! 👋

I built Clouvel because I kept hitting the same problem: Claude Code would break something, I'd fix it, and next session it would break the exact same thing again.

AI coding tools are incredibly fast — but they have zero memory between sessions. Your decisions, your errors, your context: all gone.

Clouvel is an MCP server that gives Claude Code a persistent brain:

🔴 Regression Memory — records every error pattern. If the same bug tries to ship again, it gets caught automatically.

🟡 8 AI Managers — before you code, a virtual CTO, QA lead, and security officer review your plan and ask the questions you forgot.

🟢 Ship with Proof — one command runs lint → test → build and generates a signed evidence file. No more "it works on my machine."

How to try it:
  pip install clouvel

10 tools are completely free. No account needed. No data leaves your machine.

5,100+ monthly installs so far. Would love feedback from this community! 🙏

Docs: https://clouvels.com/docs-en
GitHub: https://github.com/Whitening-Sinabro/clouvel
```

---

## 4. Gallery Images (1270×760)

| # | Content | Status | File |
|---|---------|--------|------|
| 1 | **Hero**: "Stop Claude Code from breaking your code" + terminal mockup | ✅ HTML | mockups/ph_hero.html |
| 2 | **Problem → Solution**: "Without/With Clouvel" split view | ✅ HTML | mockups/ph_problem_solution.html |
| 3 | **Regression Memory**: Record → Match → Prevent flow | ✅ HTML | mockups/ph_regression_memory.html |
| 4 | **8 AI Managers**: meeting transcript screenshot | ✅ 기존 | mockups/manager_feedback.html |
| 5 | **Ship Evidence**: PASS output + "One command. Proof it works." | ✅ HTML | mockups/ph_ship_evidence.html |

> 기존 can_code_block/pass 스크린샷은 v3.0 "PRD gate" 메시지라 교체 필요

### 갤러리 이미지 제작 방법
1. HTML mockup 파일 생성 (docs/marketing/mockups/)
2. 브라우저에서 열고 1270×760 뷰포트
3. 스크린샷 캡처 → PNG 저장
4. 또는 Figma/Canva로 제작

---

## 5. Assets Checklist

- [ ] Logo 240×240 PNG (현재 있으나 리사이즈 확인 필요)
- [ ] Gallery Image 1 — Hero (HTML 완성, 스크린샷 필요)
- [ ] Gallery Image 2 — Problem/Solution (HTML 완성, 스크린샷 필요)
- [ ] Gallery Image 3 — Regression Memory flow (HTML 완성, 스크린샷 필요)
- [ ] Gallery Image 4 — Manager Meeting (기존 HTML, 스크린샷 필요)
- [ ] Gallery Image 5 — Ship Evidence (HTML 완성, 스크린샷 필요)
- [ ] OG Image 1200×630 (현재 og-image.png 확인)
- [ ] Demo GIF or Video (선택, 강력 추천)

---

## 6. Pre-Launch (D-7 ~ D-1)

- [ ] PH에 product page draft 생성 (producthunt.com/posts/new)
- [ ] "Coming Soon" 페이지 활성화 → early followers 확보
- [ ] Gallery images 5장 업로드
- [ ] Maker profile 완성 (bio, avatar, links)
- [ ] Twitter/X에 teaser 포스트 (D-3)
- [ ] r/ClaudeAI에 value post 1개 (PH 언급 없이, 가치 제공)
- [ ] GitHub README에 "Launching on PH [date]" 배너 추가
- [ ] 랜딩 페이지에 PH launch badge 추가 (launch day에 활성화)
- [ ] 지인/커뮤니티에 DM으로 런칭일 공유

---

## 7. Launch Day (D-Day)

### 00:01 PST — 런칭
- [ ] PH에서 제품 publish
- [ ] First comment 즉시 게시

### +1h — 초기 확산
- [ ] Twitter/X 런칭 포스트 (아래 SNS Posts 참고)
- [ ] GitHub README에 PH badge 활성화
- [ ] 랜딩에 PH badge 표시

### +2~4h — 커뮤니티
- [ ] r/ClaudeAI 포스트
- [ ] r/SideProject 포스트
- [ ] r/IndieHackers 포스트

### 종일 — 참여
- [ ] PH 댓글에 30분 이내 답변
- [ ] Twitter 멘션 답변
- [ ] Reddit 댓글 답변

### End of Day — 기록
- [ ] 최종 순위 스크린샷
- [ ] upvote/comment 수 기록
- [ ] current.md 업데이트

---

## 8. Post-Launch (D+1 ~ D+7)

- [ ] Hacker News "Show HN" 포스트
- [ ] Dev.to 블로그 글 ("Why I built Clouvel")
- [ ] PH followers에게 감사 코멘트
- [ ] 피드백 기반 quick wins 구현
- [ ] weekly download/star 추이 기록

---

## 9. Key Metrics to Track

| Metric | Current | Launch Target |
|--------|---------|---------------|
| PH Upvotes | — | 100+ |
| PH Rank | — | Top 10 |
| GitHub Stars | 2 | 20+ |
| PyPI Monthly | 5,124 | 8,000+ |
| Website visitors (launch day) | ~50/day | 500+ |

---

## 10. Launch Timing Strategy

| 옵션 | 날짜 | 장단점 |
|------|------|--------|
| **A (추천)** | 화 02-24 | 화요일 = PH 최적일, 준비 시간 3일 |
| B | 수 02-25 | 하루 더 준비, 여전히 좋은 요일 |
| C | 화 03-03 | 넉넉한 준비, gallery 완벽하게 |

> ⚠️ 금/토/일/월 런칭 절대 금지 — 트래픽 최저
