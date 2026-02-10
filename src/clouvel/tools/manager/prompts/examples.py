# Few-shot Examples
# Example data for light tuning
# Format: (context, meeting_output) pairs

from typing import Dict, List, Any

# Good meeting notes examples (for few-shot)
EXAMPLES: Dict[str, List[Dict[str, str]]] = {

    # Auth-related example
    "auth": [
        {
            "context": "Login feature implementation plan. OAuth social login (Google, GitHub) + email login support planned.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: Login feature implementation. As defined in PRD section 3.1, we'll support OAuth social login + email login. Within MVP scope, timeline is 2 weeks.

**🛠️ CTO**: No technical issues. NextAuth.js makes OAuth integration fast. For email login, I recommend magic link approach. Storing passwords increases security risk.

**🔒 CSO**: Agree with CTO. Magic link is safer than passwords. But OAuth scope minimization is essential. Google: email, profile only. GitHub: user:email only. Excessive permissions cause user churn.

**🧪 QA**: I'll organize test cases. Need to cover social login failure cases (token expiry, permission denied), magic link expiry scenario, concurrent login handling.

**🔥 ERROR**: Need to consider fallback for external OAuth server outages. If Google auth server goes down, our service login shouldn't be blocked. Session extension can help.

**👔 PM**: Summary - 1) NextAuth + magic link approach, 2) Minimize OAuth scope, 3) Session extension for external outages. Proceeding with this plan.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | NextAuth.js setup + OAuth integration | P0 |
| 2 | 🛠️ CTO | Magic link email login implementation | P0 |
| 3 | 🔒 CSO | Review and minimize OAuth scope | P1 |
| 4 | 🧪 QA | Write login failure case tests | P1 |
| 5 | 🔥 ERROR | Fallback logic for OAuth outage | P2 |

## ⚠️ Warnings
- ❌ NEVER: Store plaintext passwords, Request excessive OAuth scope
- ✅ ALWAYS: Encrypt session tokens, Log login failures
"""
        }
    ],

    # API design example
    "api": [
        {
            "context": "REST API design review. User CRUD + Post CRUD. JWT auth planned.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: API design review. Basic structure is User CRUD, Post CRUD. Auth will be JWT.

**🛠️ CTO**: Structure looks good, but a few things to add. First, API versioning - add /api/v1 prefix. Needed for future breaking changes. Second, pagination should be cursor-based for scalability.

**🔒 CSO**: Important notes on JWT. Access token 15 min, Refresh token 7 days - keep them short. And Refresh token rotation is essential. For theft prevention.

**🧪 QA**: I'll add API test automation, but please unify error response format. Like `{error: {code, message}}`. Without consistency, frontend error handling is painful.

**💰 CFO**: Rate limit is a must. Unlimited API calls = cost explosion. Start with 100/min and increase as needed.

**👔 PM**: Summary - 1) Add API versioning, 2) Short JWT lifespan + rotation, 3) Unify error response format, 4) Set rate limit. Let's proceed in this order.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | Apply API versioning (/api/v1) | P0 |
| 2 | 🛠️ CTO | Implement cursor-based pagination | P1 |
| 3 | 🔒 CSO | Document JWT token policy | P1 |
| 4 | 🧪 QA | Define API error response spec | P1 |
| 5 | 💰 CFO | Define rate limit policy | P2 |

## ⚠️ Warnings
- ❌ NEVER: Expose sensitive API without auth, Deploy without rate limit
- ✅ ALWAYS: Document API spec (OpenAPI), Maintain error code consistency
"""
        }
    ],

    # Maintenance plan example
    "maintenance": [
        {
            "context": "Landing page theme system maintenance plan. 6 themes + dynamic layout switching feature.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: Discussing maintenance plan for landing page theme system. We have 6 themes + dynamic layout switching. Need to define how to maintain this.

**🛠️ CTO**: Looking at code structure, there are CSS files in themes/ folder and HTML templates in layouts.js. Two main maintenance points. First, CSS variable + Tailwind override consistency when adding/modifying themes. Second, DOM manipulation stability when changing layouts.

**🎨 CDO**: From design perspective, consistency between themes is key. Need a checklist when adding new themes. Color palette, typography, spacing all need to match for brand consistency.

**🧪 QA**: Theme switching test automation is needed. 6 themes × dark mode × 3 viewports = 36 combinations. Can't handle manual testing, need Playwright visual regression tests.

**🔥 ERROR**: I've seen localStorage issues. Theme storage is localStorage but it sometimes gets corrupted. Need initialization logic and fallback. Also fallback to default theme when theme CSS fails to load.

**👔 PM**: Good. Summary - 1) Document theme addition checklist, 2) Automate visual regression tests, 3) localStorage error handling. Maintenance cycle: monthly CDN check, quarterly design review.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🎨 CDO | Write theme addition checklist | P0 |
| 2 | 🛠️ CTO | CSS variable + Tailwind override guide | P1 |
| 3 | 🧪 QA | Set up Playwright visual regression tests | P1 |
| 4 | 🔥 ERROR | Add localStorage fallback logic | P2 |

