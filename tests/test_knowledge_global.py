# -*- coding: utf-8 -*-
"""Global Memories module tests (v5.0: Cross-Project Memory Transfer)"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.db.knowledge import (
    init_knowledge_db,
    get_connection,
    get_or_create_project,
    promote_memory,
    search_global_memories,
    get_global_memory_stats,
    archive_global_memory,
    unarchive_global_memory,
    increment_global_hit,
    increment_global_save,
    KNOWLEDGE_DB_PATH,
)


@pytest.fixture
def clean_knowledge_db(tmp_path, monkeypatch):
    """Create a temporary knowledge DB for testing."""
    db_path = tmp_path / "knowledge.db"
    monkeypatch.setattr("clouvel.db.knowledge.KNOWLEDGE_DB_PATH", db_path)
    init_knowledge_db(auto_archive=False)
    yield db_path


def _make_memory_data(**overrides):
    """Helper to create memory data dict for promote_memory."""
    base = {
        "error_signature": "TypeError: <PATH>",
        "error_category": "type_error",
        "libraries": ["requests"],
        "tags": ["api"],
        "root_cause": "Missing null check before property access",
        "prevention_rule": "Always check for null before accessing object properties",
        "negative_constraint": "",
        "severity": 3,
        "source_memory_id": 1,
    }
    base.update(overrides)
    return base


# ============================================================
# Schema
# ============================================================

class TestGlobalMemoriesSchema:
    """Verify global_memories table and FTS5 index creation."""

    def test_table_exists(self, clean_knowledge_db):
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='global_memories'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_fts5_index_exists(self, clean_knowledge_db):
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='global_memories_fts'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_indexes_exist(self, clean_knowledge_db):
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name LIKE 'idx_global_memories_%'"
            )
            indexes = [r["name"] for r in cursor.fetchall()]
            assert "idx_global_memories_project" in indexes
            assert "idx_global_memories_signature" in indexes
            assert "idx_global_memories_category" in indexes
            assert "idx_global_memories_archived" in indexes
        finally:
            conn.close()


# ============================================================
# promote_memory
# ============================================================

class TestPromoteMemory:
    """Promote local memory to global."""

    def test_promote_success(self, clean_knowledge_db):
        project_id = get_or_create_project("test-project", path="/tmp/test")
        data = _make_memory_data()
        result = promote_memory(data, project_id, "test-project")
        assert result["status"] == "promoted"
        assert "id" in result

    def test_promote_duplicate_returns_duplicate(self, clean_knowledge_db):
        project_id = get_or_create_project("test-project", path="/tmp/test")
        data = _make_memory_data()
        result1 = promote_memory(data, project_id, "test-project")
        assert result1["status"] == "promoted"

        result2 = promote_memory(data, project_id, "test-project")
        assert result2["status"] == "duplicate"
        assert result2["existing_id"] == result1["id"]

    def test_same_signature_different_project_ok(self, clean_knowledge_db):
        project_a = get_or_create_project("project-a", path="/tmp/a")
        project_b = get_or_create_project("project-b", path="/tmp/b")
        data = _make_memory_data()

        result_a = promote_memory(data, project_a, "project-a")
        result_b = promote_memory(data, project_b, "project-b")
        assert result_a["status"] == "promoted"
        assert result_b["status"] == "promoted"
        assert result_a["id"] != result_b["id"]

    def test_error_text_not_stored(self, clean_knowledge_db):
        """Ensure no error_text field is stored in global_memories."""
        project_id = get_or_create_project("test-project", path="/tmp/test")
        data = _make_memory_data()
        result = promote_memory(data, project_id, "test-project")

        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM global_memories WHERE id = ?", (result["id"],)
            ).fetchone()
            columns = row.keys()
            assert "error_text" not in columns
            assert "code_snippet" not in columns
            assert "fix_snippet" not in columns
        finally:
            conn.close()

    def test_promote_stores_metadata(self, clean_knowledge_db):
        project_id = get_or_create_project("test-project", path="/tmp/test")
        data = _make_memory_data(
            libraries=["flask", "sqlalchemy"],
            tags=["api", "database"],
            severity=5,
        )
        result = promote_memory(data, project_id, "test-project")

        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT * FROM global_memories WHERE id = ?", (result["id"],)
            ).fetchone()
            assert row["origin_project_name"] == "test-project"
            assert row["severity"] == 5
            assert row["source_memory_id"] == 1
            assert row["archived"] == 0
        finally:
            conn.close()

    def test_promote_syncs_fts(self, clean_knowledge_db):
        """FTS5 index should be searchable after promote."""
        project_id = get_or_create_project("test-project", path="/tmp/test")
        data = _make_memory_data(
            root_cause="Unique xylophone error pattern",
            prevention_rule="Always tune the xylophone"
        )
        promote_memory(data, project_id, "test-project")

        results = search_global_memories("xylophone")
        assert len(results) >= 1


# ============================================================
# search_global_memories
# ============================================================

class TestSearchGlobalMemories:
    """Global memory search tests."""

    def test_fts_search(self, clean_knowledge_db):
        project_id = get_or_create_project("proj-a", path="/tmp/a")
        promote_memory(
            _make_memory_data(root_cause="Buffer overflow in parser module"),
            project_id, "proj-a"
        )
        results = search_global_memories("buffer overflow")
        assert len(results) >= 1

    def test_exclude_current_project(self, clean_knowledge_db):
        project_id = get_or_create_project("my-project", path="/tmp/mine")
        promote_memory(
            _make_memory_data(root_cause="Authentication token expired"),
            project_id, "my-project"
        )
        # Searching with exclude should return nothing
        results = search_global_memories("Authentication token", project_id_exclude=project_id)
        assert len(results) == 0

        # Without exclude should find it
        results = search_global_memories("Authentication token")
        assert len(results) >= 1

    def test_category_filter(self, clean_knowledge_db):
        project_id = get_or_create_project("proj", path="/tmp/proj")
        promote_memory(
            _make_memory_data(
                root_cause="Network timeout in API call",
                error_category="network_error",
                error_signature="net_timeout",
            ),
            project_id, "proj"
        )
        promote_memory(
            _make_memory_data(
                root_cause="Network parsing failure",
                error_category="type_error",
                error_signature="net_parse",
            ),
            project_id, "proj"
        )

        # Filter by network_error
        results = search_global_memories("Network", category="network_error")
        assert len(results) == 1
        assert results[0]["error_category"] == "network_error"

    def test_excludes_archived(self, clean_knowledge_db):
        project_id = get_or_create_project("proj", path="/tmp/proj")
        result = promote_memory(
            _make_memory_data(root_cause="Archived memory pattern"),
            project_id, "proj"
        )
        archive_global_memory(result["id"])

        results = search_global_memories("Archived memory")
        assert len(results) == 0

    def test_empty_results(self, clean_knowledge_db):
        results = search_global_memories("nonexistent quantum flux capacitor")
        assert len(results) == 0

    def test_like_fallback(self, clean_knowledge_db):
        """LIKE search should work when FTS returns nothing for special chars."""
        project_id = get_or_create_project("proj", path="/tmp/proj")
        promote_memory(
            _make_memory_data(root_cause="Error in v3.1 migration script"),
            project_id, "proj"
        )
        # This should trigger LIKE fallback due to special FTS5 chars
        results = search_global_memories("v3.1")
        assert len(results) >= 1


# ============================================================
# get_global_memory_stats
# ============================================================

class TestGlobalMemoryStats:
    """Global memory statistics tests."""

    def test_empty_stats(self, clean_knowledge_db):
        stats = get_global_memory_stats()
        assert stats["total"] == 0
        assert stats["active"] == 0
        assert stats["archived"] == 0
        assert stats["top_memories"] == []
        assert stats["top_categories"] == {}

    def test_stats_with_data(self, clean_knowledge_db):
        project_id = get_or_create_project("proj-a", path="/tmp/a")
        r1 = promote_memory(
            _make_memory_data(error_category="type_error", error_signature="sig1"),
            project_id, "proj-a"
        )
        promote_memory(
            _make_memory_data(error_category="import_error", error_signature="sig2"),
            project_id, "proj-a"
        )

        increment_global_hit(r1["id"])
        increment_global_hit(r1["id"])
        increment_global_save(r1["id"])

        stats = get_global_memory_stats()
        assert stats["total"] == 2
        assert stats["active"] == 2
        assert stats["archived"] == 0
        assert len(stats["top_memories"]) == 2
        assert "type_error" in stats["top_categories"]
        assert "import_error" in stats["top_categories"]

    def test_stats_excludes_archived(self, clean_knowledge_db):
        project_id = get_or_create_project("proj", path="/tmp/proj")
        r1 = promote_memory(
            _make_memory_data(error_signature="arch1"),
            project_id, "proj"
        )
        archive_global_memory(r1["id"])

        stats = get_global_memory_stats()
        assert stats["total"] == 1
        assert stats["active"] == 0
        assert stats["archived"] == 1


# ============================================================
# archive / unarchive
# ============================================================

class TestGlobalMemoryArchive:
    """Archive / unarchive global memories."""

    def test_archive(self, clean_knowledge_db):
        project_id = get_or_create_project("proj", path="/tmp/proj")
        r = promote_memory(_make_memory_data(), project_id, "proj")

        result = archive_global_memory(r["id"])
        assert result["status"] == "archived"

        # Verify in DB
        conn = get_connection()
        try:
            row = conn.execute("SELECT archived FROM global_memories WHERE id = ?", (r["id"],)).fetchone()
            assert row["archived"] == 1
        finally:
            conn.close()

    def test_unarchive(self, clean_knowledge_db):
        project_id = get_or_create_project("proj", path="/tmp/proj")
        r = promote_memory(_make_memory_data(), project_id, "proj")
        archive_global_memory(r["id"])

        result = unarchive_global_memory(r["id"])
        assert result["status"] == "unarchived"

        conn = get_connection()
        try:
            row = conn.execute("SELECT archived FROM global_memories WHERE id = ?", (r["id"],)).fetchone()
            assert row["archived"] == 0
        finally:
            conn.close()

    def test_archive_not_found(self, clean_knowledge_db):
        result = archive_global_memory(99999)
        assert result["status"] == "not_found"

    def test_unarchive_not_found(self, clean_knowledge_db):
        result = unarchive_global_memory(99999)
        assert result["status"] == "not_found"


# ============================================================
# Counters
# ============================================================

class TestGlobalHitSaveCounters:
    """Hit and save counter tests."""

    def test_increment_hit(self, clean_knowledge_db):
        project_id = get_or_create_project("proj", path="/tmp/proj")
        r = promote_memory(_make_memory_data(), project_id, "proj")

        increment_global_hit(r["id"])
        increment_global_hit(r["id"])

        conn = get_connection()
        try:
            row = conn.execute("SELECT hit_count FROM global_memories WHERE id = ?", (r["id"],)).fetchone()
            assert row["hit_count"] == 2
        finally:
            conn.close()

    def test_increment_save(self, clean_knowledge_db):
        project_id = get_or_create_project("proj", path="/tmp/proj")
        r = promote_memory(_make_memory_data(), project_id, "proj")

        increment_global_save(r["id"])

        conn = get_connection()
        try:
            row = conn.execute("SELECT times_saved FROM global_memories WHERE id = ?", (r["id"],)).fetchone()
            assert row["times_saved"] == 1
        finally:
            conn.close()

    def test_increment_nonexistent_no_error(self, clean_knowledge_db):
        """Incrementing a non-existent ID should not raise."""
        increment_global_hit(99999)
        increment_global_save(99999)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
