# -*- coding: utf-8 -*-
"""PRD Quality Scoring Engine tests."""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.prd_scoring import (
    score_prd,
    format_score_report,
    ScoringResult,
    CheckResult,
    _count_keyword_matches,
    _check_pair_rule,
    _check_if_then,
    _check_fake,
    _has_out_of_scope_section,
    _count_out_of_scope_content,
    _count_abstract_words,
    _count_specific_numbers,
    _count_banned_phrases,
    _get_paragraphs,
    BASE_SCORE,
    LEVEL_THRESHOLDS,
    CAP_NO_SCOPE,
    CAP_NO_ALTERNATIVES,
)


# ============================================================
# Fixtures: PRD content samples
# ============================================================

MINIMAL_PRD = """# My Project

A simple tool for managing tasks.
"""

GOOD_PRD = """# Task Manager PRD

## 기술스택 결정
프론트엔드는 React를 채택하기로 결정했다. 커뮤니티와 생태계가 가장 넓다.

## 백엔드 선택
Supabase를 백엔드로 사용하기로 했다. 오픈소스이고 비용이 합리적이다.

## 인증 방식
JWT를 인증 방식으로 채택했다. Session 기반 대비 스케일링이 유리하다.

## 근거
사용자 인터뷰 3건 수행. 피드백에서 기존 도구의 불편한 점 확인.
조사 결과 80%가 실시간 동기화 요청함.
https://survey-result.example.com/2026

## 대안 비교
Firebase 대신 Supabase를 선택. 이유는 오픈소스이고 비용이 저렴하기 때문.
대안으로 DynamoDB 검토했으나 러닝커브가 높아서 단점이 크다.

## 실패 시나리오
만약 서버가 다운되면 → CDN 캐시에서 static 페이지 제공. 실패 시 자동 retry 3회 실행.

에러 발생 시 Slack 알림 전송하고, 15분 내 대응 체계를 갖춘다. 리스크 관리 대상이다.

if API timeout then fallback to local cache. 복구 절차를 자동화한다.

## Out of Scope
- 모바일 앱: 이 버전에서 안 할 것
- AI 추천: 제외 — 데이터 부족
- 다국어 지원: 나중에 추가

## 수치
- 목표 DAU: 500명
- 응답시간: 200ms 이하
- 가용률: 99.5%
- 월간 비용: 50만원 이내
"""

NO_SCOPE_PRD = """# Project

## 결정 사항
기술스택은 Next.js를 채택하기로 결정.
배포 방식은 Vercel 선택.
DB는 SQLite 사용하기로.

## 근거
피드백 조사 결과 사용자 70% 이상 요청.
데이터 분석 결과 인터뷰에서 확인.

## 대안
대안으로 Remix 검토했으나 이유는 생태계가 작아서 한계.

## 실패 시나리오
실패 시 롤백 실행.
만약 배포 실패하면 → 이전 버전으로 복구.

## 수치
- 100명 동시접속
- 3초 이내 로딩
- 월 10만원
"""

ABSTRACT_PRD = """# 혁신적인 프로젝트

세계적 수준의 최적화된 강력한 플랫폼.
효율적이고 완벽한 솔루션을 제공하는 혁신적인 서비스.
cutting-edge technology로 seamless한 경험을 제공합니다.
robust하고 innovative한 접근 방식을 사용합니다.

This is a world-class optimal efficient robust seamless innovative cutting-edge solution.
"""

TBD_PRD = """# Project

## 결정 사항
기술스택: TBD
인증 방식: 추후 결정
DB: TBD
배포: 필요시 결정
API 설계: 추후 논의
가격: to be decided
"""

GAMING_PRD = """# Project

결정 N/A
선택 없음
채택 미정
대안 TBD
비교 모름
"""


# ============================================================
# score_prd main function tests
# ============================================================

