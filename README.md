# MuOrg

Music library organizer - organize your music collection by artist and album tags.

## Installation

```bash
pip install muorg
```

## Usage

```bash
muorg path/to/music/library/
```

### Options

| Flag | Description |
|------|-------------|
| `--dry-run` | Show what would be done without making changes |
| `-v, --verbose` | Enable verbose output |
| `-f, --force` | Force re-organization even if files are already organized |
| `--cleanup` | Remove collision duplicate files (*-1.ext, *-2.ext, etc.) |
| `-y, --yes` | Skip confirmation prompts (use with --cleanup) |
| `--version` | Show version number |
| `-h, --help` | Show help message |

## How It Works

MuOrg scans your music library for audio files (MP3, FLAC, OGG, M4A, WAV) and organizes them into a hierarchy:

```
Artist/
├── AlbumName/
│   ├── track1.mp3
│   └── track2.mp3
└── AnotherAlbum/
    └── track1.mp3
```

- **Artist** is taken from the `artist` or `albumartist` tag
- **Album** is taken from the `album` tag. If no album exists, the track title is used
- Files are moved to the new location and backed up to `.muorg_backup/`

## Safe & Idempotent

Running MuOrg on an already-organized library does nothing by default - it detects organized files and skips them safely.

## Examples

```bash
# Dry run to see what would happen
muorg ~/Music --dry-run

# Actually organize (skips already organized files)
muorg ~/Music -v

# Force re-organization (processes all files fresh)
muorg ~/Music --force -v

# Clean up collision duplicates from previous runs
muorg ~/Music --cleanup --yes
```

## License

MIT