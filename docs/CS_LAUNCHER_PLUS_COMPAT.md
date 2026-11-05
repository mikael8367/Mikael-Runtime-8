# CS Launcher Plus compatibility

## Target and verified launcher contract

The target is the public fork `mikael8367/CS-LAUNCHER-PLUS-fork` (branch `main`). Its runtime manager uses `MultiRTUtils` and reads each installed runtime from the app-private runtime directory. It identifies the Java major version and architecture from the top-level `release` file.

The fork's runtime installer extracts a `.tar.xz` archive into a runtime directory, runs Java 8 `.pack` unpacking where needed, and performs post-install library preparation. The launcher profile selects the runtime using its runtime name. Java 8 is the required major version for Minecraft 1.12.2.

## Required Mikael Runtime 8 archive contract

The final archive must be a plain `.tar.xz` whose entries are rooted directly at the JRE contents, not inside an additional parent folder:

- `release` at archive root.
- `release` contains `JAVA_VERSION="1.8...."`.
- `release` contains `OS_ARCH="aarch64"` (accepted alias: `arm64`).
- `bin/java` exists, is executable and is an ELF64 little-endian AArch64 binary.
- `lib/` contains the HotSpot `libjvm.so` and the native runtime libraries.
- Every packaged native `.so` must be ELF64 little-endian AArch64.
- All required Java libraries and native dependencies are included.
- File modes and symbolic links are preserved.
- No binary from a different ABI is mixed into the package.

The CS Launcher Plus runtime parser accepts `aarch64` and maps it to ARM64. The launcher download naming convention uses `arm64` in the archive filename; that filename does not replace the architecture metadata in `release`.

**Important limitation:** ELF architecture checks do not prove Android/Bionic compatibility, API-level compatibility, absence of unresolved symbols, or successful execution on a physical device. Those require NDK/linker inspection and device tests.

## Build and validate the compatible archive

After a real Java 8 ARM64 JRE has been compiled, run:

```bash
python scripts/package_cslauncher_runtime.py /path/to/jre8-arm64 mikael-runtime8-cslauncher-arm64.tar.xz
```

The packager checks Java version and architecture metadata, executable presence, ELF class/endianness/AArch64 machine ID for `bin/java` and every native `.so`, and the presence and architecture of HotSpot `libjvm.so`. It creates the archive with JRE contents at its root, reopens it, and validates the archive layout and ELF headers. It rejects source symlinks that escape the JRE, special files, archive symlink escapes, non-canonical/traversal paths, duplicate entries, and hard links or other unsupported tar entry types.

Automated regression tests use synthetic ELF headers to exercise valid ARM64, wrong-machine, non-ELF and metadata cases. They cover the packaging gate, including source symlink escapes and unsafe archive entry types; they do not emulate or certify a real JVM.

## Installation status

**Not yet installable in CS Launcher Plus.** The repository does not contain a compiled JRE or release archive. The packager is the compatibility boundary; it does not compile OpenJDK and does not add a download URL to the launcher. A later launcher integration can add a Mikael Runtime entry once a tested archive is published and its checksum and license notices are available.

For now, do not select a fabricated runtime name or manually rename another runtime. A profile can only use Mikael Runtime 8 after the archive has been installed and the launcher's runtime manager can read its Java 8 metadata.

## Mods, OptiFine e modpacks

A runtime deve ser transparente ao classpath criado pelo launcher: não reordenar nem filtrar JARs de mods e bibliotecas. O launcher continua responsável por resolver dependências, disponibilizar o diretório do jogo e extrair as bibliotecas nativas LWJGL adequadas.

A integração não está testada com uma JRE real. Antes de anunciar suporte, validar a sequência Vanilla, Forge, OptiFine isolado, Forge + OptiFine, mods em grupos e modpack grande nos dois launchers. Ver [MOD_COMPATIBILITY.md](MOD_COMPATIBILITY.md).
