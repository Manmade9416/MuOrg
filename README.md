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
| `--cleanup` | Run smart cleanup: remove duplicates, ghost files, empty dirs |
| `--clean-extras` | Include image and playlist files in cleanup (use with --cleanup) |
| `--hash-algo` | Hash algorithm for duplicate detection (md5, sha1, sha256) |
| `--min-size` | Minimum file size in bytes to keep (default: 1024) |
| `--dry-run-clean` | Run cleanup in dry-run mode |
| `-y, --yes` | Skip confirmation prompts |
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

# Smart cleanup - remove duplicates and ghost files (shows preview)
muorg ~/Music --cleanup --dry-run-clean

# Smart cleanup with auto-confirm
muorg ~/Music --cleanup --yes

# Cleanup including images and playlists
muorg ~/Music --cleanup --clean-extras --yes

# Cleanup with custom min file size (e.g., 512 bytes)
muorg ~/Music --cleanup --min-size 512 --yes
```

## License

[GNU General Public License v3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.html)