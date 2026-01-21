# Clouvel Manager Tool (Pro)
# 8명의 C-Level 매니저가 컨텍스트 기반 협업 피드백 제공

import re
from typing import Dict, Any, List, Set

# 8명의 매니저 정의
MANAGERS = {
    "PM": {
        "emoji": "👔",
        "title": "Product Manager",
        "focus": ["PRD", "기능", "우선순위", "스코프", "요구사항", "유저 스토리", "백로그"],
        "keywords": ["feature", "기능", "요구사항", "우선순위", "스코프", "prd", "spec", "요구", "목표", "mvp", "backlog"],
        "questions": [
            "이 기능이 PRD에 정의되어 있나요?",
            "MVP 범위에 포함되는 기능인가요?",
            "우선순위가 명확히 정의되어 있나요?",
            "사용자 스토리가 작성되어 있나요?",
            "성공 지표는 무엇인가요?"
        ],
        "checklist": [
            "PRD에 기능 정의 존재",
            "우선순위 태그 (P0/P1/P2)",
            "완료 조건 명시",
            "영향 범위 파악"
        ]
    },
    "CTO": {
        "emoji": "🛠️",
        "title": "Chief Technology Officer",
        "focus": ["아키텍처", "기술 스택", "성능", "확장성", "코드 품질", "기술 부채"],
        "keywords": ["architecture", "아키텍처", "성능", "performance", "scale", "확장", "기술", "stack", "database", "db", "api", "backend", "frontend", "infra", "deploy", "배포"],
        "questions": [
            "현재 아키텍처와 일관성이 있나요?",
            "성능 영향은 고려했나요?",
            "확장성 문제가 있을 수 있나요?",
            "기술 부채가 발생하지 않나요?",
            "기존 코드 패턴을 따르고 있나요?"
        ],
        "checklist": [
            "아키텍처 문서 업데이트",
            "성능 벤치마크",
            "기술 부채 평가",
            "코드 리뷰 완료"
        ]
    },
    "QA": {
        "emoji": "🧪",
        "title": "QA Manager",
        "focus": ["테스트", "엣지 케이스", "검증", "커버리지", "버그", "품질"],
        "keywords": ["test", "테스트", "검증", "verify", "qa", "bug", "버그", "edge", "엣지", "coverage", "커버리지", "assert", "expect", "unit", "e2e", "integration"],
        "questions": [
            "테스트 케이스가 작성되어 있나요?",
            "엣지 케이스를 고려했나요?",
            "실패 시나리오는 어떻게 처리되나요?",
            "테스트 커버리지는 충분한가요?",
            "회귀 테스트가 필요한가요?"
        ],
        "checklist": [
            "Unit Test 작성",
            "Integration Test 작성",
            "엣지 케이스 테스트",
            "에러 시나리오 테스트"
        ]
    },
    "CDO": {
        "emoji": "🎨",
        "title": "Chief Design Officer",
        "focus": ["UI/UX", "디자인", "접근성", "사용성", "AI 패턴 방지"],
        "keywords": ["ui", "ux", "design", "디자인", "component", "컴포넌트", "style", "스타일", "css", "layout", "레이아웃", "접근성", "accessibility", "a11y", "button", "input", "form"],
        "questions": [
            "디자인 시스템과 일관성이 있나요?",
            "접근성(a11y)을 고려했나요?",
            "AI스러운 패턴을 사용하고 있지 않나요?",
            "사용자 경험이 직관적인가요?",
            "반응형 디자인이 적용되어 있나요?"
        ],
        "checklist": [
            "디자인 시스템 준수",
            "접근성 검사 (WCAG)",
            "반응형 테스트",
            "AI 패턴 체크 (과도한 이모지, 불필요한 애니메이션 등)"
        ],
        "anti_patterns": [
            "과도한 이모지 사용",
            "불필요한 로딩 애니메이션",
            "복잡한 다단계 모달",
            "자동 재생 미디어"
        ]
    },
    "CMO": {
        "emoji": "📢",
        "title": "Chief Marketing Officer",
        "focus": ["GTM", "포지셔닝", "경쟁사", "메시징", "브랜딩"],
        "keywords": ["marketing", "마케팅", "brand", "브랜드", "message", "메시지", "landing", "랜딩", "copy", "카피", "gtm", "launch", "런칭", "competitor", "경쟁"],
        "questions": [
            "사용자에게 어떤 가치를 제공하나요?",
            "경쟁사 대비 차별점은 무엇인가요?",
            "메시지가 명확하고 일관성 있나요?",
            "브랜드 가이드라인을 따르고 있나요?",
            "타겟 사용자가 명확한가요?"
        ],
        "checklist": [
            "가치 제안 명확화",
            "경쟁사 분석",
            "타겟 페르소나 정의",
            "메시지 일관성 검토"
        ]
    },
    "CFO": {
        "emoji": "💰",
        "title": "Chief Financial Officer",
        "focus": ["비용", "수익화", "가격", "ROI", "예산"],
        "keywords": ["cost", "비용", "price", "가격", "revenue", "수익", "payment", "결제", "subscription", "구독", "billing", "budget", "예산", "roi", "monetization"],
        "questions": [
            "이 기능의 비용 영향은 어떻게 되나요?",
            "수익화 모델에 어떤 영향을 주나요?",
            "인프라 비용이 증가하나요?",
            "ROI가 측정 가능한가요?",
            "예산 범위 내인가요?"
        ],
        "checklist": [
            "인프라 비용 산정",
            "개발 비용 추정",
            "수익 영향 분석",
            "ROI 계산"
        ]
    },
    "CSO": {
        "emoji": "🔒",
        "title": "Chief Security Officer",
        "focus": ["보안", "인증", "권한", "취약점", "데이터 보호"],
        "keywords": ["security", "보안", "auth", "인증", "권한", "permission", "token", "jwt", "session", "encrypt", "암호화", "password", "비밀번호", "sql", "injection", "xss", "csrf", "vulnerability"],
        "questions": [
            "인증/인가가 제대로 구현되어 있나요?",
            "민감 데이터가 적절히 보호되나요?",
            "OWASP Top 10 취약점을 고려했나요?",
            "입력값 검증이 되어 있나요?",
            "보안 로깅이 적용되어 있나요?"
        ],
        "checklist": [
            "인증 체크",
            "권한 체크 (RLS 등)",
            "입력값 검증",
            "민감 데이터 암호화",
            "SQL Injection 방지",
            "XSS 방지"
        ],
        "critical_patterns": [
            "하드코딩된 시크릿",
            "평문 비밀번호",
            "SQL 문자열 연결",
            "innerHTML 직접 할당"
        ]
    },
    "ERROR": {
        "emoji": "🔥",
        "title": "Error Manager",
        "focus": ["에러 패턴", "5 Whys", "NEVER/ALWAYS 규칙", "예방", "재발 방지"],
        "keywords": ["error", "에러", "exception", "예외", "bug", "버그", "crash", "fail", "실패", "catch", "try", "throw", "debug", "디버그", "log", "로그", "trace"],
        "questions": [
            "이전에 비슷한 에러가 발생한 적이 있나요?",
            "에러의 근본 원인(Root Cause)은 무엇인가요?",
            "재발 방지를 위한 규칙이 필요한가요?",
            "에러 로깅이 적절히 되어 있나요?",
            "복구 전략은 무엇인가요?"
        ],
        "checklist": [
            "에러 로깅 구현",
            "에러 복구 전략",
            "5 Whys 분석",
            "NEVER/ALWAYS 규칙 추가",
            "모니터링 설정"
        ],
        "analysis_template": """
### 🔥 에러 분석 (5 Whys)

**문제**: {problem}

1. Why? →
2. Why? →
3. Why? →
4. Why? →
5. Why? → (Root Cause)

**예방 규칙**:
- NEVER:
- ALWAYS:
"""
    }
}

