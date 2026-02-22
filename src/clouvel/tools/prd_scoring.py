# -*- coding: utf-8 -*-
"""PRD Quality Scoring Engine — DEAD framework.

Evaluates PRD content using regex/keyword analysis.
No NLP libraries, no LLM API calls. Free tier compatible.

Scoring: DEAD (Decision, Evidence, Alternatives, Doomsday) + Out of Scope
Anti-gaming: pair rules, If/Then structure, fake detection, banned phrases, density check.
"""

import re
from dataclasses import dataclass, field

# ============================================================
# Constants
# ============================================================

BASE_SCORE = 30  # PRD file exists

# DEAD check definitions
DEAD_CHECKS = {
    "decision": {
        "keywords_ko": ["결정", "선택", "채택", "사용하기로", "기술스택", "기술 스택"],
        "keywords_en": ["decision", "chose", "selected", "adopted", "tech stack", "pricing", "decided"],
        "min_matches": 3,
        "score": 15,
        "label": "Decision (결정 흔적)",
        "hint": "기술스택, 데이터 모델, 인증 방식 중 어떤 결정을 했나요?",
    },
    "evidence": {
        "keywords_ko": ["인터뷰", "데이터", "조사", "피드백", "사용자", "불편", "요청"],
        "keywords_en": ["interview", "data", "research", "feedback", "user", "survey", "pain"],
        "url_pattern": r"https?://\S+",
        "min_matches": 2,
        "score": 10,
        "label": "Evidence (근거/증거)",
        "hint": "어떤 근거로 이 문제가 실제로 존재한다고 판단했나요?",
    },
    "alternatives": {
        "keywords_ko": ["대안", "비교", "대신", "선택하지 않은", "고려했", "검토했"],
        "keywords_en": ["alternative", "vs", "compared", "instead", "rejected", "trade-?off"],
        "pair_keywords_ko": ["이유", "때문", "단점", "한계", "부족"],
        "pair_keywords_en": ["reason", "because", "downside", "tradeoff", "limitation"],
        "min_matches": 1,
        "score": 15,
        "label": "Alternatives (대안/포기 이유)",
        "hint": "왜 다른 방법을 안 썼나요? (예: Firebase 대신 Supabase — 이유는?)",
    },
    "doomsday": {
        "keywords_ko": ["실패", "리스크", "만약", "에러", "장애", "복구"],
        "keywords_en": ["fail", "risk", "if", "error", "worst case", "fallback", "retry", "crash"],
        "if_then_patterns": [
            r"만약\s*.+[면].*[→\-]",          # 만약 ~면 → ~
            r"if\s+.+then",                     # if...then
            r"[~면을시]\s*[→\->:]\s*\S+",       # ~면 → 대응
            r"실패\s*시\s*.+",                  # 실패 시 ~
            r"error.{0,20}(handle|처리|대응)",  # error handling
            r"fallback.{0,30}",                 # fallback ~
        ],
        "min_if_then": 1,
        "min_matches": 2,
        "score": 15,
        "label": "Doomsday (실패 시나리오)",
        "hint": "서비스가 다운되거나 에러가 나면 어떻게 대응하나요?",
    },
}

OUT_OF_SCOPE_KEYWORDS_KO = ["안 할", "하지 않", "제외", "포함하지 않", "범위 밖", "나중에"]
OUT_OF_SCOPE_KEYWORDS_EN = ["out of scope", "non-goal", "not included", "won't build", "excluded", "deferred"]
OUT_OF_SCOPE_SECTION_PATTERNS = [
    r"##\s*(out\s*of\s*scope|non.?goals?|하지\s*않을|제외|범위\s*제외|안\s*할\s*것)",
]
OUT_OF_SCOPE_SCORE = 15

# Penalties
ABSTRACT_WORDS = [
    "혁신", "최적", "강력한", "효율적", "최고", "완벽", "세계적",
    "seamless", "robust", "efficient", "innovative", "optimal", "cutting-edge", "world-class",
]
ABSTRACT_THRESHOLD = 5
ABSTRACT_PENALTY = -10

