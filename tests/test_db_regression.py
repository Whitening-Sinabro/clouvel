# -*- coding: utf-8 -*-
"""Regression Memory module tests (v4.0)"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.db.schema import init_db
from clouvel.db.regression import (
    normalize_error_signature,
    create_memory,
    get_memory,
    list_memories,
    match_level1_exact,
    match_level2_tags,
    match_level3_fts,
    match_all_levels,
    increment_hit_count,
    increment_times_saved,
    archive_memory,
    unarchive_memory,
    get_memory_stats,
    # v4.0 Phase 2
    search_memories,
    mark_stale_memories,
    get_memory_report,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory with initialized DB."""
    temp_dir = tempfile.mkdtemp()
    init_db(temp_dir)
    yield temp_dir
    shutil.rmtree(temp_dir)


# ============================================================
# normalize_error_signature
# ============================================================

class TestNormalizeErrorSignature:
    """Error signature normalization tests."""

    def test_removes_file_paths(self):
        sig = normalize_error_signature("Error in /home/user/project/main.py")
        assert "/home/user" not in sig
        assert "<PATH>" in sig

    def test_removes_windows_paths(self):
        sig = normalize_error_signature("Error in C:\\Users\\dev\\app.js")
        assert "C:\\Users" not in sig
        assert "<PATH>" in sig

    def test_removes_line_numbers(self):
        sig = normalize_error_signature("File main.py:42 error")
        assert ":42" not in sig
        assert ":<LINE>" in sig

    def test_removes_hex_addresses(self):
        sig = normalize_error_signature("Segfault at 0x7fff1234abcd")
        assert "0x7fff1234abcd" not in sig
        assert "<HEX>" in sig

    def test_removes_timestamps(self):
        sig = normalize_error_signature("Error at 2026-01-25T14:30:00")
        assert "2026-01-25" not in sig
        assert "<TIME>" in sig

    def test_removes_uuids(self):
        sig = normalize_error_signature("Request 550e8400-e29b-41d4-a716-446655440000 failed")
        assert "550e8400" not in sig
        assert "<UUID>" in sig

    def test_collapses_whitespace(self):
        sig = normalize_error_signature("Error   in   function")
        assert "  " not in sig

    def test_same_error_same_signature(self):
        """Same logical error at different paths should produce same signature."""
        sig1 = normalize_error_signature("TypeError: Cannot read property 'x' at /home/a/main.py:10")
        sig2 = normalize_error_signature("TypeError: Cannot read property 'x' at /home/b/main.py:42")
        assert sig1 == sig2


# ============================================================
# create_memory + get_memory
# ============================================================

class TestCreateMemory:
    """CRUD tests for regression memories."""

    def test_create_returns_id(self, temp_project):
        result = create_memory(
            error_signature="TypeError: <PATH>",
            root_cause="Missing null check",
            project_path=temp_project,
        )
        assert "id" in result
        assert result["status"] == "created"

    def test_get_memory(self, temp_project):
        result = create_memory(
            error_signature="ImportError: no module",
            root_cause="Dependency missing",
            error_category="import_error",
            project_path=temp_project,
        )
        mem = get_memory(result["id"], project_path=temp_project)
        assert mem is not None
        assert mem["error_signature"] == "ImportError: no module"
        assert mem["root_cause"] == "Dependency missing"
        assert mem["error_category"] == "import_error"

    def test_get_memory_not_found(self, temp_project):
        mem = get_memory(99999, project_path=temp_project)
        assert mem is None

    def test_create_with_json_fields(self, temp_project):
        result = create_memory(
            error_signature="Test",
            root_cause="Test",
            file_paths=["src/main.py", "src/utils.py"],
            libraries=["requests", "flask"],
            tags=["api", "network"],
            project_path=temp_project,
        )
        mem = get_memory(result["id"], project_path=temp_project)
        assert mem["file_paths"] == ["src/main.py", "src/utils.py"]
        assert mem["libraries"] == ["requests", "flask"]
        assert mem["tags"] == ["api", "network"]

    def test_list_memories(self, temp_project):
        create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        create_memory(error_signature="E2", root_cause="R2", project_path=temp_project)
        memories = list_memories(project_path=temp_project)
        assert len(memories) == 2

    def test_list_excludes_archived_by_default(self, temp_project):
        r1 = create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        create_memory(error_signature="E2", root_cause="R2", project_path=temp_project)
        archive_memory(r1["id"], project_path=temp_project)
        memories = list_memories(project_path=temp_project)
        assert len(memories) == 1

    def test_list_includes_archived(self, temp_project):
        r1 = create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        create_memory(error_signature="E2", root_cause="R2", project_path=temp_project)
        archive_memory(r1["id"], project_path=temp_project)
        memories = list_memories(include_archived=True, project_path=temp_project)
        assert len(memories) == 2


