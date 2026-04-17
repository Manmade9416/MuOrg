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

## Supported Audio Formats

Mutagen supports: MP3, FLAC, OGG, M4A, WAV, WMA, AAC, and more.

Key implementation details in `tags.py`:
- **Tag reading**: Uses `mutagen.File` factory for all formats (single call, no redundant ID3 parsing)
- **MP3**: Uses `mutagen.mp3.MP3` for isinstance check, ID3 tags with frame map (TPE1, TPE2, TALB, TIT2)
- **M4A/MP4**: Uses MP4-specific atoms (©ART, aART, ©alb, ©nam)
- **Other formats**: Uses generic mutagen tags

Artist names are normalized to lowercase for consistent folder grouping.
- **Artist cleaning**: Handles multiple delimiters (`;`, `,`, `/`, `&`, `|`, ` and `) - takes first artist from multi-artist tags

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
pip install dist/muorg-*.whl --force-reinstall

# Clean old versions
rm dist/muorg-0.*
```

## Version Bumping

When releasing a new version:
1. Update `muorg/__init__.py` - `__version__`
2. Update `pyproject.toml` - `version`
3. Build: `python3 -m build`
4. Install: `pip install dist/muorg-*.whl --force-reinstall`
5. Test the new version
6. Commit with message describing changes