NUMBER_PATTERN = r"\d+\s*[%명개일월만원$]"
NUMBER_MIN = 3
NUMBER_PENALTY = -10

BANNED_PHRASES = ["TBD", "추후 결정", "적절히", "필요시", "추후 논의", "나중에 결정", "to be decided", "to be determined"]
BANNED_THRESHOLD = 3
BANNED_PENALTY = -5

# Caps
CAP_NO_SCOPE = 55
CAP_NO_ALTERNATIVES = 65

# Level thresholds
LEVEL_THRESHOLDS = {
    "lite": {"block": 40, "pass": 60},
    "standard": {"block": 50, "pass": 70},
    "ship": {"block": 60, "pass": 75},
}

# Max missing items to show
MAX_MISSING_DISPLAY = 3

# Minimum paragraph density (chars) around keyword for validity
MIN_KEYWORD_DENSITY = 30


# ============================================================
# Helper Functions
# ============================================================

def _get_paragraphs(content: str) -> list[str]:
    """Split content into paragraphs (double newline separated)."""
    return [p.strip() for p in re.split(r"\n\s*\n", content) if p.strip()]


def _count_keyword_matches(content: str, keywords_ko: list, keywords_en: list,
                           url_pattern: str = None) -> list[str]:
    """Count valid keyword matches with density check.

    Returns list of matched text snippets (for reporting).
    """
    matches = []
    paragraphs = _get_paragraphs(content)

    all_keywords = keywords_ko + keywords_en

    for para in paragraphs:
        if len(para) < MIN_KEYWORD_DENSITY:
            continue  # Skip too-short paragraphs

        for kw in all_keywords:
            if re.search(re.escape(kw), para, re.IGNORECASE):
                # Extract a snippet around the keyword
                snippet = para[:80].replace("\n", " ")
                if snippet not in matches:
                    matches.append(snippet)
                break  # One match per paragraph

    # URL matches (special case for evidence)
    if url_pattern:
        for para in paragraphs:
            if len(para) < MIN_KEYWORD_DENSITY:
                continue
            urls = re.findall(url_pattern, para)
            for url in urls:
                snippet = f"URL: {url[:60]}"
                if snippet not in matches:
                    matches.append(snippet)

    return matches


def _check_pair_rule(content: str, primary_ko: list, primary_en: list,
                     pair_ko: list, pair_en: list) -> list[str]:
    """Check pair rule: primary keyword + reason keyword within adjacent 2 lines.

    Returns valid matches only (where both primary and pair keywords co-occur).
    """
    matches = []
    lines = content.split("\n")

    primary_all = primary_ko + primary_en
    pair_all = pair_ko + pair_en

    for i, line in enumerate(lines):
        # Check if primary keyword in this line
        has_primary = any(re.search(re.escape(kw), line, re.IGNORECASE) for kw in primary_all)
        if not has_primary:
            continue

        # Check adjacent lines (current + next 2) for pair keyword
        window = "\n".join(lines[max(0, i):min(len(lines), i + 3)])
        has_pair = any(re.search(re.escape(kw), window, re.IGNORECASE) for kw in pair_all)

        if has_pair and len(line.strip()) >= MIN_KEYWORD_DENSITY:
            snippet = line.strip()[:80]
            if snippet not in matches:
                matches.append(snippet)

    return matches


def _check_if_then(content: str, patterns: list[str]) -> list[str]:
    """Check for If/Then patterns in content."""
    matches = []
    for pattern in patterns:
        found = re.findall(pattern, content, re.IGNORECASE | re.MULTILINE)
        for m in found:
            text = m if isinstance(m, str) else str(m)
            snippet = text.strip()[:80]
            if snippet and snippet not in matches:
                matches.append(snippet)
    return matches