## ⚠️ Warnings
- ❌ NEVER: Abuse !important in theme CSS, Add themes without checklist
- ✅ ALWAYS: Test all breakpoints for new themes, Specify dark mode support
"""
        }
    ],

    # Error/incident response example
    "error": [
        {
            "context": "Production incident. API response time over 10 seconds, some users timing out. DB query suspected as cause.",
            "output": """## 🏢 C-Level Meeting Notes

**🔥 ERROR**: Emergency. Production API response time over 10 seconds, some users timing out. Dashboard shows DB query time spiked.

**🛠️ CTO**: Checked logs. Full table scan on `users` table is the issue. Yesterday's deploy has `SELECT *` without `WHERE` clause. Not hitting index.

**🔥 ERROR**: Rollback or hotfix?

**🛠️ CTO**: Hotfix is faster. Just add `LIMIT` to query and add index. 5 min fix.

**🧪 QA**: Wait, need to verify query execution plan on staging before deploying hotfix. Run `EXPLAIN ANALYZE` to confirm index is used before deploy.

**👔 PM**: Good. Hotfix route, but verify on staging per QA's point. Postmortem tomorrow. Focus on recovery now.

**🔥 ERROR**: Got it. After recovery I'll do 5 Whys analysis and document prevention measures. Need to add slow query alerts too.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | Hotfix: Add query LIMIT + index | P0 (now) |
| 2 | 🧪 QA | Verify EXPLAIN ANALYZE on staging | P0 (now) |
| 3 | 🔥 ERROR | Set slow query alert (over 1 sec) | P1 |
| 4 | 🔥 ERROR | Write 5 Whys postmortem | P1 (tomorrow) |

## ⚠️ Warnings
- ❌ NEVER: SELECT * without WHERE, Query large tables without index
- ✅ ALWAYS: Verify query execution plan before deploy, Monitor slow queries
"""
        }
    ],

    # Cost-related example
    "cost": [
        {
            "context": "Cloud cost review. AWS costs increased 200% from last month. Need root cause analysis.",
            "output": """## 🏢 C-Level Meeting Notes

**💰 CFO**: Urgent cost issue. AWS costs went from $500 last month to $1,500 this month - 200% increase. Impacts runway, need to identify cause.

**🛠️ CTO**: Checked Cost Explorer. Two causes. First, EC2 instance size went from t3.medium to t3.xlarge. Second, S3 data transfer costs increased 10x.

**💰 CFO**: Why was EC2 size increased?

**🛠️ CTO**: Memory issue last week, temporarily upgraded but forgot to downgrade. Memory leak is fixed so we can go back to t3.medium.

**🔥 ERROR**: I looked at S3 costs - log files are being stored in S3 with no retention policy. They were piling up indefinitely. Just need to add 30-day delete policy.

**💰 CFO**: Got it. These two fixes should get us back to normal. Also need to set AWS Budget alert. Alert when over $600.

**👔 PM**: Good. Summary - 1) EC2 downsize, 2) S3 lifecycle policy, 3) Budget alerts. Complete this week.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | Downsize EC2 t3.xlarge → t3.medium | P0 |
| 2 | 🔥 ERROR | Add S3 lifecycle policy (delete after 30 days) | P0 |
| 3 | 💰 CFO | Set AWS Budget alert ($600) | P1 |
| 4 | 🛠️ CTO | Add cost dashboard to Grafana | P2 |

