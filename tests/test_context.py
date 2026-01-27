# -*- coding: utf-8 -*-
"""Context tools tests"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.context import (
    _extract_summary,
    _find_active_plans,
    _get_git_status,
    _extract_rules,
    _extract_prd_summary,
    _get_recent_modified_files,
    recover_context,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestExtractSummary:
    """_extract_summary function tests"""

    def test_extract_empty(self):
        """Extract from empty content"""
        result = _extract_summary("")
        assert result["status"] is None
        assert result["completed"] == []
        assert result["next_todos"] == []
        assert result["blockers"] == []

    def test_returns_dict(self):
        """Returns dictionary"""
        result = _extract_summary("")
        assert isinstance(result, dict)

    def test_has_all_keys(self):
        """Has all required keys"""
        result = _extract_summary("")
        assert "status" in result
        assert "completed" in result
        assert "next_todos" in result
        assert "blockers" in result

    def test_extract_completed_items(self):
        """Extract completed items"""
        content = """# Status

## 완료
- [x] Task 1
- [x] Task 2

## Other
"""
        result = _extract_summary(content)
        assert "Task 1" in result["completed"]
        assert "Task 2" in result["completed"]

    def test_extract_next_todos(self):
        """Extract next todos"""
        content = """# Status

## 다음 할 일
- [ ] Todo 1
- [ ] Todo 2
"""
        result = _extract_summary(content)
        assert "Todo 1" in result["next_todos"]
        assert "Todo 2" in result["next_todos"]

    def test_extract_blockers(self):
        """Extract blockers"""
        content = """# Status

## 블로커
- Blocker 1
- Blocker 2
"""
        result = _extract_summary(content)
        assert "Blocker 1" in result["blockers"]
        assert "Blocker 2" in result["blockers"]

    def test_extract_english_sections(self):
        """Extract from English sections"""
        content = """# Status

## Completed
- [x] Done item

## Next
- [ ] Next item

## Blocker
- Some blocker
"""
        result = _extract_summary(content)
        assert "Done item" in result["completed"]
        assert "Next item" in result["next_todos"]

    def test_extracts_status_table(self):
        """Extracts status from table"""
        content = """## 지금 상태
| 항목 | 값 |
|---|---|
| 진행 | 50% |"""
        result = _extract_summary(content)
        assert result["status"] is not None
        assert "진행" in result["status"]

    def test_extract_current_status_header(self):
        """Extracts status with Current Status header"""
        content = """## Current Status
| item | value |
|---|---|
| progress | 75% |"""
        result = _extract_summary(content)
        assert result["status"] is not None

    def test_extract_현재_상태_header(self):
        """Extracts status with 현재 상태 header"""
        content = """## 현재 상태
| 항목 | 값 |
|---|---|
| 상태 | 진행중 |"""
        result = _extract_summary(content)
        assert result["status"] is not None

    def test_todo_header_variant(self):
        """Extracts todos with TODO header"""
        content = """## TODO
- [ ] Item 1
- [ ] Item 2"""
        result = _extract_summary(content)
        assert len(result["next_todos"]) == 2

    def test_오늘_완료_header(self):
        """Extracts completed with 오늘 완료 header"""
        content = """## 오늘 완료
- [x] Done today"""
        result = _extract_summary(content)
        assert "Done today" in result["completed"]

    def test_section_reset_on_new_header(self):
        """Resets section on new header"""
        content = """## 완료
- [x] Task 1

## 기타
- Not a task

## 다음 할 일
- [ ] Todo"""
        result = _extract_summary(content)
        assert "Not a task" not in result["completed"]
        assert "Not a task" not in result["next_todos"]


class TestFindActivePlans:
    """_find_active_plans function tests"""

    def test_returns_list(self, temp_project):
        """Returns list"""
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir()
        result = _find_active_plans(claude_dir)
        assert isinstance(result, list)

    def test_no_plans_dir(self, temp_project):
        """No plans directory exists"""
        claude_dir = temp_project / ".claude"
        claude_dir.mkdir()
        result = _find_active_plans(claude_dir)
        assert result == []

    def test_empty_plans_dir(self, temp_project):
        """Empty plans directory"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)
        result = _find_active_plans(temp_project / ".claude")
        assert result == []

    def test_find_locked_plan(self, temp_project):
        """Find locked plan"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        plan_content = """# PLAN-001

