import unittest

from scripts.prepare_mojo_openjdk8_build import (
    GCC_SHA256, OPENJDK_COMMIT, PATCH_BLOBS, git_blob_sha,
    hardened_scripts, strict_patch_block,
)

class PrepareMojoBuildTests(unittest.TestCase):
    def test_git_blob_hash_is_correct(self):
        self.assertEqual(git_blob_sha(b"hello\n"), "ce013625030ba8dba906f756967f9e9ca394464a")

    def test_all_source_and_patch_pins_are_immutable(self):
        self.assertEqual(len(OPENJDK_COMMIT), 40)
        self.assertEqual(len(PATCH_BLOBS), 3)
        self.assertTrue(all(len(value) == 40 for value in PATCH_BLOBS.values()))
        self.assertEqual(len(GCC_SHA256), 64)

    def test_scripts_pin_all_build_inputs(self):
        scripts = hardened_scripts()
        self.assertIn(OPENJDK_COMMIT, scripts["clonejdk.sh"])
        self.assertIn("6a2b3e4007e794bfc6c91030d0ed987f925164a8", scripts["getlibs.sh"])
        self.assertIn("070e33a4c9dfdb21638de0fedb2904391c30d070", scripts["getlibs.sh"])
        self.assertIn("./autogen.sh", scripts["getlibs.sh"])
        self.assertIn("test -x ./configure", scripts["getlibs.sh"])
        self.assertIn(GCC_SHA256, scripts["maketoolchain.sh"])
        self.assertIn(': "${BUILD_IOS:=0}"', scripts["maketoolchain.sh"])
        self.assertIn(': "${BUILD_IOS:=0}"', scripts["tarjdk.sh"])
        self.assertIn("d08dfdc73ff5b6061e134b90bec16489655015f5", scripts["tarjdk.sh"])
        self.assertIn("\n", scripts["clonejdk.sh"])
        self.assertIn("tr -d '[:space:]'", scripts["tarjdk.sh"])

    def test_patch_block_fails_closed(self):
        block = strict_patch_block()
        self.assertIn("git apply --check", block)
        self.assertIn("git diff --check", block)
        self.assertNotIn("--reject", block)
        self.assertNotIn("|| echo", block)
        self.assertIn("ba84685b24586d4794e7822f2927f62e960f0c4e", block)

if __name__ == "__main__":
    unittest.main()
