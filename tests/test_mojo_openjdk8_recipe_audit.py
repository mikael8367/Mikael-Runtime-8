import unittest

from scripts.audit_mojo_openjdk8_recipe import git_blob_sha, inspect_recipe_text


class MojoRecipeAuditTests(unittest.TestCase):
    def test_git_blob_sha_matches_git_object_format(self):
        self.assertEqual(git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_detects_partial_patch_and_unpinned_source(self):
        findings = inspect_recipe_text({
            "buildjdk.sh": "git apply --reject patch.diff || echo failed",
            "clonejdk.sh": "git clone --depth 1 https://github.com/openjdk/jdk8u openjdk",
        })
        self.assertTrue(any("partial" in item for item in findings))
        self.assertTrue(any("moving branch" in item for item in findings))

    def test_detects_download_and_ci_risks(self):
        findings = inspect_recipe_text({
            "getlibs.sh": "wget https://example.invalid/freetype.tar.gz",
            "maketoolchain.sh": "wget https://example.invalid/gcc.tar.xz",
            "ci_build_global.sh": "bash ./maketoolchain.sh",
            "setdevkitpath.sh": "export NDK_VERSION=r10e",
            "tarjdk.sh": "git clone --depth 1 -b 'v2.2.0' https://github.com/termux/termux-elf-cleaner",
            ".github/workflows/build.yml": "uses: mxschmitt/action-tmate@v3",
        })
        self.assertGreaterEqual(len([x for x in findings if x.startswith("HIGH:")]), 4)
        self.assertTrue(any("no explicit NDK" in item for item in findings))

    def test_clean_recipe_still_requires_manual_review(self):
        self.assertTrue(any("manual review" in item for item in inspect_recipe_text({})))


if __name__ == "__main__":
    unittest.main()
