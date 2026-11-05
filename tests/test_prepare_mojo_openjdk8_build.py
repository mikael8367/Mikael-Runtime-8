import unittest

from scripts.prepare_mojo_openjdk8_build import (
    GCC_SHA256, OPENJDK_COMMIT, PATCH_BLOBS, git_blob_sha,
    hardened_scripts, harden_buildlibs_script, inject_toolchain_smoke_test, smoke_test_script, strict_patch_block,
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

    def test_freetype_failure_reports_real_config_log(self):
        original = '''if [[ "$error_code" -ne 0 ]]; then
  echo "\\n\\nCONFIGURE ERROR $error_code , config.log:"
  cat config.log
  exit $error_code
fi'''
        hardened = harden_buildlibs_script(original)
        self.assertIn("builds/unix/config.log", hardened)
        self.assertIn("find . -name config.log", hardened)
        self.assertNotIn("cat config.log", hardened)

    def test_arm64_toolchain_smoke_test_compiles_and_checks_architecture(self):
        script = smoke_test_script()
        self.assertIn('"$compiler" -v', script)
        self.assertIn('${BUILD_IOS:-0}', script)
        self.assertNotIn('if [[ "$BUILD_IOS"', script)
        self.assertNotIn('\\n  echo', script)
        self.assertIn('-print-file-name=', script)
        self.assertIn('-fPIE -pie', script)
        self.assertIn("grep -q 'AArch64'", script)

    def test_smoke_test_is_inserted_after_toolchain_build(self):
        source = "#!/bin/bash\n  ./maketoolchain.sh\nelse\n  echo ios\nfi\n"
        result = inject_toolchain_smoke_test(source)
        self.assertIn(
            "  ./maketoolchain.sh\n  bash ./smoke_test_android_toolchain.sh\nelse",
            result,
        )
        with self.assertRaises(ValueError):
            inject_toolchain_smoke_test("#!/bin/bash\necho no hook\n")
        with self.assertRaises(ValueError):
            inject_toolchain_smoke_test("  ./maketoolchain.sh\n  ./maketoolchain.sh\n")

    def test_patch_block_fails_closed(self):
        block = strict_patch_block()
        self.assertIn("git apply --check", block)
        self.assertIn("git diff --check", block)
        self.assertNotIn("--reject", block)
        self.assertNotIn("|| echo", block)
        self.assertIn("ba84685b24586d4794e7822f2927f62e960f0c4e", block)

if __name__ == "__main__":
    unittest.main()
