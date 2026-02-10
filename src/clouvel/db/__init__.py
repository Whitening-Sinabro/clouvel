"""Clouvel Error Database Module."""

from .schema import init_db, get_db_path
from .errors import (
    record_error,
    get_error,
    list_errors,
    resolve_error,
    search_errors_by_type,
    get_error_stats,
)
from .rules import (
    add_rule,
    get_rules,
    apply_rule,
    export_rules_to_markdown,
)
from .vectors import (
    is_vector_search_available,
    search_similar_errors,
    add_error_embedding,
    embed_all_errors,
)
from .migrate import (
    full_migration,
    migrate_error_files,
    extract_rules_from_claude_md,
)
from .regression import (
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
    # v5.0: Cross-Project Memory Transfer
    get_memory_for_promote,
)

__all__ = [
    # Schema
    "init_db",
    "get_db_path",
    # Errors
    "record_error",
    "get_error",
    "list_errors",
    "resolve_error",
    "search_errors_by_type",
    "get_error_stats",
    # Rules
    "add_rule",
    "get_rules",
    "apply_rule",
    "export_rules_to_markdown",
    # Vectors
    "is_vector_search_available",
    "search_similar_errors",
    "add_error_embedding",
    "embed_all_errors",
    # Migration
    "full_migration",
    "migrate_error_files",
    "extract_rules_from_claude_md",
    # Regression Memory
    "normalize_error_signature",
    "create_memory",
    "get_memory",
    "list_memories",
    "match_level1_exact",
    "match_level2_tags",
    "match_level3_fts",
    "match_all_levels",
    "increment_hit_count",
    "increment_times_saved",
    "archive_memory",
    "unarchive_memory",
    "get_memory_stats",
    "search_memories",
    "mark_stale_memories",
    "get_memory_report",
    "get_memory_for_promote",
]
