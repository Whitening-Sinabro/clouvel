# Manager Core
# Main logic

from typing import Dict, Any, List, Optional

from .data import MANAGERS, FREE_MANAGERS, PRO_ONLY_MANAGERS, PRO_ONLY_DESCRIPTIONS

# Knowledge Base integration (optional)
_HAS_KNOWLEDGE = False
try:
    from clouvel.db.knowledge import (
        search_knowledge,
        get_recent_decisions,
        get_or_create_project,
        KNOWLEDGE_DB_PATH,
    )
    _HAS_KNOWLEDGE = KNOWLEDGE_DB_PATH.exists()
except ImportError:
    pass

# Rich UI (optional)
_HAS_RICH_UI = False
_render_quick_perspectives = None
try:
    from clouvel.ui import render_quick_perspectives as _render_quick_perspectives, HAS_RICH
    _HAS_RICH_UI = HAS_RICH
except ImportError:
    pass


def _get_kb_context(context: str, topic: str, project_path: str = None) -> str:
    """Get relevant context from Knowledge Base for manager meeting.

    Returns formatted string with past decisions and relevant history.
    """
    if not _HAS_KNOWLEDGE:
        return ""

    try:
        # Get project ID if path provided
        project_id = None
        if project_path:
            from pathlib import Path
            project_name = Path(project_path).name
            project_id = get_or_create_project(project_name, project_path)

        sections = []

        # 1. Search for relevant past decisions based on topic
        search_results = search_knowledge(topic, project_id=project_id, limit=5)
        relevant_decisions = [r for r in search_results if r.get('type') == 'decision']

        if relevant_decisions:
            sections.append("### 📚 Relevant Past Decisions")
            sections.append("_Consider how these relate to the current discussion:_\n")
            for r in relevant_decisions[:3]:
                content = r.get('content', '')[:150]
                sections.append(f"- {content}...")
            sections.append("")

        # 2. Get recent decisions for broader context
        recent = get_recent_decisions(project_id=project_id, limit=5)
        if recent:
            sections.append("### 🕐 Recent Decisions")
            sections.append("_For context on current project direction:_\n")
            for d in recent[:3]:
                category = d.get('category', 'general')
                decision = d.get('decision', '')[:100]
                sections.append(f"- **[{category}]** {decision}...")
            sections.append("")

        if not sections:
            return ""

        # Add instruction for managers
        header = """
---
## 💡 Project History (from Knowledge Base)

_Use this context to make questions more relevant. Reference past decisions when applicable._
_Example: "Last time you chose X for auth. Does that still apply here?"_

"""
        return header + "\n".join(sections)

    except Exception:
        return ""

# Pro license check
def _check_pro_license() -> bool:
    """Check if Pro license is valid (license only, no trial)"""
    # 1. 표준 개발자 감지 (git remote 체크 포함)
    try:
        from ...license_common import is_developer
        if is_developer():
            return True
    except ImportError:
        pass

    # 2. Official license check
    try:
        from ...license import verify_license
        result = verify_license()
        return result.get("valid", False)
    except ImportError:
        # license.py not found = Free version (stub)
        return False


def _check_pro_or_trial(feature: str = "manager") -> Dict[str, Any]:
    """Check Pro license OR trial availability.

    Returns:
        {
            "allowed": bool,
            "reason": "license" | "trial" | "exhausted",
            "trial_info": {...} if using trial
        }
    """
    # 1. Check Pro license first
    if _check_pro_license():
        return {"allowed": True, "reason": "license"}

    # 2. Check trial availability
    try:
        from ...trial import check_trial_available, increment_trial_usage, get_trial_remaining

        if check_trial_available(feature):
            # Use trial and increment counter
            trial_info = increment_trial_usage(feature)
            return {
                "allowed": True,
                "reason": "trial",
                "trial_info": trial_info,
            }
        else:
            # Trial exhausted
            remaining = get_trial_remaining(feature)
            return {
                "allowed": False,
                "reason": "exhausted",
                "trial_info": {"remaining": remaining or 0},
            }
    except ImportError:
        # Trial module not available
        return {"allowed": False, "reason": "no_license"}


def _trial_exhausted_response(feature: str) -> Dict[str, Any]:
    """Response when trial is exhausted"""
    try:
        from ...trial import get_trial_exhausted_message, TRIAL_LIMITS
        limit = TRIAL_LIMITS.get(feature, 0)
        message = get_trial_exhausted_message(feature)
    except ImportError:
        limit = 0
        message = "Trial exhausted. Please upgrade to Pro."

    return {
        "error": "Trial exhausted",
        "message": f"You've used all {limit} free trial uses of {feature}.",
        "upgrade_url": "https://polar.sh/clouvel",
        "formatted_output": message,
    }


