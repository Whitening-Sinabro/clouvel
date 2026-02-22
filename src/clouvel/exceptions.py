# -*- coding: utf-8 -*-
"""Clouvel Exception Hierarchy

Custom exceptions for specific error handling instead of broad except blocks.
"""


class ClouvelError(Exception):
    """Base exception for all Clouvel errors."""
    pass


class LicenseError(ClouvelError):
    """License validation, cache, or activation errors."""
    pass


class ToolError(ClouvelError):
    """Error during tool execution."""
    pass


class ProjectError(ClouvelError):
    """Project registration, tracking, or path errors."""
    pass


class ConfigError(ClouvelError):
    """Configuration file read/write errors."""
    pass


class DatabaseError(ClouvelError):
    """SQLite or knowledge base errors."""
    pass
