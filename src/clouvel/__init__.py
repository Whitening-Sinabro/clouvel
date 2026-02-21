def main():
    """Lazy-loaded entry point — avoids importing server.py on package import.

    This keeps 'python -m clouvel.gate_check' fast by not loading
    the full MCP server module tree during package init.
    """
    from .server import main as _main
    _main()

__all__ = ["main"]
