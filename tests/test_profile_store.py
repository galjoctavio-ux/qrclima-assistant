"""Offline checks: private data isolation, concurrent edits and uncertain results."""
import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
import zipfile
from pathlib import Path

KIT_ROOT = Path(__file__).resolve().parents[1]


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


store = load_module("qrclima_store", KIT_ROOT / "public/scripts/profile_store.py")
builder = load_module("qrclima_builder", KIT_ROOT / "tools/build_package.py")


def declared(value, source_type="user"):
    return {"value": value, "status": "declared", "source": {"type": source_type, "reference": "synthetic-test"}, "observed_at": "2026-10-05T12:00:00Z", "verified_at": None}


def patch(path, value):
    return {"changes": [{"path": path, "value": value}]}


class LocalProfileTests(unittest.TestCase):
    def setUp(self):
        self.test_root = KIT_ROOT / "private-test-runs"
        self.test_root.mkdir(exist_ok=True)
        self.directory = Path(tempfile.mkdtemp(prefix="isolated-", dir=self.test_root)).resolve()
        self.path = store.init_profile(self.directory, "prueba")

    def tearDown(self):
        # Verify the exact deletion target stays in the disposable test workspace.
        resolved = self.directory.resolve()
        if resolved == self.test_root.resolve() or not resolved.is_relative_to(self.test_root.resolve()):
            raise RuntimeError("Unexpected cleanup target")
        shutil.rmtree(resolved)

    def profile(self):
        return store.load_profile(self.path, "prueba")

    def test_initialization_has_no_inherited_identity_or_authority(self):
        profile = self.profile()
        self.assertIsNone(profile["person"]["display_name"]["value"])
        self.assertIsNone(profile["qrclima"]["account_uid"]["value"])
        self.assertEqual(profile["qrclima"]["organizations"], [])
        self.assertEqual(profile["authorizations"], [])
        self.assertEqual(profile["operation_policy"]["sales"], "draft_only")
        self.assertEqual(profile["connections"]["vm"]["used"]["status"], "unknown")

    def test_profiles_are_isolated_and_existing_profile_is_preserved(self):
        store.init_profile(self.directory, "segunda")
        store.apply_patch(self.directory, "prueba", 0, patch("/person/display_name", declared("Ejemplo")))
        other = store.load_profile(store.profile_path(self.directory, "segunda"), "segunda")
        self.assertIsNone(other["person"]["display_name"]["value"])
        with self.assertRaises(store.ProfileError):
            store.init_profile(self.directory, "prueba")
        self.assertEqual(self.profile()["person"]["display_name"]["value"], "Ejemplo")

    def test_stale_chat_cannot_overwrite_a_newer_revision(self):
        store.apply_patch(self.directory, "prueba", 0, patch("/person/language", declared("es")))
        with self.assertRaisesRegex(store.ProfileError, "revision"):
            store.apply_patch(self.directory, "prueba", 0, patch("/person/time_zone", declared("America/Mexico_City")))
        profile = self.profile()
        self.assertEqual(profile["revision"], 1)
        self.assertEqual(profile["person"]["language"]["value"], "es")
        self.assertIsNone(profile["person"]["time_zone"]["value"])

    def test_write_lock_rejects_competing_writer(self):
        lock = self.path.parent / ".write-lock"
        lock.mkdir()
        try:
            with self.assertRaisesRegex(store.ProfileError, "bloqueo"):
                store.apply_patch(self.directory, "prueba", 0, patch("/person/language", declared("es")))
        finally:
            lock.rmdir()
        self.assertEqual(self.profile()["revision"], 0)

    def test_invalid_second_change_does_not_partially_commit(self):
        changes = {"changes": [{"path": "/person/language", "value": declared("es")}, {"path": "/operation_policy/sales", "value": "confirm_each"}]}
        with self.assertRaises(store.ProfileError):
            store.apply_patch(self.directory, "prueba", 0, changes)
        self.assertIsNone(self.profile()["person"]["language"]["value"])
        self.assertEqual(self.profile()["revision"], 0)

    def test_secrets_are_rejected_without_echoing_the_value(self):
        secret = "sk-" + "FAKE1234" * 4
        with self.assertRaises(store.ProfileError) as error:
            store.apply_patch(self.directory, "prueba", 0, patch("/connections/vm/credential_reference", declared(secret)))
        self.assertNotIn(secret, str(error.exception))
        self.assertNotIn(secret, self.path.read_text(encoding="utf-8"))
        self.assertEqual(self.profile()["revision"], 0)

    def test_user_claim_cannot_be_marked_verified(self):
        value = declared("org-ficticia")
        value.update(status="verified", verified_at="2026-10-05T12:00:00Z")
        with self.assertRaises(store.ProfileError):
            store.apply_patch(self.directory, "prueba", 0, patch("/qrclima/account_uid", value))

    def test_qrclima_identity_requires_a_qrclima_evidence_type(self):
        value = declared("uid-ficticio", "local_check")
        value.update(status="verified", verified_at="2026-10-05T12:00:00Z")
        with self.assertRaises(store.ProfileError):
            store.apply_patch(self.directory, "prueba", 0, patch("/qrclima/account_uid", value))
        value["source"]["type"] = "qrclima_ui"
        store.apply_patch(self.directory, "prueba", 0, patch("/qrclima/account_uid", value))
        self.assertEqual(self.profile()["qrclima"]["account_uid"]["value"], "uid-ficticio")

    def test_unknown_and_nonfinite_data_cannot_masquerade_as_known(self):
        for value in ({**store.fact(), "value": "es"}, declared(float("nan"))):
            with self.subTest(value_type=type(value["value"]).__name__):
                with self.assertRaises(store.ProfileError):
                    store.apply_patch(self.directory, "prueba", 0, patch("/person/language", value))
        self.assertEqual(self.profile()["revision"], 0)

    def test_aliases_and_public_directory_cannot_receive_private_data(self):
        for alias in ("../escape", "con", "Case", "otra/raiz"):
            with self.subTest(alias=alias):
                with self.assertRaises(store.ProfileError):
                    store.profile_path(self.directory, alias)
        with self.assertRaises(store.ProfileError):
            store.init_profile(KIT_ROOT / "public", "prueba")

    def test_profile_symlink_cannot_escape_the_chosen_private_root(self):
        link = self.directory / "profiles" / "escape"
        outside = self.directory / "outside"
        outside.mkdir()
        try:
            link.symlink_to(outside, target_is_directory=True)
        except OSError:
            self.skipTest("This Windows session cannot create directory symlinks")
        # A target inside the root is fine; a target in its parent is not.
        store.profile_path(self.directory, "escape")
        link.unlink()
        link.symlink_to(self.test_root, target_is_directory=True)
        try:
            with self.assertRaises(store.ProfileError):
                store.profile_path(self.directory, "escape")
        finally:
            link.unlink()

    def test_configuration_cannot_enable_admin_writes_or_messages(self):
        for pointer, value in (("/connections/sdk/mode", "enabled"), ("/connections/whatsapp/mode", "enabled"), ("/authorizations", [])):
            with self.subTest(pointer=pointer):
                with self.assertRaises(store.ProfileError):
                    store.apply_patch(self.directory, "prueba", 0, patch(pointer, value))
        self.assertEqual(self.profile()["revision"], 0)

    def test_mode_change_has_separate_instruction_provenance(self):
        with self.assertRaises(store.ProfileError):
            store.set_mode(self.directory, "prueba", 0, "sales", "confirm_each", " ")
        store.set_mode(self.directory, "prueba", 0, "sales", "confirm_each", "synthetic-user-instruction")
        profile = self.profile()
        self.assertEqual(profile["policy_history"][0]["evidence_ref"], "synthetic-user-instruction")
        self.assertEqual(profile["operation_policy"]["sdk_writes"], "disabled")
        self.assertEqual(profile["authorizations"], [])

    def test_organization_switch_requires_a_registered_unique_id(self):
        with self.assertRaises(store.ProfileError):
            store.apply_patch(self.directory, "prueba", 0, patch("/qrclima/active_organization_id", "inexistente"))
        org = {"id": declared("org-ficticia"), "name": declared("Empresa ficticia"), "plan": store.fact(), "membership_role": store.fact(), "membership_active": store.fact()}
        with self.assertRaises(store.ProfileError):
            store.apply_patch(self.directory, "prueba", 0, patch("/qrclima/organizations", [org, copy.deepcopy(org)]))
        store.apply_patch(self.directory, "prueba", 0, {"changes": [{"path": "/qrclima/organizations", "value": [org]}, {"path": "/qrclima/active_organization_id", "value": "org-ficticia"}]})
        self.assertEqual(self.profile()["qrclima"]["active_organization_id"], "org-ficticia")

    def test_journal_records_revision_and_fields_without_profile_values(self):
        store.apply_patch(self.directory, "prueba", 0, patch("/person/display_name", declared("Nombre privado ficticio")))
        text = self.path.with_name("journal.jsonl").read_text(encoding="utf-8")
        self.assertNotIn("Nombre privado ficticio", text)
        events = [json.loads(line) for line in text.splitlines()]
        self.assertEqual([entry["state"] for entry in events], ["prepared", "committed", "prepared", "committed"])
        self.assertEqual(events[-1]["revision"], 1)

    def test_configuration_text_is_stored_as_data_without_execution(self):
        sentinel = self.directory / "must-not-exist.txt"
        value = declared(f"$(New-Item '{sentinel}')")
        store.apply_patch(self.directory, "prueba", 0, patch("/paths/documents_directory", value))
        self.assertFalse(sentinel.exists())
        self.assertEqual(self.profile()["paths"]["documents_directory"], value)

    def test_ambiguous_write_is_not_accepted_as_a_verified_result(self):
        operation = store.read_json(KIT_ROOT / "public/templates/operation-draft.example.json")
        store.validate_operation(operation)
        operation.update(state="outcome_unknown", organization_id="org-ficticia", actor_uid="uid-ficticio", authorization_ref="synthetic-user-instruction")
        store.validate_operation(operation)
        operation["state"] = "verified"
        with self.assertRaises(store.ProfileError):
            store.validate_operation(operation)
        operation["missing_fields"] = []
        operation["result"] = {"qrclima_record_id": "sale-ficticia", "record_type": "sale", "reread_at": "2026-10-05T12:00:00Z", "evidence_refs": ["synthetic-reread"], "linked_record_ids": []}
        store.validate_operation(operation)
        operation["authorization_ref"] = None
        with self.assertRaises(store.ProfileError):
            store.validate_operation(operation)

    def test_archive_has_only_public_contents_and_does_not_overwrite(self):
        output = self.directory / "qrclima-agent-kit.zip"
        builder.build_package(output)
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
            self.assertIn("plugin.json", names)
            self.assertEqual(len([name for name in names if name.endswith("/SKILL.md")]), 8)
            self.assertIn("LICENSE", names)
            self.assertNotIn("profile.json", names)
            self.assertFalse(any("private" in name or "__pycache__" in name for name in names))
        with self.assertRaises(FileExistsError):
            builder.build_package(output)

    def test_package_rejects_accidental_private_profile_or_secret(self):
        fixture = self.directory / "fixture"
        fixture.mkdir()
        (fixture / "profile.json").write_text("{}", encoding="utf-8")
        with self.assertRaises(builder.PackageError):
            builder.public_files(fixture)
        (fixture / "profile.json").unlink()
        (fixture / "secret.md").write_text("sk-" + "FAKE1234" * 4, encoding="utf-8")
        with self.assertRaises(builder.PackageError):
            builder.validate_public(fixture)

    def test_broken_or_escaping_skill_reference_blocks_packaging(self):
        source = KIT_ROOT / "public/skills/qrclima-configurar-perfil/SKILL.md"
        for link in ("[archivo](../../../../../private-demo/profile.json)", "[archivo](inexistente.md)"):
            with self.subTest(link=link):
                with self.assertRaises(builder.PackageError):
                    builder.validate_links(source, link, KIT_ROOT / "public")


if __name__ == "__main__":
    unittest.main()
