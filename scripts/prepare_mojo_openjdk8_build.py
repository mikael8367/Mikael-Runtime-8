#!/usr/bin/env python3
"""Create a hardened, pinned ARM64 OpenJDK build recipe from the audited Mojo source."""
from __future__ import annotations
import argparse
import hashlib
import re
import subprocess
from pathlib import Path

RECIPE_COMMIT = "a0d811b6c5ebd251374751438ec8b635f0746ab4"
OPENJDK_COMMIT = "b661ee6ff840d6922aa7424a4d8f24760b21cf26"
PATCH_BLOBS = {
    "jdk8u_android.diff": "35137738d48cee5fbcbd41d335d3414ee4a6f91f",
    "jdk8u_android_branding.diff": "ba84685b24586d4794e7822f2927f62e960f0c4e",
    "jdk8u_android_main.diff": "8ba2f3c46963b3d125eb416cfb5185a4f53b69f6",
}
FREETYPE_COMMIT = "6a2b3e4007e794bfc6c91030d0ed987f925164a8"
CUPS_COMMIT = "070e33a4c9dfdb21638de0fedb2904391c30d070"
ELF_CLEANER_COMMIT = "d08dfdc73ff5b6061e134b90bec16489655015f5"
GCC_SHA256 = "ad32f8952dc2bbe5d9e7a6f4a6f0a185a8b1dfbe6f0e7410db5da8ba45f3453f"

def git_blob_sha(data: bytes) -> str:
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()

def compatible_branding_patch() -> str:
    """Rebuild the branding hunk without stale JDK_UPDATE_VERSION context."""
    return """diff --git a/common/autoconf/version-numbers b/common/autoconf/version-numbers
--- a/common/autoconf/version-numbers
+++ b/common/autoconf/version-numbers
@@ -32,3 +32,3 @@
 PRODUCT_NAME=OpenJDK
-PRODUCT_SUFFIX="Runtime Environment"
+PRODUCT_SUFFIX="Runtime Environment (Android)"
 JDK_RC_PLATFORM_NAME=Platform
"""


def pinned_clone(repo_url: str, directory: str, commit: str) -> str:
    return f"""git init "{directory}"
git -C "{directory}" remote add origin "{repo_url}"
git -C "{directory}" fetch --depth 1 origin "{commit}"
git -C "{directory}" checkout --detach FETCH_HEAD
test "$(git -C "{directory}" rev-parse HEAD)" = "{commit}"
"""

def hardened_scripts(openjdk_commit: str = OPENJDK_COMMIT) -> dict[str, str]:
    clone = "#!/usr/bin/env bash\nset -euo pipefail\n" + pinned_clone(
        "https://github.com/openjdk/jdk8u.git", "openjdk", openjdk_commit
    ) + "./remove_emudhra.sh\n"
    libs = "#!/usr/bin/env bash\nset -euo pipefail\n" + pinned_clone(
        "https://github.com/freetype/freetype.git", "freetype-2.10.4", FREETYPE_COMMIT
    ) + pinned_clone(
        "https://github.com/apple/cups.git", "cups-2.2.4", CUPS_COMMIT
    ) + """\n# FreeType 2.10.4 stores configure.raw in git; generate the configure script.\npushd freetype-2.10.4\n./autogen.sh\ntest -x ./configure\npopd\n"""
    toolchain = f"""#!/usr/bin/env bash
set -euo pipefail
: "${{BUILD_IOS:=0}}"
. setdevkitpath.sh
mkdir -p "$NDK/generated-toolchains/android-$TARGET_SHORT-toolchain"
pushd "$NDK/generated-toolchains/android-$TARGET_SHORT-toolchain"
asset="gcc-13-$TARGET_SHORT-21.tar.xz"
curl --fail --location --retry 3 --output "$asset" "https://github.com/MojoLauncher/gcc-toolchain/releases/download/prebuilt/$asset"
echo "{GCC_SHA256}  $asset" | sha256sum --check --status
tar -xJf "$asset"
rm "$asset"
rm sysroot/usr/lib/libstdc++.a
rm sysroot/usr/lib/libstdc++.so
popd
cp "devkit.info.$TARGET_SHORT" "$NDK/generated-toolchains/android-$TARGET_SHORT-toolchain/"
"""
    elf_cleaner = f"""#!/usr/bin/env bash
set -euo pipefail
: "${{BUILD_IOS:=0}}"
if [[ "$BUILD_IOS" != "1" ]]; then
  git init termux-elf-cleaner
  git -C termux-elf-cleaner remote add origin https://github.com/termux/termux-elf-cleaner.git
  git -C termux-elf-cleaner fetch --depth 1 origin "{ELF_CLEANER_COMMIT}"
  git -C termux-elf-cleaner checkout --detach FETCH_HEAD
  test "$(git -C termux-elf-cleaner rev-parse HEAD)" = "{ELF_CLEANER_COMMIT}"
  pushd termux-elf-cleaner
  autoreconf --install
  # This is a host utility that runs on the Ubuntu runner, not on Android.
  # Do not inherit the Android cross-toolchain from setdevkitpath.sh.
  env -u CC -u CXX -u CPP -u AR -u AS -u LD -u NM -u RANLIB -u STRIP -u CFLAGS -u CXXFLAGS -u CPPFLAGS -u LDFLAGS CC=cc CXX=c++ AR=ar RANLIB=ranlib ./configure --build="$(./config.guess)"
  make
  popd
  clean_elfs() {{
    local root="$1"
    while IFS= read -r -d '' file; do
      if [[ "$(od -An -tx1 -N4 "$file" | tr -d '[:space:]')" == "7f454c46" ]]; then
        ./termux-elf-cleaner/termux-elf-cleaner "$file"
      fi
    done < <(find "$root" -type f -print0)
  }}
  clean_elfs jreout
  clean_elfs jdkout
fi
cp -Rf jre_override/lib/* jreout/lib/
cp -Rf jre_override/lib/* jdkout/jre/lib/
find jreout -name '*.so' -execdir "$NDK$NDK_PREBUILT_ARCH" {{}} \\;
tar cJf "jre8-$TARGET_SHORT-$(date -u +%Y%m%d)-$JDK_DEBUG_LEVEL.tar.xz" -C jreout .
tar cJf "jdk8-$TARGET_SHORT-$(date -u +%Y%m%d)-$JDK_DEBUG_LEVEL.tar.xz" -C jdkout .
"""
    return {
        "clonejdk.sh": clone,
        "getlibs.sh": libs,
        "maketoolchain.sh": toolchain,
        "tarjdk.sh": elf_cleaner,
    }

