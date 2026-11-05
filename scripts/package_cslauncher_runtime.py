#!/usr/bin/env python3
"""Validate and package a Java 8 Android ARM64 JRE for CS Launcher Plus MultiRT."""
from __future__ import annotations

import argparse
import lzma
import posixpath
import re
import sys
import tarfile
from pathlib import Path, PurePosixPath

JAVA_VERSION_RE = re.compile(r'^JAVA_VERSION="([^"]+)"$', re.MULTILINE)
OS_ARCH_RE = re.compile(r'^OS_ARCH="([^"]+)"$', re.MULTILINE)
ELF_MACHINE_AARCH64 = 183


def elf_errors(data: bytes, label: str) -> list[str]:
    if len(data) < 20 or data[:4] != b"\x7fELF":
        return [f"{label} is not a valid ELF file."]
    errors: list[str] = []
    if data[4] != 2:
        errors.append(f"{label} is not ELF64 (required for ARM64).")
    if data[5] != 1:
        errors.append(f"{label} is not little-endian ELF.")
    if int.from_bytes(data[18:20], "little") != ELF_MACHINE_AARCH64:
        errors.append(f"{label} is not AArch64 (ELF machine must be 183).")
    return errors


def read_elf_header(path: Path) -> bytes:
    with path.open("rb") as stream:
        return stream.read(64)


def _source_tree_errors(root: Path) -> list[str]:
    errors: list[str] = []
    for path in root.rglob("*"):
        try:
            if path.is_symlink():
                try:
                    resolved = path.resolve(strict=True)
                    resolved.relative_to(root.resolve(strict=True))
                except FileNotFoundError:
                    errors.append(f"Dangling symlink in JRE directory: {path.relative_to(root)}")
                except (OSError, RuntimeError, ValueError):
                    errors.append(f"Symlink escapes or cannot be resolved inside JRE: {path.relative_to(root)}")
            elif not (path.is_file() or path.is_dir()):
                errors.append(f"Unsupported special file in JRE: {path.relative_to(root)}")
        except OSError as exc:
            errors.append(f"Cannot inspect {path.relative_to(root)}: {exc}")
    return errors


def validate_jre(root: Path) -> list[str]:
    errors: list[str] = []
    if not root.is_dir():
        return [f"JRE directory does not exist: {root}"]
    root = root.resolve()
    errors.extend(_source_tree_errors(root))

    release = root / "release"
    java = root / "bin" / "java"
    lib = root / "lib"
    if not release.is_file() or release.is_symlink():
        errors.append("Missing regular release file at JRE root.")
        release_text = ""
    else:
        release_text = release.read_text(encoding="utf-8", errors="replace")

    version_match = JAVA_VERSION_RE.search(release_text)
    arch_match = OS_ARCH_RE.search(release_text)
    if not version_match:
        errors.append('release must contain JAVA_VERSION="..."')
    elif not (version_match.group(1).startswith("1.8.") or version_match.group(1).startswith("8.")):
        errors.append(f"Expected Java 8 in release, found {version_match.group(1)!r}.")
    if not arch_match:
        errors.append('release must contain OS_ARCH="..."')
    elif arch_match.group(1).lower() not in {"aarch64", "arm64"}:
        errors.append(f"Expected ARM64 OS_ARCH, found {arch_match.group(1)!r}.")

    if not java.is_file() or java.is_symlink():
        errors.append("Missing regular bin/java executable.")
    else:
        if not java.stat().st_mode & 0o111:
            errors.append("bin/java is not marked executable.")
        else:
            errors.extend(elf_errors(read_elf_header(java), "bin/java"))

    if not lib.is_dir() or lib.is_symlink():
        errors.append("Missing regular lib directory.")
        native_files = []
    else:
        native_files = [p for p in lib.rglob("*.so") if p.is_file() and not p.is_symlink()]
        if not native_files:
            errors.append("No native .so libraries found under lib/.")

    jvm = next((p for p in native_files if p.name == "libjvm.so"), None)
    if jvm is None:
        errors.append("Missing HotSpot VM library libjvm.so under lib/.")

    for native in native_files:
        errors.extend(elf_errors(read_elf_header(native), str(native.relative_to(root))))
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