def _pro_required_response() -> Dict[str, Any]:
    """Pro-only feature response"""
    return {
        "error": "Pro-only feature",
        "message": "The manager tool is only available in the Pro version.",
        "upgrade_url": "https://polar.sh/clouvel",
        "features": [
            "8 C-Level manager feedback",
            "Context-based auto manager selection",
            "Auto execution plan generation",
            "Phase-based action items",
            "Auto checklist generation",
            "Dynamic meeting generation (use_dynamic=True)",
        ],
        "formatted_output": """
==================================================
🔒 PRO-ONLY FEATURE
==================================================

The **manager** tool is only available in the Pro version.

### Included Features
- 👔 PM, 🛠️ CTO, 🧪 QA, 🎨 CDO
- 📢 CMO, 💰 CFO, 🔒 CSO, 🔥 ERROR
- Context-based auto manager selection
- Phase-based execution plan generation
- Dynamic meeting generation (use_dynamic=True)

### Purchase
https://polar.sh/clouvel

==================================================
"""
    }
from .utils import (
    _analyze_context,
    _select_managers_by_context,
    _extract_feature_name,
    _check_pattern,
    _generate_action_items,
    _group_by_phase,
    _generate_recommendations,
    _calculate_relevance_score,
    _run_critical_checks,
    RELEVANCE_THRESHOLD,
)
from .formatter import _format_output

# 동적 회의록 생성 모듈
from .generator import (
    generate_meeting,
    MeetingConfig,
    save_meeting_log,
)
from .prompts import (
    PERSONAS,
    get_system_prompt,
    get_topic_guide,
    format_examples_for_prompt,
)


