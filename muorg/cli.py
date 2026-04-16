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
        dry_run=args.dry_run,
        verbose=args.verbose,
        force=args.force,
    )
    organizer.organize()

    return 0


if __name__ == "__main__":
    sys.exit(main())