# ============================================================
# Level 1: Exact match
# ============================================================

class TestMatchLevel1:
    """Exact signature matching tests."""

    def test_exact_match(self, temp_project):
        create_memory(
            error_signature="TypeError: undefined is not a function",
            root_cause="Called method on null",
            project_path=temp_project,
        )
        results = match_level1_exact("TypeError: undefined is not a function", project_path=temp_project)
        assert len(results) == 1

    def test_no_match(self, temp_project):
        create_memory(
            error_signature="TypeError: something",
            root_cause="Test",
            project_path=temp_project,
        )
        results = match_level1_exact("ImportError: different", project_path=temp_project)
        assert len(results) == 0

    def test_excludes_archived(self, temp_project):
        r = create_memory(
            error_signature="TypeError: test",
            root_cause="Test",
            project_path=temp_project,
        )
        archive_memory(r["id"], project_path=temp_project)
        results = match_level1_exact("TypeError: test", project_path=temp_project)
        assert len(results) == 0


# ============================================================
# Level 2: Tag scoring
# ============================================================

class TestMatchLevel2:
    """Weighted tag scoring tests."""

    def test_file_match_scores_3(self, temp_project):
        create_memory(
            error_signature="E1",
            root_cause="R1",
            file_paths=["src/auth.py"],
            error_category="type_error",
            project_path=temp_project,
        )
        # file(3) + category(1) = 4, should match
        results = match_level2_tags(
            file_paths=["src/auth.py"],
            error_category="type_error",
            project_path=temp_project,
        )
        assert len(results) == 1
        assert results[0]["match_score"] >= 4

    def test_library_match_scores_2(self, temp_project):
        create_memory(
            error_signature="E2",
            root_cause="R2",
            file_paths=["src/api.py"],
            libraries=["requests"],
            error_category="network_error",
            project_path=temp_project,
        )
        # file(3) + lib(2) + cat(1) = 6
        results = match_level2_tags(
            file_paths=["src/api.py"],
            libraries=["requests"],
            error_category="network_error",
            project_path=temp_project,
        )
        assert len(results) == 1
        assert results[0]["match_score"] >= 4

    def test_below_threshold_excluded(self, temp_project):
        create_memory(
            error_signature="E3",
            root_cause="R3",
            error_category="type_error",
            project_path=temp_project,
        )
        # category only = 1, below threshold
        results = match_level2_tags(
            error_category="type_error",
            project_path=temp_project,
        )
        assert len(results) == 0


# ============================================================
# Level 3: FTS search
# ============================================================

class TestMatchLevel3:
    """FTS5 keyword search tests."""

    def test_fts_match_root_cause(self, temp_project):
        create_memory(
            error_signature="E1",
            root_cause="Missing authentication token in header",
            task_description="Implementing login endpoint",
            project_path=temp_project,
        )
        results = match_level3_fts("authentication token", project_path=temp_project)
        assert len(results) >= 1

    def test_fts_match_prevention(self, temp_project):
        create_memory(
            error_signature="E2",
            root_cause="Buffer overflow",
            prevention_rule="Always validate input length before processing",
            project_path=temp_project,
        )
        results = match_level3_fts("validate input length", project_path=temp_project)
        assert len(results) >= 1

    def test_fts_no_match(self, temp_project):
        create_memory(
            error_signature="E3",
            root_cause="Database connection timeout",
            project_path=temp_project,
        )
        results = match_level3_fts("quantum computing entanglement", project_path=temp_project)
        assert len(results) == 0


# ============================================================
# match_all_levels
# ============================================================

