#!/usr/bin/env python3
"""Audit the exact historical Android OpenJDK 8 build recipe without executing it."""
from __future__ import annotations

import argparse
import hashlib
import subprocess
import sys
from pathlib import Path

PINNED_RECIPE_COMMIT = "04b90441da7e9649cb6508a037423f08d1fc531f"
EXPECTED_BLOBS = {
    "buildjdk.sh": "56d7b05d35ac20d02c23206cfee974af356c2431",
    "clonejdk.sh": "869f6bfd7bdbb8d97fedc0aa65f56a02c9efb4d3",
    "getlibs.sh": "2fe68739ddacf15ca7714bffe7509066f0010ddc",
    "ci_build_global.sh": "0f7b14cff5f1bfb46a3fe0b8a1920e165442834b",
    "setdevkitpath.sh": "ffda37592870116ce4c32d0539f603bab68ef6ac",
    "extractndk.sh": "785ed3617a73a4353c6d4c44cacdbcc0bc7ce626",
    "maketoolchain.sh": "d236f9e794803a00c099355506ef8820f5f55c26",
    "buildlibs.sh": "3b9ee684ce03bfea710940d696795891f1198c05",
    "ci_build_arch_aarch64.sh": "9342d4c0f13c448dcbf7acfad15bccaa9bb53098",
    "tarjdk.sh": "211b2fb218d48a7da2e4d4cae62afaf4cf5bbcd4",
    "removejdkdebuginfo.sh": "0193d35fcd0f694fcf4cce3409d08a63129b72f8",
    ".github/workflows/build.yml": "368445eba127aeef3e0961eadc098781d593ca16",
}


def git_blob_sha(data: bytes) -> str:
    header = f"blob {len(data)}\\0".encode("ascii")
    return hashlib.sha1(header + data).hexdigest()


def inspect_recipe_text(files: dict[str, str]) -> list[str]:
    findings: list[str] = []
    build = files.get("buildjdk.sh", "")
    clone = files.get("clonejdk.sh", "")
    libs = files.get("getlibs.sh", "")
    global_build = files.get("ci_build_global.sh", "")
    pack = files.get("tarjdk.sh", "")
    workflow = files.get(".github/workflows/build.yml", "")
    devkit = files.get("setdevkitpath.sh", "")

    if "git apply --reject" in build and "|| echo" in build:
        findings.append("BLOCKER: buildjdk.sh tolerates failed/partial patch application.")
    if "git clone --depth 1 https://github.com/openjdk/jdk8u openjdk" in clone:
        findings.append("BLOCKER: clonejdk.sh clones a moving OpenJDK branch without a commit SHA.")
    if "wget " in libs and "sha256sum" not in libs and "sha256" not in libs.lower():
        findings.append("HIGH: getlibs.sh downloads FreeType/CUPS without checksum or signature verification.")
    if "wget " in global_build and "sha256sum" not in global_build and "sha256" not in global_build.lower():
        findings.append("HIGH: ci_build_global.sh downloads the NDK without integrity verification.")
    if "unzip" in global_build:
        findings.append("HIGH: ci_build_global.sh extracts the NDK immediately after download.")
    if "git clone --depth 1 -b 'v2.2.0' https://github.com/termux/termux-elf-cleaner" in pack:
        findings.append("HIGH: tarjdk.sh obtains termux-elf-cleaner by mutable tag, without a commit/hash pin.")
    if "action-tmate" in workflow:
        findings.append("HIGH: upstream CI starts an interactive tmate session on failure.")
    if "export NDK_VERSION=r10e" in devkit and "export API=21" in devkit:
        findings.append("INFO: recipe requires legacy NDK r10e and Android API 21; toolchain reproduction is a separate blocker.")
    if not findings:
        findings.append("No known legacy-risk patterns detected; manual review is still required.")
    return findings


def audit_repository(repo: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    report: list[str] = []
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=False, capture_output=True, text=True,
    )
    actual_commit = head.stdout.strip() if head.returncode == 0 else ""
    report.append(f"Recipe commit expected: {PINNED_RECIPE_COMMIT}")
    report.append(f"Recipe commit actual:   {actual_commit or 'UNAVAILABLE'}")
    if actual_commit != PINNED_RECIPE_COMMIT:
        errors.append("Recipe checkout does not match the pinned commit.")

    contents: dict[str, str] = {}
    for relative_path, expected_sha in EXPECTED_BLOBS.items():
        path = repo / relative_path
        if not path.is_file():
            errors.append(f"Missing pinned recipe file: {relative_path}")
            report.append(f"{relative_path}: MISSING")
            continue
        data = path.read_bytes()
        actual_sha = git_blob_sha(data)
        report.append(f"{relative_path}: {actual_sha}")
        if actual_sha != expected_sha:
            errors.append(f"Blob SHA mismatch for {relative_path}: expected {expected_sha}, got {actual_sha}")
        contents[relative_path] = data.decode("utf-8", errors="replace")

    findings = inspect_recipe_text(contents)
    report.extend(["", "Static risk findings (the recipe is NOT executed):", *findings])
    report.extend(["", "Audit conclusion: source identity can be checked; known unsafe build steps remain blocked pending replacement."])
    return errors, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True, help="Checkout of the pinned upstream recipe")
    parser.add_argument("--output", type=Path, help="Optional UTF-8 report path")
    args = parser.parse_args()

    errors, report = audit_repository(args.repo)
    if errors:
        report.extend(["", "IDENTITY ERRORS:", *errors])
    rendered = "\\n".join(report) + "\\n"
    print(rendered, end="")
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    if errors:
        return 1
    print("Pinned upstream recipe identity verified. No build commands were executed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
