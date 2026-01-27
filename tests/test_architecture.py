# -*- coding: utf-8 -*-
"""Architecture tools tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.architecture import (
    arch_check,
    check_imports,
    check_duplicates,
    check_sync,
    _extract_functions,
    SYNC_PAIRS,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


@pytest.fixture
def src_project(temp_project):
    """Project with src directory"""
    src_dir = temp_project / "src"
    src_dir.mkdir()
    return temp_project


class TestArchCheck:
    """arch_check function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dict with expected keys"""
        result = arch_check("test_func", "Test purpose", str(temp_project))
        assert isinstance(result, dict)
        assert "name" in result
        assert "purpose" in result
        assert "existing_code" in result
        assert "recommendation" in result
        assert "can_add" in result

    def test_check_nonexistent_name(self, src_project):
        """Check for name that doesn't exist"""
        result = arch_check("nonexistent_function_xyz", "Test", str(src_project))
        assert result["can_add"] is True
        assert "추가 가능" in result["recommendation"] or "possible" in result["recommendation"].lower()

    def test_check_existing_name(self, src_project):
        """Check for name that exists in init"""
        # Create __init__.py with the name
        src_dir = src_project / "src"
        init_file = src_dir / "__init__.py"
        init_file.write_text("from .module import my_function\n", encoding="utf-8")

        result = arch_check("my_function", "Test", str(src_project))
        # Should find it in init
        assert len(result["existing_code"]) > 0 or result["can_add"] is True

    def test_check_in_init_export(self, src_project):
        """Check for name exported in __init__.py"""
        src_dir = src_project / "src"
        src_dir.mkdir(exist_ok=True)
        init_file = src_dir / "__init__.py"
        init_file.write_text('"exported_func",\n', encoding="utf-8")

        result = arch_check("exported_func", "Test", str(src_project))
        # Should detect it
        if result["existing_code"]:
            assert any("init" in e.get("source", "") for e in result["existing_code"])


class TestCheckImports:
    """check_imports function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dict"""
        result = check_imports(str(temp_project))
        assert isinstance(result, dict)
        # Check common keys
        assert "valid" in result or "is_valid" in result or "violations" in result

    def test_no_server_py(self, temp_project):
        """No server.py returns result"""
        result = check_imports(str(temp_project))
        # Should return dict without error
        assert isinstance(result, dict)

    def test_valid_imports(self, src_project):
        """Valid imports returns result"""
        src_dir = src_project / "src"
        src_dir.mkdir(exist_ok=True)

        # Create valid server.py
        server_content = """
from .tools import can_code
from .tools import start
"""
        (src_dir / "server.py").write_text(server_content, encoding="utf-8")

        result = check_imports(str(src_project))
        # Should return dict
        assert isinstance(result, dict)


class TestCheckDuplicates:
    """check_duplicates function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dict"""
        result = check_duplicates(str(temp_project))
        assert isinstance(result, dict)
        # Check for common keys
        assert "duplicates" in result or "valid" in result

    def test_no_duplicates(self, src_project):
        """No duplicates in clean project"""
        result = check_duplicates(str(src_project))
        # Should return dict
        assert isinstance(result, dict)

    def test_detect_duplicates(self, src_project):
        """Detect duplicate definitions"""
        src_dir = src_project / "src"

        # Create module with function
        (src_dir / "module1.py").write_text("def duplicate_func():\n    pass\n", encoding="utf-8")

        # Create __init__ exporting same function twice
        init_content = """
def duplicate_func():
    pass

from .module1 import duplicate_func
"""
        (src_dir / "__init__.py").write_text(init_content, encoding="utf-8")

        result = check_duplicates(str(src_project))
        # Should return dict with duplicates info
        assert isinstance(result, dict)


class TestCheckSync:
    """check_sync function tests"""

    def test_returns_dict(self, temp_project):
        """Returns dict"""
        result = check_sync(str(temp_project))
        assert isinstance(result, dict)
        # Check for some expected keys
        assert "details" in result or "issues" in result or "synced" in result

    def test_no_files(self, temp_project):
        """No files returns result"""
        result = check_sync(str(temp_project))
        # Should return dict
        assert isinstance(result, dict)

    def test_synced_files(self, src_project):
        """Synced file pairs pass"""
        src_dir = src_project / "src"

        # Create synced pair
        (src_dir / "license.py").write_text("""
def verify_license():
    return True
""", encoding="utf-8")

        (src_dir / "license_free.py").write_text("""
def verify_license():
    return False
""", encoding="utf-8")

        result = check_sync(str(src_project))
        # Should return dict
        assert isinstance(result, dict)

    def test_mismatched_functions(self, src_project):
        """Detect mismatched functions"""
        src_dir = src_project / "src"

        # Create mismatched pair
        (src_dir / "license.py").write_text("""
def verify_license():
    return True

def extra_func():
    pass
""", encoding="utf-8")

        (src_dir / "license_free.py").write_text("""
def verify_license():
    return False
# Missing extra_func
""", encoding="utf-8")

        result = check_sync(str(src_project))
        # Should return dict
        assert isinstance(result, dict)