class TestMatchAllLevels:
    """Integrated 3-level matching tests."""

    def test_returns_deduplicated(self, temp_project):
        """Same memory shouldn't appear twice even if matched at multiple levels."""
        create_memory(
            error_signature="TypeError: undefined is not a function",
            root_cause="Called method on null object",
            error_category="type_error",
            file_paths=["src/app.py"],
            project_path=temp_project,
        )
        results = match_all_levels(
            error_text="TypeError: undefined is not a function",
            file_paths=["src/app.py"],
            error_category="type_error",
            project_path=temp_project,
        )
        ids = [r["id"] for r in results]
        assert len(ids) == len(set(ids))  # no duplicates

    def test_level1_prioritized(self, temp_project):
        """Exact matches should come first."""
        create_memory(
            error_signature="TypeError: x is not a function",
            root_cause="Exact match",
            project_path=temp_project,
        )
        create_memory(
            error_signature="Different error",
            root_cause="TypeError x is not a function related context",
            task_description="TypeError x is not a function related task",
            project_path=temp_project,
        )
        results = match_all_levels(
            error_text="TypeError: x is not a function",
            project_path=temp_project,
        )
        if len(results) >= 1:
            assert results[0]["match_level"] == 1

    def test_top_n_limit(self, temp_project):
        for i in range(10):
            create_memory(
                error_signature=f"Error{i}: unique signature {i}",
                root_cause=f"common search keyword root cause {i}",
                task_description=f"common search keyword task {i}",
                project_path=temp_project,
            )
        results = match_all_levels(
            error_text="common search keyword",
            top_n=3,
            project_path=temp_project,
        )
        assert len(results) <= 3


# ============================================================
# Counters
# ============================================================

class TestIncrementCounters:
    """Counter increment tests."""

    def test_increment_hit_count(self, temp_project):
        r = create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        mem = get_memory(r["id"], project_path=temp_project)
        assert mem["hit_count"] == 0

        increment_hit_count(r["id"], project_path=temp_project)
        increment_hit_count(r["id"], project_path=temp_project)
        mem = get_memory(r["id"], project_path=temp_project)
        assert mem["hit_count"] == 2

    def test_increment_times_saved(self, temp_project):
        r = create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        increment_times_saved(r["id"], project_path=temp_project)
        mem = get_memory(r["id"], project_path=temp_project)
        assert mem["times_saved"] == 1


# ============================================================
# Archive
# ============================================================

class TestArchiveMemory:
    """Soft-archive tests."""

    def test_archive(self, temp_project):
        r = create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        result = archive_memory(r["id"], project_path=temp_project)
        assert result["status"] == "archived"

        mem = get_memory(r["id"], project_path=temp_project)
        assert mem["archived"] == 1

    def test_unarchive(self, temp_project):
        r = create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        archive_memory(r["id"], project_path=temp_project)
        result = unarchive_memory(r["id"], project_path=temp_project)
        assert result["status"] == "unarchived"

        mem = get_memory(r["id"], project_path=temp_project)
        assert mem["archived"] == 0

    def test_archive_not_found(self, temp_project):
        result = archive_memory(99999, project_path=temp_project)
        assert result["status"] == "not_found"


# ============================================================
# Stats
# ============================================================

class TestGetMemoryStats:
    """Statistics tests."""

    def test_empty_stats(self, temp_project):
        stats = get_memory_stats(project_path=temp_project)
        assert stats["total"] == 0
        assert stats["active"] == 0
        assert stats["archived"] == 0
        assert stats["total_hits"] == 0
        assert stats["total_saves"] == 0
        assert stats["save_rate"] == 0.0

    def test_stats_with_data(self, temp_project):
        r1 = create_memory(
            error_signature="E1", root_cause="R1",
            error_category="type_error",
            project_path=temp_project,
        )
        create_memory(
            error_signature="E2", root_cause="R2",
            error_category="import_error",
            project_path=temp_project,
        )
        increment_hit_count(r1["id"], project_path=temp_project)
        increment_hit_count(r1["id"], project_path=temp_project)
        increment_times_saved(r1["id"], project_path=temp_project)

        stats = get_memory_stats(project_path=temp_project)
        assert stats["total"] == 2
        assert stats["active"] == 2
        assert stats["total_hits"] == 2
        assert stats["total_saves"] == 1
        assert stats["save_rate"] == 50.0
        assert "type_error" in stats["categories"]
        assert "import_error" in stats["categories"]

    def test_stats_with_archived(self, temp_project):
        r1 = create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        create_memory(error_signature="E2", root_cause="R2", project_path=temp_project)
        archive_memory(r1["id"], project_path=temp_project)

        stats = get_memory_stats(project_path=temp_project)
        assert stats["total"] == 2
        assert stats["active"] == 1
        assert stats["archived"] == 1


