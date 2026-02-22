# -*- coding: utf-8 -*-
"""Meeting Knowledge Base Integration

Enhanced KB integration for meeting context enrichment.
- Fetch relevant past decisions with reasoning
- Include related code locations
- Analyze project patterns for manager selection

Phase 3: KB-enhanced meetings
"""

from typing import Optional, List, Dict, Any
from pathlib import Path

# Knowledge Base integration
_HAS_KNOWLEDGE = False
try:
    from ...db.knowledge import (
        search_knowledge,
        get_recent_decisions,
        get_recent_locations,
        get_or_create_project,
        KNOWLEDGE_DB_PATH,
    )
    _HAS_KNOWLEDGE = KNOWLEDGE_DB_PATH.exists()
except ImportError:
    pass


def get_enriched_kb_context(
    context: str,
    topic: str,
    project_path: Optional[str] = None,
    max_decisions: int = 5,
    max_locations: int = 3,
    include_reasoning: bool = True,
) -> Optional[str]:
    """
    Get enriched Knowledge Base context for meeting.

    Enhanced version that includes:
    - Past decisions with reasoning
    - Related code locations
    - Locked decisions (important constraints)

    Args:
        context: Meeting context for relevance matching
        topic: Detected topic
        project_path: Project path for filtering
        max_decisions: Maximum decisions to include
        max_locations: Maximum code locations to include
        include_reasoning: Include decision reasoning

    Returns:
        Formatted KB context string or None
    """
    if not _HAS_KNOWLEDGE:
        return None

    try:
        # Get project ID
        project_id = None
        project_name = None
        if project_path:
            project_name = Path(project_path).name
            project_id = get_or_create_project(project_name, project_path)

        sections = []

        # 1. Search for topic-relevant decisions
        search_results = search_knowledge(topic, project_id=project_id, limit=max_decisions * 2)
        relevant_decisions = [r for r in search_results if r.get('type') == 'decision']

        # 2. Also search by context keywords
        context_keywords = _extract_keywords(context)
        for keyword in context_keywords[:3]:
            keyword_results = search_knowledge(keyword, project_id=project_id, limit=3)
            for r in keyword_results:
                if r.get('type') == 'decision' and r not in relevant_decisions:
                    relevant_decisions.append(r)

        # 3. Separate locked vs regular decisions
        locked_decisions = []
        regular_decisions = []

        for d in relevant_decisions[:max_decisions]:
            content = d.get('content', '')
            category = d.get('category', '')

            if 'locked:' in category or 'LOCKED' in content:
                locked_decisions.append(d)
            else:
                regular_decisions.append(d)

        # 4. Build locked decisions section (constraints)
        if locked_decisions:
            sections.append("### 🔒 제약사항 (변경 불가)")
            sections.append("_아래 결정은 LOCKED 상태입니다. 회의에서 이를 존중해주세요._\n")
            for d in locked_decisions[:3]:
                content = d.get('content', '')[:150]
                category = d.get('category', '').replace('locked:', '')
                sections.append(f"- **[{category}]** {content}...")

        # 5. Build related decisions section
        if regular_decisions:
            sections.append("\n### 📋 관련 과거 결정")
            for d in regular_decisions[:max_decisions - len(locked_decisions)]:
                content = d.get('content', '')[:120]
                category = d.get('category', '')

                decision_line = f"- **[{category}]** {content}..."

                # Add reasoning if available and enabled
                if include_reasoning:
                    reasoning = d.get('reasoning', '')
                    if reasoning:
                        decision_line += f"\n  _이유: {reasoning[:80]}..._"

                sections.append(decision_line)

        # 6. Get recent decisions (for general context)
        recent = get_recent_decisions(project_id=project_id, limit=3)
        recent_not_in_relevant = [
            d for d in recent
            if d.get('decision', '') not in [r.get('content', '') for r in relevant_decisions]
        ]

        if recent_not_in_relevant:
            sections.append("\n### 🕐 최근 결정사항")
            for d in recent_not_in_relevant[:2]:
                category = d.get('category', 'general')
                decision = d.get('decision', '')[:80]
                if category.startswith("locked:"):
                    category = category[7:]
                    sections.append(f"- **[{category}]** {decision}... *(LOCKED)*")
                else:
                    sections.append(f"- **[{category}]** {decision}...")

        # 7. Get related code locations
        locations = get_recent_locations(project_id=project_id, limit=max_locations * 2)

        # Filter locations by topic relevance
        relevant_locations = []
        for loc in locations:
            name = loc.get('name', '').lower()
            path = loc.get('path', '').lower()
            desc = loc.get('description', '').lower()

            # Check if location is relevant to topic
            topic_keywords = _get_topic_keywords(topic)
            if any(kw in name or kw in path or kw in desc for kw in topic_keywords):
                relevant_locations.append(loc)

        if relevant_locations:
            sections.append("\n### 📍 관련 코드 위치")
            for loc in relevant_locations[:max_locations]:
                name = loc.get('name', '')
                repo = loc.get('repo', '')
                path = loc.get('path', '')
                desc = loc.get('description', '')[:60] if loc.get('description') else ''

                loc_line = f"- **{name}**: `{repo}/{path}`"
                if desc:
                    loc_line += f"\n  _{desc}_"
                sections.append(loc_line)

        if sections:
            header = "## 💡 프로젝트 컨텍스트"
            if project_name:
                header += f" ({project_name})"
            header += "\n_아래 정보를 참고하여 회의를 진행하세요._\n"

            return header + "\n".join(sections)

        return None

    except Exception:
        return None