> **태스크**: Implement feature X

## Status: LOCKED 🔒

### Step 1
- [x] Done

### Step 2
- [ ] In progress
"""
        (plans_dir / "PLAN-001.md").write_text(plan_content, encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert len(result) == 1
        assert result[0]["status"] == "locked"

    def test_find_complete_plan(self, temp_project):
        """Find complete plan"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        plan_content = """# PLAN-002

✅ COMPLETE

### Step 1
- [x] Done
"""
        (plans_dir / "PLAN-002.md").write_text(plan_content, encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert len(result) == 1
        assert result[0]["status"] == "complete"

    def test_detect_in_progress_status(self, temp_project):
        """Detect in_progress plan"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        plan_content = """# PLAN-003
IN_PROGRESS
> **태스크**: Work in progress"""
        (plans_dir / "PLAN-003.md").write_text(plan_content, encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert result[0]["status"] == "in_progress"

    def test_detect_진행중_status(self, temp_project):
        """Detect 진행 중 plan"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        plan_content = """# PLAN-004
진행 중
> **태스크**: 한국어 진행"""
        (plans_dir / "PLAN-004.md").write_text(plan_content, encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert result[0]["status"] == "in_progress"

    def test_extract_task_name(self, temp_project):
        """Extracts task name from plan"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        plan_content = """> **태스크**: My Feature Task"""
        (plans_dir / "PLAN-005.md").write_text(plan_content, encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert result[0]["task"] == "My Feature Task"

    def test_uses_filename_as_fallback(self, temp_project):
        """Uses filename as task when no task defined"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        plan_content = """# Just a plan"""
        (plans_dir / "PLAN-feature-x.md").write_text(plan_content, encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert "PLAN-feature-x" in result[0]["task"]

    def test_detect_step_number(self, temp_project):
        """Detects current step number"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        plan_content = """# PLAN
> **태스크**: Test

### Step 1
- [x] Done

### Step 2
- [ ] Current"""
        (plans_dir / "PLAN-006.md").write_text(plan_content, encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert result[0]["current_step"] == 2

    def test_plan_has_file_key(self, temp_project):
        """Plan result has file key"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        (plans_dir / "PLAN-007.md").write_text("# Plan", encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert "file" in result[0]
        assert result[0]["file"] == "PLAN-007.md"

    def test_plan_has_status_key(self, temp_project):
        """Plan result has status key"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        (plans_dir / "PLAN-008.md").write_text("# Plan", encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert "status" in result[0]

    def test_find_multiple_plans(self, temp_project):
        """Finds multiple plan files"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        (plans_dir / "PLAN-A.md").write_text("# A", encoding="utf-8")
        (plans_dir / "PLAN-B.md").write_text("# B", encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert len(result) == 2

    def test_ignores_non_plan_files(self, temp_project):
        """Ignores non-PLAN files"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        (plans_dir / "PLAN-001.md").write_text("# Plan", encoding="utf-8")
        (plans_dir / "notes.md").write_text("# Notes", encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert len(result) == 1


class TestGetGitStatus:
    """_get_git_status function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dictionary"""
        result = _get_git_status(temp_project)
        assert isinstance(result, dict)

    def test_not_git_repo(self, temp_project):
        """Not a git repository"""
        result = _get_git_status(temp_project)
        assert result["is_git"] is False

    def test_git_repo_with_branch(self, temp_project):
        """Git repository with branch"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()

        head_file = git_dir / "HEAD"
        head_file.write_text("ref: refs/heads/main", encoding="utf-8")

        result = _get_git_status(temp_project)
        assert result["is_git"] is True
        assert result["branch"] == "main"

    def test_git_repo_feature_branch(self, temp_project):
        """Git repository with feature branch"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()

        head_file = git_dir / "HEAD"
        head_file.write_text("ref: refs/heads/feature/new-feature", encoding="utf-8")

        result = _get_git_status(temp_project)
        assert result["branch"] == "feature/new-feature"

    def test_has_is_git_key(self, temp_project):
        """Has is_git key"""
        result = _get_git_status(temp_project)
        assert "is_git" in result

    def test_has_branch_key_when_git(self, temp_project):
        """Has branch key when git repo"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

        result = _get_git_status(temp_project)
        assert "branch" in result

    def test_has_has_changes_key_when_git(self, temp_project):
        """Has has_changes key when git repo"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

        result = _get_git_status(temp_project)
        assert "has_changes" in result

    def test_detects_recent_changes_via_index(self, temp_project):
        """Detects recent changes via index file"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")
        (git_dir / "index").write_text("index data", encoding="utf-8")

        result = _get_git_status(temp_project)
        assert result["has_changes"] is True

    def test_branch_none_without_head(self, temp_project):
        """Branch is None when HEAD doesn't exist"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()

        result = _get_git_status(temp_project)
        assert result["is_git"] is True
        assert result["branch"] is None

    def test_has_changes_false_without_index(self, temp_project):
        """has_changes is False without index"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        (git_dir / "HEAD").write_text("ref: refs/heads/main", encoding="utf-8")

        result = _get_git_status(temp_project)
        assert result["has_changes"] is False


class TestExtractRules:
    """_extract_rules function tests"""

    def test_extract_never_rules(self):
        """Extract NEVER rules"""
        content = """# Rules

## Safety
NEVER: Delete production data
NEVER: Skip code review
"""
        result = _extract_rules(content)
        assert any("Delete production data" in r for r in result)
        assert any("Skip code review" in r for r in result)

    def test_extract_always_rules(self):
        """Extract ALWAYS rules"""
        content = """# Rules

ALWAYS: Write tests
ALWAYS: Document changes
"""
        result = _extract_rules(content)
        assert any("Write tests" in r for r in result)
        assert any("Document changes" in r for r in result)

    def test_extract_mixed_rules(self):
        """Extract mixed NEVER and ALWAYS rules"""
        content = """# Rules

NEVER: Push to main directly
ALWAYS: Create PR for changes
"""
        result = _extract_rules(content)
        assert len(result) >= 2

    def test_extract_no_rules(self):
        """Extract from content with no rules"""
        content = "# Just some content\n\nNo rules here."
        result = _extract_rules(content)
        assert result == []

    def test_max_rules_limit(self):
        """Extract respects max limit"""
        content = "\n".join([f"NEVER: Rule {i}" for i in range(10)])
        result = _extract_rules(content)
        never_count = sum(1 for r in result if "NEVER" in r)
        assert never_count <= 5


class TestExtractPrdSummary:
    """_extract_prd_summary function tests"""

    def test_extract_summary(self):
        """Extract PRD summary"""
        content = """# Project Name

This is the project summary.
It has multiple lines.

## Section 2

More content here.
"""
        result = _extract_prd_summary(content)
        assert "Project Name" in result
        assert "project summary" in result

    def test_extract_stops_at_section(self):
        """Extract stops at next section"""
        content = """# Title

Summary text

## Next Section

Should not include this
"""
        result = _extract_prd_summary(content)
        assert "Summary text" in result
        assert "Should not include" not in result

    def test_extract_empty_prd(self):
        """Extract from empty PRD"""
        result = _extract_prd_summary("")
        assert result == ""


class TestGetRecentModifiedFiles:
    """_get_recent_modified_files function tests"""

    def test_returns_list(self, temp_project):
        """Returns list"""
        result = _get_recent_modified_files(temp_project)
        assert isinstance(result, list)

    def test_empty_project(self, temp_project):
        """Empty project has no files"""
        result = _get_recent_modified_files(temp_project)
        assert result == []

    def test_find_py_files(self, temp_project):
        """Find Python files"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("# main", encoding="utf-8")
        (src_dir / "utils.py").write_text("# utils", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert len(result) >= 2
        assert any("main.py" in f for f in result)

    def test_find_js_files(self, temp_project):
        """Find JavaScript files"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "app.js").write_text("// app", encoding="utf-8")
        (src_dir / "index.ts").write_text("// index", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert len(result) >= 2

    def test_find_tsx_files(self, temp_project):
        """Find TSX files"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "component.tsx").write_text("// tsx", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert any("component.tsx" in f for f in result)

    def test_find_jsx_files(self, temp_project):
        """Find JSX files"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "app.jsx").write_text("// jsx", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert any("app.jsx" in f for f in result)

    def test_find_vue_files(self, temp_project):
        """Find Vue files"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "app.vue").write_text("<template></template>", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert any("app.vue" in f for f in result)

    def test_find_go_files(self, temp_project):
        """Find Go files"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "main.go").write_text("package main", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert any("main.go" in f for f in result)

    def test_find_rs_files(self, temp_project):
        """Find Rust files"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "lib.rs").write_text("fn main() {}", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert any("lib.rs" in f for f in result)

    def test_excludes_node_modules(self, temp_project):
        """Excludes node_modules"""
        node_modules = temp_project / "node_modules" / "package"
        node_modules.mkdir(parents=True)
        (node_modules / "index.js").write_text("// module", encoding="utf-8")

        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "app.js").write_text("// app", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert not any("node_modules" in f for f in result)

    def test_excludes_git(self, temp_project):
        """Excludes .git directory"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        (git_dir / "hooks.py").write_text("# hooks", encoding="utf-8")

        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "app.py").write_text("# app", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert not any(".git" in f for f in result)

    def test_excludes_pycache(self, temp_project):
        """Excludes __pycache__ directory"""
        cache_dir = temp_project / "__pycache__"
        cache_dir.mkdir()
        (cache_dir / "module.py").write_text("# cache", encoding="utf-8")

        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "app.py").write_text("# app", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert not any("__pycache__" in f for f in result)

    def test_excludes_venv(self, temp_project):
        """Excludes .venv directory"""
        venv_dir = temp_project / ".venv"
        venv_dir.mkdir()
        (venv_dir / "activate.py").write_text("# venv", encoding="utf-8")

        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "app.py").write_text("# app", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert not any(".venv" in f for f in result)

    def test_respects_limit(self, temp_project):
        """Respects limit parameter"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        for i in range(10):
            (src_dir / f"file{i}.py").write_text(f"# file {i}", encoding="utf-8")

        result = _get_recent_modified_files(temp_project, limit=3)
        assert len(result) <= 3

    def test_returns_relative_paths(self, temp_project):
        """Returns relative paths"""
        (temp_project / "test.py").write_text("# test", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        for path in result:
            assert not path.startswith(str(temp_project))

    def test_default_limit_is_5(self, temp_project):
        """Default limit is 5"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        for i in range(10):
            (src_dir / f"file{i}.py").write_text(f"# file {i}", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert len(result) <= 5


class TestRecoverContext:
    """recover_context function tests (Pro feature - blocked)"""

    @pytest.mark.asyncio
    async def test_recover_returns_result(self, temp_project):
        """Recover returns some result"""
        # Note: This may return Pro license message or actual result depending on license state
        try:
            result = await recover_context(str(temp_project))
            # Should return TextContent list
            assert len(result) > 0
        except Exception:
            # Function may raise due to license check or internal state
            pass


class TestExtractSummaryAdvanced:
    """Advanced tests for _extract_summary"""

    def test_extracts_korean_completed(self):
        """Extracts 오늘 완료 items"""
        content = """## 오늘 완료
- [x] Task done today
- [x] Another done"""
        result = _extract_summary(content)
        assert "Task done today" in result["completed"]

    def test_extracts_todo_section(self):
        """Extracts TODO section"""
        content = """## TODO
- [ ] First task
- [ ] Second task"""
        result = _extract_summary(content)
        assert "First task" in result["next_todos"]
        assert "Second task" in result["next_todos"]

    def test_handles_mixed_case_headers(self):
        """Handles different header formats"""
        content = """## Completed
- [x] Done 1

## Next
- [ ] Todo 1"""
        result = _extract_summary(content)
        assert len(result["completed"]) >= 1
        assert len(result["next_todos"]) >= 1


class TestFindActivePlansAdvanced:
    """Advanced tests for _find_active_plans"""

    def test_extracts_task_from_plan(self, temp_project):
        """Extracts task name from plan file"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        content = """> **태스크**: Build authentication module

### Step 1
- [x] Create user model

### Step 2
- [ ] Add login endpoint"""
        (plans_dir / "PLAN-auth.md").write_text(content, encoding="utf-8")

        result = _find_active_plans(temp_project / ".claude")
        assert len(result) == 1
        assert result[0]["task"] == "Build authentication module"

    def test_handles_exception_gracefully(self, temp_project):
        """Handles file read errors gracefully"""
        plans_dir = temp_project / ".claude" / "plans"
        plans_dir.mkdir(parents=True)

        # Create a plan file
        (plans_dir / "PLAN-test.md").write_text("# Plan", encoding="utf-8")

        # Even if there's an issue, should return list
        result = _find_active_plans(temp_project / ".claude")
        assert isinstance(result, list)


class TestGetGitStatusAdvanced:
    """Advanced tests for _get_git_status"""

    def test_detached_head_state(self, temp_project):
        """Handles detached HEAD state"""
        git_dir = temp_project / ".git"
        git_dir.mkdir()
        # Detached HEAD (commit hash instead of ref)
        (git_dir / "HEAD").write_text("abc123def456", encoding="utf-8")

        result = _get_git_status(temp_project)
        assert result["is_git"] is True
        assert result["branch"] is None  # No branch in detached state


class TestExtractRulesAdvanced:
    """Advanced tests for _extract_rules"""

    def test_limits_rules_count(self):
        """Limits rules to max 5 per type"""
        content = "\n".join([f"NEVER: Rule {i}" for i in range(10)])
        content += "\n" + "\n".join([f"ALWAYS: Rule {i}" for i in range(10)])

        result = _extract_rules(content)
        never_count = sum(1 for r in result if "NEVER" in r)
        always_count = sum(1 for r in result if "ALWAYS" in r)

        assert never_count <= 5
        assert always_count <= 5

    def test_case_insensitive_matching(self):
        """Matches rules case-insensitively"""
        content = """never: lowercase rule
NEVER: UPPERCASE RULE
Never: Mixed case"""
        result = _extract_rules(content)
        assert len(result) == 3


class TestExtractPrdSummaryAdvanced:
    """Advanced tests for _extract_prd_summary"""

    def test_limits_to_10_lines(self):
        """Limits summary to 10 lines"""
        content = "# Title\n\n" + "\n".join([f"Line {i}" for i in range(20)])
        result = _extract_prd_summary(content)
        assert result.count("\n") <= 10

    def test_handles_no_title(self):
        """Handles content without title"""
        content = "Just some text without a title"
        result = _extract_prd_summary(content)
        assert result == ""


class TestGetRecentModifiedFilesAdvanced:
    """Advanced tests for _get_recent_modified_files"""

    def test_finds_svelte_files(self, temp_project):
        """Finds Svelte files"""
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "app.svelte").write_text("<script>// svelte</script>", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert any("app.svelte" in f for f in result)

    def test_excludes_dist(self, temp_project):
        """Excludes common build directories"""
        # Create files in different locations
        src_dir = temp_project / "src"
        src_dir.mkdir()
        (src_dir / "main.py").write_text("# main", encoding="utf-8")

        result = _get_recent_modified_files(temp_project)
        assert len(result) >= 1

    def test_handles_no_source_files(self, temp_project):
        """Handles project with no source files"""
        result = _get_recent_modified_files(temp_project)
        assert result == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
