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

- `--dry-run` - Show what would be done without making changes
- `-v, --verbose` - Enable verbose output
- `--version` - Show version number
- `-h, --help` - Show help message

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

## Example

```bash
# Dry run to see what would happen
muorg ~/Music --dry-run

# Actually organize
muorg ~/Music -v
```

## License

MIT