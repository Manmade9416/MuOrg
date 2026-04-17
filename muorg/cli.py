"""Command-line interface for MuOrg."""
import argparse
import sys
from pathlib import Path
from .organizer import MusicOrganizer
from . import __version__


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser."""
    parser = argparse.ArgumentParser(
        prog="muorg",
        description="Organize music library by artist and album tags",
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Path to music library",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Force re-organization even if files are already organized",
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Run smart cleanup: remove duplicates, ghost files, empty dirs, and optionally non-audio files",
    )
    parser.add_argument(
        "--clean-extras",
        action="store_true",
        help="Include image and playlist files in cleanup (use with --cleanup)",
    )
    parser.add_argument(
        "--hash-algo",
        choices=["md5", "sha1", "sha256"],
        default="sha256",
        help="Hash algorithm for duplicate detection (default: sha256)",
    )
    parser.add_argument(
        "--min-size",
        type=int,
        default=1024,
        help="Minimum file size in bytes to keep; smaller files are considered garbage (default: 1024)",
    )
    parser.add_argument(
        "--dry-run-clean",
        action="store_true",
        help="Run cleanup in dry-run mode (use with --cleanup)",
    )
    parser.add_argument(
        "--yes", "-y",
        action="store_true",
        help="Skip confirmation prompts",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"muorg {__version__}",
    )
    return parser


def main() -> int:
    """Main entry point."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.path.exists():
        print(f"Error: Path does not exist: {args.path}", file=sys.stderr)
        return 1

    if not args.path.is_dir():
        print(f"Error: Path is not a directory: {args.path}", file=sys.stderr)
        return 1

    organizer = MusicOrganizer(
        root_path=args.path,
        dry_run=args.dry_run or args.dry_run_clean,
        verbose=args.verbose,
        force=args.force,
        cleanup=args.cleanup,
        yes=args.yes,
        clean_extras=args.clean_extras,
        hash_algo=args.hash_algo,
        min_size=args.min_size,
        dry_run_clean=args.dry_run_clean,
    )
    organizer.organize()

    return 0


if __name__ == "__main__":
    sys.exit(main())