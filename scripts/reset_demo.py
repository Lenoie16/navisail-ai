"""Remove generated synthetic/demo artifacts while preserving directory documentation."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--directory",
        type=Path,
        default=Path("data"),
        help="data root containing synthetic/ and demo/",
    )
    args = parser.parse_args()
    removed = 0
    for folder_name in ("synthetic", "demo"):
        folder = args.directory / folder_name
        if not folder.exists():
            continue
        for path in folder.iterdir():
            if path.name == "README.md" or path.name == ".gitkeep":
                continue
            if path.is_file():
                path.unlink()
                removed += 1
    print(f"Removed {removed} generated demo artifact(s).")


if __name__ == "__main__":
    main()
