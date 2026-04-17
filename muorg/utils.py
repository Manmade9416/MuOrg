"""Utility functions for file operations."""
from pathlib import Path
import shutil
import sys
import hashlib

AUDIO_EXTENSIONS = {".mp3", ".flac", ".ogg", ".m4a", ".wav", ".wma", ".aac"}
AUX_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif"}
AUX_PLAYLIST_EXTENSIONS = {".m3u", ".m3u8", ".pls", ".cue"}
BACKUP_DIR_NAME = ".muorg_backup"


def find_audio_files(root_path: Path) -> list[Path]:
    """Recursively find all audio files in directory."""
    audio_files = []
    backup_dir = root_path / BACKUP_DIR_NAME
    for path in root_path.rglob("*"):
        if path.is_file() and path.suffix.lower() in AUDIO_EXTENSIONS:
            if path.is_relative_to(backup_dir):
                continue
            audio_files.append(path)
    return sorted(audio_files)


def create_backup(source: Path, backup_root: Path) -> Path:
    """Create backup copy of file, return backup path."""
    rel_path = source.name
    backup_path = backup_root / rel_path
    backup_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, backup_path)
    return backup_path


def sanitize_filename(name: str) -> str:
    """Sanitize folder/file name for filesystem compatibility."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    name = name.strip(". ")
    if not name:
        name = "Unknown"
    return name[:200]


def resolve_collision(target: Path) -> Path:
    """Resolve filename collision by appending -1, -2, etc."""
    if not target.exists():
        return target
    stem = target.stem
    suffix = target.suffix
    parent = target.parent
    counter = 1
    while target.exists():
        target = parent / f"{stem}-{counter}{suffix}"
        counter += 1
    return target


def ensure_directory(path: Path) -> None:
    """Ensure directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def confirm(prompt: str) -> bool:
    """Ask user for confirmation."""
    try:
        response = input(f"{prompt} [y/N]: ").strip().lower()
        return response in ("y", "yes")
    except (KeyboardInterrupt, EOFError):
        print()
        return False


def print_verbose(message: str, verbose: bool) -> None:
    """Print message if verbose mode enabled."""
    if verbose:
        print(message, file=sys.stderr)


def is_already_organized(file_path: Path, artist: str, album: str, root_path: Path) -> bool:
    """Check if file is already in the expected organized location."""
    expected_dir = root_path / sanitize_filename(artist) / sanitize_filename(album)
    return file_path.parent.resolve() == expected_dir.resolve()


def find_collision_duplicates(root_path: Path) -> list[Path]:
    """Find files with -1, -2, etc. suffix (collision duplicates)."""
    backup_dir = root_path / BACKUP_DIR_NAME
    duplicates = []
    for path in root_path.rglob("*"):
        if not path.is_file():
            continue
        if path.is_relative_to(backup_dir):
            continue
        stem = path.stem
        if stem.endswith("-1") or stem.endswith("-2") or stem.endswith("-3") or stem.endswith("-4") or stem.endswith("-5"):
            if path.suffix.lower() in AUDIO_EXTENSIONS:
                duplicates.append(path)
    return sorted(duplicates)


def compute_hash(file_path: Path, algo: str = "sha256") -> str:
    """Compute hash of a file using specified algorithm."""
    if algo == "md5":
        hasher = hashlib.md5()
    elif algo == "sha1":
        hasher = hashlib.sha1()
    else:
        hasher = hashlib.sha256()

    with open(file_path, "rb") as f:
        while chunk := f.read(1024 * 1024):  # 1 MB chunks
            hasher.update(chunk)
    return hasher.hexdigest()


def is_aux_file(path: Path) -> bool:
    """Check if file is an auxiliary file (image or playlist)."""
    suffix = path.suffix.lower()
    return suffix in AUX_IMAGE_EXTENSIONS or suffix in AUX_PLAYLIST_EXTENSIONS


def is_audio_file(path: Path) -> bool:
    """Check if file is a supported audio file."""
    return path.suffix.lower() in AUDIO_EXTENSIONS