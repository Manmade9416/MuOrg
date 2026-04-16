# AGENTS.md - Development Guide

## Testing

```bash
# Test installation
pip install -e .

# Test CLI
muorg --help
muorg --version

# Run dry-run test
muorg /path/to/music --dry-run -v

# Test organization (first run)
muorg /path/to/music -v

# Test skip already organized (second run)
muorg /path/to/music -v

# Test force flag
muorg /path/to/music --force -v

# Test cleanup
muorg /path/to/music --cleanup --yes
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

# Clean old versions
rm dist/muorg-0.*
```

## Version Bumping

When releasing a new version:
1. Update `muorg/__init__.py` - `__version__`
2. Update `pyproject.toml` - `version`
3. Build: `python3 -m build`
4. Install: `pip install dist/*.whl --force-reinstall`
5. Test the new version
6. Commit with message describing changes