def manager(
    context: str,
    mode: str = "auto",
    managers: List[str] = None,
    include_checklist: bool = True,
    use_dynamic: bool = False,
    include_prompt: bool = False,
    topic: Optional[str] = None,
    include_examples: bool = True,
    auto_log: bool = True,
) -> Dict[str, Any]:
    """
    Provides feedback from managers based on context.

    Args:
        context: Content to review (plan, code, questions, etc.)
        mode: 'auto' (auto-detect), 'all' (all managers), 'specific' (specified)
        managers: List of managers to use when mode='specific'
        include_checklist: Whether to include checklist
        use_dynamic: If True, generates dynamic meeting (returns LLM prompt)
        include_prompt: If True, includes LLM prompt in result
        topic: Topic hint (auth, api, error, etc.) - used in use_dynamic/include_prompt
        include_examples: Whether to include few-shot examples - used in use_dynamic
        auto_log: Whether to auto-save tuning data - used in use_dynamic

    Returns:
        Feedback and recommendations from each manager
    """
    # Check Pro license
    # Free tier: PM, CTO, QA (3 managers) - unlimited
    # Pro tier: All 8 managers - unlimited
    is_pro = _check_pro_license()

    # Dynamic meeting generation mode
    if use_dynamic:
        return manager_dynamic(
            context=context,
            mode=mode,
            managers=managers,
            topic=topic,
            include_examples=include_examples,
            auto_log=auto_log,
            is_pro=is_pro,
        )

    result = {
        "context_analysis": {},
        "active_managers": [],
        "feedback": {},
        "action_items": [],
        "action_items_by_phase": {},
        "combined_checklist": [],
        "warnings": [],
        "recommendations": [],
        "prompt": None,  # LLM prompt (when include_prompt=True)
    }

    # 1. Context analysis
    detected_contexts = _analyze_context(context)
    result["context_analysis"] = {
        "detected_topics": detected_contexts,
        "context_length": len(context)
    }

    # 2. Determine active managers
    if mode == "all":
        active_managers = list(MANAGERS.keys())
    elif mode == "specific" and managers:
        active_managers = [m.upper() for m in managers if m.upper() in MANAGERS]
    else:  # auto
        active_managers = _select_managers_by_context(context, detected_contexts)

    # Filter for Free tier (PM, CTO, QA only)
    missed_perspectives = []
    if not is_pro:
        # Track which Pro-only managers were requested but filtered
        missed_perspectives = [m for m in active_managers if m in PRO_ONLY_MANAGERS]
        active_managers = [m for m in active_managers if m in FREE_MANAGERS]

        # Ensure at least one manager is active
        if not active_managers:
            active_managers = FREE_MANAGERS.copy()

    result["active_managers"] = active_managers
    result["is_pro"] = is_pro
    result["missed_perspectives"] = missed_perspectives

    # 3. Generate feedback from each manager
    all_critical_issues = []
    all_missing_items = []

    for manager_key in active_managers:
        manager_info = MANAGERS[manager_key]
        feedback = _generate_feedback(manager_key, manager_info, context)
        result["feedback"][manager_key] = feedback

        # Combine checklists
        if include_checklist:
            for item in manager_info.get("checklist", []):
                combined_item = f"[{manager_info['emoji']} {manager_key}] {item}"
                if combined_item not in result["combined_checklist"]:
                    result["combined_checklist"].append(combined_item)

        # Collect warnings
        if feedback.get("warnings"):
            result["warnings"].extend(feedback["warnings"])

        # Collect critical issues
        if feedback.get("critical_issues"):
            for issue in feedback["critical_issues"]:
                all_critical_issues.append(f"[{manager_info['emoji']} {manager_key}] {issue}")

        # Collect missing items
        if feedback.get("missing_items"):
            for item in feedback["missing_items"]:
                all_missing_items.append(f"[{manager_info['emoji']} {manager_key}] {item}")

    result["critical_issues"] = all_critical_issues
    result["missing_items"] = all_missing_items

    # Determine overall approval status
    if all_critical_issues:
        result["overall_status"] = "BLOCKED"
    elif result["warnings"] or all_missing_items:
        result["overall_status"] = "NEEDS_REVISION"
    else:
        result["overall_status"] = "APPROVED"

    # 3.5. Generate action items
    action_items = _generate_action_items(context, active_managers)
    result["action_items"] = action_items
    result["action_items_by_phase"] = _group_by_phase(action_items)

    # 4. Generate combined recommendations
    result["recommendations"] = _generate_recommendations(result)

    # 5. Format output
    result["formatted_output"] = _format_output(result)

    # 5.5. Add "missed perspectives" hint for Free tier
    if missed_perspectives:
        hint_lines = [
            "",
            "---",
            "",
            "💡 **Pro에서 추가로 볼 수 있는 관점:**",
            "",
        ]
        for m in missed_perspectives:
            desc = PRO_ONLY_DESCRIPTIONS.get(m, {})
            emoji = desc.get("emoji", "👤")
            hint = desc.get("hint", m)
            hint_lines.append(f"  {emoji} **{m}**: {hint}")

        hint_lines.extend([
            "",
            "👉 Pro 업그레이드 ($7.99/mo): https://polar.sh/clouvel",
            "",
        ])
        result["formatted_output"] += "\n".join(hint_lines)

    # 6. Include LLM prompt (optional)
    if include_prompt:
        prompt_topic = topic if topic else (detected_contexts[0] if detected_contexts else "feature")
        meeting_result = generate_meeting(
            context=context,
            topic=prompt_topic,
            config=MeetingConfig(include_examples=include_examples),
        )
        result["prompt"] = {
            "system": meeting_result["system_prompt"],
            "user": meeting_result["user_prompt"],
        }

    return result


