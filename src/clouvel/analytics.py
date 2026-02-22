"""
Clouvel Analytics - 도구 사용량 로컬 추적

저장 위치: .clouvel/analytics.json (프로젝트 로컬)
개인정보 없음, 순수 사용량 통계만 기록
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional


def get_analytics_path(project_path: Optional[str] = None) -> Path:
    """analytics.json 경로 반환"""
    if project_path:
        base = Path(project_path)
    else:
        base = Path.cwd()

    clouvel_dir = base / ".clouvel"
    clouvel_dir.mkdir(parents=True, exist_ok=True)
    return clouvel_dir / "analytics.json"


def load_analytics(project_path: Optional[str] = None) -> dict:
    """analytics 데이터 로드"""
    path = get_analytics_path(project_path)
    if path.exists():
        try:
            return json.loads(path.read_text(encoding='utf-8'))
        except (json.JSONDecodeError, IOError):
            return {"events": [], "version": "1.0"}
    return {"events": [], "version": "1.0"}


def save_analytics(data: dict, project_path: Optional[str] = None) -> None:
    """analytics 데이터 저장"""
    path = get_analytics_path(project_path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')


def log_tool_call(tool_name: str, success: bool = True, project_path: Optional[str] = None) -> None:
    """도구 호출 기록"""
    data = load_analytics(project_path)

    event = {
        "tool": tool_name,
        "ts": datetime.now().isoformat(),
        "success": success
    }

    data["events"].append(event)

    # 최근 1000개만 유지 (메모리 관리)
    if len(data["events"]) > 1000:
        data["events"] = data["events"][-1000:]

    save_analytics(data, project_path)


def get_stats(project_path: Optional[str] = None, days: int = 30) -> dict:
    """사용량 통계 반환"""
    data = load_analytics(project_path)
    events = data.get("events", [])

    if not events:
        return {
            "total_calls": 0,
            "by_tool": {},
            "by_date": {},
            "success_rate": 0,
            "period_days": days
        }

    # 기간 필터
    cutoff = datetime.now() - timedelta(days=days)
    filtered = []
    for e in events:
        try:
            ts = datetime.fromisoformat(e["ts"])
            if ts >= cutoff:
                filtered.append(e)
        except (KeyError, ValueError):
            continue

    # 도구별 집계
    by_tool = {}
    by_date = {}
    success_count = 0

    for e in filtered:
        tool = e.get("tool", "unknown")
        by_tool[tool] = by_tool.get(tool, 0) + 1

        try:
            date = datetime.fromisoformat(e["ts"]).strftime("%Y-%m-%d")
            by_date[date] = by_date.get(date, 0) + 1
        except (KeyError, ValueError):
            pass

        if e.get("success", True):
            success_count += 1

    total = len(filtered)

    return {
        "total_calls": total,
        "by_tool": dict(sorted(by_tool.items(), key=lambda x: x[1], reverse=True)),
        "by_date": dict(sorted(by_date.items())),
        "success_rate": round(success_count / total * 100, 1) if total > 0 else 0,
        "period_days": days
    }


def log_event(event_type: str, metadata: dict = None) -> None:
    """Log a conversion/upsell event to ~/.clouvel/events.jsonl.

    Event types:
    - project_limit_hit: User hit project limit
    - kb_write_blocked: KB trial expired, write blocked
    - upgrade_message_shown: Pro upgrade message displayed
    - warn_accumulated: WARN count reached threshold
    - weekly_meeting_used: Weekly full meeting trial used
    """
    import os

    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()

    events_file = base / ".clouvel" / "events.jsonl"
    events_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "type": event_type,
        "ts": datetime.now().isoformat(),
        "metadata": metadata or {},
    }

    try:
        with open(events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except Exception:
        pass


def format_stats(stats: dict) -> str:
    """통계를 읽기 좋은 문자열로 변환"""
    lines = [
        f"# Clouvel 사용량 통계 (최근 {stats['period_days']}일)",
        "",
        "## 요약",
        f"- 총 호출: {stats['total_calls']}회",
        f"- 성공률: {stats['success_rate']}%",
        "",
    ]

    if stats["by_tool"]:
        lines.append("## 도구별 사용량")
        lines.append("")
        lines.append("| 도구 | 횟수 | 비율 |")
        lines.append("|------|------|------|")
        total = stats["total_calls"]
        for tool, count in stats["by_tool"].items():
            pct = round(count / total * 100, 1) if total > 0 else 0
            lines.append(f"| {tool} | {count} | {pct}% |")
        lines.append("")

    if stats["by_date"]:
        lines.append("## 일별 사용량")
        lines.append("")
        # 최근 7일만 표시
        recent_dates = list(stats["by_date"].items())[-7:]
        for date, count in recent_dates:
            bar = "█" * min(count, 20)
            lines.append(f"- {date}: {bar} {count}")
        lines.append("")

    if stats["total_calls"] == 0:
        lines.append("아직 기록된 사용량이 없습니다.")

    return "\n".join(lines)


# ============================================================
# A/B Testing Analytics (v3.3 - Week 3)
# ============================================================

def get_ab_events(days: int = 7) -> list:
    """Get A/B test events from ~/.clouvel/events.jsonl.

    Filters for events with 'ab_' prefix or experiment-related events.
    """
    import os

    if os.name == 'nt':
        base = Path(os.environ.get('USERPROFILE', '~'))
    else:
        base = Path.home()

    events_file = base / ".clouvel" / "events.jsonl"
    if not events_file.exists():
        return []

    cutoff = datetime.now() - timedelta(days=days)
    events = []

    try:
        with open(events_file, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    ts = datetime.fromisoformat(event.get("ts", "2000-01-01"))
                    if ts >= cutoff:
                        event_type = event.get("type", "")
                        # Include A/B events and conversion events
                        if event_type.startswith("ab_") or event_type in [
                            "experiment_assigned",
                            "project_limit_hit",
                            "kb_write_blocked",
                            "upgrade_message_shown",
                            "warn_accumulated",
                            "weekly_meeting_used",
                            "pro_conversion",
                        ]:
                            events.append(event)
                except (json.JSONDecodeError, ValueError):
                    continue
    except Exception:
        pass

    return events


def analyze_ab_experiment(experiment_name: str, days: int = 7) -> dict:
    """Analyze A/B test results for a specific experiment.

    Returns:
        {
            "experiment": "project_limit",
            "variants": {
                "control": {"users": 45, "conversions": 1, "rate": 2.2},
                "variant_a": {"users": 42, "conversions": 3, "rate": 7.1},
            },
            "uplift": 223.2,  # % improvement over control
            "winner": "variant_a",
            "confidence": "low",  # low/medium/high based on sample size
            "total_events": 156,
        }
    """
    events = get_ab_events(days)

    # Group by variant
    variant_data = {}
    conversions = {}

    for event in events:
        metadata = event.get("metadata", {})
        if metadata.get("experiment") == experiment_name:
            variant = metadata.get("variant", "unknown")
            event_type = event.get("type", "")

            if variant not in variant_data:
                variant_data[variant] = {"impressions": 0, "conversions": 0}
                conversions[variant] = set()

            # Count impressions (any touchpoint)
            if event_type.startswith("ab_"):
                variant_data[variant]["impressions"] += 1

            # Count conversions
            if event_type in ["ab_pro_conversion", "pro_conversion"]:
                user_id = metadata.get("user_id_hash", str(hash(event.get("ts", ""))))
                conversions[variant].add(user_id)

    # Calculate metrics
    results = {
        "experiment": experiment_name,
        "variants": {},
        "days": days,
        "total_events": len(events),
    }

    control_rate = 0
    best_variant = None
    best_rate = 0

    for variant, data in variant_data.items():
        impressions = data["impressions"]
        unique_conversions = len(conversions.get(variant, set()))
        rate = (unique_conversions / impressions * 100) if impressions > 0 else 0

        results["variants"][variant] = {
            "impressions": impressions,
            "conversions": unique_conversions,
            "rate": round(rate, 2),
        }

        if variant == "control":
            control_rate = rate
        if rate > best_rate:
            best_rate = rate
            best_variant = variant

    # Calculate uplift vs control
    if control_rate > 0 and best_variant != "control":
        results["uplift"] = round((best_rate - control_rate) / control_rate * 100, 1)
    else:
        results["uplift"] = 0

    results["winner"] = best_variant

    # Confidence based on sample size
    total_impressions = sum(v.get("impressions", 0) for v in results["variants"].values())
    if total_impressions >= 1000:
        results["confidence"] = "high"
    elif total_impressions >= 100:
        results["confidence"] = "medium"
    else:
        results["confidence"] = "low"

    return results


def get_ab_report(days: int = 7) -> dict:
    """Get comprehensive A/B testing report for all experiments.

    Returns a report with all experiments, their status, and recommendations.
    """
    from .licensing.experiments import EXPERIMENTS

    report = {
        "generated_at": datetime.now().isoformat(),
        "period_days": days,
        "experiments": {},
        "summary": {
            "total_experiments": len(EXPERIMENTS),
            "active_experiments": 0,
            "winning_variants": [],
        },
    }

    for exp_name, config in EXPERIMENTS.items():
        analysis = analyze_ab_experiment(exp_name, days)
        rollout = config.get("rollout_percent", 100)

        exp_report = {
            "description": config.get("description", ""),
            "rollout_percent": rollout,
            "started_at": config.get("started_at", "unknown"),
            "analysis": analysis,
            "status": "active" if rollout > 0 else "paused",
            "recommendation": "",
        }

        # Generate recommendation
        if analysis["confidence"] == "low":
            exp_report["recommendation"] = "Collect more data (need 100+ impressions)"
        elif analysis["uplift"] > 20 and analysis["confidence"] in ["medium", "high"]:
            winner = analysis.get("winner", "unknown")
            exp_report["recommendation"] = f"Consider promoting {winner} to 100%"
            report["summary"]["winning_variants"].append(f"{exp_name}:{winner}")
        elif analysis["uplift"] < -10:
            exp_report["recommendation"] = "Variant underperforming - consider stopping"
        else:
            exp_report["recommendation"] = "Continue monitoring"

        if rollout > 0:
            report["summary"]["active_experiments"] += 1

        report["experiments"][exp_name] = exp_report

    return report


def format_ab_report(report: dict) -> str:
    """Format A/B test report as readable markdown."""
    lines = [
        "# A/B Testing Report",
        f"Generated: {report['generated_at'][:19]}",
        f"Period: Last {report['period_days']} days",
        "",
        "## Summary",
        f"- Active experiments: {report['summary']['active_experiments']}/{report['summary']['total_experiments']}",
    ]

    if report["summary"]["winning_variants"]:
        lines.append(f"- Winning variants: {', '.join(report['summary']['winning_variants'])}")
    lines.append("")

    for exp_name, exp_data in report["experiments"].items():
        lines.append(f"## {exp_name}")
        lines.append(f"**{exp_data['description']}**")
        lines.append(f"- Status: {exp_data['status']} ({exp_data['rollout_percent']}% rollout)")
        lines.append(f"- Started: {exp_data['started_at']}")
        lines.append("")

        analysis = exp_data["analysis"]
        if analysis["variants"]:
            lines.append("| Variant | Impressions | Conversions | Rate |")
            lines.append("|---------|-------------|-------------|------|")
            for variant, data in analysis["variants"].items():
                winner_mark = " *" if variant == analysis.get("winner") else ""
                lines.append(
                    f"| {variant}{winner_mark} | {data['impressions']} | "
                    f"{data['conversions']} | {data['rate']}% |"
                )
            lines.append("")

            if analysis["uplift"] != 0:
                lines.append(f"**Uplift vs control:** {analysis['uplift']:+.1f}%")
            lines.append(f"**Confidence:** {analysis['confidence']}")
            lines.append(f"**Recommendation:** {exp_data['recommendation']}")
        else:
            lines.append("_No data collected yet_")
        lines.append("")

    return "\n".join(lines)


# ============================================================
# Week 4: Optimization & KPI Dashboard (v3.3)
# ============================================================

def decide_experiment_winner(experiment_name: str, min_confidence: str = "medium") -> dict:
    """Automatically decide winner based on analysis.

    Args:
        experiment_name: Name of the experiment
        min_confidence: Minimum confidence level required ("low", "medium", "high")

    Returns:
        {
            "decision": "promote" | "continue" | "stop",
            "winner": "variant_a",
            "reason": "...",
            "ready_for_rollout": True/False
        }
    """
    analysis = analyze_ab_experiment(experiment_name, days=14)

    confidence_order = ["low", "medium", "high"]
    current_confidence = analysis.get("confidence", "low")
    min_idx = confidence_order.index(min_confidence)
    current_idx = confidence_order.index(current_confidence)

    result = {
        "experiment": experiment_name,
        "analysis": analysis,
        "decision": "continue",
        "winner": None,
        "reason": "",
        "ready_for_rollout": False,
    }

    # Not enough data
    if current_idx < min_idx:
        result["reason"] = f"Need more data (current: {current_confidence}, required: {min_confidence})"
        return result

    # Check uplift
    uplift = analysis.get("uplift", 0)
    winner = analysis.get("winner")

    if uplift > 20:
        result["decision"] = "promote"
        result["winner"] = winner
        result["reason"] = f"Variant {winner} shows +{uplift}% uplift with {current_confidence} confidence"
        result["ready_for_rollout"] = True
    elif uplift < -10:
        result["decision"] = "stop"
        result["reason"] = f"Experiment underperforming ({uplift}% vs control)"
    else:
        result["decision"] = "continue"
        result["reason"] = f"Results not significant enough (uplift: {uplift}%)"

    return result


def get_conversion_funnel(days: int = 30, exclude_pro: bool = True) -> dict:
    """Get conversion funnel metrics.

    Funnel stages:
    1. First touch (start, can_code)
    2. Engagement (meeting, manager)
    3. Limit hit (project_limit, meeting_quota, kb_blocked)
    4. Upgrade prompt shown
    5. Pro conversion

    Args:
        days: Number of days to look back
        exclude_pro: If True, exclude Pro/developer/trial users from funnel
                     to avoid data contamination (default: True)
    """
    events = get_ab_events(days)

    # v5.1: Collect Pro user hashes to exclude from funnel
    pro_user_hashes = set()
    if exclude_pro:
        for event in events:
            metadata = event.get("metadata", {})
            license_tier = metadata.get("license_tier", "")
            if license_tier in ("pro", "developer", "trial"):
                user_hash = metadata.get("user_id_hash", "")
                if user_hash:
                    pro_user_hashes.add(user_hash)

    # Count unique users at each stage
    stages = {
        "first_touch": set(),
        "engaged": set(),
        "limit_hit": set(),
        "upgrade_shown": set(),
        "converted": set(),
    }

    # v5.1: Separate tier tracking for breakdown
    tier_breakdown = {"free": set(), "pro": set(), "first": set(), "additional": set()}

    for event in events:
        event_type = event.get("type", "")
        metadata = event.get("metadata", {})
        user_hash = metadata.get("user_id_hash", "")

        if not user_hash:
            continue

        # v5.1: Skip Pro-equivalent users if exclude_pro
        if exclude_pro and user_hash in pro_user_hashes:
            tier_breakdown["pro"].add(user_hash)
            continue

        # v5.1: Track project tier
        project_tier = metadata.get("project_tier", "")
        if project_tier == "first":
            tier_breakdown["first"].add(user_hash)
        elif project_tier == "additional":
            tier_breakdown["additional"].add(user_hash)
        else:
            tier_breakdown["free"].add(user_hash)

        # Stage 1: First touch
        if event_type in ["experiment_assigned"]:
            stages["first_touch"].add(user_hash)

        # Stage 2: Engagement
        if event_type.startswith("ab_") and "meeting" in event_type.lower():
            stages["engaged"].add(user_hash)

        # Stage 3: Limit hit
        if event_type in ["project_limit_hit", "ab_limit_hit", "ab_quota_exhausted"]:
            stages["limit_hit"].add(user_hash)

        # Stage 4: Upgrade prompt shown
        if event_type in ["upgrade_message_shown", "ab_upgrade_prompt_shown"]:
            stages["upgrade_shown"].add(user_hash)

        # Stage 5: Conversion
        if event_type in ["pro_conversion", "ab_pro_conversion"]:
            stages["converted"].add(user_hash)

    # Calculate funnel metrics
    funnel = {
        "period_days": days,
        "stages": {},
        "overall_conversion": 0,
        "excluded_pro_users": len(pro_user_hashes),
    }

    stage_names = ["first_touch", "engaged", "limit_hit", "upgrade_shown", "converted"]
    prev_count = None

    for stage in stage_names:
        count = len(stages[stage])
        drop_rate = 0
        if prev_count and prev_count > 0:
            drop_rate = round((1 - count / prev_count) * 100, 1)

        funnel["stages"][stage] = {
            "users": count,
            "drop_rate": drop_rate,
        }
        prev_count = count if count > 0 else prev_count

    # Overall conversion rate
    first_touch = len(stages["first_touch"])
    converted = len(stages["converted"])
    if first_touch > 0:
        funnel["overall_conversion"] = round(converted / first_touch * 100, 2)

    # v5.1: Tier breakdown
    funnel["tier_breakdown"] = {
        k: len(v) for k, v in tier_breakdown.items()
    }

    return funnel


def get_monthly_kpis(days: int = 30) -> dict:
    """Get monthly KPI dashboard metrics.

    KPIs tracked:
    - Conversion rate (Free -> Pro)
    - Pain point effectiveness
    - Meeting trial conversion
    - Retention D7/D14/D30
    """
    funnel = get_conversion_funnel(days)
    events = get_ab_events(days)

    # Calculate KPIs
    kpis = {
        "period_days": days,
        "generated_at": datetime.now().isoformat(),
        "metrics": {},
    }

    # 1. Overall conversion rate
    kpis["metrics"]["conversion_rate"] = {
        "value": funnel["overall_conversion"],
        "target": 5.0,
        "unit": "%",
        "status": "on_track" if funnel["overall_conversion"] >= 5 else "needs_attention",
    }

    # v5.1: Add tier breakdown from funnel
    if "tier_breakdown" in funnel:
        kpis["metrics"]["tier_breakdown"] = {
            "value": funnel["tier_breakdown"],
            "unit": "users",
            "status": "info",
        }

    # v5.1: Track excluded Pro users
    if "excluded_pro_users" in funnel:
        kpis["metrics"]["excluded_pro_users"] = {
            "value": funnel["excluded_pro_users"],
            "unit": "users",
            "status": "info",
        }

    # 2. Pain point effectiveness (conversions within 24h of limit hit)
    limit_events = [e for e in events if e.get("type") in ["project_limit_hit", "ab_limit_hit", "ab_quota_exhausted"]]
    conversion_events = [e for e in events if e.get("type") in ["pro_conversion", "ab_pro_conversion"]]

    pain_point_conversions = 0
    for limit_event in limit_events:
        limit_ts = datetime.fromisoformat(limit_event.get("ts", "2000-01-01"))
        for conv_event in conversion_events:
            conv_ts = datetime.fromisoformat(conv_event.get("ts", "2000-01-01"))
            if 0 < (conv_ts - limit_ts).total_seconds() < 86400:  # 24 hours
                pain_point_conversions += 1
                break

    pain_point_rate = (pain_point_conversions / len(limit_events) * 100) if limit_events else 0

    kpis["metrics"]["pain_point_effectiveness"] = {
        "value": round(pain_point_rate, 1),
        "target": 10.0,
        "unit": "%",
        "status": "on_track" if pain_point_rate >= 10 else "needs_attention",
    }

    # 3. Funnel drop rates
    kpis["metrics"]["funnel_drop_rates"] = {
        "value": funnel["stages"],
        "target": "< 50% at each stage",
        "unit": "stages",
        "status": "on_track",
    }

    # 4. Total events (activity indicator)
    kpis["metrics"]["total_events"] = {
        "value": len(events),
        "target": 100,
        "unit": "events",
        "status": "on_track" if len(events) >= 100 else "needs_attention",
    }

    return kpis


def format_monthly_report(kpis: dict) -> str:
    """Format monthly KPI report as markdown."""
    lines = [
        "# Monthly Conversion Report",
        f"Generated: {kpis['generated_at'][:19]}",
        f"Period: Last {kpis['period_days']} days",
        "",
        "## Key Metrics",
        "",
        "| Metric | Value | Target | Status |",
        "|--------|-------|--------|--------|",
    ]

    metrics = kpis.get("metrics", {})

    # Conversion rate
    cr = metrics.get("conversion_rate", {})
    status_icon = "[OK]" if cr.get("status") == "on_track" else "[!!]"
    lines.append(f"| Conversion Rate | {cr.get('value', 0)}% | {cr.get('target', 0)}% | {status_icon} |")

    # Pain point effectiveness
    pp = metrics.get("pain_point_effectiveness", {})
    status_icon = "[OK]" if pp.get("status") == "on_track" else "[!!]"
    lines.append(f"| Pain Point Conversion | {pp.get('value', 0)}% | {pp.get('target', 0)}% | {status_icon} |")

    # Total events
    te = metrics.get("total_events", {})
    status_icon = "[OK]" if te.get("status") == "on_track" else "[!!]"
    lines.append(f"| Total Events | {te.get('value', 0)} | {te.get('target', 0)}+ | {status_icon} |")

    # v5.1: Excluded pro users
    excluded = metrics.get("excluded_pro_users", {})
    if excluded and excluded.get("value", 0) > 0:
        lines.append(f"| Excluded Pro Users | {excluded.get('value', 0)} | - | [info] |")

    lines.append("")

    # v5.1: Tier breakdown
    tier_data = metrics.get("tier_breakdown", {}).get("value", {})
    if tier_data and any(v > 0 for v in tier_data.values()):
        lines.extend([
            "## User Tier Breakdown",
            "",
            "| Tier | Users |",
            "|------|-------|",
        ])
        tier_labels = {"free": "Free", "pro": "Pro (excluded)", "first": "First Project", "additional": "Additional Project"}
        for tier, count in tier_data.items():
            label = tier_labels.get(tier, tier)
            lines.append(f"| {label} | {count} |")
        lines.append("")

    # Funnel breakdown
    funnel = metrics.get("funnel_drop_rates", {}).get("value", {})
    if funnel:
        lines.extend([
            "## Conversion Funnel",
            "",
            "| Stage | Users | Drop Rate |",
            "|-------|-------|-----------|",
        ])
        stage_labels = {
            "first_touch": "First Touch",
            "engaged": "Engaged",
            "limit_hit": "Hit Limit",
            "upgrade_shown": "Saw Upgrade",
            "converted": "Converted",
        }
        for stage, data in funnel.items():
            label = stage_labels.get(stage, stage)
            drop = data.get("drop_rate", 0)
            drop_str = f"{drop}%" if drop > 0 else "-"
            lines.append(f"| {label} | {data.get('users', 0)} | {drop_str} |")
        lines.append("")

    # Recommendations
    lines.extend([
        "## Recommendations",
        "",
    ])

    cr_value = cr.get("value", 0)
    if cr_value < 1:
        lines.append("1. **Critical**: Conversion rate < 1%. Focus on pain point messaging.")
    elif cr_value < 5:
        lines.append("1. **Priority**: Conversion rate below target. Consider increasing limit restrictions.")
    else:
        lines.append("1. **Good**: Conversion rate on track. Continue monitoring.")

    pp_value = pp.get("value", 0)
    if pp_value < 5:
        lines.append("2. **Action**: Pain point messages not converting. A/B test different copy.")
    elif pp_value < 10:
        lines.append("2. **Monitor**: Pain point conversion below target.")
    else:
        lines.append("2. **Good**: Pain point messaging effective.")

    te_value = te.get("value", 0)
    if te_value < 50:
        lines.append("3. **Note**: Low event volume. Results may not be statistically significant.")

    return "\n".join(lines)


def promote_winning_variant(experiment_name: str) -> dict:
    """Promote winning variant to 100% rollout.

    This updates the EXPERIMENTS config to set rollout_percent to 100
    and marks the winner as the default.

    Note: This is a dry-run function that returns what WOULD be changed.
    Actual config changes should be done manually or via CI.
    """
    decision = decide_experiment_winner(experiment_name)

    if not decision["ready_for_rollout"]:
        return {
            "success": False,
            "experiment": experiment_name,
            "reason": decision["reason"],
            "action_required": "Continue collecting data",
        }

    winner = decision["winner"]
    from .licensing.experiments import EXPERIMENTS

    current_config = EXPERIMENTS.get(experiment_name, {})
    winner_value = current_config.get("values", {}).get(winner)

    return {
        "success": True,
        "experiment": experiment_name,
        "winner": winner,
        "winner_value": winner_value,
        "previous_rollout": current_config.get("rollout_percent", 0),
        "new_rollout": 100,
        "action_required": f"Update EXPERIMENTS['{experiment_name}']['rollout_percent'] = 100",
        "code_change": f"""
# In licensing/experiments.py, update:
EXPERIMENTS["{experiment_name}"] = {{
    ...
    "rollout_percent": 100,
    "winner": "{winner}",
    "promoted_at": "{datetime.now().isoformat()[:10]}",
}}
""",
    }
