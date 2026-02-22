# -*- coding: utf-8 -*-
"""License/trial/upgrade formatters.

Extracted from tool_dispatch.py _wrap_activate_license, _wrap_license_status,
_wrap_start_trial, _upgrade_pro.
"""


def format_activate_license_no_key() -> str:
    return """
# ❌ Please enter license key

## Usage
```
license_status(action="activate", license_key="YOUR-KEY")
```

Or start a free trial: `license_status(action="trial")`
"""


def format_activate_license_success(result: dict) -> str:
    tier_info = result.get("tier_info", {})
    machine_id = result.get("machine_id", "unknown")
    product = result.get("product", "Clouvel Pro")

    extra_info = ""
    if result.get("test_license"):
        expires_at = result.get("expires_at", "")
        expires_in_days = result.get("expires_in_days", 7)
        extra_info = f"""
## ⚠️ Test License
- **Expires**: {expires_at}
- **Days remaining**: {expires_in_days}
"""

    return f"""
# ✅ License Activated

## Info
- **Tier**: {tier_info.get('name', 'Unknown')}
- **Product**: {product}
- **Machine**: `{machine_id[:8]}...`
{extra_info}
## 🔒 Machine Binding

This license is bound to the current machine.
- Personal: Can only be used on 1 machine
- Team: Can be used on up to 10 machines
- Enterprise: Unlimited machines

To use on another machine, deactivate the existing machine or upgrade to a higher tier.
"""


def format_activate_license_failure(result: dict) -> str:
    return f"""
# ❌ License Activation Failed

{result.get('message', 'Unknown error')}

## Checklist
- Verify license key is correct
- Check network connection
- Check activation limit (Personal: 1)

Need a key? `license_status(action="upgrade")`
"""


def format_license_status_none(result: dict) -> str:
    return f"""
# License Status

**Status**: Not activated

{result.get('message', '')}

## Quick Actions
- **Free trial**: `license_status(action="trial")` — 7 days, no credit card
- **Activate key**: `license_status(action="activate", license_key="YOUR-KEY")`
- **Pricing**: `license_status(action="upgrade")`
"""


def format_license_status_active(result: dict) -> str:
    tier_info = result.get("tier_info", {})
    machine_id = result.get("machine_id", "unknown")
    activated_at = result.get("activated_at", "N/A")
    days = result.get("days_since_activation", 0)
    premium_unlocked = result.get("premium_unlocked", False)
    remaining = result.get("premium_unlock_remaining", 0)
    unlock_status = "Unlocked" if premium_unlocked else f"{remaining} days remaining"

    return f"""
# License Status

**Status**: Active

## Info
- **Tier**: {tier_info.get('name', 'Unknown')} ({tier_info.get('price', '?')})
- **Machine**: `{machine_id[:8]}...`
- **Activated at**: {activated_at[:19] if len(activated_at) > 19 else activated_at}
- **Days since activation**: {days}
- **Premium features**: {unlock_status}
"""


def format_trial_already_licensed() -> str:
    return """
# Pro Trial

You already have an active Pro license. No trial needed!

Use `license_status` to check your current plan.
"""


def format_trial_active(remaining: int) -> str:
    return f"""
# Pro Trial Active

**{remaining} day(s) remaining** | All Pro features unlocked

Included:
- 8 C-Level AI managers (PM, CTO, QA, CDO, CMO, CFO, CSO, ERROR)
- Knowledge Base (decisions preserved across sessions)
- BLOCK mode (enforced spec-first)
- ship (lint -> test -> build -> evidence)
- Unlimited projects

Like it? Keep it:
- Monthly: **$7.99/mo**
- Annual: **$49/yr** (Early Adopter Pricing)

→ `license_status(action="upgrade")`
"""


def format_trial_expired() -> str:
    return """
# Pro Trial Expired

Your 7-day trial has ended.

- Monthly: **$7.99/mo**
- Annual: **$49/yr** (Early Adopter Pricing)

→ `license_status(action="upgrade")`
"""


def format_trial_started(remaining: int) -> str:
    return f"""
# Pro Trial Started!

**{remaining} days of full Pro access** - no credit card required.

You now have:
- 8 C-Level AI managers (PM, CTO, QA, CDO, CMO, CFO, CSO, ERROR)
- Knowledge Base (decisions preserved across sessions)
- BLOCK mode (enforced spec-first coding)
- ship (one-click lint -> test -> build -> evidence)
- Unlimited projects
- All Pro templates (standard + detailed)

## Try these first
1. `manager(context="your current task")` - get 8-manager review
2. `record_decision(category="architecture", decision="...")` - save a decision
3. `ship(path=".")` - run full verification

## After trial
- Monthly: **$7.99/mo**
- Annual: **$49/yr** (Early Adopter Pricing)
→ `license_status(action="upgrade")`
"""


def format_upgrade_pro() -> str:
    return """
# Clouvel Pro

10 more tools that make Claude Code reliable.

## What You Get

| Tool | What it does |
|------|-------------|
| `error_learn` | Auto-generate NEVER/ALWAYS rules from error patterns |
| `memory_status` | Error memory dashboard with hit counts |
| `memory_search` | Search past errors by keyword |
| `memory_global_search` | Share error patterns across all projects |
| `drift_check` | Detect when work drifts from goals |
| `plan` | Detailed execution plans with dependencies |
| `meeting` | Full 8-manager C-Level review |
| `ship` | One-click lint+test+build with evidence |
| `record_decision` | Persistent knowledge base for decisions |
| `search_knowledge` | Search past decisions and context |

## Also Unlocked
- Full error history (not just last 5)
- 50 checkpoint slots (not 1)
- 4 managers + 2 questions each (not 2+1)

## Pricing

| Plan | Price |
|------|-------|
| Monthly | **$7.99/mo** |
| Annual | **$49/yr** (Early Adopter Pricing) |

## Purchase

https://polar.sh/clouvel

Or start a free 7-day trial first: `license_status(action="trial")`
"""