# ============================================================
# search_memories (Phase 2)
# ============================================================

class TestSearchMemories:
    """FTS search + category filter tests."""

    def test_fts_search_root_cause(self, temp_project):
        create_memory(
            error_signature="E1",
            root_cause="Null pointer dereference in authentication module",
            project_path=temp_project,
        )
        results = search_memories(query="authentication module", project_path=temp_project)
        assert len(results) >= 1

    def test_fts_search_prevention(self, temp_project):
        create_memory(
            error_signature="E1",
            root_cause="Test",
            prevention_rule="Always validate JWT token expiration",
            project_path=temp_project,
        )
        results = search_memories(query="JWT token", project_path=temp_project)
        assert len(results) >= 1

    def test_search_no_results(self, temp_project):
        create_memory(
            error_signature="E1",
            root_cause="Database timeout",
            project_path=temp_project,
        )
        results = search_memories(query="quantum teleportation", project_path=temp_project)
        assert len(results) == 0

    def test_search_with_category_filter(self, temp_project):
        create_memory(
            error_signature="E1",
            root_cause="Network connection failed",
            error_category="network_error",
            project_path=temp_project,
        )
        create_memory(
            error_signature="E2",
            root_cause="Network timeout in retry",
            error_category="type_error",
            project_path=temp_project,
        )
        # Both match "Network" but only one is network_error
        results = search_memories(query="Network", category="network_error", project_path=temp_project)
        assert len(results) == 1
        assert results[0]["error_category"] == "network_error"

    def test_search_excludes_archived_by_default(self, temp_project):
        r = create_memory(
            error_signature="E1",
            root_cause="Archived error pattern",
            project_path=temp_project,
        )
        archive_memory(r["id"], project_path=temp_project)
        results = search_memories(query="Archived error", project_path=temp_project)
        assert len(results) == 0

    def test_search_includes_archived_when_requested(self, temp_project):
        r = create_memory(
            error_signature="E1",
            root_cause="Archived error pattern for inclusion",
            project_path=temp_project,
        )
        archive_memory(r["id"], project_path=temp_project)
        results = search_memories(query="Archived error", include_archived=True, project_path=temp_project)
        assert len(results) >= 1

    def test_search_empty_query_lists_all(self, temp_project):
        create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        create_memory(error_signature="E2", root_cause="R2", project_path=temp_project)
        results = search_memories(query="", project_path=temp_project)
        assert len(results) == 2

    def test_search_empty_query_with_category(self, temp_project):
        create_memory(error_signature="E1", root_cause="R1", error_category="type_error", project_path=temp_project)
        create_memory(error_signature="E2", root_cause="R2", error_category="import_error", project_path=temp_project)
        results = search_memories(query="", category="type_error", project_path=temp_project)
        assert len(results) == 1


# ============================================================
# mark_stale_memories (Phase 2)
# ============================================================

