"""Privacy invariants for personal preferences, exports and Git publication."""
import copy
import json
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

import test_profile_store as helpers

KIT_ROOT = Path(__file__).resolve().parents[1]
store = helpers.store
builder = helpers.builder
release = helpers.load_module("qrclima_release_checks", KIT_ROOT / "tools/check_public.py")


class ReleaseAndPreferenceTests(unittest.TestCase):
    def setUp(self):
        self.test_root = KIT_ROOT / "private-test-runs"
        self.test_root.mkdir(exist_ok=True)
        self.directory = Path(tempfile.mkdtemp(prefix="release-", dir=self.test_root)).resolve()
        self.path = store.init_profile(self.directory / "data", "prueba")

    def tearDown(self):
        if self.directory == self.test_root.resolve() or not self.directory.is_relative_to(self.test_root.resolve()):
            raise RuntimeError("Unexpected cleanup target")
        def retry_readonly(function, name, error):
            target = Path(name).resolve()
            if not target.is_relative_to(self.directory) or not isinstance(error[1], PermissionError):
                raise error[1]
            target.chmod(target.stat().st_mode | stat.S_IWRITE)
            function(name)
        shutil.rmtree(self.directory, onerror=retry_readonly)

    def profile(self):
        return store.load_profile(self.path, "prueba")

    def git(self, *args):
        result = subprocess.run(["git", "-C", str(self.directory), *args], capture_output=True)
        self.assertEqual(result.returncode, 0, "Fixture Git operation failed")
        return result.stdout

    def init_git(self):
        self.git("init", "-q")
        self.git("config", "user.name", "Synthetic test")
        self.git("config", "user.email", "test@example.invalid")

    def test_personal_preference_does_not_change_export_or_another_user(self):
        entries_before = builder.workspace_entries()
        preferences = self.profile()["preferences"]
        self.assertTrue(all(item["setting"] == store.fact() for item in preferences))
        preferences[0]["setting"] = helpers.declared("PRIVATE-PILOT-VALUE-DO-NOT-EXPORT")
        store.apply_patch(self.directory / "data", "prueba", 0, helpers.patch("/preferences", preferences))
        store.init_profile(self.directory / "data", "otra")
        other = store.load_profile(store.profile_path(self.directory / "data", "otra"), "otra")
        self.assertTrue(all(item["setting"]["value"] is None for item in other["preferences"]))
        self.assertEqual(entries_before, builder.workspace_entries())
        self.assertFalse(any(b"PRIVATE-PILOT-VALUE" in data for data in entries_before.values()))

    def test_legacy_profile_gains_empty_slots_without_losing_existing_data(self):
        data = self.profile()
        data["person"]["display_name"] = helpers.declared("Fictional person")
        del data["preferences"], data["improvement_proposals"]
        self.path.write_text(json.dumps(data), encoding="utf-8")
        loaded = self.profile()
        self.assertEqual(loaded["person"]["display_name"]["value"], "Fictional person")
        self.assertTrue(all(item["setting"]["value"] is None for item in loaded["preferences"]))
        self.assertEqual(loaded["improvement_proposals"], [])
        store.apply_patch(self.directory / "data", "prueba", 0, helpers.patch("/person/language", helpers.declared("es")))
        self.assertEqual(self.profile()["person"]["display_name"]["value"], "Fictional person")

    def test_duplicate_or_wrong_organization_preference_is_rejected_atomically(self):
        preferences = self.profile()["preferences"]
        preferences.append(copy.deepcopy(preferences[0]))
        with self.assertRaises(store.ProfileError):
            store.apply_patch(self.directory / "data", "prueba", 0, helpers.patch("/preferences", preferences))
        preferences = self.profile()["preferences"]
        preferences[0]["organization_id"] = "unregistered-org"
        with self.assertRaises(store.ProfileError):
            store.apply_patch(self.directory / "data", "prueba", 0, helpers.patch("/preferences", preferences))
        self.assertEqual(self.profile()["revision"], 0)

    def test_preference_does_not_grant_operational_permissions(self):
        initial = self.profile()["operation_policy"]
        preferences = self.profile()["preferences"]
        preferences.append({"key": "skip-confirmation", "organization_id": None, "setting": helpers.declared(True)})
        store.apply_patch(self.directory / "data", "prueba", 0, helpers.patch("/preferences", preferences))
        self.assertEqual(self.profile()["operation_policy"], initial)
        self.assertEqual(self.profile()["authorizations"], [])

    def test_mixed_proposal_remains_private_with_no_automatic_public_summary(self):
        proposal = {"id": "signature-configuration", "classification": "mixed", "summary": "PRIVATE-PROPOSAL-VALUE", "status": "proposed", "evidence_ref": "private-fixture", "public_summary": None}
        store.apply_patch(self.directory / "data", "prueba", 0, helpers.patch("/improvement_proposals", [proposal]))
        self.assertIsNone(self.profile()["improvement_proposals"][0]["public_summary"])
        self.assertFalse(any(b"PRIVATE-PROPOSAL-VALUE" in value for value in builder.workspace_entries().values()))
        with self.assertRaises(store.ProfileError):
            store.apply_patch(self.directory / "data", "prueba", 1, helpers.patch("/improvement_proposals", [proposal, proposal]))

    def test_adapters_resolve_to_same_canonical_procedure_and_license_is_included(self):
        entries = builder.workspace_entries()
        self.assertIn("LICENSE", entries)
        self.assertEqual(entries["CLAUDE.md"].strip(), b"@AGENTS.md")
        self.assertEqual(entries["GEMINI.md"].strip(), b"@./AGENTS.md")
        for name in entries:
            if name.startswith(".claude/skills/"):
                self.assertIn("../../../.agents/skills/".encode(), entries[name])
                self.assertIn(name.replace(".claude/", ".agents/"), entries)

    def test_index_checks_staged_secret_even_if_working_copy_was_cleaned(self):
        self.init_git()
        readme = self.directory / "README.md"
        readme.write_text("sk-" + "FAKE1234" * 4, encoding="utf-8")
        self.git("add", "--", "README.md")
        readme.write_text("Clean working text", encoding="utf-8")
        with self.assertRaises(release.ReleaseError):
            release.check_index(self.directory)

    def test_history_detects_private_file_deleted_from_current_commit(self):
        self.init_git()
        private = self.directory / ".qrclima/profiles/prueba/profile.json"
        private.parent.mkdir(parents=True)
        private.write_text("{}", encoding="utf-8")
        self.git("add", "--", ".qrclima/profiles/prueba/profile.json")
        self.git("commit", "-qm", "Synthetic private fixture")
        self.git("rm", "--", ".qrclima/profiles/prueba/profile.json")
        (self.directory / "README.md").write_text("Public fixture", encoding="utf-8")
        self.git("add", "--", "README.md")
        self.git("commit", "-qm", "Remove synthetic fixture")
        self.assertEqual(release.check_index(self.directory), 1)
        with self.assertRaises(release.ReleaseError):
            release.check_history(self.directory)

    def test_force_staged_private_path_is_rejected(self):
        self.init_git()
        private = self.directory / "private-preferences.md"
        private.write_text("Synthetic preference", encoding="utf-8")
        self.git("add", "--", private.name)
        with self.assertRaises(release.ReleaseError):
            release.check_index(self.directory)

    def test_clean_public_index_and_history_are_accepted(self):
        self.init_git()
        (self.directory / "README.md").write_text("Public fictional fixture", encoding="utf-8")
        self.git("add", "--", "README.md")
        self.git("commit", "-qm", "Synthetic public fixture")
        self.assertEqual(release.check_index(self.directory), 1)
        self.assertEqual(release.check_history(self.directory), 1)


if __name__ == "__main__":
    unittest.main()