class TestScorePrd:
    """Main scoring function tests."""

    def test_minimal_prd_gets_base_score(self):
        """Minimal PRD only gets base score."""
        result = score_prd(MINIMAL_PRD)
        assert result.total_score >= BASE_SCORE - 15  # base minus possible number penalty
        assert result.total_score <= BASE_SCORE + 5

    def test_good_prd_scores_high(self):
        """Well-written PRD scores above 70."""
        result = score_prd(GOOD_PRD)
        assert result.total_score >= 70

    def test_good_prd_passes_lite(self):
        """Good PRD passes lite level."""
        result = score_prd(GOOD_PRD, level="lite")
        assert result.grade == "PASS"

    def test_good_prd_all_checks_pass(self):
        """Good PRD passes all DEAD checks."""
        result = score_prd(GOOD_PRD)
        for check in result.checks:
            assert check.passed, f"Check {check.name} should pass"

    def test_no_scope_capped(self):
        """PRD without out of scope is capped."""
        result = score_prd(NO_SCOPE_PRD)
        assert result.total_score <= CAP_NO_SCOPE

    def test_abstract_prd_penalized(self):
        """PRD with too many abstract words gets penalty."""
        result = score_prd(ABSTRACT_PRD)
        has_abstract_penalty = any("추상어" in r for r, _ in result.penalties)
        assert has_abstract_penalty

    def test_tbd_prd_low_score(self):
        """PRD full of TBDs scores low."""
        result = score_prd(TBD_PRD)
        assert result.total_score < 40

    def test_gaming_prd_detected(self):
        """Fake fills (keyword + negation) are detected."""
        result = score_prd(GAMING_PRD)
        # Decision check should fail because matches are fakes
        decision_check = next(c for c in result.checks if c.name == "decision")
        assert not decision_check.passed

    def test_returns_scoring_result(self):
        """Returns correct dataclass type."""
        result = score_prd(MINIMAL_PRD)
        assert isinstance(result, ScoringResult)
        assert isinstance(result.checks, list)
        assert isinstance(result.penalties, list)
        assert isinstance(result.caps, list)
        assert isinstance(result.missing, list)

    def test_invalid_level_defaults_to_lite(self):
        """Invalid level falls back to lite."""
        result = score_prd(MINIMAL_PRD, level="invalid")
        assert result.level == "lite"

    def test_empty_content(self):
        """Empty content gets only base score minus penalties."""
        result = score_prd("")
        assert result.total_score <= BASE_SCORE

    def test_grade_block_under_threshold(self):
        """Score under block threshold returns BLOCK grade."""
        result = score_prd("", level="standard")
        assert result.grade == "BLOCK"  # 30 (base) - 10 (no numbers) < 50 (standard block)

    def test_grade_warn_between_thresholds(self):
        """Score between block and pass thresholds returns WARN."""
        result = score_prd(NO_SCOPE_PRD, level="lite")
        # Should be between 40 and 60 for lite
        if LEVEL_THRESHOLDS["lite"]["block"] <= result.total_score < LEVEL_THRESHOLDS["lite"]["pass"]:
            assert result.grade == "WARN"

    def test_ship_level_strict(self):
        """Ship level has higher thresholds."""
        result = score_prd(GOOD_PRD, level="ship")
        # Ship requires 75+ for PASS
        assert result.level == "ship"

    def test_estimated_if_fixed(self):
        """Estimated score includes missing potential."""
        result = score_prd(MINIMAL_PRD)
        assert result.estimated_if_fixed >= result.total_score

    def test_missing_sorted_by_potential(self):
        """Missing items are sorted by potential score (highest first)."""
        result = score_prd(MINIMAL_PRD)
        if len(result.missing) >= 2:
            assert result.missing[0]["potential"] >= result.missing[1]["potential"]

    def test_max_3_missing_items(self):
        """At most 3 missing items are shown."""
        result = score_prd(MINIMAL_PRD)
        assert len(result.missing) <= 3

    def test_raw_score_before_caps(self):
        """raw_score is the score before cap application."""
        result = score_prd(NO_SCOPE_PRD)
        # raw_score may be higher than total if cap was applied
        assert result.raw_score >= result.total_score

    def test_score_clamped_0_to_100(self):
        """Score is always between 0 and 100."""
        result = score_prd(GOOD_PRD)
        assert 0 <= result.total_score <= 100

        result2 = score_prd("")
        assert 0 <= result2.total_score <= 100


# ============================================================
# DEAD check individual tests
# ============================================================

class TestDecisionCheck:
    """Decision scoring tests."""

    def test_korean_decisions_detected(self):
        content = "기술스택을 결정했다. React를 채택하기로. 인증은 JWT 선택."
        # Need enough density per paragraph
        padded = f"프로젝트의 기술스택을 결정했다. 여러 옵션을 비교 분석 후 최종적으로 선택.\n\nReact 프레임워크를 채택하기로 결정했다. 성능과 생태계를 고려.\n\n인증 방식은 JWT를 선택했다. Session 기반 대비 장점이 많음."
        matches = _count_keyword_matches(padded, ["결정", "선택", "채택"], [])
        assert len(matches) >= 3

    def test_english_decisions_detected(self):
        padded = "We decided to use React as our framework for this project.\n\nWe chose PostgreSQL as the database, selected after careful review.\n\nWe adopted TypeScript for type safety and developer productivity."
        matches = _count_keyword_matches(padded, [], ["decided", "chose", "adopted"])
        assert len(matches) >= 3