def _check_fake(content: str, keywords_ko: list, keywords_en: list) -> int:
    """Detect fake fills: keyword immediately followed by negation.

    Returns count of fake matches (to subtract from valid matches).
    """
    fake_count = 0
    all_keywords = keywords_ko + keywords_en
    negations = ["없", "TBD", "모름", "미정", "없음", "N/A", "none", "not yet", "to be"]

    for kw in all_keywords:
        for neg in negations:
            pattern = re.escape(kw) + r".{0,25}" + re.escape(neg)
            if re.search(pattern, content, re.IGNORECASE):
                fake_count += 1
                break  # One fake per keyword

    return fake_count


def _has_out_of_scope_section(content: str) -> bool:
    """Check if Out of Scope section header exists."""
    for pattern in OUT_OF_SCOPE_SECTION_PATTERNS:
        if re.search(pattern, content, re.IGNORECASE | re.MULTILINE):
            return True
    return False


def _count_out_of_scope_content(content: str) -> list[str]:
    """Count Out of Scope keywords in content."""
    matches = []
    all_kw = OUT_OF_SCOPE_KEYWORDS_KO + OUT_OF_SCOPE_KEYWORDS_EN
    paragraphs = _get_paragraphs(content)

    for para in paragraphs:
        if len(para) < MIN_KEYWORD_DENSITY:
            continue
        for kw in all_kw:
            if re.search(re.escape(kw), para, re.IGNORECASE):
                snippet = para[:80].replace("\n", " ")
                if snippet not in matches:
                    matches.append(snippet)
                break

    return matches


def _count_abstract_words(content: str) -> int:
    """Count abstract/vague words."""
    count = 0
    for word in ABSTRACT_WORDS:
        count += len(re.findall(re.escape(word), content, re.IGNORECASE))
    return count


def _count_specific_numbers(content: str) -> int:
    """Count specific numbers with units."""
    return len(re.findall(NUMBER_PATTERN, content))


def _count_banned_phrases(content: str) -> int:
    """Count banned placeholder phrases."""
    count = 0
    for phrase in BANNED_PHRASES:
        count += len(re.findall(re.escape(phrase), content, re.IGNORECASE))
    return count


# ============================================================
# Main Scoring Function
# ============================================================

@dataclass
class CheckResult:
    name: str
    label: str
    score: int
    max_score: int
    passed: bool
    matches: list = field(default_factory=list)
    hint: str = ""


@dataclass
class ScoringResult:
    total_score: int
    grade: str  # "BLOCK" | "WARN" | "PASS"
    level: str
    checks: list  # list of CheckResult
    penalties: list  # list of (reason, points)
    caps: list  # list of (reason, cap_value)
    missing: list  # list of {item, potential, hint} — top 3
    estimated_if_fixed: int
    raw_score: int  # before caps


