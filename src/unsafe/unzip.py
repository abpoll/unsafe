"""Utilities for extracting downloaded archive files."""

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from zipfile import BadZipFile, ZipFile
from time import perf_counter
from itertools import groupby

import py7zr


SUPPORTED_EXTS = {
        ".zip",
        ".7z",
    }

@dataclass(frozen=True)
class ArchiveExtraction:
    """Represents a single archive extraction."""

    archive_path: Path
    output_dir: Path
    repository: Path

def format_elapsed(seconds: float) -> str:
    """Return a human-readable elapsed time."""

    if seconds < 60:
        return f"{seconds:.1f} s"

    minutes, seconds = divmod(int(seconds), 60)

    if minutes < 60:
        return f"{minutes:d} min {seconds:02d} s"

    hours, minutes = divmod(minutes, 60)
    return f"{hours:d} hr {minutes:02d} min"

def discover_archives(
    archive_root: Path,
    outdir_root: Path,
    relative_to: Path | None = None,
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

    relative_to
        Preserve the directory structure relative to this parent directory.
        If None, output paths are constructed relative to archive_root.

    Returns
    -------
    list[ArchiveExtraction]
        One extraction plan for each supported archive.
    """

    extractions = []

    for archive_path in archive_root.rglob("*"):

        if (
            not archive_path.is_file()
            or archive_path.name.startswith(".")
            or archive_path.suffix.lower() not in SUPPORTED_EXTS
        ):
            continue

        # Repository relative to either the archive root or a
        # user-specified parent directory
        if relative_to is None:
            repository = archive_path.relative_to(archive_root).parent
        else:
            repository = archive_path.relative_to(relative_to).parent

        extractions.append(
            ArchiveExtraction(
                archive_path=archive_path,
                output_dir=outdir_root / repository,
                repository=repository,
            )
        )

    # Sort in place by repository & archives within
    extractions.sort(
        key=lambda extraction: (
            extraction.repository,
            extraction.archive_path.name,
        )
    )
    return extractions

def unzip_raw(archive_root : Path,
              outdir_root: Path,
              relative_to: Path | None = None):
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

    relative_to
        Preserve the directory structure relative to this parent directory.
        If None, output paths are constructed relative to archive_root.
    """
    overall_start = perf_counter()
    
    extractions = discover_archives(archive_root,
                                    outdir_root,
                                    relative_to=relative_to)

    if not extractions:
        print("No supported archives found.")
        return

    # User friendly print messages
    # Report how many repositories found and how many files
    # to extract within them
    repository_counts = Counter(
        extraction.repository for extraction in extractions
    )

    print("=" * 60)
    print("Archive Extraction")
    print("=" * 60)
    print()

    print(
        f"Found {len(extractions)} archives "
        f"across {len(repository_counts)} repositories.\n"
    )

    width = max(len(str(repository)) for repository in repository_counts)

    for repository, count in sorted(repository_counts.items()):
        label = "archive" if count == 1 else "archives"
        print(f"  {str(repository):<{width}} : {count} {label}")

    print()

    # Loop through each file to extract
    counts = Counter(e.output_dir for e in extractions)
    duplicate_dirs = {d for d, n in counts.items() if n > 1}

    failed = []

    archive_number = 1

    for repository, archives in groupby(
        extractions,
        key=lambda extraction: extraction.repository,
    ):

        archives = list(archives)

        print("-" * 60)
        print(
            f"Repository: {repository} "
            f"({len(archives)} archives)"
        )
        print("-" * 60)

        for extraction in archives:

            archive = extraction.archive_path
            out_dir = extraction.output_dir

            if out_dir in duplicate_dirs:
                out_dir /= archive.stem

            out_dir.mkdir(parents=True, exist_ok=True)

            start = perf_counter()

            try:

                if archive.suffix.lower() == ".zip":

                    with ZipFile(archive) as z:
                        z.extractall(out_dir)

                elif archive.suffix.lower() == ".7z":

                    with py7zr.SevenZipFile(archive) as z:
                        z.extractall(out_dir)

                elapsed = perf_counter() - start

                print(
                    f"[{archive_number:>3}/{len(extractions)}] "
                    f"{archive.name:<40}"
                    f"{format_elapsed(elapsed)}"
                )

            except BadZipFile as e:

                failed.append((archive, str(e)))

            except Exception as e:

                failed.append((archive, str(e)))

            archive_number += 1

        print()

    print("=" * 60)
    print("Finished")
    print("=" * 60)

    print(f"Archives processed : {len(extractions)}")
    print(f"Succeeded          : {len(extractions) - len(failed)}")
    print(f"Failed             : {len(failed)}")
    print(
        f"Elapsed time       : "
        f"{format_elapsed(perf_counter() - overall_start)}"
    )

    if failed:

        print("\nFailed archives:\n")

        for archive, reason in failed:
            print(f"  {archive}")
            print(f"      {reason}")

        print(
            "\nIf the archive uses Deflate64 compression, install "
            "'zipfile-deflate64' and import it before calling unzip_raw()."
        )