# 컨텍스트 기반 매니저 그룹핑
CONTEXT_GROUPS = {
    "auth": ["CSO", "CTO", "QA", "ERROR"],  # 인증/로그인
    "payment": ["CFO", "CSO", "CTO", "QA", "ERROR"],  # 결제
    "api": ["CTO", "QA", "CSO", "ERROR"],  # API 개발
    "ui": ["CDO", "PM", "QA"],  # UI 개발
    "feature": ["PM", "CTO", "QA"],  # 기능 개발
    "security": ["CSO", "CTO", "QA", "ERROR"],  # 보안
    "performance": ["CTO", "QA", "CFO"],  # 성능
    "launch": ["CMO", "PM", "CFO", "QA"],  # 런칭
    "error": ["ERROR", "CTO", "QA"],  # 에러 처리
    "design": ["CDO", "PM", "CMO"],  # 디자인
    "database": ["CTO", "CSO", "QA", "ERROR"],  # 데이터베이스
}


def manager(
    context: str,
    mode: str = "auto",
    managers: List[str] = None,
    include_checklist: bool = True
) -> Dict[str, Any]:
    """
    컨텍스트에 맞는 매니저들의 피드백을 제공합니다.

    Args:
        context: 검토할 내용 (플랜, 코드, 질문 등)
        mode: 'auto' (자동 감지), 'all' (전체), 'specific' (지정)
        managers: mode='specific'일 때 사용할 매니저 목록
        include_checklist: 체크리스트 포함 여부

    Returns:
        각 매니저의 피드백과 추천 사항
    """
    result = {
        "context_analysis": {},
        "active_managers": [],
        "feedback": {},
        "combined_checklist": [],
        "warnings": [],
        "recommendations": []
    }

    # 1. 컨텍스트 분석
    detected_contexts = _analyze_context(context)
    result["context_analysis"] = {
        "detected_topics": detected_contexts,
        "context_length": len(context)
    }

    # 2. 활성화할 매니저 결정
    if mode == "all":
        active_managers = list(MANAGERS.keys())
    elif mode == "specific" and managers:
        active_managers = [m.upper() for m in managers if m.upper() in MANAGERS]
    else:  # auto
        active_managers = _select_managers_by_context(context, detected_contexts)

    result["active_managers"] = active_managers

    # 3. 각 매니저의 피드백 생성
    for manager_key in active_managers:
        manager_info = MANAGERS[manager_key]
        feedback = _generate_feedback(manager_key, manager_info, context)
        result["feedback"][manager_key] = feedback

        # 체크리스트 통합
        if include_checklist:
            for item in manager_info.get("checklist", []):
                combined_item = f"[{manager_info['emoji']} {manager_key}] {item}"
                if combined_item not in result["combined_checklist"]:
                    result["combined_checklist"].append(combined_item)

        # 경고 수집
        if feedback.get("warnings"):
            result["warnings"].extend(feedback["warnings"])

    # 4. 종합 추천 사항
    result["recommendations"] = _generate_recommendations(result)

    # 5. 출력 포맷팅
    result["formatted_output"] = _format_output(result)

    return result