def harden_buildlibs_script(original: str) -> str:
    old = '''if [[ "$error_code" -ne 0 ]]; then
  echo "\\n\\nCONFIGURE ERROR $error_code , config.log:"
  cat config.log
  exit $error_code
fi'''
    new = '''if [[ "${error_code:-0}" -ne 0 ]]; then
  echo "\\n\\nFREETYPE CONFIGURE ERROR $error_code; expected log: builds/unix/config.log"
  if [[ -f builds/unix/config.log ]]; then
    cat builds/unix/config.log
  else
    find . -name config.log -type f -print -exec tail -n 200 {} \\;
  fi
  exit "$error_code"
fi'''
    if old not in original:
        raise ValueError("Could not locate the pinned FreeType configure error handler.")
    return original.replace(old, new, 1)


def smoke_test_script() -> str:
    return '''#!/usr/bin/env bash
set -euo pipefail
if [[ "${BUILD_IOS:-0}" == "1" ]]; then
  echo "Android toolchain smoke test skipped for iOS build."
  exit 0
fi
glibc_version="$(getconf GNU_LIBC_VERSION | awk '{print $2}')"
echo "Host GLIBC: $glibc_version"
if ! awk -v version="$glibc_version" 'BEGIN { split(version, v, /\\./); exit ! (v[1] > 2 || (v[1] == 2 && v[2] >= 38)) }'; then
  echo "Pinned GCC 13 toolchain requires host GLIBC >= 2.38." >&2
  exit 1
fi
compiler="$TOOLCHAIN/bin/$TARGET-gcc"
test -x "$compiler"
echo "=== Cross compiler identity ==="
"$compiler" --version
"$compiler" -v
echo "=== Sysroot and runtime files ==="
"$compiler" -print-sysroot
for item in crtbegin_dynamic.o libc.so libgcc.a; do
  resolved="$("$compiler" -print-file-name="$item")"
  printf '%s -> %s\\n' "$item" "$resolved"
  test -f "$resolved"
done
cat > .mikael-toolchain-smoke.c <<'EOF'
int main(void) { return 0; }
EOF
echo "=== Compile and link Android ARM64 executable ==="
"$compiler" --sysroot="$TOOLCHAIN/sysroot" -fPIE -pie .mikael-toolchain-smoke.c -o .mikael-toolchain-smoke
file .mikael-toolchain-smoke
readelf -h .mikael-toolchain-smoke
readelf -h .mikael-toolchain-smoke | grep -q 'AArch64'
rm -f .mikael-toolchain-smoke .mikael-toolchain-smoke.c
echo "Android ARM64 toolchain smoke test passed."
'''

