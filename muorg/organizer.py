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
    find_collision_duplicates,
    compute_hash,
    is_aux_file,
    is_audio_file,
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

    def __init__(self, root_path: Path, dry_run: bool = False, verbose: bool = False, force: bool = False, cleanup: bool = False, yes: bool = False, clean_extras: bool = False, hash_algo: str = "sha256", min_size: int = 1024, dry_run_clean: bool = False):
        self.root_path = root_path.resolve()
        self.dry_run = dry_run
        self.verbose = verbose
        self.force = force
        self.cleanup = cleanup
        self.yes = yes
        self.clean_extras = clean_extras
        self.hash_algo = hash_algo
        self.min_size = min_size
        self.dry_run_clean = dry_run_clean
        self.backup_root = self.root_path / BACKUP_DIR_NAME
        self.result = OrganizationResult()

    def organize(self) -> OrganizationResult:
        """Organize all music files in the library."""
        if self.cleanup:
            return self._smart_cleanup()

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

    def _remove_collision_duplicates(self) -> list[Path]:
        """Find files with -1, -2, etc. suffix (collision duplicates)."""
        return find_collision_duplicates(self.root_path)

    def _smart_cleanup(self) -> OrganizationResult:
        """Run smart cleanup: duplicates, ghost files, empty dirs."""
        backup_dir = self.root_path / BACKUP_DIR_NAME
        hash_to_paths: dict[str, list[Path]] = {}
        all_files: list[Path] = []

        print("Scanning files...")

        for path in self.root_path.rglob("*"):
            if not path.is_file():
                continue
            if path.is_relative_to(backup_dir):
                continue

            all_files.append(path)

            try:
                file_hash = compute_hash(path, self.hash_algo)
                hash_to_paths.setdefault(file_hash, []).append(path)
            except Exception as e:
                self._log(f"Error hashing {path.name}: {e}")

        duplicate_files = set()
        for file_hash, paths in hash_to_paths.items():
            if len(paths) > 1:
                sorted_paths = sorted(paths, key=lambda p: p.stat().st_size, reverse=True)
                for p in sorted_paths[1:]:
                    duplicate_files.add(p)

        print(f"Computing duplicate sets...")

        ghost_files = set()
        for path in all_files:
            if path in duplicate_files:
                continue
            try:
                size = path.stat().st_size
                if size < self.min_size:
                    ghost_files.add(path)
                    continue

                if is_audio_file(path):
                    pass
                elif is_aux_file(path):
                    if self.clean_extras:
                        ghost_files.add(path)
                else:
                    ghost_files.add(path)

            except Exception as e:
                self._log(f"Error checking {path.name}: {e}")

        collision_dups = set(self._remove_collision_duplicates())

        files_to_delete = duplicate_files | ghost_files | collision_dups

        if not files_to_delete:
            print("\nNo files to clean up.")
            return self.result

        total_count = len(files_to_delete)
        total_size = sum(p.stat().st_size for p in files_to_delete if p.exists())

        print("\n" + "=" * 50)
        print("\033[91mCLEANUP SUMMARY\033[0m")
        print("=" * 50)
        print(f"Duplicate files (byte-identical): {len(duplicate_files)}")
        print(f"Ghost/tiny files (< {self.min_size} bytes): {len(ghost_files)}")
        print(f"Collision duplicates (*-1.ext): {len(collision_dups)}")
        print(f"Total files to delete: {total_count}")
        print(f"Total space to free: {total_size:,} bytes ({total_size / 1024 / 1024:.2f} MB)")
        print("=" * 50)

        print("\nFiles to be deleted:")
        for f in sorted(files_to_delete):
            print(f"  - {f.relative_to(self.root_path)}")

        if not self.yes:
            print()
            confirm = input("Delete these files? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Cleanup cancelled.")
                return self.result
        else:
            print("\nDeleting files (--yes flag)...")

        deleted = 0
        for f in files_to_delete:
            try:
                f.unlink()
                if self.verbose:
                    print(f"  Deleted: {f.name}")
                deleted += 1
            except Exception as e:
                print(f"  Error deleting {f.name}: {e}")

        self._cleanup_empty_dirs()

        print(f"\nCleanup Summary:")
        print(f"  Deleted: {deleted}")
        print(f"  Errors: {total_count - deleted}")
        return self.result

    def _cleanup_collisions(self) -> OrganizationResult:

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

    def _cleanup_collisions(self) -> OrganizationResult:
        """Find and optionally remove collision duplicates (*-1.ext)."""
        duplicates = find_collision_duplicates(self.root_path)

        if not duplicates:
            print("No collision duplicates found.")
            return self.result

        print(f"Found {len(duplicates)} collision duplicate(s):")
        for dup in duplicates:
            print(f"  - {dup.name}")

        if not self.yes:
            confirm = input("\nDelete these files? [y/N]: ").strip().lower()
            if confirm not in ("y", "yes"):
                print("Cleanup cancelled.")
                return self.result
        else:
            print("\nDeleting files (--yes flag)...")

        deleted = 0
        for dup in duplicates:
            try:
                dup.unlink()
                if self.verbose:
                    print(f"  Deleted: {dup.name}")
                deleted += 1
            except Exception as e:
                print(f"  Error deleting {dup.name}: {e}")

        self._cleanup_empty_dirs()

        print(f"\nCleanup Summary:")
        print(f"  Deleted: {deleted}")
        print(f"  Errors: {len(duplicates) - deleted}")
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
            target_file_resolved = resolve_collision(target_file)

            if target_file_resolved.resolve() == file_path.resolve():
                self.result.already_organized_count += 1
                self._log(f"Already in place: {file_path.name}")
                return

            target_file = target_file_resolved

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