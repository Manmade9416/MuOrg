# AGENTS.md - Development Guide

## Testing

Run tests:
```bash
# Test installation
pip install -e .

# Test CLI
muorg --help
muorg --version

# Run dry-run test
muorg /path/to/music --dry-run -v
```

## Linting

```bash
# Syntax check
python3 -m py_compile muorg/*.py

# Import check
python3 -c "import muorg; from muorg import organizer, tags, utils, cli"
```

## Building

```bash
# Build package
pip install build
python3 -m build

# Install from wheel
pip install dist/*.whl
```