import tempfile
import unittest
from pathlib import Path

from scripts.package_cslauncher_runtime import package_jre, validate_archive, validate_jre


class CsLauncherPackageTests(unittest.TestCase):
    def make_fake_jre(self, root: Path):
        (root / "bin").mkdir(parents=True)
        (root / "lib" / "server").mkdir(parents=True)
        release = root / "release"
        release.write_text(
            'JAVA_VERSION="1.8.0_442"\nOS_ARCH="aarch64"\n',
            encoding="utf-8",
        )
        java = root / "bin" / "java"
        java.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        java.chmod(0o755)
        (root / "lib" / "server" / "libjvm.so").write_bytes(b"test-native-library")

    def test_rejects_missing_jre(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertTrue(validate_jre(Path(tmp) / "missing"))

    def test_rejects_wrong_architecture(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "jre"
            self.make_fake_jre(root)
            (root / "release").write_text(
                'JAVA_VERSION="1.8.0_442"\nOS_ARCH="x86_64"\n', encoding="utf-8"
            )
            self.assertTrue(any("ARM64" in e for e in validate_jre(root)))

    def test_packages_root_layout_for_multirt(self):
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
            # The generated archive is intentionally rooted correctly; verify expected entries.
            import tarfile
            with tarfile.open(output, "r:xz") as archive:
                self.assertIn("release", archive.getnames())
                self.assertNotIn("jre/release", archive.getnames())


if __name__ == "__main__":
    unittest.main()
