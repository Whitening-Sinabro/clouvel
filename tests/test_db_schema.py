# -*- coding: utf-8 -*-
"""Database schema module tests"""

import pytest
import sqlite3
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.db.schema import (
    get_db_path,
    get_connection,
    init_db,
    DEFAULT_DB_NAME,
    SCHEMA_SQL,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestDefaultDbName:
    """DEFAULT_DB_NAME constant tests"""

    def test_db_name_value(self):
        """DB name is errors.db"""
        assert DEFAULT_DB_NAME == "errors.db"

    def test_db_name_is_string(self):
        """DB name is string"""
        assert isinstance(DEFAULT_DB_NAME, str)


class TestSchemaSql:
    """SCHEMA_SQL constant tests"""

    def test_schema_contains_tables(self):
        """Schema defines expected tables"""
        assert "CREATE TABLE" in SCHEMA_SQL
        assert "errors" in SCHEMA_SQL
        assert "rules" in SCHEMA_SQL

    def test_schema_has_indexes(self):
        """Schema defines indexes"""
        assert "CREATE INDEX" in SCHEMA_SQL

    def test_schema_has_foreign_keys(self):
        """Schema has foreign key constraints"""
        assert "FOREIGN KEY" in SCHEMA_SQL


class TestGetDbPath:
    """get_db_path function tests"""

    def test_returns_path(self, temp_project):
        """Returns Path object"""
        result = get_db_path(str(temp_project))
        assert isinstance(result, Path)

    def test_path_includes_clouvel(self, temp_project):
        """Path includes .clouvel directory"""
        result = get_db_path(str(temp_project))
        assert ".clouvel" in str(result)

    def test_path_ends_with_db(self, temp_project):
        """Path ends with errors.db"""
        result = get_db_path(str(temp_project))
        assert result.name == DEFAULT_DB_NAME

    def test_creates_parent_dir(self, temp_project):
        """Creates .clouvel directory if not exists"""
        clouvel_dir = temp_project / ".clouvel"
        assert not clouvel_dir.exists()

        get_db_path(str(temp_project))
        assert clouvel_dir.exists()

    def test_none_path_uses_cwd(self):
        """None path uses current working directory"""
        result = get_db_path(None)
        assert isinstance(result, Path)
        assert ".clouvel" in str(result)


class TestGetConnection:
    """get_connection function tests"""

    def test_returns_connection(self, temp_project):
        """Returns sqlite3 Connection"""
        db_path = get_db_path(str(temp_project))
        conn = get_connection(db_path)
        try:
            assert isinstance(conn, sqlite3.Connection)
        finally:
            conn.close()

    def test_row_factory_set(self, temp_project):
        """Row factory is sqlite3.Row"""
        db_path = get_db_path(str(temp_project))
        conn = get_connection(db_path)
        try:
            assert conn.row_factory == sqlite3.Row
        finally:
            conn.close()

    def test_foreign_keys_enabled(self, temp_project):
        """Foreign keys are enabled"""
        db_path = get_db_path(str(temp_project))
        conn = get_connection(db_path)
        try:
            result = conn.execute("PRAGMA foreign_keys").fetchone()
            assert result[0] == 1
        finally:
            conn.close()


class TestInitDb:
    """init_db function tests"""

    def test_returns_path(self, temp_project):
        """Returns database path"""
        result = init_db(str(temp_project))
        assert isinstance(result, Path)

    def test_creates_db_file(self, temp_project):
        """Creates database file"""
        db_path = init_db(str(temp_project))
        assert db_path.exists()

    def test_creates_errors_table(self, temp_project):
        """Creates errors table"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='errors'"
            )
            result = cursor.fetchone()
            assert result is not None
        finally:
            conn.close()

    def test_creates_rules_table(self, temp_project):
        """Creates rules table"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='rules'"
            )
            result = cursor.fetchone()
            assert result is not None
        finally:
            conn.close()

    def test_creates_error_rule_mapping(self, temp_project):
        """Creates error_rule_mapping table"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='error_rule_mapping'"
            )
            result = cursor.fetchone()
            assert result is not None
        finally:
            conn.close()

    def test_creates_error_embeddings(self, temp_project):
        """Creates error_embeddings table"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='error_embeddings'"
            )
            result = cursor.fetchone()
            assert result is not None
        finally:
            conn.close()

    def test_creates_indexes(self, temp_project):
        """Creates indexes"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='index'"
            )
            indexes = [row[0] for row in cursor.fetchall()]
            assert len(indexes) > 0
        finally:
            conn.close()

    def test_idempotent(self, temp_project):
        """Can be called multiple times"""
        init_db(str(temp_project))
        init_db(str(temp_project))  # Should not raise

    def test_errors_table_schema(self, temp_project):
        """Errors table has expected columns"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute("PRAGMA table_info(errors)")
            columns = [row[1] for row in cursor.fetchall()]

            assert "id" in columns
            assert "error_type" in columns
            assert "error_message" in columns
            assert "stack_trace" in columns
            assert "five_whys" in columns
            assert "root_cause" in columns
            assert "solution" in columns
        finally:
            conn.close()

    def test_rules_table_schema(self, temp_project):
        """Rules table has expected columns"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute("PRAGMA table_info(rules)")
            columns = [row[1] for row in cursor.fetchall()]

            assert "id" in columns
            assert "rule_type" in columns
            assert "content" in columns
            assert "category" in columns
        finally:
            conn.close()


class TestRegressionMemoryTable:
    """regression_memory table tests (v4.0)"""

    def test_table_exists(self, temp_project):
        """regression_memory table is created"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='regression_memory'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_table_columns(self, temp_project):
        """regression_memory table has expected columns"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute("PRAGMA table_info(regression_memory)")
            columns = [row[1] for row in cursor.fetchall()]
            for col in ["id", "error_signature", "error_category", "file_paths",
                        "libraries", "tags", "root_cause", "prevention_rule",
                        "hit_count", "times_saved", "archived", "source_error_id"]:
                assert col in columns, f"Missing column: {col}"
        finally:
            conn.close()

    def test_fts_table_exists(self, temp_project):
        """regression_memory_fts virtual table is created"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name='regression_memory_fts'"
            )
            assert cursor.fetchone() is not None
        finally:
            conn.close()

    def test_indexes_exist(self, temp_project):
        """regression_memory indexes are created"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
            indexes = [row[0] for row in cursor.fetchall()]
            assert "idx_regression_signature" in indexes
            assert "idx_regression_category" in indexes
            assert "idx_regression_archived" in indexes
            assert "idx_regression_timestamp" in indexes
        finally:
            conn.close()


class TestDbIntegration:
    """Integration tests for database operations"""

    def test_insert_and_query_error(self, temp_project):
        """Can insert and query errors"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute(
                "INSERT INTO errors (id, error_message) VALUES (?, ?)",
                ("err-001", "Test error message")
            )
            conn.commit()

            cursor = conn.execute("SELECT * FROM errors WHERE id = ?", ("err-001",))
            result = cursor.fetchone()
            assert result is not None
        finally:
            conn.close()

    def test_insert_and_query_rule(self, temp_project):
        """Can insert and query rules"""
        db_path = init_db(str(temp_project))
        conn = sqlite3.connect(str(db_path))
        try:
            conn.execute(
                "INSERT INTO rules (id, rule_type, content) VALUES (?, ?, ?)",
                ("rule-001", "NEVER", "Test rule content")
            )
            conn.commit()

            cursor = conn.execute("SELECT * FROM rules WHERE id = ?", ("rule-001",))
            result = cursor.fetchone()
            assert result is not None
        finally:
            conn.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
