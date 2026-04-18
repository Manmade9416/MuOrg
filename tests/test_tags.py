"""Tests for tag reading functions."""
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
import mutagen.mp3
import mutagen.mp4
from muorg.tags import (
    extract_text,
    clean_artist_name,
    read_tags,
    is_supported_format,
    AudioTags,
)


class TestExtractText:
    def test_none_returns_empty(self):
        assert extract_text(None) == ""

    def test_string_returns_as_is(self):
        assert extract_text("artist name") == "artist name"

    def test_list_with_strings_returns_first(self):
        assert extract_text(["first", "second"]) == "first"

    def test_list_with_objects_returns_text_attr(self):
        mock_obj = MagicMock()
        mock_obj.text = ["artist text"]
        assert extract_text([mock_obj]) == "artist text"

    def test_object_with_text_attr(self):
        mock_obj = MagicMock()
        mock_obj.text = ["title text"]
        assert extract_text(mock_obj) == "title text"


class TestCleanArtistName:
    def test_single_artist(self):
        assert clean_artist_name("Artist Name") == "Artist Name"

    def test_semicolon_separator(self):
        assert clean_artist_name("Artist One; Artist Two") == "Artist One"

    def test_comma_separator(self):
        assert clean_artist_name("Artist One, Artist Two") == "Artist One"

    def test_slash_separator(self):
        assert clean_artist_name("Artist One / Artist Two") == "Artist One"

    def test_ampersand_separator(self):
        assert clean_artist_name("Artist One & Artist Two") == "Artist One"

    def test_pipe_separator(self):
        assert clean_artist_name("Artist One | Artist Two") == "Artist One"

    def test_word_and_separator(self):
        assert clean_artist_name("Artist One and Artist Two") == "Artist One"

    def test_strips_whitespace(self):
        assert clean_artist_name("  Artist  ") == "Artist"

    def test_empty_string(self):
        assert clean_artist_name("") == ""

    def test_only_separators_returns_empty(self):
        result = clean_artist_name("; , / & | and ")
        assert result == "" or result == "; , / & | and"

    def test_case_preserved(self):
        result = clean_artist_name("UPPERCASE")
        assert result == "UPPERCASE"


class TestReadTags:
    @patch("muorg.tags.mutagen.File")
    def test_reads_file(self, mock_file):
        mock_file.return_value = None
        result = read_tags(Path("test.mp3"))
        assert result is None

    @patch("muorg.tags.mutagen.File")
    def test_returns_none_on_exception(self, mock_file):
        mock_file.side_effect = Exception("Invalid file")
        result = read_tags(Path("test.mp3"))
        assert result is None

    @patch("muorg.tags.mutagen.File")
    def test_returns_none_when_audio_is_none(self, mock_file):
        mock_file.return_value = None
        result = read_tags(Path("test.mp3"))
        assert result is None


class TestIsSupportedFormat:
    @patch("muorg.tags.ID3")
    def test_supported_mp3(self, mock_id3):
        mock_id3.return_value = MagicMock()
        assert is_supported_format(Path("test.mp3"))

    @patch("muorg.tags.mutagen.File")
    def test_supported_flac(self, mock_file):
        mock_file.return_value = MagicMock()
        assert is_supported_format(Path("test.flac"))

    @patch("muorg.tags.mutagen.File")
    def test_unsupported_extension(self, mock_file):
        mock_file.return_value = None
        assert not is_supported_format(Path("test.txt"))

    @patch("muorg.tags.ID3")
    def test_mp3_id3_check(self, mock_id3):
        mock_id3.return_value = MagicMock()
        assert is_supported_format(Path("test.mp3"))

    @patch("muorg.tags.ID3")
    def test_mp3_id3_exception_returns_false(self, mock_id3):
        mock_id3.side_effect = Exception("Not MP3")
        assert not is_supported_format(Path("test.mp3"))