def analyze_project_patterns(project_path: str) -> Dict[str, Any]:
    """
    Analyze project patterns from KB history.

    Returns insights like:
    - Most common topics
    - Frequently involved managers
    - Key constraints (locked decisions)

    Args:
        project_path: Project root path

    Returns:
        Pattern analysis dict
    """
    if not _HAS_KNOWLEDGE:
        return {}

    try:
        project_name = Path(project_path).name
        project_id = get_or_create_project(project_name, project_path)

        # Get all decisions for this project
        decisions = get_recent_decisions(project_id=project_id, limit=100)

        if not decisions:
            return {}

        # Analyze categories
        category_counts = {}
        locked_count = 0

        for d in decisions:
            category = d.get('category', 'general')
            if category.startswith('locked:'):
                locked_count += 1
                category = category[7:]

            category_counts[category] = category_counts.get(category, 0) + 1

        # Map categories to topics
        category_to_topic = {
            'architecture': 'api',
            'security': 'security',
            'auth': 'auth',
            'payment': 'payment',
            'ui': 'ui',
            'design': 'design',
            'performance': 'performance',
            'cost': 'cost',
            'feature': 'feature',
        }

        topic_counts = {}
        for cat, count in category_counts.items():
            topic = category_to_topic.get(cat, 'feature')
            topic_counts[topic] = topic_counts.get(topic, 0) + count

        # Determine project focus
        sorted_topics = sorted(topic_counts.items(), key=lambda x: -x[1])
        primary_focus = sorted_topics[0][0] if sorted_topics else 'feature'

        # Recommend manager weights based on focus
        manager_weights = _get_manager_weights_for_focus(primary_focus, locked_count)

        return {
            'total_decisions': len(decisions),
            'locked_decisions': locked_count,
            'category_distribution': category_counts,
            'topic_focus': sorted_topics[:3],
            'primary_focus': primary_focus,
            'recommended_manager_weights': manager_weights,
        }

    except Exception:
        return {}


def get_recommended_managers(
    topic: str,
    project_path: Optional[str] = None,
) -> List[str]:
    """
    Get recommended managers for a topic, considering project patterns.

    Args:
        topic: Meeting topic
        project_path: Project path for pattern analysis

    Returns:
        Ordered list of recommended managers
    """
    # Default topic-based selection
    from ..manager.prompts import get_topic_guide
    guide = get_topic_guide(topic)
    default_managers = guide.get("participants", ["PM", "CTO", "QA"])

    # Always include PM
    if "PM" not in default_managers:
        default_managers = ["PM"] + default_managers

    # If no project path, return default
    if not project_path:
        return default_managers[:5]

    # Analyze project patterns
    patterns = analyze_project_patterns(project_path)
    if not patterns:
        return default_managers[:5]

    # Adjust based on project focus
    weights = patterns.get('recommended_manager_weights', {})
    if not weights:
        return default_managers[:5]

    # Score each manager
    manager_scores = {}
    all_managers = ["PM", "CTO", "QA", "CSO", "CDO", "CMO", "CFO", "ERROR"]

    for mgr in all_managers:
        # Base score: in default list
        score = 10 if mgr in default_managers else 0

        # Add weight from project patterns
        score += weights.get(mgr, 0)

        manager_scores[mgr] = score

    # Sort by score
    sorted_managers = sorted(manager_scores.items(), key=lambda x: -x[1])

    # Return top 5, ensuring PM is first
    result = [mgr for mgr, _ in sorted_managers[:5]]
    if "PM" not in result:
        result = ["PM"] + result[:4]
    elif result[0] != "PM":
        result.remove("PM")
        result = ["PM"] + result[:4]

    return result


