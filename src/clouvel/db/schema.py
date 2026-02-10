"""SQLite schema for Clouvel Error System v2.0."""

import sqlite3
from pathlib import Path
from typing import Optional

# 기본 DB 경로: 프로젝트 .clouvel 폴더
DEFAULT_DB_NAME = "errors.db"


def get_db_path(project_path: Optional[str] = None) -> Path:
    """Get database path for a project."""
    if project_path:
        base = Path(project_path) / ".clouvel"
    else:
        base = Path.cwd() / ".clouvel"

    base.mkdir(parents=True, exist_ok=True)
    return base / DEFAULT_DB_NAME


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """Get database connection with row factory."""
    if db_path is None:
        db_path = get_db_path()

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db(project_path: Optional[str] = None) -> Path:
    """Initialize database with schema."""
    db_path = get_db_path(project_path)

    conn = get_connection(db_path)
    try:
        conn.executescript(SCHEMA_SQL)
        conn.commit()
    finally:
        conn.close()

    return db_path


SCHEMA_SQL = """
-- 에러 기록
CREATE TABLE IF NOT EXISTS errors (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    error_type TEXT,
    error_message TEXT NOT NULL,
    stack_trace TEXT,
    context TEXT,
    file_path TEXT,
    five_whys TEXT,  -- JSON array
    root_cause TEXT,
    solution TEXT,
    prevention TEXT,
    resolved_at TIMESTAMP,
    resolution_effective INTEGER  -- 0 or 1
);

-- 학습된 규칙
CREATE TABLE IF NOT EXISTS rules (
    id TEXT PRIMARY KEY,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rule_type TEXT NOT NULL,  -- NEVER, ALWAYS, PREFER
    content TEXT NOT NULL,
    category TEXT,  -- api, frontend, database, security, general
    source_error_id TEXT,
    applied_count INTEGER DEFAULT 0,
    last_applied TIMESTAMP,
    FOREIGN KEY (source_error_id) REFERENCES errors(id)
);

-- 에러-규칙 연결 (다대다)
CREATE TABLE IF NOT EXISTS error_rule_mapping (
    error_id TEXT NOT NULL,
    rule_id TEXT NOT NULL,
    prevented INTEGER DEFAULT 0,  -- 규칙이 에러 예방했는지
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (error_id, rule_id),
    FOREIGN KEY (error_id) REFERENCES errors(id),
    FOREIGN KEY (rule_id) REFERENCES rules(id)
);

-- 에러 임베딩 메타데이터 (ChromaDB 연동용)
CREATE TABLE IF NOT EXISTS error_embeddings (
    error_id TEXT PRIMARY KEY,
    embedded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    embedding_model TEXT DEFAULT 'all-MiniLM-L6-v2',
    FOREIGN KEY (error_id) REFERENCES errors(id)
);

-- 인덱스
CREATE INDEX IF NOT EXISTS idx_errors_type ON errors(error_type);
CREATE INDEX IF NOT EXISTS idx_errors_created ON errors(created_at);
CREATE INDEX IF NOT EXISTS idx_errors_resolved ON errors(resolved_at);
CREATE INDEX IF NOT EXISTS idx_rules_type ON rules(rule_type);
CREATE INDEX IF NOT EXISTS idx_rules_category ON rules(category);

-- Regression Memory (v4.0)
CREATE TABLE IF NOT EXISTS regression_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    project_name TEXT,
    error_signature TEXT,
    error_category TEXT,
    file_paths TEXT,          -- JSON array
    libraries TEXT,           -- JSON array
    tags TEXT,                -- JSON array
    task_description TEXT,
    code_snippet TEXT,
    fix_snippet TEXT,
    root_cause TEXT,
    prevention_rule TEXT,
    negative_constraint TEXT,
    severity INTEGER DEFAULT 3,
    hit_count INTEGER DEFAULT 0,
    times_saved INTEGER DEFAULT 0,
    archived BOOLEAN DEFAULT 0,
    stale_check_at DATETIME,
    source_error_id TEXT,
    FOREIGN KEY (source_error_id) REFERENCES errors(id)
);

CREATE INDEX IF NOT EXISTS idx_regression_signature ON regression_memory(error_signature);
CREATE INDEX IF NOT EXISTS idx_regression_category ON regression_memory(error_category);
CREATE INDEX IF NOT EXISTS idx_regression_archived ON regression_memory(archived);
CREATE INDEX IF NOT EXISTS idx_regression_timestamp ON regression_memory(timestamp);

CREATE VIRTUAL TABLE IF NOT EXISTS regression_memory_fts USING fts5(
    task_description, root_cause, prevention_rule,
    content='regression_memory', content_rowid='id'
);
"""
