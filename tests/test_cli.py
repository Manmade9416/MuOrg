"""Tests for CLI argument parsing and main function."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO
import sys
from muorg.cli import create_parser, main


class TestCreateParser:
    def test_default_parser(self):
        parser = create_parser()
        args = parser.parse_args(["/path/to/music"])
        assert args.path == Path("/path/to/music")
        assert args.dry_run is False
        assert args.verbose is False
        assert args.force is False

    def test_dry_run_flag(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--dry-run"])
        assert args.dry_run is True

    def test_verbose_flag_short(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "-v"])
        assert args.verbose is True

    def test_verbose_flag_long(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--verbose"])
        assert args.verbose is True

    def test_force_flag_short(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "-f"])
        assert args.force is True

    def test_force_flag_long(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--force"])
        assert args.force is True

    def test_cleanup_flag(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--cleanup"])
        assert args.cleanup is True

    def test_clean_extras_flag(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--clean-extras"])
        assert args.clean_extras is True

    def test_hash_algo_default(self):
        parser = create_parser()
        args = parser.parse_args(["/path"])
        assert args.hash_algo == "sha256"

    def test_hash_algo_md5(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--hash-algo", "md5"])
        assert args.hash_algo == "md5"

    def test_hash_algo_sha1(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--hash-algo", "sha1"])
        assert args.hash_algo == "sha1"

    def test_hash_algo_sha256(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--hash-algo", "sha256"])
        assert args.hash_algo == "sha256"

    def test_min_size_default(self):
        parser = create_parser()
        args = parser.parse_args(["/path"])
        assert args.min_size == 1024

    def test_min_size_custom(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--min-size", "512"])
        assert args.min_size == 512

    def test_dry_run_clean_flag(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--dry-run-clean"])
        assert args.dry_run_clean is True

    def test_yes_flag_short(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "-y"])
        assert args.yes is True

    def test_yes_flag_long(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "--yes"])
        assert args.yes is True

    def test_multiple_flags(self):
        parser = create_parser()
        args = parser.parse_args(["/path", "-v", "-f", "--cleanup"])
        assert args.verbose is True
        assert args.force is True
        assert args.cleanup is True


class TestMain:
    @patch("muorg.cli.MusicOrganizer")
    def test_main_organizes_path(self, mock_organizer, temp_dir, capsys):
        mock_instance = MagicMock()
        mock_organizer.return_value = mock_instance

        result = main()

        mock_organizer.assert_called_once()
        mock_instance.organize.assert_called_once()
        assert result == 0

    @patch("muorg.cli.MusicOrganizer")
    def test_main_passes_dry_run(self, mock_organizer, temp_dir):
        mock_instance = MagicMock()
        mock_organizer.return_value = mock_instance

        with patch.object(sys, "argv", ["muorg", str(temp_dir), "--dry-run"]):
            result = main()

        call_kwargs = mock_organizer.call_args[1]
        assert call_kwargs["dry_run"] is True

    @patch("muorg.cli.MusicOrganizer")
    def test_main_passes_verbose(self, mock_organizer, temp_dir):
        mock_instance = MagicMock()
        mock_organizer.return_value = mock_instance

        with patch.object(sys, "argv", ["muorg", str(temp_dir), "-v"]):
            result = main()

        call_kwargs = mock_organizer.call_args[1]
        assert call_kwargs["verbose"] is True

    @patch("muorg.cli.MusicOrganizer")
    def test_main_passes_cleanup(self, mock_organizer, temp_dir):
        mock_instance = MagicMock()
        mock_organizer.return_value = mock_instance

        with patch.object(sys, "argv", ["muorg", str(temp_dir), "--cleanup"]):
            result = main()

        call_kwargs = mock_organizer.call_args[1]
        assert call_kwargs["cleanup"] is True

    def test_main_returns_error_for_nonexistent_path(self, temp_dir):
        nonexistent = temp_dir / "does_not_exist"
        
        with patch.object(sys, "argv", ["muorg", str(nonexistent)]):
            result = main()

        assert result == 1

    def test_main_returns_error_for_non_directory(self, temp_dir):
        non_dir = temp_dir / "file.txt"
        non_dir.write_text("content")
        
        with patch.object(sys, "argv", ["muorg", str(non_dir)]):
            result = main()

        assert result == 1

    @patch("muorg.cli.MusicOrganizer")
    def test_dry_run_clean_enables_dry_run(self, mock_organizer, temp_dir):
        mock_instance = MagicMock()
        mock_organizer.return_value = mock_instance

        with patch.object(sys, "argv", ["muorg", str(temp_dir), "--cleanup", "--dry-run-clean"]):
            result = main()

        call_kwargs = mock_organizer.call_args[1]
        assert call_kwargs["dry_run"] is True


class TestVersion:
    @patch("muorg.cli.MusicOrganizer")
    def test_version_in_help(self, mock_organizer):
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--version"])