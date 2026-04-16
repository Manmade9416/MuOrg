"""Core organization logic for MuOrg."""
from pathlib import Path
from dataclasses import dataclass, field
import shutil
import os
from .utils import (
    find_audio_files,
    create_backup,
    sanitize_filename,
    resolve_collision,
    ensure_directory,
    is_already_organized,
    BACKUP_DIR_NAME,
)
from .tags import read_tags


@dataclass
class OrganizationResult:
    """Result of organization operation."""
    moved_count: int = 0
    skipped_count: int = 0
    already_organized_count: int = 0
    error_count: int = 0
    errors: list[str] = field(default_factory=list)


class MusicOrganizer:
    """Handles music file organization."""

    def __init__(self, root_path: Path, dry_run: bool = False, verbose: bool = False, force: bool = False):
        self.root_path = root_path.resolve()
        self.dry_run = dry_run
        self.verbose = verbose
        self.force = force
        self.backup_root = self.root_path / BACKUP_DIR_NAME
        self.result = OrganizationResult()

    def organize(self) -> OrganizationResult:
        """Organize all music files in the library."""
        audio_files = find_audio_files(self.root_path)

        if not audio_files:
            print(f"No audio files found in {self.root_path}")
            return self.result

        if self.dry_run:
            print(f"[DRY RUN] Found {len(audio_files)} audio files")

        for audio_file in audio_files:
            self._process_file(audio_file)

        if not self.dry_run:
            self._cleanup_empty_dirs()

        self._print_summary()
        return self.result

    def _process_file(self, file_path: Path) -> None:
        """Process a single audio file."""
        try:
            tags = read_tags(file_path)
            if tags is None:
                self.result.skipped_count += 1
                self._log(f"Skipped (cannot read tags): {file_path.name}")
                return

            artist_folder = sanitize_filename(tags.artist)
            album_folder = sanitize_filename(tags.album)

            if not self.force and is_already_organized(file_path, tags.artist, tags.album, self.root_path):
                self.result.already_organized_count += 1
                self._log(f"Already organized: {file_path.name}")
                return

            target_dir = self.root_path / artist_folder / album_folder
            target_file = target_dir / file_path.name
            target_file = resolve_collision(target_file)

            if self.dry_run:
                self._log(f"Would move: {file_path.name} -> {target_file}")
                self.result.moved_count += 1
                return

            backup_path = create_backup(file_path, self.backup_root)
            self._log(f"Backed up: {file_path.name} -> {backup_path}")

            ensure_directory(target_dir)
            shutil.move(str(file_path), str(target_file))
            self._log(f"Moved: {file_path.name} -> {target_file}")
            self.result.moved_count += 1

        except Exception as e:
            self.result.error_count += 1
            self.result.errors.append(f"{file_path.name}: {str(e)}")
            self._log(f"Error processing {file_path.name}: {e}")

    def _log(self, message: str) -> None:
        """Log message if verbose enabled."""
        if self.verbose:
            print(f"  {message}")

    def _cleanup_empty_dirs(self) -> None:
        """Remove empty directories left behind after moving files."""
        backup_dir = self.root_path / BACKUP_DIR_NAME
        for dirpath, dirnames, filenames in os.walk(self.root_path, topdown=False):
            dir_path = Path(dirpath)
            if dir_path == backup_dir:
                continue
            if dir_path == self.root_path:
                continue
            try:
                if dir_path.exists() and not any(dir_path.iterdir()):
                    dir_path.rmdir()
                    self._log(f"Removed empty dir: {dir_path}")
            except Exception as e:
                pass

    def _print_summary(self) -> None:
        """Print operation summary."""
        mode = "DRY RUN" if self.dry_run else "Organized"
        print(f"\n{mode} Summary:")
        print(f"  Moved: {self.result.moved_count}")
        print(f"  Skipped (no tags): {self.result.skipped_count}")
        if self.result.already_organized_count > 0:
            print(f"  Already organized: {self.result.already_organized_count}")
        print(f"  Errors: {self.result.error_count}")

        if self.result.errors:
            print("\nErrors:")
            for error in self.result.errors:
                print(f"  - {error}")