def inject_toolchain_smoke_test(global_text: str) -> str:
    marker = "  ./maketoolchain.sh"
    lines = global_text.splitlines(keepends=True)
    matches = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == marker]
    if len(matches) != 1:
        raise ValueError(
            "Expected exactly one ./maketoolchain.sh hook in ci_build_global.sh; "
            f"found {len(matches)}."
        )
    index = matches[0]
    newline = "\r\n" if lines[index].endswith("\r\n") else "\n"
    lines.insert(index + 1, "  bash ./smoke_test_android_toolchain.sh" + newline)
    return "".join(lines)

def strict_patch_block() -> str:
    return """# Apply the pinned Android patch set strictly; any mismatch aborts the build.
for patch in jdk8u_android.diff jdk8u_android_branding.diff jdk8u_android_main.diff; do
  expected=""
  case "$patch" in
    jdk8u_android.diff) expected="35137738d48cee5fbcbd41d335d3414ee4a6f91f" ;;
    jdk8u_android_branding.diff) expected="ba84685b24586d4794e7822f2927f62e960f0c4e" ;;
    jdk8u_android_main.diff) expected="8ba2f3c46963b3d125eb416cfb5185a4f53b69f6" ;;
  esac
  actual="$(git hash-object "../patches/$patch")"
  test "$actual" = "$expected"
  apply_path="../patches/$patch"
  if [[ "$patch" == "jdk8u_android_branding.diff" ]]; then
    apply_path="../patches/.mikael-android-branding.compat.diff"
  fi
  git apply --check --whitespace=fix "$apply_path"
  git apply --whitespace=fix "$apply_path"
  git diff --check
done
"""

def prepare(recipe_dir: Path, openjdk_commit: str = OPENJDK_COMMIT) -> None:
    recipe_dir = recipe_dir.resolve()
    head = subprocess.run(
        ["git", "-C", str(recipe_dir), "rev-parse", "HEAD"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    if head != RECIPE_COMMIT:
        raise ValueError(f"Unexpected recipe commit: {head}; expected {RECIPE_COMMIT}")
    for filename, expected in PATCH_BLOBS.items():
        path = recipe_dir / "patches" / filename
        if not path.is_file() or git_blob_sha(path.read_bytes()) != expected:
            raise ValueError(f"Patch missing or changed: {filename}")
    (recipe_dir / "patches" / ".mikael-android-branding.compat.diff").write_text(
        compatible_branding_patch(), encoding="utf-8"
    )
    build_file = recipe_dir / "buildjdk.sh"
    original = build_file.read_text(encoding="utf-8")
    start = original.find("# Apply patches")
    end = original.find("#   --with-extra-cxxflags", start)
    if start < 0 or end < 0:
        raise ValueError("Could not identify the upstream patch application section safely.")
    hardened_build = original[:start] + strict_patch_block() + "\n" + original[end:]
    if "git apply --reject" in hardened_build or "|| echo" in hardened_build:
        raise ValueError("Unsafe patch application remains in buildjdk.sh")
    for name, content in hardened_scripts(openjdk_commit).items():
        (recipe_dir / name).write_text(content, encoding="utf-8")
    buildlibs_file = recipe_dir / "buildlibs.sh"
    buildlibs_file.write_text(
        harden_buildlibs_script(buildlibs_file.read_text(encoding="utf-8")),
        encoding="utf-8",
    )
    (recipe_dir / "smoke_test_android_toolchain.sh").write_text(
        smoke_test_script(), encoding="utf-8"
    )
    global_build = recipe_dir / "ci_build_global.sh"
    global_text = global_build.read_text(encoding="utf-8")
    global_build.write_text(
        inject_toolchain_smoke_test(global_text), encoding="utf-8"
    )
    build_file.write_text(hardened_build, encoding="utf-8")
    workflow = recipe_dir / ".github" / "workflows" / "build.yml"
    workflow_text = workflow.read_text(encoding="utf-8")
    workflow_text = re.sub(
        r"\n    - name: Setup tmate session if failed\n      if:.*?\n      uses: mxschmitt/action-tmate@v3\n",
        "\n", workflow_text, flags=re.DOTALL,
    )
    if "action-tmate" in workflow_text:
        raise ValueError("Interactive tmate action could not be removed safely.")
    workflow.write_text(workflow_text, encoding="utf-8")

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--recipe-dir", type=Path, required=True)
    parser.add_argument("--openjdk-commit", default=OPENJDK_COMMIT)
    args = parser.parse_args()
    prepare(args.recipe_dir, args.openjdk_commit)
    print(f"Prepared hardened AArch64 build recipe from {RECIPE_COMMIT}")
    print(f"OpenJDK source pinned to {args.openjdk_commit}")
    print("Patch application is hash-checked, preflighted, sequential, and fatal.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
