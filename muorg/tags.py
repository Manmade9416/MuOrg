"""Tag reading using mutagen library."""
from pathlib import Path
from dataclasses import dataclass
import mutagen
from mutagen.id3 import ID3


@dataclass
class AudioTags:
    """Container for audio metadata tags."""
    artist: str
    album: str
    title: str


TAG_TO_FRAME_MAP = {
    "artist": "TPE1",
    "albumartist": "TPE2",
    "album": "TALB",
    "title": "TIT2",
}


def extract_text(value) -> str:
    """Extract text from mutagen tag value."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if hasattr(value, "text"):
        return str(value.text[0]) if value.text else ""
    return ""


def read_tags(file_path: Path) -> AudioTags | None:
    """Read tags from audio file using mutagen."""
    audio = None

    suffix = file_path.suffix.lower()
    if suffix == ".mp3":
        try:
            audio = ID3(file_path)
        except Exception:
            pass

    if audio is None:
        try:
            audio = mutagen.File(file_path)
        except Exception:
            pass

    if audio is None:
        return None

    def get_first(key: str) -> str:
        """Safely get first value from tag."""
        try:
            if isinstance(audio, ID3):
                frame_id = TAG_TO_FRAME_MAP.get(key, key)
                return extract_text(audio.get(frame_id))
            return extract_text(audio.get(key))
        except Exception:
            return ""

    artist = get_first("artist") or get_first("albumartist") or ""
    album = get_first("album") or ""
    title = get_first("title") or file_path.stem

    if not artist:
        artist = "Unknown Artist"
    if not album:
        album = title
    if not title:
        title = file_path.stem

    return AudioTags(artist=artist, album=album, title=title)


def is_supported_format(file_path: Path) -> bool:
    """Check if file format is supported by mutagen."""
    suffix = file_path.suffix.lower()
    if suffix == ".mp3":
        try:
            ID3(file_path)
            return True
        except Exception:
            return False

    try:
        audio = mutagen.File(file_path)
        return audio is not None
    except Exception:
        return False