def _analyze_context(context: str) -> List[str]:
    """컨텍스트에서 주요 토픽을 감지합니다."""
    context_lower = context.lower()
    detected = []

    # 키워드 기반 감지
    topic_keywords = {
        "auth": ["login", "로그인", "auth", "인증", "session", "jwt", "token", "password", "비밀번호"],
        "payment": ["payment", "결제", "billing", "subscription", "구독", "price", "가격"],
        "api": ["api", "endpoint", "rest", "graphql", "request", "response"],
        "ui": ["ui", "component", "컴포넌트", "button", "input", "form", "style", "css"],
        "security": ["security", "보안", "encrypt", "암호화", "vulnerability", "취약점"],
        "performance": ["performance", "성능", "optimize", "최적화", "cache", "캐시"],
        "error": ["error", "에러", "exception", "예외", "bug", "버그", "fix"],
        "database": ["database", "db", "sql", "query", "migration", "schema"],
        "design": ["design", "디자인", "ux", "ui", "layout", "레이아웃"],
        "feature": ["feature", "기능", "implement", "구현", "add", "추가"],
        "launch": ["launch", "런칭", "deploy", "배포", "release", "릴리즈"]
    }

    for topic, keywords in topic_keywords.items():
        if any(kw in context_lower for kw in keywords):
            detected.append(topic)

    return detected if detected else ["feature"]  # 기본값


