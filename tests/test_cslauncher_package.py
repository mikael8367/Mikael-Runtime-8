import tarfile
import tempfile
import unittest
from pathlib import Path

from scripts.package_cslauncher_runtime import package_jre, validate_archive, validate_jre


def fake_elf(machine=183, elf_class=2):
    header = bytearray(64)
    header[:4] = b"\x7fELF"
    header[4] = elf_class
    header[5] = 1
    header[6] = 1
    header[18:20] = machine.to_bytes(2, "little")
    return bytes(header)


class CsLauncherPackageTests(unittest.TestCase):
    def make_fake_jre(self, root: Path, machine=183):
        (root / "bin").mkdir(parents=True)
        (root / "lib" / "aarch64" / "server").mkdir(parents=True)
        (root / "release").write_text(
            'JAVA_VERSION="1.8.0_442"\nOS_ARCH="aarch64"\n', encoding="utf-8"
        )
        java = root / "bin" / "java"
        java.write_bytes(fake_elf(machine))
        java.chmod(0o755)
        (root / "lib" / "aarch64" / "server" / "libjvm.so").write_bytes(fake_elf(machine))
        (root / "lib" / "rt.jar").write_bytes(b"fake-rt-jar")

    def test_rejects_missing_jre(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(validate_jre(Path(tmp) / "missing"))

    def test_rejects_wrong_release_architecture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root)
            (root / "release").write_text(
                'JAVA_VERSION="1.8.0_442"\nOS_ARCH="x86_64"\n', encoding="utf-8"
            )
            self.assertTrue(any("ARM64" in e for e in validate_jre(root)))

    def test_rejects_wrong_elf_machine(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root, machine=62)
            errors = validate_jre(root)
            self.assertTrue(any("AArch64" in e for e in errors))

    def test_rejects_libjvm_in_wrong_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root)
            jvm = root / "lib" / "aarch64" / "server" / "libjvm.so"
            wrong = root / "lib" / "server" / "libjvm.so"
            wrong.parent.mkdir(parents=True)
            jvm.rename(wrong)
            self.assertTrue(any("lib/aarch64/server/libjvm.so" in e for e in validate_jre(root)))

    def test_rejects_missing_core_rt_jar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root)
            (root / "lib" / "rt.jar").unlink()
            self.assertTrue(any("lib/rt.jar" in e for e in validate_jre(root)))

    def test_rejects_non_elf_java(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root)
            (root / "bin" / "java").write_text("#!/bin/sh\n", encoding="utf-8")
            self.assertTrue(any("valid ELF" in e for e in validate_jre(root)))

    def test_rejects_symlink_outside_jre(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            root = base / "jre"
            self.make_fake_jre(root)
            external = base / "outside.so"
            external.write_bytes(fake_elf())
            (root / "lib" / "aarch64" / "server" / "escape.so").symlink_to(external)
            self.assertTrue(any("Symlink escapes" in e for e in validate_jre(root)))

    def test_rejects_dangling_symlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root)
            (root / "lib" / "aarch64" / "server" / "dangling.so").symlink_to("missing.so")
            self.assertTrue(any("Dangling symlink" in e for e in validate_jre(root)))

    def test_rejects_wrong_archive_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root)
            with self.assertRaisesRegex(ValueError, r"\\.tar\\.xz"):
                package_jre(root, Path(tmp) / "runtime.zip")

    def test_archive_is_xz_compressed_tar_with_flat_jre_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            output = Path(tmp) / "Mikael-Runtime-8-Android-ARM64.tar.xz"
            self.make_fake_jre(root)
            package_jre(root, output)
            self.assertEqual(output.read_bytes()[:6], bytes([253, 55, 122, 88, 90, 0]))
            with tarfile.open(output, "r:xz") as archive:
                names = set(archive.getnames())
                self.assertIn("bin/java", names)
                self.assertIn("release", names)
                self.assertIn("lib/rt.jar", names)
                self.assertNotIn("jre/bin/java", names)

    def test_packages_root_layout_and_validates_elf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            output = Path(tmp) / "mikael-runtime8.tar.xz"
            self.make_fake_jre(root)
            package_jre(root, output)
            self.assertEqual(validate_archive(output), [])

    def test_rejects_archive_with_wrong_extension(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive = Path(tmp) / "runtime.zip"
            archive.write_bytes(b"not a runtime")
            self.assertTrue(any(".tar.xz" in e for e in validate_archive(archive)))

    def test_rejects_archive_symlink_escape(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "unsafe.tar.xz"
            with tarfile.open(output, "w:xz") as archive:
                info = tarfile.TarInfo("lib/escape.so")
                info.type = tarfile.SYMTYPE
                info.linkname = "../../outside.so"
                archive.addfile(info)
            errors = validate_archive(output)
            self.assertTrue(any("Symlink escapes archive root" in e for e in errors))

    def test_rejects_duplicate_archive_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "duplicate.tar.xz"
            with tarfile.open(output, "w:xz") as archive:
                for _ in range(2):
                    info = tarfile.TarInfo("release")
                    info.size = 1
                    archive.addfile(info, fileobj=__import__("io").BytesIO(b"x"))
            errors = validate_archive(output)
            self.assertTrue(any("Duplicate archive path" in e for e in errors))

    def test_rejects_archive_hardlink(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "unsafe.tar.xz"
            with tarfile.open(output, "w:xz") as archive:
                info = tarfile.TarInfo("dev/device")
                info.type = tarfile.LNKTYPE
                info.linkname = "release"
                archive.addfile(info)
            errors = validate_archive(output)
            self.assertTrue(any("Unsupported archive entry type" in e for e in errors))

    def test_rejects_archive_with_extra_root_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            output = Path(tmp) / "mikael-runtime8.tar.xz"
            self.make_fake_jre(root)
            package_jre(root, output)
            with tarfile.open(output, "r:xz") as archive:
                self.assertIn("release", archive.getnames())
                self.assertNotIn("jre/release", archive.getnames())


if __name__ == "__main__":
    unittest.main()
