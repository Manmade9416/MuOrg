"""Tests for utility functions."""
import pytest
from pathlib import Path
import tempfile
import shutil
from muorg.utils import (
    find_audio_files,
    sanitize_filename,
    resolve_collision,
    ensure_directory,
    is_already_organized,
    find_collision_duplicates,
    compute_hash,
    is_aux_file,
    is_audio_file,
    BACKUP_DIR_NAME,
)


class TestSanitizeFilename:
    def test_no_change_needed(self):
        assert sanitize_filename("Artist Name") == "Artist Name"

    def test_replaces_invalid_chars(self):
        assert sanitize_filename("Artist: Name") == "Artist_ Name"
        assert sanitize_filename("Artist <Name>") == "Artist _Name_"
        assert sanitize_filename("Artist/Name") == "Artist_Name"

    def test_trims_whitespace(self):
        assert sanitize_filename("  Artist  ") == "Artist"
        assert sanitize_filename(".Artist.") == "Artist"

    def test_empty_name_becomes_unknown(self):
        assert sanitize_filename("") == "Unknown"
        assert sanitize_filename("   ") == "Unknown"

    def test_truncates_long_names(self):
        long_name = "A" * 300
        result = sanitize_filename(long_name)
        assert len(result) == 200


class TestResolveCollision:
    def test_no_collision_returns_original(self, temp_dir):
        target = temp_dir / "song.mp3"
        result = resolve_collision(target)
        assert result == target

    def test_collision_appends_minus_1(self, temp_dir):
        target = temp_dir / "song.mp3"
        target.write_bytes(b"content")
        result = resolve_collision(target)
        assert result == temp_dir / "song-1.mp3"

    def test_multiple_collisions_increments(self, temp_dir):
        (temp_dir / "song.mp3").write_bytes(b"content")
        (temp_dir / "song-1.mp3").write_bytes(b"content")
        (temp_dir / "song-2.mp3").write_bytes(b"content")
        result = resolve_collision(temp_dir / "song.mp3")
        assert result == temp_dir / "song-3.mp3"


class TestFindAudioFiles:
    def test_finds_audio_files(self, temp_dir):
        (temp_dir / "song1.mp3").write_bytes(b"audio")
        (temp_dir / "song2.flac").write_bytes(b"audio")
        files = find_audio_files(temp_dir)
        assert len(files) == 2

    def test_recursive_search(self, temp_dir):
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        (temp_dir / "song1.mp3").write_bytes(b"audio")
        (subdir / "song2.mp3").write_bytes(b"audio")
        files = find_audio_files(temp_dir)
        assert len(files) == 2

    def test_excludes_backup_dir(self, temp_dir):
        backup_dir = temp_dir / BACKUP_DIR_NAME
        backup_dir.mkdir()
        (temp_dir / "song.mp3").write_bytes(b"audio")
        (backup_dir / "backup.mp3").write_bytes(b"audio")
        files = find_audio_files(temp_dir)
        assert len(files) == 1

    def test_ignores_non_audio_files(self, temp_dir):
        (temp_dir / "song.mp3").write_bytes(b"audio")
        (temp_dir / "image.jpg").write_bytes(b"image")
        (temp_dir / "readme.txt").write_text("text")
        files = find_audio_files(temp_dir)
        assert len(files) == 1


class TestIsAudioFile:
    def test_supported_extensions(self):
        assert is_audio_file(Path("song.mp3"))
        assert is_audio_file(Path("song.flac"))
        assert is_audio_file(Path("song.ogg"))
        assert is_audio_file(Path("song.m4a"))
        assert is_audio_file(Path("song.wav"))
        assert is_audio_file(Path("song.wma"))
        assert is_audio_file(Path("song.aac"))

    def test_unsupported_extensions(self):
        assert not is_audio_file(Path("song.txt"))
        assert not is_audio_file(Path("song.jpg"))
        assert not is_audio_file(Path("song.pdf"))


class TestIsAuxFile:
    def test_image_extensions(self):
        assert is_aux_file(Path("image.jpg"))
        assert is_aux_file(Path("image.jpeg"))
        assert is_aux_file(Path("image.png"))
        assert is_aux_file(Path("image.gif"))

    def test_playlist_extensions(self):
        assert is_aux_file(Path("playlist.m3u"))
        assert is_aux_file(Path("playlist.m3u8"))
        assert is_aux_file(Path("playlist.pls"))
        assert is_aux_file(Path("playlist.cue"))

    def test_non_aux_files(self):
        assert not is_aux_file(Path("song.mp3"))
        assert not is_aux_file(Path("readme.txt"))


class TestEnsureDirectory:
    def test_creates_directory(self, temp_dir):
        target = temp_dir / "new" / "nested" / "dir"
        ensure_directory(target)
        assert target.exists()
        assert target.is_dir()


class TestIsAlreadyOrganized:
    def test_is_organized(self, temp_dir):
        artist_dir = temp_dir / "artist" / "album"
        artist_dir.mkdir(parents=True)
        file_path = artist_dir / "song.mp3"
        file_path.write_bytes(b"audio")
        assert is_already_organized(file_path, "artist", "album", temp_dir)

    def test_not_organized(self, temp_dir):
        file_path = temp_dir / "song.mp3"
        file_path.write_bytes(b"audio")
        assert not is_already_organized(file_path, "artist", "album", temp_dir)

    def test_different_album(self, temp_dir):
        artist_dir = temp_dir / "artist" / "other_album"
        artist_dir.mkdir(parents=True)
        file_path = artist_dir / "song.mp3"
        file_path.write_bytes(b"audio")
        assert not is_already_organized(file_path, "artist", "album", temp_dir)


class TestComputeHash:
    def test_sha256_default(self, temp_dir):
        file = temp_dir / "test.txt"
        file.write_text("hello")
        result = compute_hash(file, "sha256")
        assert len(result) == 64

    def test_md5(self, temp_dir):
        file = temp_dir / "test.txt"
        file.write_text("hello")
        result = compute_hash(file, "md5")
        assert len(result) == 32

    def test_sha1(self, temp_dir):
        file = temp_dir / "test.txt"
        file.write_text("hello")
        result = compute_hash(file, "sha1")
        assert len(result) == 40

    def test_consistent_results(self, temp_dir):
        file = temp_dir / "test.txt"
        file.write_text("hello")
        result1 = compute_hash(file, "sha256")
        result2 = compute_hash(file, "sha256")
        assert result1 == result2


class TestFindCollisionDuplicates:
    def test_finds_collision_files(self, temp_dir):
        (temp_dir / "song.mp3").write_bytes(b"audio")
        (temp_dir / "song-1.mp3").write_bytes(b"audio")
        (temp_dir / "song-2.mp3").write_bytes(b"audio")
        dups = find_collision_duplicates(temp_dir)
        assert len(dups) == 2

    def test_ignores_non_audio_collision(self, temp_dir):
        (temp_dir / "song-1.txt").write_text("text")
        dups = find_collision_duplicates(temp_dir)
        assert len(dups) == 0

    def test_excludes_backup_dir(self, temp_dir):
        backup_dir = temp_dir / BACKUP_DIR_NAME
        backup_dir.mkdir()
        (backup_dir / "song-1.mp3").write_bytes(b"audio")
        dups = find_collision_duplicates(temp_dir)
        assert len(dups) == 0