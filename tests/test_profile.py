import json
import unittest
from pathlib import Path

from scripts.validate_profile import validate_profile

PROFILE_PATH = Path(__file__).parents[1] / "config" / "minecraft-1.12.2.json"


class ProfileValidationTests(unittest.TestCase):
    def setUp(self):
        self.profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    def test_repository_profile_is_valid(self):
        self.assertEqual(validate_profile(self.profile), [])

    def test_rejects_wrong_java_major(self):
        self.profile["javaMajor"] = 17
        self.assertTrue(any("javaMajor" in e for e in validate_profile(self.profile)))

    def test_rejects_heap_argument_mismatch(self):
        self.profile["jvmArguments"][-1] = "-Xmx2048M"
        self.assertTrue(any("-Xmx" in e for e in validate_profile(self.profile)))

    def test_rejects_heap_above_guardrail(self):
        self.profile["memory"]["maximumHeapMb"] = 4096
        self.profile["jvmArguments"][-1] = "-Xmx4G"
        self.assertTrue(any("teto" in e for e in validate_profile(self.profile)))

    def test_rejects_duplicate_arguments(self):
        self.profile["jvmArguments"].append("-Xms512M")
        self.assertTrue(any("duplicados" in e for e in validate_profile(self.profile)))

    def test_rejects_unknown_fields(self):
        self.profile["experimentalMagicFlag"] = True
        self.assertTrue(any("desconhecidos" in e for e in validate_profile(self.profile)))

    def test_rejects_non_object_root(self):
        self.assertTrue(validate_profile([]))


if __name__ == "__main__":
    unittest.main()
