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
    set_project_domain,
    get_project_domain,
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


# ============================================================
# Domain Scoping (v1.0)
# ============================================================

class TestDomainScoping:
    """Domain scoping for memory isolation."""

    def test_domain_column_exists_in_projects(self, clean_knowledge_db):
        """ALTER TABLE migration adds domain column to projects."""
        conn = get_connection()
        try:
            cursor = conn.execute("PRAGMA table_info(projects)")
            columns = [r["name"] for r in cursor.fetchall()]
            assert "domain" in columns
        finally:
            conn.close()

    def test_domain_column_exists_in_global_memories(self, clean_knowledge_db):
        """ALTER TABLE migration adds domain column to global_memories."""
        conn = get_connection()
        try:
            cursor = conn.execute("PRAGMA table_info(global_memories)")
            columns = [r["name"] for r in cursor.fetchall()]
            assert "domain" in columns
        finally:
            conn.close()

    def test_domain_index_exists(self, clean_knowledge_db):
        """Index on global_memories.domain should exist."""
        conn = get_connection()
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index' AND name='idx_global_memories_domain'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_set_and_get_project_domain(self, clean_knowledge_db):
        """CRUD: set domain then get it back."""
        project_id = get_or_create_project("dom-test", path="/tmp/dom")
        assert get_project_domain(project_id) is None  # default

        result = set_project_domain(project_id, "work")
        assert result["status"] == "updated"
        assert result["domain"] == "work"

        assert get_project_domain(project_id) == "work"

    def test_set_domain_not_found(self, clean_knowledge_db):
        """Setting domain for nonexistent project returns not_found."""
        result = set_project_domain("nonexistent_id", "personal")
        assert result["status"] == "not_found"

    def test_get_domain_nonexistent_project(self, clean_knowledge_db):
        """Getting domain for nonexistent project returns None."""
        assert get_project_domain("nonexistent_id") is None

    def test_promote_inherits_project_domain(self, clean_knowledge_db):
        """Promoted memory should carry the domain if passed."""
        project_id = get_or_create_project("work-proj", path="/tmp/work")
        set_project_domain(project_id, "work")

        data = _make_memory_data(error_signature="domain_inherit_test")
        result = promote_memory(data, project_id, "work-proj", domain="work")
        assert result["status"] == "promoted"

        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT domain FROM global_memories WHERE id = ?", (result["id"],)
            ).fetchone()
            assert row["domain"] == "work"
        finally:
            conn.close()

    def test_promote_without_domain_is_null(self, clean_knowledge_db):
        """Promoted memory without domain should have NULL domain."""
        project_id = get_or_create_project("no-domain", path="/tmp/nodomain")
        data = _make_memory_data(error_signature="no_domain_test")
        result = promote_memory(data, project_id, "no-domain")
        assert result["status"] == "promoted"

        conn = get_connection()
        try:
            row = conn.execute(
                "SELECT domain FROM global_memories WHERE id = ?", (result["id"],)
            ).fetchone()
            assert row["domain"] is None
        finally:
            conn.close()

    def test_search_filters_by_domain(self, clean_knowledge_db):
        """Search with domain filter should only return matching domain."""
        proj_work = get_or_create_project("proj-work", path="/tmp/work")
        proj_client = get_or_create_project("proj-client", path="/tmp/client")

        promote_memory(
            _make_memory_data(root_cause="Domain filter work error", error_signature="df_work"),
            proj_work, "proj-work", domain="work",
        )
        promote_memory(
            _make_memory_data(root_cause="Domain filter client error", error_signature="df_client"),
            proj_client, "proj-client", domain="client",
        )

        # Filter by "work" domain
        results = search_global_memories("Domain filter", domain="work")
        assert len(results) == 1
        assert results[0]["domain"] == "work"

        # Filter by "client" domain
        results = search_global_memories("Domain filter", domain="client")
        assert len(results) == 1
        assert results[0]["domain"] == "client"

    def test_search_null_domain_matches_personal(self, clean_knowledge_db):
        """NULL domain in DB should be treated as 'personal' for filtering."""
        project_id = get_or_create_project("null-dom", path="/tmp/nulldom")
        # Promote without explicit domain (NULL in DB)
        promote_memory(
            _make_memory_data(root_cause="Null domain personal compat", error_signature="null_personal"),
            project_id, "null-dom",
        )

        # Searching with domain="personal" should find it (NULL = personal)
        results = search_global_memories("Null domain personal", domain="personal")
        assert len(results) == 1

    def test_search_no_domain_returns_all(self, clean_knowledge_db):
        """Search without domain filter returns all memories."""
        proj_work = get_or_create_project("all-work", path="/tmp/allwork")
        proj_client = get_or_create_project("all-client", path="/tmp/allclient")

        promote_memory(
            _make_memory_data(root_cause="All search work result", error_signature="all_work"),
            proj_work, "all-work", domain="work",
        )
        promote_memory(
            _make_memory_data(root_cause="All search client result", error_signature="all_client"),
            proj_client, "all-client", domain="client",
        )

        # No domain filter — should return all
        results = search_global_memories("All search")
        assert len(results) == 2

    def test_cross_domain_isolation(self, clean_knowledge_db):
        """Client domain memories should NOT appear in personal domain search."""
        project_id = get_or_create_project("isolated", path="/tmp/isolated")

        promote_memory(
            _make_memory_data(root_cause="Cross isolation secret client data", error_signature="iso_client"),
            project_id, "isolated", domain="client",
        )

        # Searching from "personal" domain should NOT find "client" memory
        results = search_global_memories("Cross isolation secret", domain="personal")
        assert len(results) == 0

        # Searching from "client" domain should find it
        results = search_global_memories("Cross isolation secret", domain="client")
        assert len(results) == 1

    def test_get_or_create_project_with_domain(self, clean_knowledge_db):
        """Creating a project with domain should store it."""
        project_id = get_or_create_project("dom-create", path="/tmp/domcreate", domain="client")

        assert get_project_domain(project_id) == "client"

    def test_get_or_create_existing_ignores_domain(self, clean_knowledge_db):
        """Getting existing project should NOT overwrite domain."""
        project_id_1 = get_or_create_project("existing-dom", path="/tmp/existdom", domain="work")
        project_id_2 = get_or_create_project("existing-dom", path="/tmp/existdom", domain="client")

        # Same project returned
        assert project_id_1 == project_id_2
        # Domain should still be "work" (first creation)
        assert get_project_domain(project_id_1) == "work"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