class TestMarkStaleMemories:
    """Auto-archive stale memories tests."""

    def test_no_stale_with_fresh_memories(self, temp_project):
        create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        result = mark_stale_memories(days_threshold=60, project_path=temp_project)
        assert result["archived_count"] == 0
        assert result["ids"] == []

    def test_archives_old_zero_hit_memories(self, temp_project):
        """Memories with 0 hits older than threshold should be archived."""
        from clouvel.db.schema import get_connection, get_db_path

        # Create a memory and manually backdate it
        r = create_memory(error_signature="Old", root_cause="Old cause", project_path=temp_project)
        db_path = get_db_path(temp_project)
        conn = get_connection(db_path)
        conn.execute(
            "UPDATE regression_memory SET timestamp = datetime('now', '-90 days') WHERE id = ?",
            (r["id"],),
        )
        conn.commit()
        conn.close()

        result = mark_stale_memories(days_threshold=60, project_path=temp_project)
        assert result["archived_count"] == 1
        assert r["id"] in result["ids"]

        # Verify it's actually archived
        mem = get_memory(r["id"], project_path=temp_project)
        assert mem["archived"] == 1

    def test_does_not_archive_if_has_hits(self, temp_project):
        """Memories with hits should not be archived even if old."""
        from clouvel.db.schema import get_connection, get_db_path

        r = create_memory(error_signature="HitMem", root_cause="Has hits", project_path=temp_project)
        increment_hit_count(r["id"], project_path=temp_project)

        db_path = get_db_path(temp_project)
        conn = get_connection(db_path)
        conn.execute(
            "UPDATE regression_memory SET timestamp = datetime('now', '-90 days') WHERE id = ?",
            (r["id"],),
        )
        conn.commit()
        conn.close()

        result = mark_stale_memories(days_threshold=60, project_path=temp_project)
        assert result["archived_count"] == 0

    def test_does_not_archive_already_archived(self, temp_project):
        """Already archived memories should not be counted."""
        from clouvel.db.schema import get_connection, get_db_path

        r = create_memory(error_signature="AlreadyArch", root_cause="Test", project_path=temp_project)
        archive_memory(r["id"], project_path=temp_project)

        db_path = get_db_path(temp_project)
        conn = get_connection(db_path)
        conn.execute(
            "UPDATE regression_memory SET timestamp = datetime('now', '-90 days') WHERE id = ?",
            (r["id"],),
        )
        conn.commit()
        conn.close()

        result = mark_stale_memories(days_threshold=60, project_path=temp_project)
        assert result["archived_count"] == 0


# ============================================================
# get_memory_report (Phase 2)
# ============================================================

class TestGetMemoryReport:
    """Memory report generation tests."""

    def test_empty_report(self, temp_project):
        report = get_memory_report(days=30, project_path=temp_project)
        assert report["period_days"] == 30
        assert report["new_memories"] == 0
        assert report["active"] == 0
        assert report["total_hits"] == 0
        assert report["total_saves"] == 0
        assert report["time_saved_minutes"] == 0
        assert report["time_saved_hours"] == 0.0

    def test_report_with_data(self, temp_project):
        r1 = create_memory(
            error_signature="E1", root_cause="R1",
            error_category="type_error",
            project_path=temp_project,
        )
        create_memory(
            error_signature="E2", root_cause="R2",
            error_category="import_error",
            project_path=temp_project,
        )
        increment_hit_count(r1["id"], project_path=temp_project)
        increment_hit_count(r1["id"], project_path=temp_project)
        increment_times_saved(r1["id"], project_path=temp_project)

        report = get_memory_report(days=30, project_path=temp_project)
        assert report["new_memories"] == 2
        assert report["active"] == 2
        assert report["total_hits"] == 2
        assert report["total_saves"] == 1
        assert report["save_rate"] == 50.0
        assert report["time_saved_minutes"] == 15
        assert report["time_saved_hours"] == 0.2

    def test_report_top_memories(self, temp_project):
        r1 = create_memory(error_signature="E1", root_cause="Root 1", project_path=temp_project)
        increment_hit_count(r1["id"], project_path=temp_project)

        report = get_memory_report(days=30, project_path=temp_project)
        assert len(report["top_memories"]) >= 1
        assert report["top_memories"][0]["id"] == r1["id"]

    def test_report_top_categories(self, temp_project):
        create_memory(error_signature="E1", root_cause="R1", error_category="type_error", project_path=temp_project)
        create_memory(error_signature="E2", root_cause="R2", error_category="type_error", project_path=temp_project)
        create_memory(error_signature="E3", root_cause="R3", error_category="import_error", project_path=temp_project)

        report = get_memory_report(days=30, project_path=temp_project)
        assert len(report["top_categories"]) >= 1
        # type_error should be first (2 > 1)
        assert report["top_categories"][0]["category"] == "type_error"
        assert report["top_categories"][0]["count"] == 2

    def test_report_excludes_archived_from_top(self, temp_project):
        r1 = create_memory(error_signature="E1", root_cause="R1", project_path=temp_project)
        increment_hit_count(r1["id"], project_path=temp_project)
        archive_memory(r1["id"], project_path=temp_project)

        report = get_memory_report(days=30, project_path=temp_project)
        # Archived memories should not appear in top_memories
        top_ids = [m["id"] for m in report["top_memories"]]
        assert r1["id"] not in top_ids


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