def _generate_feedback(manager_key: str, manager_info: Dict, context: str) -> Dict[str, Any]:
    """Generates feedback for each manager."""
    feedback = {
        "emoji": manager_info["emoji"],
        "title": manager_info["title"],
        "focus": manager_info["focus"],
        "questions": [],
        "opinions": [],
        "concerns": [],
        "warnings": [],
        "critical_issues": [],  # Critical issues (must be resolved)
        "missing_items": [],    # Missing items
        "action_items": [],
        "approval_status": "REVIEW_NEEDED",
        "relevance_score": 0.0
    }

    context_lower = context.lower()
    feature_name = _extract_feature_name(context)
    manager_keywords = manager_info.get("keywords", [])

    # 1. Generate context-based opinions
    opinions_dict = manager_info.get("opinions", {})
    detected_topics = _analyze_context(context)

    opinion_added = False
    for topic in detected_topics:
        if topic in opinions_dict:
            opinion = opinions_dict[topic].replace("{feature}", feature_name)
            feedback["opinions"].append(opinion)
            opinion_added = True
            break

    if not opinion_added and "default" in opinions_dict:
        feedback["opinions"].append(opinions_dict["default"])

    # 2. Add relevant questions (based on relevance score)
    all_scored_questions = []
    for question in manager_info["questions"]:
        score = _calculate_relevance_score(question, context, manager_keywords)
        all_scored_questions.append((question, score))

    # Sort by score descending
    all_scored_questions.sort(key=lambda x: x[1], reverse=True)

    # Filter questions above threshold
    filtered_questions = [(q, s) for q, s in all_scored_questions if s >= RELEVANCE_THRESHOLD]

    # Fallback: if no questions after filtering, include top 1
    if not filtered_questions and all_scored_questions:
        filtered_questions = [all_scored_questions[0]]

    # Select top 2
    feedback["questions"] = [q for q, _ in filtered_questions[:2]]

    # Calculate overall manager relevance score
    manager_relevance = sum(1 for kw in manager_keywords if kw.lower() in context_lower) / max(len(manager_keywords), 1)
    feedback["relevance_score"] = manager_relevance

    # Generate individual manager action items
    templates = manager_info.get("action_templates", [])
    for template in templates:
        trigger = template.get("trigger", "")
        trigger_patterns = trigger.split("|")
        if any(pattern.lower() in context_lower for pattern in trigger_patterns):
            for action in template.get("actions", []):
                feedback["action_items"].append({
                    "id": action["id"],
                    "action": action["action"],
                    "depends": action.get("depends", []),
                    "verify": action.get("verify", ""),
                    "phase": action.get("phase", "검증")
                })

    # Check warning patterns
    if manager_key == "CSO":
        critical_patterns = manager_info.get("critical_patterns", [])
        for pattern in critical_patterns:
            if pattern.lower() in context_lower or _check_pattern(pattern, context):
                feedback["warnings"].append(f"⚠️ Security risk: {pattern}")
                feedback["approval_status"] = "BLOCKED"

    if manager_key == "CDO":
        anti_patterns = manager_info.get("anti_patterns", [])
        for pattern in anti_patterns:
            if pattern.lower() in context_lower:
                feedback["concerns"].append(f"🎨 Design concern: {pattern}")

    if manager_key == "ERROR":
        if "error" in context_lower or "exception" in context_lower:
            feedback["concerns"].append("🔥 Error handling logic needs review")
            if "Have you completed the 5 Whys analysis?" not in feedback["questions"]:
                feedback["questions"].append("Have you completed the 5 Whys analysis?")

    # Run critical checks
    _run_critical_checks(manager_key, feedback, context, context_lower)

    # Determine final approval status
    if feedback["critical_issues"]:
        feedback["approval_status"] = "BLOCKED"
    elif feedback["warnings"] or feedback["missing_items"]:
        feedback["approval_status"] = "NEEDS_REVISION"
    elif feedback["concerns"]:
        feedback["approval_status"] = "REVIEW_NEEDED"
    else:
        feedback["approval_status"] = "APPROVED"

    return feedback


def ask_manager(manager_key: str, question: str) -> Dict[str, Any]:
    """Ask a specific manager a question."""
    manager_key = manager_key.upper()
    if manager_key not in MANAGERS:
        return {"error": f"Unknown manager: {manager_key}"}

    return manager(
        context=question,
        mode="specific",
        managers=[manager_key]
    )