## ⚠️ Warnings
- ❌ NEVER: Upsize instance and leave it, Store logs without retention
- ✅ ALWAYS: Alert on cost changes, Monthly cost review
"""
        }
    ],

    # Basic feature implementation example
    "feature": [
        {
            "context": "Adding comment feature to board. Support nested replies and likes.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: Comment feature addition. As per PRD section 4.2, includes nested replies + likes. MVP scope, timeline is 1 week.

**🛠️ CTO**: Two options for nested comments structure. Adjacency list (parent_id) vs nested set. Solo dev, small scale, so parent_id is sufficient. Lower query complexity is better.

**🧪 QA**: Thinking about test cases, handling replies when deleting parent comment is important. What happens to children when parent is deleted? Recommend soft delete showing "Comment deleted".

**🛠️ CTO**: QA's point is right. Hard delete breaks reply chain. Add deleted_at column for soft delete.

**🔒 CSO**: XSS filtering on comment input is essential. Escape HTML tags, only allow whitelisted domains for links.

**👔 PM**: Summary - 1) parent_id approach for nested comments, 2) soft delete handling, 3) XSS filtering. Proceeding with this.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | Design comment table schema (parent_id, deleted_at) | P0 |
| 2 | 🛠️ CTO | Implement comment CRUD API | P0 |
| 3 | 🔒 CSO | Apply XSS filtering middleware | P1 |
| 4 | 🧪 QA | Test nested reply/delete scenarios | P1 |

## ⚠️ Warnings
- ❌ NEVER: Hard delete comments, Store input without filtering
- ✅ ALWAYS: Soft delete, Limit comment depth (prevent infinite nesting)
"""
        }
    ],

    # Payment-related example
    "payment": [
        {
            "context": "Implementing subscription payment system. Monthly/annual subscriptions, using Stripe.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: Discussing subscription payment system. Monthly and annual plans, using Stripe. See PRD section 5.1.

**💰 CFO**: Annual subscriptions need discount to improve conversion. Industry standard is 2 months free (16% discount). Also need 3-day grace period for renewal failures.

**🛠️ CTO**: Using Stripe billing with customer portal. Recurring payments via webhooks, retry up to 3 times on failure. Watch DB transactions - don't update subscription status before payment is confirmed.

**🔒 CSO**: Never store card info on our servers. Only store Stripe customer ID. PCI-DSS compliance is mandatory. Payment logs must mask sensitive info.

**🧪 QA**: Need payment simulation in test environment. Stripe has test mode, use that. Need to cover subscription expire/renew/cancel scenarios.

**🔥 ERROR**: Need to prepare for payment gateway outages. Service shouldn't be blocked if payment fails, continue providing service during grace period.

**👔 PM**: Summary - 1) 16% annual discount, 2) Stripe billing + webhooks, 3) 3-day grace period, 4) Mask payment logs. Proceeding in this order.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | Stripe billing integration | P0 |
| 2 | 🛠️ CTO | Implement subscription webhook handler | P0 |
| 3 | 💰 CFO | Document pricing policy (including discounts) | P1 |
| 4 | 🔒 CSO | Define payment log masking policy | P1 |
| 5 | 🧪 QA | Write sandbox test scenarios | P1 |
| 6 | 🔥 ERROR | Grace period logic for gateway outage | P2 |

