"""Tests for the music organizer."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from muorg.organizer import MusicOrganizer, OrganizationResult


class TestMusicOrganizer:
    def test_initialization(self, temp_dir):
        org = MusicOrganizer(temp_dir)
        assert org.root_path == temp_dir
        assert org.dry_run is False
        assert org.verbose is False
        assert org.force is False

    def test_initialization_with_options(self, temp_dir):
        org = MusicOrganizer(temp_dir, dry_run=True, verbose=True, force=True)
        assert org.dry_run is True
        assert org.verbose is True
        assert org.force is True

    def test_organize_no_files(self, temp_dir, capsys):
        org = MusicOrganizer(temp_dir)
        result = org.organize()
        assert result.moved_count == 0
        captured = capsys.readouterr()
        assert "No audio files found" in captured.out

    @patch("muorg.organizer.find_audio_files")
    @patch("muorg.organizer.read_tags")
    def test_organize_single_file(self, mock_read_tags, mock_find, temp_dir):
        audio_file = temp_dir / "song.mp3"
        audio_file.write_bytes(b"audio")
        mock_find.return_value = [audio_file]
        
        mock_tags = MagicMock()
        mock_tags.artist = "test artist"
        mock_tags.album = "test album"
        mock_tags.title = "test song"
        mock_read_tags.return_value = mock_tags

        org = MusicOrganizer(temp_dir)
        result = org.organize()
        
        assert result.moved_count == 1

    @patch("muorg.organizer.find_audio_files")
    @patch("muorg.organizer.read_tags")
    def test_organize_dry_run(self, mock_read_tags, mock_find, temp_dir):
        audio_file = temp_dir / "song.mp3"
        audio_file.write_bytes(b"audio")
        mock_find.return_value = [audio_file]
        
        mock_tags = MagicMock()
        mock_tags.artist = "test artist"
        mock_tags.album = "test album"
        mock_tags.title = "test song"
        mock_read_tags.return_value = mock_tags

        org = MusicOrganizer(temp_dir, dry_run=True)
        result = org.organize()
        
        assert result.moved_count == 1
        assert not (temp_dir / "test artist" / "test album").exists()

    @patch("muorg.organizer.find_audio_files")
    @patch("muorg.organizer.read_tags")
    def test_skips_unreadable_files(self, mock_read_tags, mock_find, temp_dir):
        audio_file = temp_dir / "song.mp3"
        audio_file.write_bytes(b"audio")
        mock_find.return_value = [audio_file]
        mock_read_tags.return_value = None

        org = MusicOrganizer(temp_dir)
        result = org.organize()
        
        assert result.skipped_count == 1

    @patch("muorg.organizer.find_audio_files")
    @patch("muorg.organizer.read_tags")
    @patch("muorg.organizer.is_already_organized")
    def test_skips_already_organized(self, mock_organized, mock_read_tags, mock_find, temp_dir):
        audio_file = temp_dir / "song.mp3"
        audio_file.write_bytes(b"audio")
        mock_find.return_value = [audio_file]
        mock_organized.return_value = True

        org = MusicOrganizer(temp_dir)
        result = org.organize()
        
        assert result.already_organized_count == 1

    @patch("muorg.organizer.find_audio_files")
    @patch("muorg.organizer.read_tags")
    def test_force_flag_processes_organized_files(self, mock_read_tags, mock_find, temp_dir):
        audio_file = temp_dir / "song.mp3"
        audio_file.write_bytes(b"audio")
        mock_find.return_value = [audio_file]
        
        mock_tags = MagicMock()
        mock_tags.artist = "test artist"
        mock_tags.album = "test album"
        mock_tags.title = "test song"
        mock_read_tags.return_value = mock_tags

        org = MusicOrganizer(temp_dir, force=True)
        result = org.organize()
        
        assert result.moved_count == 1

    @patch("muorg.organizer.find_audio_files")
    @patch("muorg.organizer.read_tags")
    def test_cleanup_empty_dirs(self, mock_read_tags, mock_find, temp_dir):
        audio_file = temp_dir / "song.mp3"
        audio_file.write_bytes(b"audio")
        
        subdir = temp_dir / "empty_subdir"
        subdir.mkdir()
        
        mock_find.return_value = [audio_file]
        
        mock_tags = MagicMock()
        mock_tags.artist = "test artist"
        mock_tags.album = "test album"
        mock_tags.title = "test song"
        mock_read_tags.return_value = mock_tags

        org = MusicOrganizer(temp_dir)
        result = org.organize()
        
        assert not subdir.exists()


class TestOrganizationResult:
    def test_default_values(self):
        result = OrganizationResult()
        assert result.moved_count == 0
        assert result.skipped_count == 0
        assert result.already_organized_count == 0
        assert result.error_count == 0
        assert result.errors == []


class TestSmartCleanup:
    @patch("muorg.organizer.compute_hash")
    def test_cleanup_no_files_to_delete(self, mock_hash, temp_dir, capsys):
        (temp_dir / "song.mp3").write_bytes(b"x" * 2000)
        mock_hash.return_value = "abc123"

        org = MusicOrganizer(temp_dir, cleanup=True, yes=True)
        result = org.organize()
        
        captured = capsys.readouterr()
        assert "No files to clean up" in captured.out

    @patch("muorg.organizer.compute_hash")
    def test_cleanup_finds_duplicates(self, mock_hash, temp_dir, capsys):
        (temp_dir / "song1.mp3").write_bytes(b"same content")
        (temp_dir / "song2.mp3").write_bytes(b"same content")
        mock_hash.return_value = "abc123"

        org = MusicOrganizer(temp_dir, cleanup=True, yes=True)
        result = org.organize()
        
        captured = capsys.readouterr()
        assert "Duplicate files" in captured.out

    @patch("muorg.organizer.compute_hash")
    def test_cleanup_finds_ghost_files(self, mock_hash, temp_dir, capsys):
        (temp_dir / "tiny.mp3").write_bytes(b"ab")
        
        org = MusicOrganizer(temp_dir, cleanup=True, yes=True, min_size=100)
        result = org.organize()
        
        captured = capsys.readouterr()
        assert "Ghost/tiny files" in captured.out

    @patch("muorg.organizer.compute_hash")
    def test_cleanup_finds_collision_duplicates(self, mock_hash, temp_dir, capsys):
        (temp_dir / "song.mp3").write_bytes(b"content")
        (temp_dir / "song-1.mp3").write_bytes(b"content")
        
        org = MusicOrganizer(temp_dir, cleanup=True, yes=True)
        result = org.organize()
        
        captured = capsys.readouterr()
        assert "Collision duplicates" in captured.out