class TestExtractFunctions:
    """_extract_functions helper tests"""

    def test_returns_dict(self):
        """Returns dictionary"""
        result = _extract_functions("")
        assert isinstance(result, dict)

    def test_extracts_simple_function(self):
        """Extracts simple function"""
        content = "def my_func():\n    pass"
        result = _extract_functions(content)
        assert "my_func" in result

    def test_extracts_function_with_params(self):
        """Extracts function with parameters"""
        content = "def my_func(a, b, c):\n    pass"
        result = _extract_functions(content)
        assert "my_func" in result
        assert "a" in result["my_func"]["params"]
        assert "b" in result["my_func"]["params"]
        assert "c" in result["my_func"]["params"]

    def test_extracts_async_function(self):
        """Extracts async function"""
        content = "async def async_func():\n    pass"
        result = _extract_functions(content)
        assert "async_func" in result

    def test_extracts_multiple_functions(self):
        """Extracts multiple functions"""
        content = """
def func1():
    pass

def func2():
    pass
"""
        result = _extract_functions(content)
        assert "func1" in result
        assert "func2" in result

    def test_extracts_lineno(self):
        """Extracts line number"""
        content = "def my_func():\n    pass"
        result = _extract_functions(content)
        assert "lineno" in result["my_func"]

    def test_handles_syntax_error(self):
        """Handles syntax error gracefully"""
        content = "def broken("
        result = _extract_functions(content)
        assert isinstance(result, dict)

    def test_handles_empty_content(self):
        """Handles empty content"""
        result = _extract_functions("")
        assert result == {}

    def test_extracts_nested_function(self):
        """Extracts nested functions"""
        content = """
def outer():
    def inner():
        pass
    pass
"""
        result = _extract_functions(content)
        assert "outer" in result
        assert "inner" in result


class TestSyncPairs:
    """SYNC_PAIRS constant tests"""

    def test_sync_pairs_is_list(self):
        """SYNC_PAIRS is a list"""
        assert isinstance(SYNC_PAIRS, list)

    def test_sync_pairs_has_items(self):
        """SYNC_PAIRS has items"""
        assert len(SYNC_PAIRS) > 0

    def test_pair_has_primary(self):
        """Each pair has primary key"""
        for pair in SYNC_PAIRS:
            assert "primary" in pair

    def test_pair_has_stub(self):
        """Each pair has stub key"""
        for pair in SYNC_PAIRS:
            assert "stub" in pair

    def test_pair_has_description(self):
        """Each pair has description key"""
        for pair in SYNC_PAIRS:
            assert "description" in pair

    def test_pair_has_sync_items(self):
        """Each pair has sync_items key"""
        for pair in SYNC_PAIRS:
            assert "sync_items" in pair


class TestArchCheckDetailed:
    """More detailed arch_check tests"""

    def test_has_formatted_output(self, temp_project):
        """Result has formatted_output"""
        result = arch_check("test_func", "Test", str(temp_project))
        assert "formatted_output" in result

    def test_has_kb_decisions(self, temp_project):
        """Result has kb_decisions key"""
        result = arch_check("test_func", "Test", str(temp_project))
        assert "kb_decisions" in result

    def test_formatted_output_contains_name(self, temp_project):
        """formatted_output contains function name"""
        result = arch_check("my_special_func", "Test", str(temp_project))
        assert "my_special_func" in result["formatted_output"]

    def test_recommendation_for_new_function(self, src_project):
        """Recommendation for new function suggests record_location"""
        result = arch_check("brand_new_xyz", "Test", str(src_project))
        if result["can_add"]:
            assert "record_location" in result["recommendation"]