def manager_dynamic(
    context: str,
    mode: str = "auto",
    managers: List[str] = None,
    topic: Optional[str] = None,
    include_examples: bool = True,
    auto_log: bool = True,
    project_path: Optional[str] = None,
    is_pro: bool = None,
) -> Dict[str, Any]:
    """
    Returns prompt for dynamic meeting generation.

    Instead of rule-based approach, requests LLM to simulate a meeting.
    Passing the returned prompt to Claude generates a natural meeting transcript.

    Args:
        context: Meeting topic/situation description
        mode: 'auto' (auto-detect), 'all' (all managers), 'specific' (specified)
        managers: List of managers to use when mode='specific'
        topic: Topic (auto-detected if None)
        include_examples: Whether to include few-shot examples
        auto_log: Whether to auto-log (tuning data collection)
        project_path: Project path for Knowledge Base lookup

    Returns:
        Prompt and metadata for dynamic meeting generation
    """
    # Note: Pro/Trial check is done in caller (manager function)
    # This function should only be called from manager() which already checked access

    # 1. Detect topic
    if topic is None:
        detected_topics = _analyze_context(context)
        topic = detected_topics[0] if detected_topics else "feature"
    else:
        detected_topics = [topic]

    # 2. Select managers
    if mode == "all":
        active_managers = list(PERSONAS.keys())
    elif mode == "specific" and managers:
        active_managers = [m.upper() for m in managers if m.upper() in PERSONAS]
    else:  # auto
        guide = get_topic_guide(topic)
        active_managers = guide.get("participants", ["PM", "CTO", "QA"])

    # PM is always included
    if "PM" not in active_managers:
        active_managers.insert(0, "PM")

    # 2.6. Filter for Free tier (PM, CTO, QA only)
    if is_pro is None:
        is_pro = _check_pro_license()

    missed_perspectives = []
    if not is_pro:
        missed_perspectives = [m for m in active_managers if m in PRO_ONLY_MANAGERS]
        active_managers = [m for m in active_managers if m in FREE_MANAGERS]
        if not active_managers:
            active_managers = FREE_MANAGERS.copy()

    # 2.5. Get Knowledge Base context
    kb_context = _get_kb_context(context, topic, project_path)

    # 3. Generate prompt
    config = MeetingConfig(
        auto_select_managers=False,
        forced_managers=active_managers,
        include_examples=include_examples,
        auto_log=auto_log,
    )

    # Include KB context as additional_context
    meeting_result = generate_meeting(
        context=context,
        topic=topic,
        config=config,
        additional_context=kb_context if kb_context else None,
    )

    # 4. Include rule-based analysis too (for critical checks)
    critical_issues = []
    warnings = []
    missing_items = []

    for manager_key in active_managers:
        if manager_key in MANAGERS:
            manager_info = MANAGERS[manager_key]
            feedback = _generate_feedback(manager_key, manager_info, context)

            if feedback.get("critical_issues"):
                for issue in feedback["critical_issues"]:
                    critical_issues.append(f"[{manager_info['emoji']} {manager_key}] {issue}")

            if feedback.get("warnings"):
                warnings.extend(feedback["warnings"])

            if feedback.get("missing_items"):
                for item in feedback["missing_items"]:
                    missing_items.append(f"[{manager_info['emoji']} {manager_key}] {item}")

    # 5. Compose result
    result = {
        "mode": "dynamic",
        "context": context,
        "topic": topic,
        "detected_topics": detected_topics,
        "active_managers": active_managers,
        "is_pro": is_pro,
        "missed_perspectives": missed_perspectives,

        # LLM prompt
        "prompt": {
            "system": meeting_result["system_prompt"],
            "user": meeting_result["user_prompt"],
        },

        # Rule-based critical checks (security and other important issues)
        "critical_issues": critical_issues,
        "warnings": warnings,
        "missing_items": missing_items,

        # Status
        "overall_status": (
            "BLOCKED" if critical_issues else
            "NEEDS_REVISION" if warnings or missing_items else
            "APPROVED"
        ),

        # Metadata
        "timestamp": meeting_result["timestamp"],

        # Usage instructions
        "instruction": """
Pass prompt.system and prompt.user from this result to Claude
to generate a natural C-Level meeting transcript.

Usage example:
```python
response = client.messages.create(
    model="claude-sonnet-4-20250514",
    system=result["prompt"]["system"],
    messages=[{"role": "user", "content": result["prompt"]["user"]}]
)
print(response.content[0].text)
```

Or use generate_meeting_sync():
```python
from clouvel.tools.manager.generator import generate_meeting_sync
meeting = generate_meeting_sync(context="...")
```
""".strip()
    }

    # 6. Add "missed perspectives" hint for Free tier
    if missed_perspectives:
        hint_lines = [
            "",
            "---",
            "",
            "💡 **Pro에서 추가로 볼 수 있는 관점:**",
            "",
        ]
        for m in missed_perspectives:
            desc = PRO_ONLY_DESCRIPTIONS.get(m, {})
            emoji = desc.get("emoji", "👤")
            hint = desc.get("hint", m)
            hint_lines.append(f"  {emoji} **{m}**: {hint}")

        hint_lines.extend([
            "",
            "👉 Pro 업그레이드 ($7.99/mo): https://polar.sh/clouvel",
            "",
        ])
        result["missed_perspectives_hint"] = "\n".join(hint_lines)

    return result


def get_meeting_prompt(context: str, topic: Optional[str] = None) -> Dict[str, str]:
    """
    Returns only the meeting generation prompt.

    Args:
        context: Meeting topic/situation description
        topic: Topic (auto-detected if None)

    Returns:
        Prompt in {"system": str, "user": str} format
    """
    result = manager_dynamic(context=context, topic=topic, auto_log=False)
    # Return error response if no Pro license
    if "error" in result:
        return {"error": result["error"], "message": result.get("message", "")}
    return result["prompt"]


