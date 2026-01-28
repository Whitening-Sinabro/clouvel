# -*- coding: utf-8 -*-
"""Meeting Data (Standalone)

Minimal persona and example data for meeting functionality.
Used when manager module is not available (PyPI Free version).

This is a subset of manager/prompts data for the meeting system.
"""

from typing import Dict, List, Any

# Minimal PERSONAS for meeting simulation
PERSONAS: Dict[str, Dict[str, Any]] = {
    "PM": {
        "emoji": "👔",
        "title": "Product Manager",
        "years": 18,
        "communication": {
            "tone": "Direct, conclusion first, speaks in numbers",
            "pet_phrases": ["So what's the user benefit?", "Is it in the PRD?"]
        },
        "probing_questions": {
            "scope": ["Is this MVP scope or post-launch?", "What's the ONE thing this feature must do?"],
            "user_value": ["Who specifically uses this?", "What problem does this solve?"],
        }
    },
    "CTO": {
        "emoji": "🛠️",
        "title": "Chief Technology Officer",
        "years": 20,
        "communication": {
            "tone": "Technical but explains for non-devs",
            "pet_phrases": ["That'll blow up later", "Did you think about scale?"]
        },
        "probing_questions": {
            "architecture": ["What happens when you have 10x users? 100x?", "Where will this break first under load?"],
            "tradeoffs": ["What are you trading off for this approach?", "Build vs buy - have you looked at existing solutions?"],
        }
    },
    "QA": {
        "emoji": "🧪",
        "title": "Quality Assurance Lead",
        "years": 16,
        "communication": {
            "tone": "Specific, scenario-based, asks many questions",
            "pet_phrases": ["Did you test that?", "Think about edge cases"]
        },
        "probing_questions": {
            "edge_cases": ["What happens with empty input? Null? Special characters?", "What if the user clicks the button 100 times fast?"],
            "failure_scenarios": ["What if this fails? Does the user see an error?", "What's the retry logic?"],
        }
    },
    "CSO": {
        "emoji": "🔒",
        "title": "Chief Security Officer",
        "years": 17,
        "communication": {
            "tone": "Warning-focused but offers alternatives",
            "pet_phrases": ["What if that gets pwned?", "Auth is missing here"]
        },
        "probing_questions": {
            "attack_surface": ["What's the worst thing an attacker could do with this?", "What data could leak if this endpoint is compromised?"],
            "auth_authz": ["How do you verify the user is who they claim?", "How do you verify they're allowed to do this action?"],
        }
    },
    "CFO": {
        "emoji": "💰",
        "title": "Chief Financial Officer",
        "years": 19,
        "communication": {
            "tone": "Numbers-based, direct, realistic",
            "pet_phrases": ["How much does that cost?", "How many months of runway?"]
        },
        "probing_questions": {
            "cost_awareness": ["What's the monthly cost of running this?", "What happens to cost if you 10x users?"],
            "revenue": ["How does this feature drive revenue?", "What's the payback period?"],
        }
    },
    "CMO": {
        "emoji": "📢",
        "title": "Chief Marketing Officer",
        "years": 15,
        "communication": {
            "tone": "Storytelling, user perspective",
            "pet_phrases": ["How do we communicate this?", "What's the hook?"]
        },
        "probing_questions": {
            "target_audience": ["Who are the first 100 users?", "Why would they tell their friends?"],
            "distribution": ["Where do these users hang out?", "What's the acquisition cost?"],
        }
    },
    "CDO": {
        "emoji": "🎨",
        "title": "Chief Design Officer",
        "years": 14,
        "communication": {
            "tone": "Visual thinking, UX-focused",
            "pet_phrases": ["Show me the user flow", "Is this intuitive?"]
        },
        "probing_questions": {
            "user_journey": ["What's the user's mental model here?", "What do they expect to happen?"],
            "visual_hierarchy": ["What's the most important thing on this screen?", "What do you want users to notice first?"],
        }
    },
    "ERROR": {
        "emoji": "🔥",
        "title": "Error & Risk Manager",
        "years": 12,
        "communication": {
            "tone": "Worst-case focused, practical",
            "pet_phrases": ["What if this fails?", "Do we have a rollback plan?"]
        },
        "probing_questions": {
            "failure_scenarios": ["What happens when this fails at 3am?", "Who gets paged?"],
            "recovery": ["How do we rollback if this goes wrong?", "What's the blast radius?"],
        }
    },
}


def get_persona(manager_key: str) -> Dict[str, Any]:
    """Get persona by manager key."""
    return PERSONAS.get(manager_key, {})


