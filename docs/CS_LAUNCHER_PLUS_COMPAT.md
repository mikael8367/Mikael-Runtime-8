# CS Launcher Plus compatibility

## Target and verified launcher contract

The target is the public fork `mikael8367/CS-LAUNCHER-PLUS-fork` (branch `main`). Its runtime manager uses `MultiRTUtils` and reads each installed runtime from the app-private runtime directory. It identifies the Java major version and architecture from the top-level `release` file.

The fork's runtime installer extracts a `.tar.xz` archive into a runtime directory, runs Java 8 `.pack` unpacking where needed, and performs post-install library preparation. The launcher profile selects the runtime using its runtime name. Java 8 is the required major version for Minecraft 1.12.2.

## Required Mikael Runtime 8 archive contract

The final archive must be a plain `.tar.xz` whose entries are rooted directly at the JRE contents, not inside an additional parent folder:

- `release` at archive root.
- `release` contains `JAVA_VERSION="1.8...."`.
- `release` contains `OS_ARCH="aarch64"` (accepted alias: `arm64`).
- `bin/java` exists and is executable.
- `lib/` exists and contains the Android ARM64 native runtime libraries, including the JVM shared library.
- All required Java libraries and native dependencies are included.
- File modes and symbolic links are preserved.
- No binary from a different ABI is mixed into the package.

The CS Launcher Plus runtime parser accepts `aarch64` and maps it to ARM64. The launcher download naming convention uses `arm64` in the archive filename; that filename does not replace the architecture metadata in `release`.

## Build the compatible archive

After a real Java 8 ARM64 JRE has been compiled and tested, run:

```bash
python scripts/package_cslauncher_runtime.py /path/to/jre8-arm64 mikael-runtime8-cslauncher-arm64.tar.xz
```

The packager checks Java version, architecture, executable presence and native libraries, creates the archive with JRE contents at its root, then reopens and validates the archive. It rejects symlinks that escape the JRE source directory.

## Installation status

**Not yet installable in CS Launcher Plus.** The repository does not contain a compiled JRE or release archive. The packager is the compatibility boundary; it does not compile OpenJDK and does not add a download URL to the launcher. A later launcher integration can add a Mikael Runtime entry once a tested archive is published and its checksum and license notices are available.

For now, do not select a fabricated runtime name or manually rename another runtime. A profile can only use Mikael Runtime 8 after the archive has been installed and the launcher's runtime manager can read its Java 8 metadata.
