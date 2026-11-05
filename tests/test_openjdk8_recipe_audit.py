import hashlib
import unittest

from scripts.audit_openjdk8_recipe import git_blob_sha, inspect_recipe_text


class OpenJDK8RecipeAuditTests(unittest.TestCase):
    def test_git_blob_sha_uses_git_blob_header(self):
        data = b"test\n"
        expected = hashlib.sha1(b"blob 5\0test\n").hexdigest()
        self.assertEqual(git_blob_sha(data), expected)

    def test_detects_unsafe_patch_application(self):
        findings = inspect_recipe_text({
            "buildjdk.sh": "git apply --reject patch.diff || echo failed"
        })
        self.assertTrue(any("BLOCKER" in item and "patch" in item.lower() for item in findings))

    def test_detects_unpinned_openjdk_clone(self):
        findings = inspect_recipe_text({
            "clonejdk.sh": "git clone --depth 1 https://github.com/openjdk/jdk8u openjdk"
        })
        self.assertTrue(any("moving OpenJDK branch" in item for item in findings))

    def test_detects_unverified_downloads(self):
        findings = inspect_recipe_text({
            "getlibs.sh": "wget https://example.invalid/source.tar.gz",
            "ci_build_global.sh": "wget https://example.invalid/ndk.zip\nunzip ndk.zip",
        })
        self.assertTrue(any("FreeType/CUPS" in item for item in findings))
        self.assertTrue(any("NDK" in item and "integrity" in item for item in findings))

    def test_detects_tmate_and_mutable_elf_cleaner_tag(self):
        findings = inspect_recipe_text({
            "tarjdk.sh": "git clone --depth 1 -b 'v2.2.0' https://github.com/termux/termux-elf-cleaner",
            ".github/workflows/build.yml": "uses: mxschmitt/action-tmate@v3",
        })
        self.assertTrue(any("termux-elf-cleaner" in item for item in findings))
        self.assertTrue(any("tmate" in item for item in findings))

    def test_reports_legacy_ndk_constraints(self):
        findings = inspect_recipe_text({
            "setdevkitpath.sh": "export NDK_VERSION=r10e\nexport API=21"
        })
        self.assertTrue(any("NDK r10e" in item for item in findings))


if __name__ == "__main__":
    unittest.main()