## ⚠️ Warnings
- ❌ NEVER: Store card info directly, Update subscription status before payment confirmed
- ✅ ALWAYS: Store only billing key, Payment failure retry logic, Webhook idempotency
"""
        }
    ],

    # UI/UX-related example
    "ui": [
        {
            "context": "Dashboard UI redesign. Feedback that current usability is poor. Mobile support needed.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: Dashboard redesign. User feedback includes "too much info", "doesn't work on mobile". Need to simplify to core metrics and add mobile support.

**🎨 CDO**: Current dashboard problem is listing everything without information hierarchy. Show top 3 KPIs prominently, hide rest in tabs or drilldowns. Mobile should be card UI with vertical scroll.

**🛠️ CTO**: Mobile-first approach simplifies code too. Tailwind CSS enables fast responsive implementation. Charts can break on mobile though, recommend Recharts over Chart.js.

**📢 CMO**: From user perspective, first impression of dashboard matters. Bounce rate spikes when loading exceeds 3 seconds. Add skeleton UI to improve perceived speed.

**🧪 QA**: Cross-browser + responsive testing scope is wide. I'll do Playwright screenshot comparison tests for key resolutions (1920, 1440, 1024, 768, 375px).

**👔 PM**: Summary - 1) Simplify to 3 KPIs, 2) Mobile card UI, 3) Skeleton UI, 4) Recharts for charts. CDO, please start with wireframes.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🎨 CDO | Dashboard wireframe (mobile/desktop) | P0 |
| 2 | 🛠️ CTO | Tailwind + Recharts setup | P1 |
| 3 | 🛠️ CTO | Implement skeleton UI component | P1 |
| 4 | 📢 CMO | Select top 3 KPIs | P1 |
| 5 | 🧪 QA | Set up responsive visual regression tests | P2 |

## ⚠️ Warnings
- ❌ NEVER: Information overload, Horizontal scroll on mobile, 3 second loading spinner
- ✅ ALWAYS: Information hierarchy, Mobile first, Skeleton UI, Touch targets 44px+
"""
        }
    ],

    # Launch-related example
    "launch": [
        {
            "context": "Beta launch prep. D-7. Invite code system, 100 user limit.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: Beta launch D-7. Invite code system, 100 user limit. Let's go through the checklist.

**📢 CMO**: Getting 100 users is no problem. 300 on waitlist, gave invite codes to 3 influencers. Launch day plan is Twitter thread + Product Hunt. Landing page seems slow though.

**🛠️ CTO**: I'll check landing page Lighthouse score. Hero image seems uncompressed, converting to WebP will speed it up. Also need to verify auto-scaling for beta traffic.

**🧪 QA**: Main flow E2E tests (signup → core feature → payment) all passed. But there's a dropdown issue on Safari that needs a hotfix.

**🔥 ERROR**: Need to verify launch day monitoring. Sentry is integrated, Slack alerts set up, but need to assign on-call. First 24 hours require fast response.

**💰 CFO**: 100 beta users, no cost concerns. But if word spreads and suddenly 1000 come, server costs can spike. Set a hard limit.

**👔 PM**: Summary - 1) Optimize landing images, 2) Safari hotfix, 3) Assign on-call, 4) Set user hard limit. Complete by Wednesday, final check Thursday.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | Landing page image optimization | P0 |
| 2 | 🧪 QA | Safari dropdown hotfix | P0 |
| 3 | 🔥 ERROR | Finalize launch day on-call schedule | P0 |
| 4 | 💰 CFO | Set beta user hard limit (100) | P1 |
| 5 | 📢 CMO | Prepare Product Hunt posting | P1 |

## ⚠️ Warnings
- ❌ NEVER: Launch without monitoring, Deploy without rollback plan
- ✅ ALWAYS: Feature flag for emergency disable, 24-hour launch standby
"""
        }
    ],

    # Security-related example
    "security": [
        {
            "context": "Security audit results review. OWASP Top 10 check. SQL Injection risk discovered.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: Sharing security audit results. Checked against OWASP Top 10, SQL Injection risk found. CSO, please explain.

**🔒 CSO**: Serious issue. Search API is putting user input directly into raw SQL query. Attacker enters `' OR 1=1 --` and entire DB is compromised. Needs immediate fix.

**🛠️ CTO**: My mistake. Was using ORM but switched to raw query for performance, forgot parameterized query. Will fix today and audit all raw query usage.

**🧪 QA**: There could be other vulnerabilities besides SQL Injection. I'll run OWASP ZAP automated scan. Also need to add security tests to CI to prevent recurrence.

**🔥 ERROR**: Need to check logs for existing attack attempts. I'll search for suspicious query patterns (OR 1=1, UNION SELECT, etc.) in logs.

**🔒 CSO**: Also need to consider WAF (Web Application Firewall). If using Cloudflare, enable managed rules. Otherwise add AWS WAF at minimum.

**👔 PM**: Summary - 1) Fix SQL Injection immediately, 2) Audit all raw queries, 3) Add security scan to CI, 4) Evaluate WAF. CTO, deploy hotfix today.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | Hotfix SQL Injection vulnerability | P0 (now) |
| 2 | 🛠️ CTO | Convert all raw queries → parameterized | P0 |
| 3 | 🔥 ERROR | Analyze logs for attack attempts | P0 |
| 4 | 🧪 QA | OWASP ZAP scan + add to CI | P1 |
| 5 | 🔒 CSO | Evaluate WAF (Cloudflare/AWS) | P1 |

## ⚠️ Warnings
- ❌ NEVER: Insert user input directly in raw SQL, Expose stack traces in error messages
- ✅ ALWAYS: Parameterized queries, ORM first, Input validation, Enable WAF
"""
        }
    ],

    # Performance-related example
    "performance": [
        {
            "context": "API response time degradation. Average response time increased from 2 sec to 5 sec. Need root cause analysis.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: API response time issue. Average went from 2 sec to 5 sec since last week. User complaints coming in, need quick root cause analysis.

**🛠️ CTO**: Checked APM (Application Performance Monitoring) data, bottleneck is in specific query. User table join query isn't hitting index, doing full scan. Broke as user count grew.

**💰 CFO**: 5 sec response means high bounce rate. Checked AWS costs too, RDS CPU over 80% so might need instance upgrade. But if index fixes it, that comes first.

**🧪 QA**: Load test results show response delay starts at 100+ concurrent users. Peak time is around 150 users so that's where it's bottlenecking.

**🔥 ERROR**: Emergency fix could be caching the problem query results. Add Redis with 5 min TTL to significantly reduce DB load. Adding index in production needs caution.

**🛠️ CTO**: Let's do both. 1) Add Redis caching first to put out the fire, 2) Index after staging verification. DB migration should be done in off-hours.

**👔 PM**: Summary - 1) Deploy Redis caching today, 2) Add index tomorrow at 3am, 3) Re-run load tests to verify. CTO, late night for you today.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | Add Redis caching layer (5 min TTL) | P0 (today) |
| 2 | 🛠️ CTO | Add index (after staging verification) | P0 (tomorrow 3am) |
| 3 | 🧪 QA | Re-run load test after caching | P1 |
| 4 | 💰 CFO | Cost estimate for RDS upgrade (backup plan) | P2 |
| 5 | 🔥 ERROR | Adjust APM alert threshold (over 2 sec) | P1 |

