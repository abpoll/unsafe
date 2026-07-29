"""Utilities for extracting downloaded archive files."""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile

import py7zr

@dataclass(frozen=True)
class ArchiveExtraction:
    """Represents a single archive extraction."""

    archive_path: Path
    output_dir: Path

def discover_archives(
    archive_root: Path,
    outdir_root: Path,
) -> list[ArchiveExtraction]:
    """
    Discover supported archives beneath a directory and determine their
    extraction destinations.

    Parameters
    ----------
    archive_root
        Root directory containing archive files.

    outdir_root
        Root directory where archives will be extracted.

    Returns
    -------
    list[ArchiveExtraction]
        One extraction plan for each supported archive.
    """

    supported_extensions = {".zip", ".7z"}

    extractions = []

    for archive_path in archive_root.rglob("*"):

        if (
            not archive_path.is_file()
            or archive_path.name.startswith(".")
            or archive_path.suffix.lower() not in supported_extensions
        ):
            continue

        relative_parent = archive_path.relative_to(archive_root).parent

        extractions.append(
            ArchiveExtraction(
                archive_path=archive_path,
                output_dir=outdir_root / relative_parent,
            )
        )

    return extractions.sort(key=lambda extraction: extraction.archive_path)

def unzip_raw(archive_root : Path, oudir_root: Path):
    """
    Extract all supported archives beneath an external data directory.

    Archives sharing the same parent directory are extracted into
    separate subdirectories named after the archive stem to avoid
    collisions.

    Parameters
    ----------
    archive_root
        Root directory containing archive files.

    outdir_root
        Root directory where archives will be extracted.
    """

    extractions = discover_archives(external_root, unzipped_root)

    counts = Counter(e.output_dir for e in extractions)
    duplicate_dirs = {d for d, n in counts.items() if n > 1}

    failed = []

    for extraction in extractions:

        archive = extraction.archive_path
        out_dir = extraction.output_dir

        if out_dir in duplicate_dirs:
            out_dir = out_dir / archive.stem

        out_dir.mkdir(parents=True, exist_ok=True)

        try:

            if archive.suffix.lower() == ".zip":

                with ZipFile(archive, "r") as z:
                    z.extractall(out_dir)

            elif archive.suffix.lower() == ".7z":

                with py7zr.SevenZipFile(archive, mode="r") as z:
                    z.extractall(out_dir)

            print(f"Extracted: {archive.name}")

        except BadZipFile as e:
            failed.append((archive, f"Invalid ZIP archive ({e})"))

        except Exception as e:
            failed.append((archive, str(e)))

    if failed:

        print("\nThe following archives could not be extracted:\n")

        for archive, reason in failed:
            print(f"  - {archive.name}")
            print(f"      Reason: {reason}")

        print(
            "\nIf the archive uses Deflate64 compression, install "
            "'zipfile-deflate64' and import it before calling unzip_raw()."
        )
