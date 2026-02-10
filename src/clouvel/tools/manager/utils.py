# Manager Utils
# Helper functions

import re
from typing import Dict, Any, List, Set

from .data import MANAGERS, CONTEXT_GROUPS, PHASE_ORDER

# Relevance score threshold (too high filters out all questions)
RELEVANCE_THRESHOLD = 0.1


def _topological_sort(action_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Topologically sorts action items based on dependencies."""
    if not action_items:
        return []

    id_to_item = {item["id"]: item for item in action_items}
    in_degree = {item["id"]: 0 for item in action_items}

    for item in action_items:
        for dep in item.get("depends", []):
            if dep in in_degree:
                in_degree[item["id"]] += 1

    queue = [item_id for item_id, degree in in_degree.items() if degree == 0]
    result = []

    while queue:
        queue.sort(key=lambda x: (
            PHASE_ORDER.get(id_to_item[x].get("phase", "Verify"), 5),
            x
        ))

        current_id = queue.pop(0)
        result.append(id_to_item[current_id])

        for item in action_items:
            if current_id in item.get("depends", []):
                in_degree[item["id"]] -= 1
                if in_degree[item["id"]] == 0:
                    queue.append(item["id"])

    remaining = [item for item in action_items if item not in result]
    remaining.sort(key=lambda x: PHASE_ORDER.get(x.get("phase", "Verify"), 5))
    result.extend(remaining)

    return result


def _group_by_phase(action_items: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    """Groups action items by phase."""
    phases = {"Prepare": [], "Design": [], "Implement": [], "Verify": []}

    for item in action_items:
        phase = item.get("phase", "Verify")
        if phase in phases:
            phases[phase].append(item)
        else:
            phases["Verify"].append(item)

    return phases


def _analyze_context(context: str) -> List[str]:
    """Detects major topics from context.

    v1.5: Enhanced with pattern-based analysis beyond keywords.
    - Keyword matching (existing)
    - Sentence pattern detection (new)
    - Problem situation detection (new)
    """
    context_lower = context.lower()
    detected = []

    # 1. Keyword matching (existing) - Korean + English
    topic_keywords = {
        "auth": ["login", "auth", "session", "jwt", "token", "password", "signin", "signup",
                 "로그인", "인증", "세션", "토큰", "비밀번호", "회원가입"],
        "payment": ["payment", "billing", "subscription", "price", "checkout", "stripe",
                    "결제", "구독", "청구", "가격", "체크아웃"],
        "api": ["api", "endpoint", "rest", "graphql", "request", "response",
                "엔드포인트", "요청", "응답"],
        "ui": ["ui", "component", "button", "input", "form", "style", "css",
               "컴포넌트", "버튼", "입력", "폼", "스타일"],
        "security": ["security", "encrypt", "vulnerability", "owasp", "xss", "injection",
                     "보안", "암호화", "취약점"],
        "performance": ["performance", "optimize", "cache", "slow", "latency",
                        "성능", "최적화", "캐시", "느림", "지연"],
        "error": ["error", "exception", "bug", "fix", "crash", "fail",
                  "에러", "오류", "버그", "수정", "실패"],
        "database": ["database", "db", "sql", "query", "migration", "schema",
                     "데이터베이스", "쿼리", "마이그레이션", "스키마"],
        "design": ["design", "ux", "ui", "layout", "figma", "wireframe",
                   "디자인", "레이아웃", "와이어프레임", "썸네일"],
        "feature": ["feature", "implement", "add", "build", "create",
                    "기능", "구현", "추가", "빌드", "생성"],
        "launch": ["launch", "deploy", "release", "ship", "production",
                   "런칭", "배포", "릴리즈", "출시", "프로덕션", "마케팅"],
        # v1.5: MCP/Clouvel internal topics
        "mcp": ["mcp", "server", "tool", "clouvel", "claude", "anthropic", "mcp server"],
        "internal": ["우리", "자체", "개선", "보강", "누락", "약속", "ourselves", "improve", "missing"],
        "tracking": ["기록", "추적", "files", "created", "current", "record", "track", "status"],
        "maintenance": ["리팩토링", "refactor", "cleanup", "debt", "todo", "fixme"],
    }

    for topic, keywords in topic_keywords.items():
        if any(kw in context_lower for kw in keywords):
            detected.append(topic)

    # 2. Pattern-based detection (v1.5 - B2, v3.1 enhanced)
    # Problem patterns (Korean + English)
    problem_patterns = [
        (r"없다|없음|안\s*됨|실패|못\s*함", "error"),
        (r"not\s+working|doesn't\s+work|failed|missing", "error"),
        (r"느리|느려|slow|latency|timeout|지연", "performance"),
        (r"보안|취약|vulnerability|leak|security", "security"),
        # v3.1: PRD/Spec related patterns
        (r"prd|spec|requirement|스펙|요구사항|명세", "feature"),
        (r"acceptance|criteria|완료\s*조건|검수", "feature"),
        (r"ship|deploy|release|배포|릴리즈|출시", "launch"),
        # v3.1: Code quality patterns
        (r"refactor|cleanup|debt|리팩토링|정리", "maintenance"),
        (r"duplicate|중복|copy|복붙", "error"),
    ]

    for pattern, topic in problem_patterns:
        if re.search(pattern, context, re.IGNORECASE):
            if topic not in detected:
                detected.append(topic)

    # Request patterns
    request_patterns = [
        (r"추가|구현|만들|add|implement|create|build", "feature"),
        (r"수정|변경|개선|modify|change|improve", "maintenance"),
        (r"테스트|검증|확인|test|verify|check", "error"),
    ]

    for pattern, topic in request_patterns:
        if re.search(pattern, context, re.IGNORECASE):
            if topic not in detected:
                detected.append(topic)

    return detected if detected else ["feature"]


def _select_managers_by_context(context: str, detected_contexts: List[str]) -> List[str]:
    """Selects managers based on context."""
    selected: Set[str] = set()

    for ctx in detected_contexts:
        if ctx in CONTEXT_GROUPS:
            selected.update(CONTEXT_GROUPS[ctx])

    context_lower = context.lower()
    for manager_key, manager_info in MANAGERS.items():
        for keyword in manager_info["keywords"]:
            if keyword in context_lower:
                selected.add(manager_key)
                break

    selected.add("PM")
    selected.add("CTO")

    priority_order = ["PM", "CTO", "QA", "CSO", "CDO", "CMO", "CFO", "ERROR"]
    return [m for m in priority_order if m in selected]


def _extract_feature_name(context: str) -> str:
    """Extracts feature/task name from context."""
    patterns = [
        r'(\w+)\s*(feature|page|screen|API|system)',
        r'(login|signup|payment|auth|dashboard|settings)',
        r'(\w+)\s*(implement|add|create|build)',
    ]

    for pattern in patterns:
        match = re.search(pattern, context, re.IGNORECASE)
        if match:
            return match.group(1)

    return context[:20].strip() if len(context) > 20 else context


def _check_pattern(pattern: str, context: str) -> bool:
    """Checks if a specific pattern exists in context."""
    pattern_checks = {
        "hardcoded secret": r'["\'](?:sk_|api_key|secret|password)["\']?\s*[:=]\s*["\'][^"\']+["\']',
        "plaintext password": r'password\s*[:=]\s*["\'][^"\']+["\']',
        "SQL string concatenation": r'(?:SELECT|INSERT|UPDATE|DELETE).*\+.*(?:str\(|f"|\')',
        "direct innerHTML assignment": r'innerHTML\s*=',
    }

    regex = pattern_checks.get(pattern)
    if regex:
        return bool(re.search(regex, context, re.IGNORECASE))
    return False


def _generate_action_items(context: str, active_managers: List[str]) -> List[Dict[str, Any]]:
    """Generates action items from all active managers based on context."""
    context_lower = context.lower()
    action_items = []

    for manager_key in active_managers:
        manager_info = MANAGERS.get(manager_key, {})
        templates = manager_info.get("action_templates", [])

        for template in templates:
            trigger = template.get("trigger", "")
            trigger_patterns = trigger.split("|")

            if any(pattern.lower() in context_lower for pattern in trigger_patterns):
                for action in template.get("actions", []):
                    action_item = {
                        **action,
                        "manager": manager_key,
                        "emoji": manager_info.get("emoji", "")
                    }
                    if not any(a["id"] == action_item["id"] for a in action_items):
                        action_items.append(action_item)

    return _topological_sort(action_items)


def _generate_recommendations(result: Dict) -> List[str]:
    """Generates combined recommendations."""
    recommendations = []

    if result["warnings"]:
        recommendations.append("🚨 Resolve security warnings first")

    active_count = len(result["active_managers"])
    if active_count >= 5:
        recommendations.append("📋 Complex task. Proceed step by step")

    managers = result["active_managers"]
    if "CSO" in managers and "CTO" in managers:
        recommendations.append("🔐 Conduct security review alongside code review")

    if "CFO" in managers:
        recommendations.append("💰 Document cost impact")

    if "ERROR" in managers:
        recommendations.append("📝 Document error handling logic and recovery strategy")

    return recommendations


def list_managers() -> List[Dict[str, str]]:
    """Returns list of available managers."""
    return [
        {
            "key": key,
            "emoji": info["emoji"],
            "title": info["title"],
            "focus": ", ".join(info["focus"][:3])
        }
        for key, info in MANAGERS.items()
    ]


def _calculate_relevance_score(question: str, context: str, manager_keywords: List[str]) -> float:
    """Calculates relevance score between question and context.

    Args:
        question: Manager's question
        context: Context provided by user
        manager_keywords: List of manager's keywords

    Returns:
        Relevance score between 0.0 and 1.0
    """
    context_lower = context.lower()
    question_lower = question.lower()

    # Stopwords (excluded from score calculation)
    stopwords = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "must", "shall", "can", "need", "dare",
        "this", "that", "these", "those", "what", "which", "who", "whom",
        "how", "when", "where", "why", "if", "then", "else", "for", "of",
        "to", "in", "on", "at", "by", "with", "about", "into", "through",
        "and", "or", "but", "nor", "so", "yet", "both", "either", "neither"
    }

    # Extract meaningful keywords from question
    question_words = set(question_lower.replace("?", "").replace(".", "").split())
    question_keywords = question_words - stopwords

    if not question_keywords:
        return 0.0

    score = 0.0
    max_score = len(question_keywords)

    # 1. Check if question keywords are in context
    for keyword in question_keywords:
        if len(keyword) >= 2 and keyword in context_lower:
            score += 1.0

    # 2. Bonus if manager keywords are in context
    manager_match_count = sum(1 for kw in manager_keywords if kw.lower() in context_lower)
    if manager_match_count > 0:
        score += min(manager_match_count * 0.5, 1.5)

    # 3. Normalize
    normalized_score = score / (max_score + 1.5) if max_score > 0 else 0.0

    return min(normalized_score, 1.0)


def _run_critical_checks(manager_key: str, feedback: Dict, context: str, context_lower: str) -> None:
    """Runs critical checks for each manager."""

    # PM: PRD/scope related checks
    if manager_key == "PM":
        if any(kw in context_lower for kw in ["feature", "implement", "build"]):
            if "prd" not in context_lower and "requirements" not in context_lower:
                feedback["missing_items"].append("No PRD or requirements document reference")
        if any(kw in context_lower for kw in ["add", "new", "create"]):
            if not any(kw in context_lower for kw in ["p0", "p1", "p2", "priority"]):
                feedback["concerns"].append("Priority undefined - verify MVP scope")

    # CTO: Architecture/tech related checks
    elif manager_key == "CTO":
        if any(kw in context_lower for kw in ["api", "endpoint", "route"]):
            if not any(kw in context_lower for kw in ["spec", "document", "doc"]):
                feedback["missing_items"].append("API spec documentation needed")
        if any(kw in context_lower for kw in ["schema", "table", "column"]):
            if "migration" not in context_lower:
                feedback["concerns"].append("DB schema changes require migration plan")
        if any(kw in context_lower for kw in ["loop", "all", "bulk", "batch"]):
            feedback["concerns"].append("Review performance impact (bulk processing possible)")

    # QA: Test related checks
    elif manager_key == "QA":
        if any(kw in context_lower for kw in ["implement", "change", "modify", "update"]):
            if not any(kw in context_lower for kw in ["test", "verify", "check"]):
                feedback["missing_items"].append("Test plan missing")
        if "input" in context_lower:
            if not any(kw in context_lower for kw in ["edge", "exception", "invalid", "boundary"]):
                feedback["concerns"].append("Verify edge case/exception input handling")

    # CSO: Security critical checks
    elif manager_key == "CSO":
        if any(kw in context_lower for kw in ["delete", "update", "admin", "modify"]):
            if not any(kw in context_lower for kw in ["auth", "permission", "authorize"]):
                feedback["critical_issues"].append("Sensitive operation may lack auth/permission check")
        if any(kw in context_lower for kw in ["user input", "request", "req.body", "form data"]):
            if not any(kw in context_lower for kw in ["validate", "sanitize", "escape"]):
                feedback["critical_issues"].append("Verify input validation logic")
        if "sql" in context_lower or "query" in context_lower:
            if "parameterized" not in context_lower and "prepared" not in context_lower:
                feedback["warnings"].append("Verify SQL Injection prevention (use parameterized query)")

    # CDO: UI/UX related checks
    elif manager_key == "CDO":
        if any(kw in context_lower for kw in ["button", "input", "form", "modal"]):
            if not any(kw in context_lower for kw in ["aria", "a11y", "accessibility"]):
                feedback["concerns"].append("Verify accessibility (a11y) attributes")
        if any(kw in context_lower for kw in ["layout", "grid", "flex"]):
            if not any(kw in context_lower for kw in ["responsive", "mobile"]):
                feedback["concerns"].append("Verify responsive design")

    # CFO: Cost related checks
    elif manager_key == "CFO":
        if any(kw in context_lower for kw in ["api call", "external api", "third party"]):
            feedback["concerns"].append("Review external API call cost impact")
        if any(kw in context_lower for kw in ["scale", "instance", "storage"]):
            feedback["warnings"].append("Potential infrastructure cost increase - review budget")

    # ERROR: Error handling related checks
    elif manager_key == "ERROR":
        if any(kw in context_lower for kw in ["async", "await", "fetch", "request", "file"]):
            if not any(kw in context_lower for kw in ["try", "catch", "except", "error handling"]):
                feedback["missing_items"].append("Async/IO operation may lack error handling")
        if "error" in context_lower or "exception" in context_lower:
            if not any(kw in context_lower for kw in ["log", "sentry", "monitoring"]):
                feedback["concerns"].append("Verify error logging/monitoring setup")
