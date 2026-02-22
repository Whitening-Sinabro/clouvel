# -*- coding: utf-8 -*-
"""Analytics formatters (ab_report, monthly_report, decide_winner).

Extracted from tool_dispatch.py _get_ab_report, _get_monthly_report, _decide_winner.
Note: _get_analytics already uses analytics.format_stats, so only AB/monthly/winner here.
"""


def format_ab_experiment(experiment: str, days: int, analysis: dict) -> str:
    lines = [
        f"# A/B Test: {experiment}",
        f"Period: Last {days} days",
        "",
    ]
    if analysis["variants"]:
        lines.append("| Variant | Impressions | Conversions | Rate |")
        lines.append("|---------|-------------|-------------|------|")
        for variant, data in analysis["variants"].items():
            winner = " *" if variant == analysis.get("winner") else ""
            lines.append(
                f"| {variant}{winner} | {data['impressions']} | "
                f"{data['conversions']} | {data['rate']}% |"
            )
        lines.append("")
        lines.append(f"**Uplift:** {analysis['uplift']:+.1f}%")
        lines.append(f"**Confidence:** {analysis['confidence']}")
    else:
        lines.append("_No data collected yet_")
    return "\n".join(lines)


def format_decide_winner(experiment: str, decision: dict, promotion: dict) -> str:
    lines = [
        f"# Experiment Decision: {experiment}",
        "",
        "## Analysis",
        f"- Decision: **{decision['decision'].upper()}**",
        f"- Reason: {decision['reason']}",
        "",
    ]

    if decision["ready_for_rollout"]:
        lines.extend([
            "## Ready for Promotion",
            f"- Winner: **{decision['winner']}**",
            f"- Winner value: `{promotion.get('winner_value')}`",
            f"- Previous rollout: {promotion.get('previous_rollout')}%",
            f"- New rollout: {promotion.get('new_rollout')}%",
            "",
            "### Code Change Required:",
            "```python",
            promotion.get("code_change", "").strip(),
            "```",
        ])
    else:
        lines.extend([
            "## Action Required",
            f"- {promotion.get('action_required', 'Continue collecting data')}",
        ])

    return "\n".join(lines)