def score_prd(content: str, level: str = "lite") -> ScoringResult:
    """Score PRD content using DEAD framework.

    Args:
        content: PRD markdown content
        level: "lite" | "standard" | "ship"

    Returns:
        ScoringResult with detailed breakdown
    """
    if level not in LEVEL_THRESHOLDS:
        level = "lite"

    checks = []
    total = BASE_SCORE
    missing_items = []

    # ── Decision ──
    cfg = DEAD_CHECKS["decision"]
    matches = _count_keyword_matches(content, cfg["keywords_ko"], cfg["keywords_en"])
    fakes = _check_fake(content, cfg["keywords_ko"], cfg["keywords_en"])
    valid = max(0, len(matches) - fakes)
    passed = valid >= cfg["min_matches"]
    score = cfg["score"] if passed else 0
    total += score
    checks.append(CheckResult(
        name="decision", label=cfg["label"], score=score,
        max_score=cfg["score"], passed=passed, matches=matches[:5],
        hint=cfg["hint"],
    ))
    if not passed:
        missing_items.append({"item": cfg["label"], "potential": cfg["score"], "hint": cfg["hint"]})

    # ── Evidence ──
    cfg = DEAD_CHECKS["evidence"]
    matches = _count_keyword_matches(
        content, cfg["keywords_ko"], cfg["keywords_en"],
        url_pattern=cfg.get("url_pattern"),
    )
    fakes = _check_fake(content, cfg["keywords_ko"], cfg["keywords_en"])
    valid = max(0, len(matches) - fakes)
    passed = valid >= cfg["min_matches"]
    score = cfg["score"] if passed else 0
    total += score
    checks.append(CheckResult(
        name="evidence", label=cfg["label"], score=score,
        max_score=cfg["score"], passed=passed, matches=matches[:5],
        hint=cfg["hint"],
    ))
    if not passed:
        missing_items.append({"item": cfg["label"], "potential": cfg["score"], "hint": cfg["hint"]})

    # ── Alternatives (with pair rule) ──
    cfg = DEAD_CHECKS["alternatives"]
    pair_matches = _check_pair_rule(
        content,
        cfg["keywords_ko"], cfg["keywords_en"],
        cfg["pair_keywords_ko"], cfg["pair_keywords_en"],
    )
    # Also count basic keyword matches (softer fallback)
    basic_matches = _count_keyword_matches(content, cfg["keywords_ko"], cfg["keywords_en"])
    fakes = _check_fake(content, cfg["keywords_ko"], cfg["keywords_en"])

    # Pair matches count full, basic matches count half
    effective = len(pair_matches) + max(0, len(basic_matches) - len(pair_matches) - fakes) * 0.5
    passed = effective >= cfg["min_matches"]
    score = cfg["score"] if passed else 0
    total += score
    all_matches = pair_matches or basic_matches
    checks.append(CheckResult(
        name="alternatives", label=cfg["label"], score=score,
        max_score=cfg["score"], passed=passed, matches=all_matches[:5],
        hint=cfg["hint"],
    ))
    if not passed:
        missing_items.append({"item": cfg["label"], "potential": cfg["score"], "hint": cfg["hint"]})

    # ── Doomsday (with If/Then) ──
    cfg = DEAD_CHECKS["doomsday"]
    keyword_matches = _count_keyword_matches(content, cfg["keywords_ko"], cfg["keywords_en"])
    if_then_matches = _check_if_then(content, cfg["if_then_patterns"])
    fakes = _check_fake(content, cfg["keywords_ko"], cfg["keywords_en"])

    # Need both keyword matches AND If/Then patterns
    keyword_valid = max(0, len(keyword_matches) - fakes) >= cfg["min_matches"]
    if_then_valid = len(if_then_matches) >= cfg["min_if_then"]
    passed = keyword_valid and if_then_valid
    # Partial credit: keywords without If/Then = half score
    if keyword_valid and not if_then_valid:
        score = cfg["score"] // 2
    elif passed:
        score = cfg["score"]
    else:
        score = 0
    total += score
    all_matches = keyword_matches[:3] + if_then_matches[:3]
    checks.append(CheckResult(
        name="doomsday", label=cfg["label"], score=score,
        max_score=cfg["score"], passed=passed, matches=all_matches[:5],
        hint=cfg["hint"],
    ))
    if not passed:
        remaining = cfg["score"] - score
        if remaining > 0:
            missing_items.append({"item": cfg["label"], "potential": remaining, "hint": cfg["hint"]})

    # ── Out of Scope ──
    has_section = _has_out_of_scope_section(content)
    scope_matches = _count_out_of_scope_content(content)
    scope_passed = has_section or len(scope_matches) >= 2
    scope_score = OUT_OF_SCOPE_SCORE if scope_passed else 0
    total += scope_score
    checks.append(CheckResult(
        name="out_of_scope", label="Out of Scope (범위 제한)",
        score=scope_score, max_score=OUT_OF_SCOPE_SCORE,
        passed=scope_passed, matches=scope_matches[:3],
        hint="이 버전에서 절대 안 만들 기능 2가지는?",
    ))
    if not scope_passed:
        missing_items.append({
            "item": "Out of Scope (범위 제한)",
            "potential": OUT_OF_SCOPE_SCORE,
            "hint": "이 버전에서 절대 안 만들 기능 2가지는?",
        })

    # ── Penalties ──
    penalties = []

    abstract_count = _count_abstract_words(content)
    if abstract_count >= ABSTRACT_THRESHOLD:
        penalties.append((f"추상어 {abstract_count}개 감지", ABSTRACT_PENALTY))
        total += ABSTRACT_PENALTY

    number_count = _count_specific_numbers(content)
    if number_count < NUMBER_MIN:
        penalties.append((f"구체적 숫자 {number_count}개 (최소 {NUMBER_MIN}개)", NUMBER_PENALTY))
        total += NUMBER_PENALTY

    banned_count = _count_banned_phrases(content)
    if banned_count >= BANNED_THRESHOLD:
        penalties.append((f"금지 문구 {banned_count}개 감지 (TBD 등)", BANNED_PENALTY))
        total += BANNED_PENALTY

    # ── Caps ──
    raw_score = total
    caps = []

    if not scope_passed and total > CAP_NO_SCOPE:
        caps.append((f"Out of Scope 없음 → max {CAP_NO_SCOPE}", CAP_NO_SCOPE))
        total = CAP_NO_SCOPE

    alt_check = next((c for c in checks if c.name == "alternatives"), None)
    if alt_check and not alt_check.passed and total > CAP_NO_ALTERNATIVES:
        caps.append((f"Alternatives 없음 → max {CAP_NO_ALTERNATIVES}", CAP_NO_ALTERNATIVES))
        total = min(total, CAP_NO_ALTERNATIVES)

    # Clamp
    total = max(0, min(100, total))

    # ── Grade ──
    thresholds = LEVEL_THRESHOLDS[level]
    if total < thresholds["block"]:
        grade = "BLOCK"
    elif total < thresholds["pass"]:
        grade = "WARN"
    else:
        grade = "PASS"

    # ── Estimated score if fixed ──
    estimated = total
    for item in missing_items[:MAX_MISSING_DISPLAY]:
        estimated += item["potential"]
    # Remove penalty effects for estimate
    for _, pen in penalties:
        estimated -= pen  # subtract negative = add
    estimated = min(100, estimated)

    # Sort missing by potential (highest first), limit to 3
    missing_items.sort(key=lambda x: x["potential"], reverse=True)
    missing_display = missing_items[:MAX_MISSING_DISPLAY]

    return ScoringResult(
        total_score=total,
        grade=grade,
        level=level,
        checks=checks,
        penalties=penalties,
        caps=caps,
        missing=missing_display,
        estimated_if_fixed=estimated,
        raw_score=raw_score,
    )


def format_score_report(result: ScoringResult) -> str:
    """Format scoring result as human-readable report for can_code output."""
    parts = []

    # Header
    parts.append(f"\n📊 PRD Quality: {result.total_score}/100 ({result.grade})")

    # Passed checks
    passed = [c for c in result.checks if c.passed]
    if passed:
        labels = ", ".join(c.label.split(" (")[0] for c in passed)
        parts.append(f"  ✅ PASS: {labels}")

    # Missing (top 3)
    for item in result.missing:
        parts.append(f"  ❌ MISSING (+{item['potential']}): {item['item']}")
        parts.append(f"     → {item['hint']}")

    # Penalties
    for reason, points in result.penalties:
        parts.append(f"  ⚠️ {reason} ({points:+d}점)")

    # Caps
    for reason, _ in result.caps:
        parts.append(f"  🔒 {reason}")

    # Estimate
    if result.missing and result.estimated_if_fixed > result.total_score:
        parts.append(f"\n  채우면 예상 점수: {result.estimated_if_fixed}/100")

    return "\n".join(parts)
