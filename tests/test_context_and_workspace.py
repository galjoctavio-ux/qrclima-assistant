"""Offline organization context and the extracted project workflow."""
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import test_profile_store as helpers

KIT_ROOT = helpers.KIT_ROOT
store = helpers.store
builder = helpers.builder
context = helpers.load_module("qrclima_context", KIT_ROOT / "public/scripts/context_store.py")


def verified(value):
    result = helpers.declared(value, "qrclima_ui")
    result.update(status="verified", verified_at="2026-10-05T12:00:00Z")
    return result


class ContextAndWorkspaceTests(unittest.TestCase):
    def setUp(self):
        self.test_root = KIT_ROOT / "private-test-runs"
        self.test_root.mkdir(exist_ok=True)
        self.directory = Path(tempfile.mkdtemp(prefix="workspace-", dir=self.test_root)).resolve()
        self.profile_path = store.init_profile(self.directory, "prueba")
        org = {"id": verified("org-ficticia"), "name": verified("Empresa ficticia"), "plan": store.fact(), "membership_role": store.fact(), "membership_active": store.fact()}
        store.apply_patch(self.directory, "prueba", 0, {"changes": [{"path": "/qrclima/organizations", "value": [org]}, {"path": "/qrclima/active_organization_id", "value": "org-ficticia"}, {"path": "/qrclima/account_reference", "value": verified("cuenta-ficticia@example.invalid")}]})
        self.snapshot = store.read_json(KIT_ROOT / "public/templates/context-snapshot.example.json")

    def tearDown(self):
        resolved = self.directory.resolve()
        if resolved == self.test_root.resolve() or not resolved.is_relative_to(self.test_root.resolve()):
            raise RuntimeError("Unexpected cleanup target")
        shutil.rmtree(resolved)

    def test_context_is_searchable_with_scope_source_and_date(self):
        context.put_snapshot(self.directory, "prueba", 0, self.snapshot)
        status = context.context_status(self.directory, "prueba")
        self.assertEqual(status["revision"], 1)
        self.assertEqual(status["snapshots"][0]["coverage"]["state"], "partial")
        result = context.search_context(self.directory, "prueba", "clients", "1234")
        self.assertEqual(result["matches_in_cache"], 1)
        self.assertEqual(result["records"][0]["source"]["type"], "qrclima_ui")
        self.assertIn("observed_at", result["records"][0])

    def test_context_cli_import_and_search_use_the_selected_private_root(self):
        source = self.directory / "snapshot-ficticio.json"
        source.write_text(json.dumps(self.snapshot), encoding="utf-8")
        script = KIT_ROOT / "public/scripts/context_store.py"
        result = subprocess.run([sys.executable, str(script), "put", "--root", str(self.directory), "--profile", "prueba", "--expected-revision", "0", "--file", str(source)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run([sys.executable, str(script), "search", "--root", str(self.directory), "--profile", "prueba", "--category", "clients", "--term", "1234"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["matches_in_cache"], 1)

    def test_older_profile_can_add_an_account_reference_without_inheriting_identity(self):
        old = store.load_profile(self.profile_path, "prueba")
        del old["qrclima"]["account_reference"]
        self.profile_path.write_text(json.dumps(old), encoding="utf-8")
        reloaded = store.load_profile(self.profile_path, "prueba")
        self.assertEqual(reloaded["qrclima"]["account_reference"]["status"], "unknown")
        store.apply_patch(self.directory, "prueba", reloaded["revision"], helpers.patch("/qrclima/account_reference", verified("cuenta-ficticia@example.invalid")))
        context.put_snapshot(self.directory, "prueba", 0, self.snapshot)

    def test_snapshots_cannot_cross_profile_organization_or_account(self):
        for key, value in (("profile_id", "otra"), ("organization_id", "otra-org"), ("account_reference", "otra@example.invalid")):
            with self.subTest(key=key):
                changed = copy.deepcopy(self.snapshot)
                changed[key] = value
                with self.assertRaises(context.store.ProfileError):
                    context.put_snapshot(self.directory, "prueba", 0, changed)
        self.assertEqual(context.context_status(self.directory, "prueba")["revision"], 0)

    def test_context_revision_and_snapshot_ids_cannot_be_overwritten(self):
        context.put_snapshot(self.directory, "prueba", 0, self.snapshot)
        with self.assertRaises(context.store.ProfileError):
            context.put_snapshot(self.directory, "prueba", 1, self.snapshot)
        other = copy.deepcopy(self.snapshot)
        other["snapshot_id"] = "clientes-ejemplo-2"
        with self.assertRaises(context.store.ProfileError):
            context.put_snapshot(self.directory, "prueba", 0, other)
        self.assertEqual(context.context_status(self.directory, "prueba")["revision"], 1)

    def test_all_supplied_account_identifiers_must_agree(self):
        profile = store.load_profile(self.profile_path, "prueba")
        store.apply_patch(self.directory, "prueba", profile["revision"], helpers.patch("/qrclima/account_uid", verified("uid-ficticio")))
        changed = copy.deepcopy(self.snapshot)
        changed.update(actor_uid="uid-ficticio", account_reference="otra@example.invalid")
        with self.assertRaises(context.store.ProfileError):
            context.put_snapshot(self.directory, "prueba", 0, changed)

    def test_unknown_identity_does_not_enable_an_import(self):
        profile = store.load_profile(self.profile_path, "prueba")
        store.apply_patch(self.directory, "prueba", profile["revision"], helpers.patch("/qrclima/account_reference", helpers.declared("cuenta-ficticia@example.invalid")))
        with self.assertRaises(context.store.ProfileError):
            context.put_snapshot(self.directory, "prueba", 0, self.snapshot)

    def test_complete_coverage_cannot_hide_pagination(self):
        changed = copy.deepcopy(self.snapshot)
        changed["coverage"]["state"] = "complete"
        with self.assertRaises(context.store.ProfileError):
            context.validate_snapshot(changed)
        changed["coverage"]["next_cursor"] = None
        context.validate_snapshot(changed)

    def test_secret_and_duplicate_records_do_not_enter_context(self):
        changed = copy.deepcopy(self.snapshot)
        changed["records"][0]["data"]["api_key"] = "ficticio"
        with self.assertRaises(context.store.ProfileError):
            context.put_snapshot(self.directory, "prueba", 0, changed)
        changed = copy.deepcopy(self.snapshot)
        changed["records"].append(copy.deepcopy(changed["records"][0]))
        with self.assertRaises(context.store.ProfileError):
            context.put_snapshot(self.directory, "prueba", 0, changed)

    def test_newer_record_wins_even_when_an_older_snapshot_arrives_later(self):
        context.put_snapshot(self.directory, "prueba", 0, self.snapshot)
        older = copy.deepcopy(self.snapshot)
        older.update(snapshot_id="clientes-anterior", observed_at="2026-10-04T12:00:00Z")
        older["records"][0]["data"]["name"] = "Nombre anterior ficticio"
        context.put_snapshot(self.directory, "prueba", 1, older)
        result = context.search_context(self.directory, "prueba", "clients", "1234")
        self.assertEqual(result["matches_in_cache"], 1)
        self.assertEqual(result["records"][0]["data"]["name"], "Cliente de demostracion")

    def test_organization_switch_does_not_search_the_previous_cache(self):
        context.put_snapshot(self.directory, "prueba", 0, self.snapshot)
        profile = store.load_profile(self.profile_path, "prueba")
        orgs = copy.deepcopy(profile["qrclima"]["organizations"])
        other = copy.deepcopy(orgs[0])
        other["id"] = verified("org-segunda")
        orgs.append(other)
        store.apply_patch(self.directory, "prueba", profile["revision"], {"changes": [{"path": "/qrclima/organizations", "value": orgs}, {"path": "/qrclima/active_organization_id", "value": "org-segunda"}]})
        result = context.search_context(self.directory, "prueba", "clients", "1234")
        self.assertEqual(result["organization_id"], "org-segunda")
        self.assertEqual(result["matches_in_cache"], 0)

    def test_browser_account_reference_does_not_invent_a_uid(self):
        operation = store.read_json(KIT_ROOT / "public/templates/operation-draft.example.json")
        operation.update(state="executing", organization_id="org-ficticia", actor_reference="synthetic-account-read", authorization_ref="synthetic-user-instruction", missing_fields=[])
        self.assertIsNone(operation["actor_uid"])
        store.validate_operation(operation)
        del operation["actor_reference"]
        with self.assertRaises(store.ProfileError):
            store.validate_operation(operation)

    def test_project_with_spaces_discovers_layout_and_keeps_data_outside_skills(self):
        project = self.directory / "Mi asistente elegido"
        builder.write_workspace(project)
        self.assertTrue((project / "AGENTS.md").is_file())
        self.assertTrue((project / "EMPIEZA-AQUI.html").is_file())
        self.assertEqual(len(list((project / ".agents/skills").glob("*/SKILL.md"))), 9)
        environment = os.environ.copy()
        environment.pop("QRCLIMA_AGENT_HOME", None)
        environment.pop("PLUGIN_DATA", None)
        result = subprocess.run([sys.executable, str(project / ".agents/scripts/profile_store.py"), "init", "--profile", "principal"], cwd=project, env=environment, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        private_profile = project / ".qrclima/profiles/principal/profile.json"
        self.assertTrue(private_profile.is_file())
        self.assertFalse(any(path.name == "profile.json" for path in (project / ".agents").rglob("*")))
        data = json.loads(private_profile.read_text(encoding="utf-8"))
        self.assertIsNone(data["qrclima"]["account_uid"]["value"])
        with self.assertRaises(FileExistsError):
            builder.write_workspace(project)

    def test_workspace_zip_stays_clean_after_an_actual_private_context_exists(self):
        context.put_snapshot(self.directory, "prueba", 0, self.snapshot)
        output = self.directory / "asistente.zip"
        builder.build_workspace_archive(output)
        with zipfile.ZipFile(output) as archive:
            names = archive.namelist()
            self.assertIsNone(archive.testzip())
            self.assertIn("Mi-asistente-QRclima/AGENTS.md", names)
            self.assertFalse(any("/.qrclima/" in name or "profile.json" in name or "/context/" in name for name in names))
            self.assertEqual(len([name for name in names if "/.agents/skills/" in name and name.endswith("/SKILL.md")]), 9)
            self.assertEqual(len([name for name in names if "/.claude/skills/" in name and name.endswith("/SKILL.md")]), 9)


if __name__ == "__main__":
    unittest.main()