# Topic guides for manager selection
TOPIC_GUIDES: Dict[str, Dict[str, Any]] = {
    "auth": {"participants": ["PM", "CTO", "QA", "CSO", "ERROR"]},
    "api": {"participants": ["PM", "CTO", "QA", "CSO", "CFO"]},
    "payment": {"participants": ["PM", "CTO", "QA", "CSO", "CFO"]},
    "ui": {"participants": ["PM", "CTO", "QA", "CDO"]},
    "feature": {"participants": ["PM", "CTO", "QA"]},
    "launch": {"participants": ["PM", "CTO", "QA", "CMO", "CFO"]},
    "error": {"participants": ["PM", "CTO", "QA", "ERROR"]},
    "security": {"participants": ["PM", "CTO", "CSO", "ERROR"]},
    "performance": {"participants": ["PM", "CTO", "QA", "CFO"]},
    "design": {"participants": ["PM", "CDO", "QA"]},
    "cost": {"participants": ["PM", "CTO", "CFO"]},
    "maintenance": {"participants": ["PM", "CTO", "QA", "ERROR"]},
}


def get_topic_guide(topic: str) -> Dict[str, Any]:
    """Get topic guide."""
    return TOPIC_GUIDES.get(topic, {"participants": ["PM", "CTO", "QA"]})


# Example outputs for few-shot learning
EXAMPLES: Dict[str, List[Dict[str, str]]] = {
    "auth": [{
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
    }],
    "payment": [{
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
    }],
    "launch": [{
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
    }],
    "feature": [{
        "context": "Adding comment feature to board. Support nested replies and likes.",
        "output": """## 🏢 C-Level Meeting Notes

**👔 PM**: Adding comment feature. Basic structure is flat comments + nested replies + likes. Timeline is 1 week.

**🛠️ CTO**: For nested replies, I recommend max 2 levels. Infinite depth creates UI/DB complexity. likes - use counter cache, real-time aggregation is expensive.

**🧪 QA**: I'll write edge case tests. Empty comment, 10K character comment, XSS patterns, concurrent likes on same comment. These need coverage.

**👔 PM**: Limit comment length to 1000 chars. 10K is unnecessary.

**🛠️ CTO**: Agreed. Also consider soft delete for comments. Hard delete leaves orphan replies.

**👔 PM**: Summary - 1) Max 2 level nesting, 2) Like counter cache, 3) 1000 char limit, 4) Soft delete. Start today.

---

## 📋 Action Items

| # | Owner | Task | Priority |
|---|-------|------|----------|
| 1 | 🛠️ CTO | Comment DB schema (with soft delete) | P0 |
| 2 | 🛠️ CTO | Nested reply logic (max 2 levels) | P0 |
| 3 | 🛠️ CTO | Like counter cache implementation | P1 |
| 4 | 🧪 QA | Write edge case tests | P1 |

## ⚠️ Warnings
- ❌ NEVER: Allow unlimited nesting, Hard delete comments with replies
- ✅ ALWAYS: Sanitize user input, Rate limit comment creation
"""
    }],
}


def get_examples_for_topic(topic: str, limit: int = 1) -> List[Dict[str, str]]:
    """Get example meeting outputs for a topic."""
    examples = EXAMPLES.get(topic, EXAMPLES.get("feature", []))
    return examples[:limit]


def format_examples_for_prompt(examples: List[Dict[str, str]]) -> str:
    """Format examples for prompt."""
    if not examples:
        return ""

    parts = []
    for ex in examples:
        parts.append(f"**Context**: {ex['context']}\n\n{ex['output']}")
    return "\n\n---\n\n".join(parts)


# Topic keywords for auto-detection
TOPIC_KEYWORDS: Dict[str, List[str]] = {
    "auth": ["login", "logout", "password", "oauth", "jwt", "token", "session", "authentication", "authorization"],
    "api": ["api", "endpoint", "rest", "graphql", "request", "response", "crud", "http"],
    "payment": ["payment", "stripe", "billing", "subscription", "checkout", "price", "invoice"],
    "ui": ["ui", "ux", "design", "button", "form", "modal", "layout", "css", "component"],
    "feature": ["feature", "implement", "add", "build", "create", "develop"],
    "launch": ["launch", "release", "deploy", "beta", "production", "go-live"],
    "error": ["error", "bug", "fix", "incident", "crash", "issue", "debug"],
    "security": ["security", "vulnerability", "hack", "attack", "encrypt", "ssl", "https"],
    "performance": ["performance", "slow", "optimize", "cache", "speed", "latency"],
    "design": ["design", "mockup", "wireframe", "prototype", "figma", "sketch"],
    "cost": ["cost", "budget", "expense", "aws", "cloud", "pricing"],
    "maintenance": ["maintenance", "refactor", "cleanup", "update", "upgrade", "migration"],
}


def analyze_context(context: str) -> List[str]:
    """Analyze context to detect topics."""
    context_lower = context.lower()
    detected = []

    for topic, keywords in TOPIC_KEYWORDS.items():
        for keyword in keywords:
            if keyword in context_lower:
                if topic not in detected:
                    detected.append(topic)
                break

    return detected if detected else ["feature"]