def quick_perspectives(
    context: str,
    max_managers: int = 4,
    questions_per_manager: int = 2,
) -> Dict[str, Any]:
    """
    Quick, lightweight perspective check before coding.

    Returns key questions from relevant managers without API calls.
    Designed to be called automatically before every coding task.

    Args:
        context: What the user wants to build/do
        max_managers: Maximum number of managers to include (default 4)
        questions_per_manager: Questions per manager (default 2)

    Returns:
        Quick perspectives from relevant managers
    """
    # 1. Detect topic and select relevant managers
    detected_topics = _analyze_context(context)
    topic = detected_topics[0] if detected_topics else "feature"

    # Get topic guide for manager selection
    guide = get_topic_guide(topic)
    relevant_managers = guide.get("participants", ["PM", "CTO", "QA"])[:max_managers]

    # Always include PM
    if "PM" not in relevant_managers:
        relevant_managers.insert(0, "PM")
        relevant_managers = relevant_managers[:max_managers]

    # 2. Get probing questions from each manager
    perspectives = []
    context_lower = context.lower()

    for manager_key in relevant_managers:
        if manager_key not in PERSONAS:
            continue

        persona = PERSONAS[manager_key]
        probing_qs = persona.get("probing_questions", {})

        # Select most relevant category based on topic
        selected_questions = []

        # Priority order based on topic
        category_priority = {
            "auth": ["auth_authz", "attack_surface", "scope", "tradeoffs"],
            "api": ["architecture", "tradeoffs", "edge_cases", "failure_modes"],
            "payment": ["cost_awareness", "attack_surface", "failure_modes", "scope"],
            "ui": ["user_journey", "visual_hierarchy", "states_and_feedback", "scope"],
            "feature": ["scope", "user_value", "tradeoffs", "test_strategy"],
            "launch": ["target_audience", "distribution", "observability", "scope"],
            "error": ["failure_scenarios", "recovery", "learning", "observability"],
            "security": ["attack_surface", "auth_authz", "data_protection", "incident_prep"],
            "performance": ["architecture", "cost_awareness", "tradeoffs", "observability"],
        }

        priority_cats = category_priority.get(topic, ["scope", "tradeoffs"])

        for cat in priority_cats:
            if cat in probing_qs:
                selected_questions.extend(probing_qs[cat][:questions_per_manager])
                break

        # Fallback: take from first available category
        if not selected_questions:
            for cat, questions in probing_qs.items():
                selected_questions.extend(questions[:questions_per_manager])
                break

        if selected_questions:
            perspectives.append({
                "manager": manager_key,
                "emoji": persona.get("emoji", "👤"),
                "title": persona.get("title", manager_key),
                "questions": selected_questions[:questions_per_manager]
            })

    # 3. Get KB context if available
    kb_hint = ""
    if _HAS_KNOWLEDGE:
        try:
            from clouvel.db.knowledge import search_knowledge
            results = search_knowledge(topic, limit=2)
            if results:
                kb_hint = f"\n💡 _Related past decision: {results[0].get('content', '')[:80]}..._"
        except Exception:
            pass

    # 4. Format output (v1.9.1: Rich UI support)
    if _HAS_RICH_UI and _render_quick_perspectives:
        # Build dict for Rich UI
        perspectives_dict = {
            p["manager"]: p["questions"] for p in perspectives
        }
        formatted_output = _render_quick_perspectives(context, perspectives_dict)
    else:
        # Plain text fallback
        lines = [
            "## 💡 Quick Perspectives",
            "",
            f"_Before building: **{context[:50]}{'...' if len(context) > 50 else ''}**_",
            ""
        ]

        for p in perspectives:
            lines.append(f"**{p['emoji']} {p['manager']}**:")
            for q in p["questions"]:
                lines.append(f"  - {q}")
            lines.append("")

        lines.append("---")
        lines.append("")
        lines.append("| Action | Command |")
        lines.append("|--------|---------|")
        lines.append("| Full 8-manager review | `manager(use_dynamic=True)` |")
        lines.append("| Proceed with coding | Continue |")

        if kb_hint:
            lines.append(kb_hint)

        formatted_output = "\n".join(lines)

    return {
        "topic": topic,
        "managers": [p["manager"] for p in perspectives],
        "perspectives": perspectives,
        "formatted_output": formatted_output,
    }
