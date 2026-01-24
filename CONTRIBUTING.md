# Contributing to Clouvel

Thank you for your interest in contributing to Clouvel! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [How Can I Contribute?](#how-can-i-contribute)
- [Development Setup](#development-setup)
- [Pull Request Process](#pull-request-process)
- [Style Guidelines](#style-guidelines)

## Code of Conduct

This project follows our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:
1. Check the [existing issues](https://github.com/Whitening-Sinabro/clouvel/issues) to avoid duplicates
2. Collect information about the bug:
   - Python version (`python --version`)
   - Clouvel version (`pip show clouvel`)
   - Operating system
   - Steps to reproduce
   - Expected vs actual behavior

Create a new issue using the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md).

### Suggesting Features

We welcome feature suggestions! Before suggesting:
1. Check if it's already been suggested
2. Consider if it fits Clouvel's philosophy: **PRD-first development**

Create a new issue using the [feature request template](.github/ISSUE_TEMPLATE/feature_request.md).

### Contributing Code

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit with a clear message
6. Push to your fork
7. Open a Pull Request

## Development Setup

### Prerequisites

- Python 3.10+
- pip
- Git

### Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/clouvel.git
cd clouvel

# Create virtual environment
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest
```

### Project Structure

```
clouvel/
├── src/clouvel/
│   ├── server.py       # MCP server entry point
│   ├── tools/          # Tool implementations
│   │   ├── core.py     # can_code, scan_docs, etc.
│   │   ├── docs.py     # PRD templates
│   │   ├── planning.py # Planning tools
│   │   └── ...
│   └── templates/      # PRD templates
├── tests/              # Test files
├── docs/               # Documentation
└── README.md
```

## Pull Request Process

1. **Update documentation** if you're changing behavior
2. **Add tests** for new features
3. **Follow the style guide** (see below)
4. **Write a clear PR description** explaining:
   - What changes were made
   - Why they were made
   - How to test them
5. **Link related issues** using `Fixes #123` or `Closes #123`

### PR Title Format

Use conventional commits format:
- `feat: add new template for mobile apps`
- `fix: resolve Windows path encoding issue`
- `docs: update installation guide`
- `refactor: simplify can_code logic`
- `test: add tests for manager tool`

## Style Guidelines

### Python

- Follow [PEP 8](https://pep8.org/)
- Use type hints where possible
- Maximum line length: 100 characters
- Use docstrings for public functions

```python
def can_code(path: str) -> dict:
    """
    Check if coding is allowed based on PRD existence.

    Args:
        path: Project root path

    Returns:
        dict with 'allowed' boolean and 'reason' string
    """
    ...
```

### Commits

- Use present tense ("Add feature" not "Added feature")
- Use imperative mood ("Move cursor to..." not "Moves cursor to...")
- Keep the first line under 50 characters
- Reference issues in the body if applicable

### Documentation

- Use clear, concise language
- Include code examples where helpful
- Keep README focused on getting started
- Put detailed docs in `/docs`

## Questions?

- Open a [Discussion](https://github.com/Whitening-Sinabro/clouvel/discussions)
- Check existing issues and discussions first

---

Thank you for contributing! 🎉
