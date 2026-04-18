"""Pytest configuration and shared fixtures."""
import pytest
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    tmp = tempfile.mkdtemp()
    yield Path(tmp)
    shutil.rmtree(tmp, ignore_errors=True)


@pytest.fixture
def audio_file(temp_dir):
    """Create a dummy audio file."""
    file_path = temp_dir / "test_song.mp3"
    file_path.write_bytes(b"dummy audio content")
    return file_path


@pytest.fixture
def audio_files(temp_dir):
    """Create multiple dummy audio files."""
    files = []
    for name in ["song1.mp3", "song2.flac", "song3.m4a"]:
        f = temp_dir / name
        f.write_bytes(b"dummy audio")
        files.append(f)
    return files


@pytest.fixture
def nested_music_dir(temp_dir):
    """Create a directory structure with audio files in subdirs."""
    subdir = temp_dir / "subdir"
    subdir.mkdir()
    
    (temp_dir / "root_song.mp3").write_bytes(b"audio")
    (subdir / "sub_song.flac").write_bytes(b"audio")
    (temp_dir / "image.jpg").write_bytes(b"image")
    
    return temp_dir