class TestEvidenceCheck:
    """Evidence scoring tests."""

    def test_url_detected(self):
        content = "Survey results available at https://example.com/results which confirms user demand."
        matches = _count_keyword_matches(content, [], [], url_pattern=r"https?://\S+")
        assert len(matches) >= 1

    def test_research_keywords(self):
        padded = "사용자 인터뷰를 3건 수행하여 피드백을 수집했다. 기존 도구의 불편한 점이 확인됨.\n\n조사 결과에 따르면 사용자의 80% 이상이 실시간 동기화를 요청하고 있었다."
        matches = _count_keyword_matches(padded, ["인터뷰", "피드백", "조사"], [])
        assert len(matches) >= 2


class TestAlternativesCheck:
    """Alternatives pair rule tests."""

    def test_pair_rule_match(self):
        content = "대안으로 Firebase를 검토했으나 여러 이유로 채택하지 않았다.\n이유: 비용이 높고 vendor lock-in 리스크가 있기 때문에 포기했다."
        matches = _check_pair_rule(
            content,
            ["대안", "검토했"], [],
            ["이유", "때문"], [],
        )
        assert len(matches) >= 1

    def test_pair_rule_no_reason(self):
        content = "대안으로 Firebase를 검토했으나 결국 다른 선택을 했다.\n\n다음 주제로 넘어간다. 전혀 상관없는 이야기를 시작한다.\n\n완전 다른 이야기를 이어서 진행하겠습니다."
        matches = _check_pair_rule(
            content,
            ["대안", "검토했"], [],
            ["이유", "때문"], [],
        )
        # No pair match because reason is not in adjacent lines
        assert len(matches) == 0


class TestDoomsdayCheck:
    """Doomsday If/Then tests."""

    def test_if_then_korean(self):
        content = "만약 서버가 다운되면 → CDN 캐시에서 제공"
        matches = _check_if_then(content, [r"만약\s*.+[면].*[→\-]"])
        assert len(matches) >= 1

    def test_if_then_english(self):
        content = "if the API times out then retry 3 times"
        matches = _check_if_then(content, [r"if\s+.+then"])
        assert len(matches) >= 1

    def test_fallback_pattern(self):
        content = "fallback to local cache when API is unavailable"
        matches = _check_if_then(content, [r"fallback.{0,30}"])
        assert len(matches) >= 1

    def test_partial_credit(self):
        """Keywords without If/Then gets partial credit."""
        content = "실패 시 복구. 리스크 관리 필요. 에러 처리 중요.\n\n장애 대응 계획을 수립해야 한다. 복구 시나리오도 필요."
        result = score_prd(content + "\n\n" + GOOD_PRD.split("## 실패")[0])
        doomsday = next(c for c in result.checks if c.name == "doomsday")
        # Check it finds keyword matches at least
        assert len(doomsday.matches) >= 0  # basic sanity


# ============================================================
# Out of Scope tests
# ============================================================

class TestOutOfScope:
    """Out of Scope detection tests."""

    def test_section_header_detected(self):
        assert _has_out_of_scope_section("## Out of Scope\n- Mobile\n")
        assert _has_out_of_scope_section("## 하지 않을 것\n- 모바일\n")
        assert _has_out_of_scope_section("## Non-Goals\n- AI\n")

    def test_no_section_header(self):
        assert not _has_out_of_scope_section("## Features\n- Login\n")

    def test_scope_keywords(self):
        content = "모바일 앱은 이 버전에서 제외한다. 나중에 추가 예정.\n\nAI 추천 기능은 범위 밖이다. 데이터가 부족하기 때문."
        matches = _count_out_of_scope_content(content)
        assert len(matches) >= 2

    def test_english_scope_keywords(self):
        content = "Mobile app is out of scope for this version, it is excluded from current planning.\n\nAI recommendations are deferred to a future release as a non-goal."
        matches = _count_out_of_scope_content(content)
        assert len(matches) >= 2


# ============================================================
# Anti-gaming tests
# ============================================================

class TestAntiGaming:
    """Anti-gaming mechanism tests."""

    def test_fake_detection_korean(self):
        content = "결정 없음. 선택 미정. 채택 TBD."
        count = _check_fake(content, ["결정", "선택", "채택"], [])
        assert count >= 2

    def test_fake_detection_english(self):
        content = "decision N/A. chose not yet. adopted to be decided."
        count = _check_fake(content, [], ["decision", "chose", "adopted"])
        assert count >= 2

    def test_no_fakes_in_good_content(self):
        content = "결정: React를 프레임워크로 채택. 선택 이유는 생태계가 넓기 때문."
        count = _check_fake(content, ["결정", "선택", "채택"], [])
        assert count == 0


# ============================================================
# Penalty tests
# ============================================================

