import tempfile
import unittest
import tarfile
from pathlib import Path

from scripts.package_cslauncher_runtime import package_jre, validate_archive, validate_jre


def fake_elf(machine=183, elf_class=2):
    header = bytearray(64)
    header[:4] = b"\\x7fELF"
    header[4] = elf_class
    header[5] = 1
    header[6] = 1
    header[18:20] = machine.to_bytes(2, "little")
    return bytes(header)


class CsLauncherPackageTests(unittest.TestCase):
    def make_fake_jre(self, root: Path, machine=183):
        (root / "bin").mkdir(parents=True)
        (root / "lib" / "server").mkdir(parents=True)
        (root / "release").write_text(
            'JAVA_VERSION="1.8.0_442"\\nOS_ARCH="aarch64"\\n', encoding="utf-8"
        )
        java = root / "bin" / "java"
        java.write_bytes(fake_elf(machine))
        java.chmod(0o755)
        (root / "lib" / "server" / "libjvm.so").write_bytes(fake_elf(machine))

    def test_rejects_missing_jre(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(validate_jre(Path(tmp) / "missing"))

    def test_rejects_wrong_release_architecture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root)
            (root / "release").write_text(
                'JAVA_VERSION="1.8.0_442"\\nOS_ARCH="x86_64"\\n', encoding="utf-8"
            )
            self.assertTrue(any("ARM64" in e for e in validate_jre(root)))

    def test_rejects_wrong_elf_machine(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root, machine=62)
            errors = validate_jre(root)
            self.assertTrue(any("AArch64" in e for e in errors))

    def test_rejects_non_elf_java(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root)
            (root / "bin" / "java").write_text("#!/bin/sh\\n", encoding="utf-8")
            self.assertTrue(any("valid ELF" in e for e in validate_jre(root)))

    def test_packages_root_layout_and_validates_elf(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            output = Path(tmp) / "mikael-runtime8.tar.xz"
            self.make_fake_jre(root)
            package_jre(root, output)
            self.assertEqual(validate_archive(output), [])

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