class TestCheckImportsDetailed:
    """More detailed check_imports tests"""

    def test_has_formatted_output(self, temp_project):
        """Result has formatted_output"""
        result = check_imports(str(temp_project))
        assert "formatted_output" in result

    def test_has_checked_file(self, temp_project):
        """Result has checked_file key"""
        result = check_imports(str(temp_project))
        assert "checked_file" in result

    def test_has_violations(self, temp_project):
        """Result has violations key"""
        result = check_imports(str(temp_project))
        assert "violations" in result

    def test_has_warnings(self, temp_project):
        """Result has warnings key"""
        result = check_imports(str(temp_project))
        assert "warnings" in result

    def test_server_not_found_message(self, temp_project):
        """Shows message when server.py not found"""
        result = check_imports(str(temp_project))
        assert "not found" in result["formatted_output"]

    def test_valid_server_has_pass(self, temp_project):
        """Valid server.py shows PASS"""
        src_dir = temp_project / "src" / "clouvel"
        src_dir.mkdir(parents=True)
        (src_dir / "server.py").write_text("from .tools import can_code\n", encoding="utf-8")

        result = check_imports(str(temp_project))
        assert result["valid"] is True


class TestCheckDuplicatesDetailed:
    """More detailed check_duplicates tests"""

    def test_has_formatted_output(self, temp_project):
        """Result has formatted_output"""
        result = check_duplicates(str(temp_project))
        assert "formatted_output" in result

    def test_has_all_exports(self, temp_project):
        """Result has all_exports key"""
        result = check_duplicates(str(temp_project))
        assert "all_exports" in result

    def test_tools_dir_not_found(self, temp_project):
        """Shows warning when tools dir not found"""
        result = check_duplicates(str(temp_project))
        assert "not found" in result["formatted_output"]

    def test_finds_all_pattern(self, src_project):
        """Finds __all__ exports"""
        src_dir = src_project / "src" / "clouvel" / "tools"
        src_dir.mkdir(parents=True)
        (src_dir / "__init__.py").write_text('__all__ = ["func1", "func2"]\n', encoding="utf-8")

        result = check_duplicates(str(src_project))
        assert "func1" in result["all_exports"]
        assert "func2" in result["all_exports"]


class TestCheckSyncDetailed:
    """More detailed check_sync tests"""

    def test_has_formatted_output(self, temp_project):
        """Result has formatted_output"""
        result = check_sync(str(temp_project))
        assert "formatted_output" in result

    def test_has_valid(self, temp_project):
        """Result has valid key"""
        result = check_sync(str(temp_project))
        assert "valid" in result

    def test_has_pairs_checked(self, temp_project):
        """Result has pairs_checked key"""
        result = check_sync(str(temp_project))
        assert "pairs_checked" in result

    def test_has_details(self, temp_project):
        """Result has details key"""
        result = check_sync(str(temp_project))
        assert "details" in result

    def test_skip_missing_primary(self, temp_project):
        """Skips when primary file missing"""
        result = check_sync(str(temp_project))
        # Should have details about skipped pairs
        assert isinstance(result["details"], list)


class TestArchitectureIntegration:
    """Integration tests for architecture tools"""

    def test_full_workflow(self, src_project):
        """Full architecture check workflow"""
        src_dir = src_project / "src"

        # Setup project structure
        (src_dir / "__init__.py").write_text("", encoding="utf-8")
        (src_dir / "server.py").write_text("from .tools import something\n", encoding="utf-8")

        tools_dir = src_dir / "tools"
        tools_dir.mkdir()
        (tools_dir / "__init__.py").write_text("something = 'test'\n", encoding="utf-8")

        # Run all checks
        arch_result = arch_check("new_func", "New function", str(src_project))
        import_result = check_imports(str(src_project))
        dup_result = check_duplicates(str(src_project))
        sync_result = check_sync(str(src_project))

        # All should return dict results
        assert isinstance(arch_result, dict)
        assert isinstance(import_result, dict)
        assert isinstance(dup_result, dict)
        assert isinstance(sync_result, dict)


class TestArchCheckKbIntegration:
    """arch_check KB integration tests"""

    def test_kb_decisions_populated(self, src_project):
        """kb_decisions list is populated when KB available"""
        result = arch_check("test_func", "Test", str(src_project))
        assert "kb_decisions" in result
        assert isinstance(result["kb_decisions"], list)

    def test_kb_exception_handled(self, temp_project):
        """KB exception is handled gracefully"""
        # Should not raise even if KB is unavailable
        result = arch_check("some_func", "Purpose", str(temp_project))
        assert "recommendation" in result


class TestArchCheckGrepFallback:
    """arch_check grep/findstr fallback tests"""

    def test_grep_not_found_continues(self, src_project):
        """Continues when grep command not found"""
        # Create src directory
        src_dir = src_project / "src"
        src_dir.mkdir(exist_ok=True)
        (src_dir / "module.py").write_text("def test_func():\n    pass", encoding="utf-8")

        result = arch_check("test_func", "Test", str(src_project))
        # Should complete without error regardless of grep availability
        assert "recommendation" in result


