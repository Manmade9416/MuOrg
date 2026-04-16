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

MP4_TAG_MAP = {
    "artist": "©ART",
    "albumartist": "aART",
    "album": "©alb",
    "title": "©nam",
}


def extract_text(value) -> str:
    """Extract text from mutagen tag value."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        if value:
            first = value[0]
            if isinstance(first, str):
                return first
            if hasattr(first, "text") and first.text:
                return str(first.text[0])
    if hasattr(value, "text") and value.text:
        return str(value.text[0])
    return ""


def clean_artist_name(artist: str) -> str:
    """Clean artist name - use first artist if multiple separated by ;"""
    if ";" in artist:
        return artist.split(";")[0].strip()
    return artist


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
            from mutagen.mp4 import MP4
            if isinstance(audio, MP4):
                frame_id = MP4_TAG_MAP.get(key, key)
                return extract_text(audio.get(frame_id))
            return extract_text(audio.get(key))
        except Exception:
            return ""

    artist = get_first("artist") or get_first("albumartist") or ""
    album = get_first("album") or ""
    title = get_first("title") or file_path.stem

    artist = clean_artist_name(artist).lower() if artist else ""

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