## ⚠️ Warnings
- ❌ NEVER: DB migration during peak hours, Data changes without cache invalidation
- ✅ ALWAYS: Slow query logging, EXPLAIN analysis before adding index, Set cache TTL
"""
        }
    ],

    # Design-related example
    "design": [
        {
            "context": "Building design system. Current component styles highly inconsistent. Plan to unify using Figma.",
            "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: Design system build. Currently buttons alone have 5 different styles mixed - no consistency. Need to unify via Figma and reflect in code.

**🎨 CDO**: Right, current state is too fragmented. Need to define design tokens first. Colors, typography, spacing, shadows. Define those, rest is just combinations. Figma Design Token plugin can export to JSON.

**🛠️ CTO**: Need to build pipeline to convert Figma tokens to code. Style Dictionary automates JSON → CSS/JS conversion. Can apply directly to Tailwind config too.

**🧪 QA**: Visual regression testing is essential when applying design system. Tools like Chromatic or Percy for component screenshot comparison prevent accidental breakage.

**📢 CMO**: From brand perspective, color palette needs careful selection. Primary color directly impacts brand recognition. Shouldn't be too similar to competitors, and accessibility (contrast ratio) matters too.

**🎨 CDO**: CMO's point is right. Need to meet WCAG 2.1 AA with 4.5:1 contrast ratio. Also better to consider dark mode from the start.

**👔 PM**: Summary - 1) Define design tokens (color, typo, spacing), 2) Figma → code pipeline, 3) Visual regression tests. CDO, please define tokens first.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🎨 CDO | Define design tokens (Figma) | P0 |
| 2 | 🎨 CDO | Define core components (Button, Input, Card) | P0 |
| 3 | 🛠️ CTO | Build Style Dictionary pipeline | P1 |
| 4 | 🛠️ CTO | Apply Tailwind custom theme | P1 |
| 5 | 🧪 QA | Set up Chromatic visual regression tests | P2 |
| 6 | 📢 CMO | Review brand color guide | P1 |

## ⚠️ Warnings
- ❌ NEVER: Hardcode without tokens, Ignore accessibility contrast, Figma-code mismatch
- ✅ ALWAYS: Centrally manage design tokens, Consider dark mode, Follow WCAG AA
"""
        }
    ]
}


def get_examples_for_topic(topic: str, limit: int = 3) -> List[Dict[str, str]]:
    """Returns examples for a specific topic."""
    examples = EXAMPLES.get(topic, EXAMPLES.get("feature", []))
    return examples[:limit]


def get_all_examples() -> List[Dict[str, str]]:
    """Returns all examples (for tuning dataset)."""
    all_examples = []
    for topic_examples in EXAMPLES.values():
        all_examples.extend(topic_examples)
    return all_examples


def format_examples_for_prompt(topic: str, limit: int = 2) -> str:
    """Generates example string for inclusion in prompt."""
    examples = get_examples_for_topic(topic, limit)

    if not examples:
        return ""

    lines = ["## Examples\n"]
    for i, ex in enumerate(examples, 1):
        lines.append(f"### Example {i}")
        lines.append(f"**Context**: {ex['context']}")
        lines.append(f"\n**Meeting Notes**:\n{ex['output']}")
        lines.append("\n---\n")

    return "\n".join(lines)
