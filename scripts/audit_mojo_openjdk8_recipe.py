#!/usr/bin/env python3
"""Audit the currently maintained MojoLauncher OpenJDK 8 Android build recipe."""
from __future__ import annotations

import argparse
import hashlib
import subprocess
from pathlib import Path

PINNED_COMMIT = "c213846ff125eccf43e6be4adf827e42c579c4ab"
EXPECTED_BLOBS = {
    ".github/workflows/build.yml": "0341c899c368dd3021f175ee98fbaa7004f17742",
    "README.md": "44784c1587c859b662936f189a690e507467af9f",
    "buildjdk.sh": "631d8c97c9842057bbee451b40d60bb253646cde",
    "clonejdk.sh": "869f6bfd7bdbb8d97fedc0aa65f56a02c9efb4d3",
    "getlibs.sh": "2fe68739ddacf15ca7714bffe7509066f0010ddc",
    "ci_build_global.sh": "0f7b14cff5f1bfb46a3fe0b8a1920e165442834b",
    "ci_build_arch_aarch64.sh": "9342d4c0f13c448dcbf7acfad15bccaa9bb53098",
    "extractndk.sh": "785ed3617a73a4353c6d4c44cacdbcc0bc7ce626",
    "maketoolchain.sh": "d236f9e794803a00c099355506ef8820f5f55c26",
    "tarjdk.sh": "211b2fb218d48a7da2e4d4cae62afaf4cf5bbcd4",
    "removejdkdebuginfo.sh": "0193d35fcd0f694fcf4cce3409d08a63129b72f8",
}

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()

def inspect_recipe_text(files: dict[str, str]) -> list[str]:
    findings: list[str] = []
    build = files.get("buildjdk.sh", "")
    clone = files.get("clonejdk.sh", "")
    libs = files.get("getlibs.sh", "")
    global_build = files.get("ci_build_global.sh", "")
    pack = files.get("tarjdk.sh", "")
    workflow = files.get(".github/workflows/build.yml", "")
    readme = files.get("README.md", "")

    if "git apply --reject" in build and "|| echo" in build:
        findings.append("BLOCKER: patch application can be partial and failures are tolerated.")
    if "git clone --depth 1 https://github.com/openjdk/jdk8u openjdk" in clone:
        findings.append("BLOCKER: OpenJDK source is cloned from a moving branch without a SHA.")
    if "wget " in libs and "sha256sum" not in libs and "sha256" not in libs.lower():
        findings.append("HIGH: FreeType/CUPS downloads have no checksum/signature verification.")
    if "wget " in global_build and "sha256sum" not in global_build and "sha256" not in global_build.lower():
        findings.append("HIGH: Android NDK download has no checksum/signature verification.")
    if "unzip" in global_build:
        findings.append("HIGH: NDK archive is extracted immediately after download.")
    if "git clone --depth 1 -b 'v2.2.0' https://github.com/termux/termux-elf-cleaner" in pack:
        findings.append("HIGH: termux-elf-cleaner is selected by tag, not immutable commit.")
    if "action-tmate" in workflow:
        findings.append("HIGH: upstream CI starts an interactive tmate session on failure.")
    if "NDK r10e" in readme:
        findings.append("INFO: build depends on historical NDK r10e; reproduce and audit its ABI/API output.")
    if not findings:
        findings.append("No known risk pattern detected; manual review is still required.")
    return findings

def audit_repository(repo: Path) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    report: list[str] = []
    head = subprocess.run(
        ["git", "-C", str(repo), "rev-parse", "HEAD"],
        check=False, capture_output=True, text=True,
    )
    actual = head.stdout.strip() if head.returncode == 0 else ""
    report.extend([f"Expected commit: {PINNED_COMMIT}", f"Actual commit:   {actual or 'UNAVAILABLE'}"])
    if actual != PINNED_COMMIT:
        errors.append("Checkout does not match the pinned MojoLauncher commit.")

    files: dict[str, str] = {}
    for relative, expected in EXPECTED_BLOBS.items():
        path = repo / relative
        if not path.is_file():
            errors.append(f"Missing required file: {relative}")
            report.append(f"{relative}: MISSING")
            continue
        data = path.read_bytes()
        actual_blob = git_blob_sha(data)
        report.append(f"{relative}: {actual_blob}")
        if actual_blob != expected:
            errors.append(f"Blob SHA mismatch for {relative}: expected {expected}, got {actual_blob}")
        files[relative] = data.decode("utf-8", errors="replace")

    report.extend(["", "Static findings (no build scripts executed):", *inspect_recipe_text(files)])
    report.extend(["", "Conclusion: recipe identity is pinned, but listed build risks remain."])
    return errors, report

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    errors, report = audit_repository(args.repo)
    if errors:
        report.extend(["", "IDENTITY ERRORS:", *errors])
    rendered = "\n".join(report) + "\n"
    print(rendered, end="")
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())
