# -*- coding: utf-8 -*-
"""Error learning tools tests"""

import pytest
import tempfile
import shutil
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from clouvel.tools.errors import (
    _get_error_log_path,
    _classify_error,
    _extract_stack_info,
    ERROR_PATTERNS,
)


@pytest.fixture
def temp_project():
    """Create temporary project directory"""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)


class TestErrorPatterns:
    """ERROR_PATTERNS constant tests"""

    def test_patterns_exist(self):
        """Error patterns dictionary exists"""
        assert len(ERROR_PATTERNS) > 0

    def test_all_patterns_have_required_keys(self):
        """All patterns have required keys"""
        for key, pattern in ERROR_PATTERNS.items():
            assert "patterns" in pattern
            assert "category" in pattern
            assert "prevention" in pattern

    def test_common_error_types_defined(self):
        """Common error types are defined"""
        assert "type_error" in ERROR_PATTERNS
        assert "null_error" in ERROR_PATTERNS
        assert "import_error" in ERROR_PATTERNS
        assert "syntax_error" in ERROR_PATTERNS


class TestGetErrorLogPath:
    """_get_error_log_path function tests"""

    def test_returns_path(self, temp_project):
        """Returns Path object"""
        result = _get_error_log_path(str(temp_project))
        assert isinstance(result, Path)

    def test_path_includes_clouvel(self, temp_project):
        """Path includes .clouvel directory"""
        result = _get_error_log_path(str(temp_project))
        assert ".clouvel" in str(result)
        assert "errors" in str(result)


class TestClassifyError:
    """_classify_error function tests"""

    def test_classify_type_error(self):
        """Classify TypeError"""
        result = _classify_error("TypeError: Cannot read property 'x' of undefined")
        assert result["type"] == "type_error"
        assert result["category"] == "Type Error"

    def test_classify_null_error(self):
        """Classify null reference error"""
        result = _classify_error("Cannot read property 'name' of null")
        assert result["type"] == "null_error"
        assert result["category"] == "Null Reference"

    def test_classify_import_error_python(self):
        """Classify Python import error"""
        result = _classify_error("ImportError: No module named 'some_module'")
        assert result["type"] == "import_error"
        assert result["category"] == "Import Error"

    def test_classify_import_error_js(self):
        """Classify JavaScript import error"""
        result = _classify_error("Error: Cannot find module 'express'")
        assert result["type"] == "import_error"

    def test_classify_syntax_error(self):
        """Classify syntax error"""
        result = _classify_error("SyntaxError: Unexpected token '}'")
        assert result["type"] == "syntax_error"
        assert result["category"] == "Syntax Error"

    def test_classify_network_error(self):
        """Classify network error"""
        result = _classify_error("Error: connect ECONNREFUSED 127.0.0.1:3000")
        assert result["type"] == "network_error"
        assert result["category"] == "Network Error"

    def test_classify_permission_error(self):
        """Classify permission error"""
        result = _classify_error("PermissionError: [Errno 13] Permission denied")
        assert result["type"] == "permission_error"

    def test_classify_database_error(self):
        """Classify database error"""
        result = _classify_error("SQLITE_CONSTRAINT: UNIQUE constraint failed")
        assert result["type"] == "database_error"

    def test_classify_unknown_error(self):
        """Classify unknown error"""
        result = _classify_error("Some random error that doesn't match any pattern")
        assert result["type"] == "unknown"
        assert result["category"] == "Other Error"

    def test_classify_has_prevention(self):
        """All classifications have prevention suggestion"""
        test_errors = [
            "TypeError: x is not a function",
            "Cannot read property of null",
            "ImportError: No module",
            "SyntaxError: Unexpected",
            "Random error message"
        ]
        for error in test_errors:
            result = _classify_error(error)
            assert "prevention" in result
            assert len(result["prevention"]) > 0


class TestExtractStackInfo:
    """_extract_stack_info function tests"""

    def test_extract_python_stack(self):
        """Extract from Python stack trace"""
        stack = '''
Traceback (most recent call last):
  File "/path/to/main.py", line 42, in run_server
    server.start()
  File "/path/to/server.py", line 10, in start
    raise ValueError("Failed")
ValueError: Failed
'''
        result = _extract_stack_info(stack)
        assert result["file"] == "/path/to/main.py"
        assert result["line"] == "42"
        assert result["function"] == "run_server"

    def test_extract_js_stack(self):
        """Extract from JavaScript stack trace"""
        stack = '''
Error: Something went wrong
    at processRequest (/app/src/handler.js:25:10)
    at Server.<anonymous> (/app/src/server.js:15:5)
'''
        result = _extract_stack_info(stack)
        assert result["function"] == "processRequest"
        assert "handler.js" in result["file"]
        assert result["line"] == "25"

    def test_extract_no_stack(self):
        """Extract from error with no stack trace"""
        result = _extract_stack_info("Error: Something failed")
        assert result["file"] is None
        assert result["line"] is None
        assert result["function"] is None

    def test_extract_partial_stack(self):
        """Extract from partial stack information"""
        # When only file info available
        stack = 'at someFunction (/path/file.js:100:5)'
        result = _extract_stack_info(stack)
        assert result["function"] == "someFunction"


class TestErrorClassificationIntegration:
    """Integration tests for error classification"""

    def test_real_world_type_error(self):
        """Real-world TypeError"""
        error = "TypeError: Cannot read properties of undefined (reading 'map')"
        result = _classify_error(error)
        assert result["type"] in ["type_error", "null_error"]

    def test_real_world_module_not_found(self):
        """Real-world ModuleNotFoundError"""
        error = "ModuleNotFoundError: No module named 'requests'"
        result = _classify_error(error)
        assert result["type"] == "import_error"

    def test_real_world_timeout(self):
        """Real-world timeout error"""
        error = "Error: ETIMEDOUT: connection timed out"
        result = _classify_error(error)
        assert result["type"] == "network_error"

    def test_multiple_patterns_first_match(self):
        """First matching pattern wins"""
        # Error that could match multiple patterns
        error = "TypeError: null is not iterable"
        result = _classify_error(error)
        # Should match type_error first (appears first in patterns)
        assert result["type"] in ["type_error", "null_error"]


class TestStackInfoIntegration:
    """Integration tests for stack info extraction"""

    def test_react_stack_trace(self):
        """React error stack trace"""
        stack = '''
TypeError: Cannot read property 'state' of undefined
    at App.render (src/App.js:15:20)
    at finishComponentSetup (node_modules/react-dom/...)
'''
        result = _extract_stack_info(stack)
        # Should extract the first user code location
        assert result["function"] is not None

    def test_fastapi_stack_trace(self):
        """FastAPI error stack trace"""
        stack = '''
Traceback (most recent call last):
  File "/app/main.py", line 10, in get_users
    return db.query(User).all()
AttributeError: 'NoneType' object has no attribute 'query'
'''
        result = _extract_stack_info(stack)
        assert result["file"] == "/app/main.py"
        assert result["function"] == "get_users"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