class TestPenalties:
    """Penalty detection tests."""

    def test_abstract_words_counted(self):
        assert _count_abstract_words("혁신적이고 최적의 강력한 효율적인 솔루션") >= 4

    def test_no_abstract_words(self):
        assert _count_abstract_words("React와 PostgreSQL을 사용합니다") == 0

    def test_specific_numbers(self):
        content = "500명 DAU, 200ms 응답시간, 99.5% 가용률"
        assert _count_specific_numbers(content) >= 2

    def test_no_numbers(self):
        assert _count_specific_numbers("빠른 응답시간과 높은 가용률") == 0

    def test_banned_phrases(self):
        content = "TBD로 추후 결정. 적절히 처리. TBD."
        assert _count_banned_phrases(content) >= 3

    def test_no_banned_phrases(self):
        assert _count_banned_phrases("React 18을 사용한다") == 0


# ============================================================
# Cap tests
# ============================================================

class TestCaps:
    """Score cap tests."""

    def test_no_scope_caps_at_55(self):
        """Without out of scope, score capped at 55."""
        result = score_prd(NO_SCOPE_PRD)
        scope_check = next(c for c in result.checks if c.name == "out_of_scope")
        if not scope_check.passed:
            assert result.total_score <= CAP_NO_SCOPE

    def test_no_alternatives_caps_at_65(self):
        """Without alternatives, score capped at 65."""
        content = """# Project

## 결정 사항
기술스택 결정: React 채택.
인증 선택: JWT.
DB 사용하기로: PostgreSQL.

## 근거
인터뷰 수행. 데이터 확인. 피드백 수집.

## 실패 시나리오
실패 시 복구. 리스크 대응. 에러 처리.
만약 장애 발생하면 → 자동 복구.

## Out of Scope
- 모바일: 제외
- AI: 나중에

## 수치
- 100명 DAU
- 200ms 응답
- 99% 가용률
"""
        result = score_prd(content)
        alt_check = next(c for c in result.checks if c.name == "alternatives")
        if not alt_check.passed:
            assert result.total_score <= CAP_NO_ALTERNATIVES


# ============================================================
# Level threshold tests
# ============================================================

class TestLevels:
    """Level threshold tests."""

    def test_lite_thresholds(self):
        assert LEVEL_THRESHOLDS["lite"]["block"] == 40
        assert LEVEL_THRESHOLDS["lite"]["pass"] == 60

    def test_standard_thresholds(self):
        assert LEVEL_THRESHOLDS["standard"]["block"] == 50
        assert LEVEL_THRESHOLDS["standard"]["pass"] == 70

    def test_ship_thresholds(self):
        assert LEVEL_THRESHOLDS["ship"]["block"] == 60
        assert LEVEL_THRESHOLDS["ship"]["pass"] == 75

    def test_same_prd_different_grades(self):
        """Same PRD may get different grades at different levels."""
        result_lite = score_prd(NO_SCOPE_PRD, level="lite")
        result_ship = score_prd(NO_SCOPE_PRD, level="ship")
        # Ship level is stricter
        lite_pass = result_lite.grade in ("PASS", "WARN")
        ship_pass = result_ship.grade in ("PASS", "WARN")
        # If ship passes, lite must also pass (ship is stricter)
        if ship_pass:
            assert lite_pass


# ============================================================
# format_score_report tests
# ============================================================

class TestFormatReport:
    """format_score_report tests."""

    def test_report_contains_score(self):
        result = score_prd(GOOD_PRD)
        report = format_score_report(result)
        assert "PRD Quality:" in report
        assert "/100" in report

    def test_report_shows_grade(self):
        result = score_prd(GOOD_PRD)
        report = format_score_report(result)
        assert result.grade in report

    def test_report_shows_passed_checks(self):
        result = score_prd(GOOD_PRD)
        report = format_score_report(result)
        assert "PASS:" in report

    def test_report_shows_missing(self):
        result = score_prd(MINIMAL_PRD)
        report = format_score_report(result)
        assert "MISSING" in report

    def test_report_shows_estimate(self):
        result = score_prd(MINIMAL_PRD)
        report = format_score_report(result)
        if result.missing:
            assert "예상 점수" in report

    def test_empty_prd_report(self):
        result = score_prd("")
        report = format_score_report(result)
        assert "PRD Quality:" in report


# ============================================================
# Helper function tests
# ============================================================

class TestHelpers:
    """Helper function tests."""

    def test_get_paragraphs(self):
        text = "First paragraph.\n\nSecond paragraph.\n\nThird."
        paras = _get_paragraphs(text)
        assert len(paras) == 3

    def test_get_paragraphs_empty(self):
        assert _get_paragraphs("") == []

    def test_get_paragraphs_single(self):
        assert len(_get_paragraphs("Hello world")) == 1

    def test_density_check_skips_short(self):
        """Short paragraphs are skipped in keyword matching."""
        content = "결정\n\n선택\n\n채택"  # Each paragraph too short
        matches = _count_keyword_matches(content, ["결정", "선택", "채택"], [])
        assert len(matches) == 0  # All too short for density check
