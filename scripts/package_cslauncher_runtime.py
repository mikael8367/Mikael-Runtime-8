#!/usr/bin/env python3
"""Package a verified Java 8 ARM64 JRE in the CS Launcher Plus MultiRT format."""
from __future__ import annotations

import argparse
import re
import sys
import tarfile
from pathlib import Path

JAVA_VERSION_RE = re.compile(r'^JAVA_VERSION="([^"]+)"$', re.MULTILINE)
OS_ARCH_RE = re.compile(r'^OS_ARCH="([^"]+)"$', re.MULTILINE)


def validate_jre(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"JRE directory does not exist: {root}"]

    release = root / "release"
    java = root / "bin" / "java"
    lib = root / "lib"
    if not release.is_file():
        errors.append("Missing release file at JRE root.")
        release_text = ""
    else:
        release_text = release.read_text(encoding="utf-8", errors="replace")

    version_match = JAVA_VERSION_RE.search(release_text)
    arch_match = OS_ARCH_RE.search(release_text)
    if not version_match:
        errors.append('release must contain JAVA_VERSION="..."')
    else:
        version = version_match.group(1)
        if not (version.startswith("1.8.") or version.startswith("8.")):
            errors.append(f"Expected Java 8 in release, found {version!r}.")
    if not arch_match:
        errors.append('release must contain OS_ARCH="..."')
    elif arch_match.group(1).lower() not in {"aarch64", "arm64"}:
        errors.append(f"Expected ARM64 OS_ARCH, found {arch_match.group(1)!r}.")

    if not java.is_file():
        errors.append("Missing bin/java executable.")
    elif not java.stat().st_mode & 0o111:
        errors.append("bin/java is not marked executable.")
    if not lib.is_dir():
        errors.append("Missing lib directory.")
    elif not any(p.is_file() for p in lib.rglob("*.so")):
        errors.append("No native .so libraries found under lib/.")

    return errors


def package_jre(root: Path, output: Path) -> None:
    root = root.resolve()
    output = output.resolve()
    errors = validate_jre(root)
    if errors:
        raise ValueError("\n".join(errors))
    if output == root or root in output.parents:
        raise ValueError("Output archive must be outside the JRE source directory.")
    output.parent.mkdir(parents=True, exist_ok=True)
    with tarfile.open(output, "w:xz", format=tarfile.PAX_FORMAT) as archive:
        for path in sorted(root.rglob("*")):
            if path.is_symlink():
                target = (path.parent / path.readlink()).resolve()
                if target != root and root not in target.parents:
                    raise ValueError(f"Symlink escapes JRE directory: {path.relative_to(root)}")
            archive.add(path, arcname=path.relative_to(root).as_posix(), recursive=False)


def validate_archive(archive_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with tarfile.open(archive_path, "r:xz") as archive:
            names = set(archive.getnames())
            if "release" not in names:
                errors.append("Archive must have release at its root (not inside an extra folder).")
            if "bin/java" not in names:
                errors.append("Archive must have bin/java at its root.")
            if not any(name.startswith("lib/") and name.endswith(".so") for name in names):
                errors.append("Archive must contain native libraries under lib/.")
            member = archive.extractfile("release") if "release" in names else None
            text = member.read().decode("utf-8", "replace") if member else ""
            version_match = JAVA_VERSION_RE.search(text)
            arch_match = OS_ARCH_RE.search(text)
            if not version_match or not (version_match.group(1).startswith("1.8.") or version_match.group(1).startswith("8.")):
                errors.append("Archive release metadata does not identify Java 8.")
            if not arch_match or arch_match.group(1).lower() not in {"aarch64", "arm64"}:
                errors.append("Archive release metadata does not identify ARM64.")
    except (OSError, tarfile.TarError, lzma_error()) as exc:
        errors.append(f"Cannot read .tar.xz archive: {exc}")
    return errors


def lzma_error():
    # Resolve the optional decompressor exception lazily for older Python builds.
    import lzma
    return lzma.LZMAError


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("jre_directory", type=Path, help="Root of the compiled Java 8 ARM64 JRE")
    parser.add_argument("output_archive", type=Path, help="Destination .tar.xz archive")
    args = parser.parse_args()
    try:
        package_jre(args.jre_directory, args.output_archive)
    except (OSError, ValueError, tarfile.TarError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    errors = validate_archive(args.output_archive)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        args.output_archive.unlink(missing_ok=True)
        return 1
    print(f"CS Launcher Plus-compatible runtime archive created: {args.output_archive}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