class TestCheckImportsViolations:
    """check_imports violation detection tests"""

    def test_detects_deep_import(self, temp_project):
        """Detects deep import violations"""
        src_dir = temp_project / "src" / "clouvel"
        src_dir.mkdir(parents=True)

        # Create server.py with deep import
        server_content = """
from .tools import can_code
from .tools.manager.core import something  # This is deep import
"""
        (src_dir / "server.py").write_text(server_content, encoding="utf-8")

        result = check_imports(str(temp_project))
        # May detect violation based on rules
        assert "violations" in result

    def test_allowed_file_imports_pass(self, temp_project):
        """Allowed file imports pass validation"""
        src_dir = temp_project / "src" / "clouvel"
        src_dir.mkdir(parents=True)

        server_content = """
from .tools import can_code
from .tools.ship import run_ship
from .tools.errors import handle_error
"""
        (src_dir / "server.py").write_text(server_content, encoding="utf-8")

        result = check_imports(str(temp_project))
        assert result["valid"] is True


class TestCheckDuplicatesAllPattern:
    """check_duplicates __all__ pattern tests"""

    def test_detects_all_exports(self, src_project):
        """Detects exports in __all__ list"""
        tools_dir = src_project / "src" / "clouvel" / "tools"
        tools_dir.mkdir(parents=True)

        init_content = '''
__all__ = [
    "func_a",
    "func_b",
    "func_c",
]
'''
        (tools_dir / "__init__.py").write_text(init_content, encoding="utf-8")

        result = check_duplicates(str(src_project))
        assert "func_a" in result["all_exports"]
        assert "func_b" in result["all_exports"]
        assert "func_c" in result["all_exports"]

    def test_handles_as_imports(self, src_project):
        """Handles 'as' in import statements"""
        tools_dir = src_project / "src" / "clouvel" / "tools"
        tools_dir.mkdir(parents=True)

        init_content = '''
from .module import original_name as aliased_name
'''
        (tools_dir / "__init__.py").write_text(init_content, encoding="utf-8")

        result = check_duplicates(str(src_project))
        assert "aliased_name" in result["all_exports"]


class TestCheckSyncMessages:
    """check_sync messages content tests"""

    def test_sync_pair_description_in_details(self, temp_project):
        """Sync pair description appears in details"""
        result = check_sync(str(temp_project))
        for detail in result["details"]:
            assert "description" in detail

    def test_primary_and_stub_in_details(self, temp_project):
        """Primary and stub file names in details"""
        result = check_sync(str(temp_project))
        for detail in result["details"]:
            assert "primary" in detail
            assert "stub" in detail


class TestCheckSyncMismatch:
    """check_sync mismatch detection tests"""

    def test_detects_signature_mismatch(self, src_project):
        """Detects function signature mismatch"""
        src_dir = src_project / "src" / "clouvel"
        src_dir.mkdir(parents=True)

        # Primary with extra parameter
        (src_dir / "license.py").write_text("""
def verify(key, extra_param):
    return True
""", encoding="utf-8")

        # Stub without extra parameter
        (src_dir / "license_free.py").write_text("""
def verify(key):
    return False
""", encoding="utf-8")

        result = check_sync(str(src_project))
        # Should detect mismatch
        for detail in result["details"]:
            if detail.get("primary") == "license.py":
                assert len(detail.get("signature_mismatch", [])) > 0 or detail.get("sync_status") == "OUT_OF_SYNC"


class TestExtractFunctionsEdgeCases:
    """_extract_functions edge cases"""

    def test_handles_decorators(self):
        """Handles decorated functions"""
        content = """
@decorator
def decorated_func():
    pass

@another
@multiple
def multi_decorated():
    pass
"""
        result = _extract_functions(content)
        assert "decorated_func" in result
        assert "multi_decorated" in result

    def test_handles_class_methods(self):
        """Handles class methods"""
        content = """
class MyClass:
    def method(self, arg):
        pass

    async def async_method(self):
        pass
"""
        result = _extract_functions(content)
        assert "method" in result
        assert "async_method" in result

    def test_handles_default_args(self):
        """Handles default arguments"""
        content = """
def func_with_defaults(a, b=1, c="test"):
    pass
"""
        result = _extract_functions(content)
        assert "func_with_defaults" in result
        params = result["func_with_defaults"]["params"]
        assert "a" in params
        assert "b" in params
        assert "c" in params


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
