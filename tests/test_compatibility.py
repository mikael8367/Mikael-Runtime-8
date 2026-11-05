import copy
import json
import unittest
from pathlib import Path

from scripts.validate_compatibility import validate_compatibility

CONTRACT_PATH = Path(__file__).parents[1] / "config" / "compatibility-minecraft-1.12.2.json"


class CompatibilityContractTests(unittest.TestCase):
    def setUp(self):
        self.contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))

    def test_repository_contract_is_valid(self):
        self.assertEqual(validate_compatibility(self.contract), [])

    def test_rejects_non_java_8_target(self):
        self.contract["target"]["javaMajor"] = 17
        self.assertTrue(any("javaMajor" in error for error in validate_compatibility(self.contract)))

    def test_rejects_wrong_bytecode_level(self):
        self.contract["target"]["maximumClassFileMajorVersion"] = 61
        self.assertTrue(any("maximumClassFileMajorVersion" in error for error in validate_compatibility(self.contract)))

    def test_requires_optional_optifine_layer(self):
        self.contract["optifine"]["enabledAsOptionalLayer"] = False
        self.assertTrue(any("opcional" in error for error in validate_compatibility(self.contract)))

    def test_requires_forge_optifine_combination_test(self):
        self.contract["optifine"]["requiresForgeCombinationTest"] = False
        self.assertTrue(any("combinação Forge" in error for error in validate_compatibility(self.contract)))

    def test_rejects_mod_library_filtering(self):
        self.contract["modLoading"]["doNotFilterModLibraries"] = False
        self.assertTrue(any("doNotFilterModLibraries" in error for error in validate_compatibility(self.contract)))

    def test_requires_large_modpack_validation(self):
        self.contract["modpacks"]["largeClasspathMustBeMeasured"] = False
        self.assertTrue(any("largeClasspathMustBeMeasured" in error for error in validate_compatibility(self.contract)))

    def test_requires_both_launchers(self):
        self.contract["launchers"] = ["FCL"]
        self.assertTrue(any("FCL e CS Launcher Plus" in error for error in validate_compatibility(self.contract)))

    def test_rejects_claim_of_verified_runtime(self):
        self.contract["status"] = "stable"
        self.assertTrue(any("target-not-yet-verified" in error for error in validate_compatibility(self.contract)))

    def test_rejects_non_object_root(self):
        self.assertTrue(validate_compatibility([]))


if __name__ == "__main__":
    unittest.main()