def _select_managers_by_context(context: str, detected_contexts: List[str]) -> List[str]:
    """컨텍스트에 맞는 매니저들을 선택합니다."""
    selected: Set[str] = set()

    # 감지된 컨텍스트에 해당하는 매니저 그룹 추가
    for ctx in detected_contexts:
        if ctx in CONTEXT_GROUPS:
            selected.update(CONTEXT_GROUPS[ctx])

    # 키워드 매칭으로 추가 매니저 선택
    context_lower = context.lower()
    for manager_key, manager_info in MANAGERS.items():
        for keyword in manager_info["keywords"]:
            if keyword in context_lower:
                selected.add(manager_key)
                break

    # 최소 PM, CTO는 항상 포함
    selected.add("PM")
    selected.add("CTO")

    # 정렬 (중요도 순)
    priority_order = ["PM", "CTO", "QA", "CSO", "CDO", "CMO", "CFO", "ERROR"]
    return [m for m in priority_order if m in selected]


def _generate_feedback(manager_key: str, manager_info: Dict, context: str) -> Dict[str, Any]:
    """매니저별 피드백을 생성합니다."""
    feedback = {
        "emoji": manager_info["emoji"],
        "title": manager_info["title"],
        "focus": manager_info["focus"],
        "questions": [],
        "concerns": [],
        "warnings": [],
        "approval_status": "REVIEW_NEEDED"
    }

    context_lower = context.lower()

    # 관련 질문 선택
    for question in manager_info["questions"]:
        # 질문이 컨텍스트와 관련있으면 추가
        question_keywords = question.lower().split()
        if any(kw in context_lower for kw in question_keywords[:3]):
            feedback["questions"].append(question)

    # 질문이 없으면 처음 2개 질문 추가
    if not feedback["questions"]:
        feedback["questions"] = manager_info["questions"][:2]

    # 경고 패턴 체크
    if manager_key == "CSO":
        critical_patterns = manager_info.get("critical_patterns", [])
        for pattern in critical_patterns:
            if pattern.lower() in context_lower or _check_pattern(pattern, context):
                feedback["warnings"].append(f"⚠️ 보안 위험: {pattern}")
                feedback["approval_status"] = "BLOCKED"

    if manager_key == "CDO":
        anti_patterns = manager_info.get("anti_patterns", [])
        for pattern in anti_patterns:
            if pattern.lower() in context_lower:
                feedback["concerns"].append(f"🎨 디자인 우려: {pattern}")

    if manager_key == "ERROR":
        if "error" in context_lower or "exception" in context_lower:
            feedback["concerns"].append("🔥 에러 처리 로직 검토 필요")
            feedback["questions"].append("5 Whys 분석이 완료되었나요?")

    return feedback


def _check_pattern(pattern: str, context: str) -> bool:
    """특정 패턴이 컨텍스트에 있는지 체크합니다."""
    pattern_checks = {
        "하드코딩된 시크릿": r'["\'](?:sk_|api_key|secret|password)["\']?\s*[:=]\s*["\'][^"\']+["\']',
        "평문 비밀번호": r'password\s*[:=]\s*["\'][^"\']+["\']',
        "SQL 문자열 연결": r'(?:SELECT|INSERT|UPDATE|DELETE).*\+.*(?:str\(|f"|\')',
        "innerHTML 직접 할당": r'innerHTML\s*=',
    }

    regex = pattern_checks.get(pattern)
    if regex:
        return bool(re.search(regex, context, re.IGNORECASE))
    return False