def _extract_keywords(text: str) -> List[str]:
    """Extract relevant keywords from text."""
    # Simple keyword extraction
    words = text.lower().split()

    # Filter common words
    stop_words = {
        'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been',
        'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
        'would', 'could', 'should', 'may', 'might', 'must', 'shall',
        'to', 'of', 'in', 'for', 'on', 'with', 'at', 'by', 'from',
        'up', 'about', 'into', 'through', 'during', 'before', 'after',
        'above', 'below', 'between', 'under', 'again', 'further', 'then',
        'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all',
        'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
        'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
        'can', 'just', 'don', 'now', 'and', 'or', 'but', 'if', 'this',
        'that', 'these', 'those', 'what', 'which', 'who', 'whom',
        '기능', '추가', '구현', '개발', '작업', '하기', '위해', '대해',
    }

    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    return keywords[:10]


def _get_topic_keywords(topic: str) -> List[str]:
    """Get keywords associated with a topic."""
    topic_keywords = {
        'auth': ['auth', 'login', 'logout', 'session', 'token', 'jwt', 'oauth', 'password', '인증', '로그인'],
        'api': ['api', 'endpoint', 'rest', 'graphql', 'request', 'response', 'route', 'controller'],
        'payment': ['payment', 'stripe', 'billing', 'subscription', 'price', '결제', '구독'],
        'security': ['security', 'auth', 'permission', 'access', 'encrypt', 'ssl', 'https', '보안'],
        'ui': ['ui', 'ux', 'component', 'button', 'form', 'modal', 'style', 'css', 'design'],
        'performance': ['performance', 'speed', 'cache', 'optimize', 'slow', 'fast', '성능'],
        'error': ['error', 'exception', 'bug', 'fix', 'crash', 'fail', '에러', '오류'],
        'launch': ['launch', 'deploy', 'release', 'production', 'beta', '출시', '배포'],
        'cost': ['cost', 'price', 'budget', 'expense', 'aws', 'cloud', '비용'],
        'design': ['design', 'figma', 'color', 'theme', 'style', 'component', '디자인'],
        'maintenance': ['maintain', 'refactor', 'update', 'upgrade', 'migrate', '유지보수'],
    }

    return topic_keywords.get(topic, ['feature', 'function', 'module'])


def _get_manager_weights_for_focus(focus: str, locked_count: int) -> Dict[str, int]:
    """Get manager weight adjustments based on project focus."""
    base_weights = {
        'PM': 5,  # Always important
        'CTO': 3,
        'QA': 2,
        'CSO': 1,
        'CDO': 1,
        'CMO': 1,
        'CFO': 1,
        'ERROR': 1,
    }

    # Adjust based on focus
    focus_adjustments = {
        'security': {'CSO': 5, 'CTO': 2, 'QA': 2},
        'auth': {'CSO': 4, 'CTO': 3, 'QA': 2},
        'payment': {'CFO': 4, 'CSO': 3, 'QA': 3},
        'ui': {'CDO': 5, 'QA': 2, 'CMO': 2},
        'design': {'CDO': 5, 'CMO': 2},
        'performance': {'CTO': 4, 'ERROR': 3, 'QA': 2},
        'error': {'ERROR': 5, 'CTO': 3, 'QA': 3},
        'launch': {'CMO': 4, 'QA': 3, 'ERROR': 3},
        'cost': {'CFO': 5, 'CTO': 2},
        'api': {'CTO': 4, 'QA': 3, 'CSO': 2},
    }

    adjustments = focus_adjustments.get(focus, {})
    for mgr, adj in adjustments.items():
        base_weights[mgr] = base_weights.get(mgr, 0) + adj

    # If many locked decisions, increase CSO weight
    if locked_count > 5:
        base_weights['CSO'] = base_weights.get('CSO', 0) + 3

    return base_weights