def _archive_member_errors(member_list: list[tarfile.TarInfo]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for member in member_list:
        name = member.name
        path = PurePosixPath(name)
        if name in seen:
            errors.append(f"Duplicate archive path: {name}")
        seen.add(name)
        canonical_name = name.rstrip("/") if member.isdir() else name
        if (not name or path.is_absolute() or ".." in path.parts or "." in path.parts
                or "\\" in name or posixpath.normpath(canonical_name) != canonical_name):
            errors.append(f"Unsafe archive path: {name}")
        if not (member.isfile() or member.isdir() or member.issym()):
            errors.append(f"Unsupported archive entry type: {name}")
        if member.issym():
            target = member.linkname
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target))
            if not target or target.startswith("/") or resolved == ".." or resolved.startswith("../"):
                errors.append(f"Symlink escapes archive root: {name} -> {target}")
    return errors


def validate_archive(archive_path: Path) -> list[str]:
    errors: list[str] = []
    try:
        with tarfile.open(archive_path, "r:xz") as archive:
            member_list = archive.getmembers()
            errors.extend(_archive_member_errors(member_list))
            members = {m.name: m for m in member_list}
            for name in members:
                path = PurePosixPath(name)
                if path.is_absolute() or ".." in path.parts:
                    errors.append(f"Unsafe archive path: {name}")
            if "release" not in members or not members["release"].isfile():
                errors.append("Archive must have a regular release file at its root.")
            if "bin/java" not in members or not members["bin/java"].isfile():
                errors.append("Archive must have a regular bin/java file at its root.")
            if not any(name.startswith("lib/") and name.endswith(".so") for name in members):
                errors.append("Archive must contain native libraries under lib/.")
            if not any(PurePosixPath(name).name == "libjvm.so" and name.startswith("lib/") and m.isfile()
                       for name, m in members.items()):
                errors.append("Archive is missing HotSpot libjvm.so under lib/.")

            release_member = members.get("release")
            release_stream = archive.extractfile(release_member) if release_member and release_member.isfile() else None
            release_text = release_stream.read().decode("utf-8", "replace") if release_stream else ""
            version_match = JAVA_VERSION_RE.search(release_text)
            arch_match = OS_ARCH_RE.search(release_text)
            if not version_match or not (version_match.group(1).startswith("1.8.") or version_match.group(1).startswith("8.")):
                errors.append("Archive release metadata does not identify Java 8.")
            if not arch_match or arch_match.group(1).lower() not in {"aarch64", "arm64"}:
                errors.append("Archive release metadata does not identify ARM64.")

            java_member = members.get("bin/java")
            if java_member and not (java_member.mode & 0o111):
                errors.append("Archive bin/java is not executable.")
            for name, member in members.items():
                if name.startswith("lib/") and name.endswith(".so") and member.isfile():
                    stream = archive.extractfile(member)
                    errors.extend(elf_errors(stream.read(64) if stream else b"", name))
            if java_member and java_member.isfile():
                stream = archive.extractfile(java_member)
                errors.extend(elf_errors(stream.read(64) if stream else b"", "bin/java"))
    except (OSError, tarfile.TarError, lzma.LZMAError) as exc:
        errors.append(f"Cannot read .tar.xz archive: {exc}")
    return errors


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
    print(f"Validated CS Launcher Plus MultiRT archive: {args.output_archive}")
    print("Checks: Java 8 metadata, ARM64 metadata, ELF64/AArch64, executable java, libjvm.so, native libraries.")
    print("Not checked: Android/Bionic symbol compatibility or execution on a physical device.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