def _generate_recommendations(result: Dict) -> List[str]:
    """종합 추천 사항을 생성합니다."""
    recommendations = []

    # 경고가 있으면 우선 처리
    if result["warnings"]:
        recommendations.append("🚨 보안 경고를 먼저 해결하세요")

    # 활성 매니저 수에 따른 추천
    active_count = len(result["active_managers"])
    if active_count >= 5:
        recommendations.append("📋 복잡한 작업입니다. 단계별로 진행하세요")

    # 특정 매니저 조합에 따른 추천
    managers = result["active_managers"]
    if "CSO" in managers and "CTO" in managers:
        recommendations.append("🔐 보안 리뷰를 코드 리뷰와 함께 진행하세요")

    if "CFO" in managers:
        recommendations.append("💰 비용 영향을 문서화하세요")

    if "ERROR" in managers:
        recommendations.append("📝 에러 처리 로직과 복구 전략을 명시하세요")

    return recommendations


def _format_output(result: Dict) -> str:
    """결과를 읽기 좋은 형식으로 포맷팅합니다."""
    lines = []

    lines.append("=" * 50)
    lines.append("🏢 C-LEVEL MANAGER REVIEW")
    lines.append("=" * 50)
    lines.append("")

    # 활성 매니저
    manager_icons = " ".join([
        f"{MANAGERS[m]['emoji']}" for m in result["active_managers"]
    ])
    lines.append(f"**활성 매니저**: {manager_icons}")
    lines.append(f"**감지된 토픽**: {', '.join(result['context_analysis']['detected_topics'])}")
    lines.append("")

    # 경고
    if result["warnings"]:
        lines.append("### ⚠️ 경고")
        for warning in result["warnings"]:
            lines.append(f"  {warning}")
        lines.append("")

    # 각 매니저 피드백
    lines.append("### 💬 피드백")
    lines.append("")

    for manager_key in result["active_managers"]:
        feedback = result["feedback"][manager_key]
        lines.append(f"#### {feedback['emoji']} {feedback['title']}")

        if feedback["questions"]:
            lines.append("**질문:**")
            for q in feedback["questions"][:3]:
                lines.append(f"  - {q}")

        if feedback["concerns"]:
            lines.append("**우려사항:**")
            for c in feedback["concerns"]:
                lines.append(f"  - {c}")

        lines.append("")

    # 체크리스트
    if result["combined_checklist"]:
        lines.append("### ✅ 체크리스트")
        for item in result["combined_checklist"][:10]:
            lines.append(f"  - [ ] {item}")
        lines.append("")

    # 추천 사항
    if result["recommendations"]:
        lines.append("### 💡 추천")
        for rec in result["recommendations"]:
            lines.append(f"  {rec}")
        lines.append("")

    lines.append("=" * 50)

    return "\n".join(lines)


# 단일 매니저 호출용 헬퍼
def ask_manager(manager_key: str, question: str) -> Dict[str, Any]:
    """특정 매니저에게 질문합니다."""
    manager_key = manager_key.upper()
    if manager_key not in MANAGERS:
        return {"error": f"Unknown manager: {manager_key}"}

    return manager(
        context=question,
        mode="specific",
        managers=[manager_key]
    )


# 매니저 목록 조회
def list_managers() -> List[Dict[str, str]]:
    """사용 가능한 매니저 목록을 반환합니다."""
    return [
        {
            "key": key,
            "emoji": info["emoji"],
            "title": info["title"],
            "focus": ", ".join(info["focus"][:3])
        }
        for key, info in MANAGERS.items()
    ]
