"""Connector boundary and private persistence tests; no real network or account."""
import copy
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import test_profile_store as helpers

client = helpers.load_module("qrclima_connector_tests", helpers.KIT_ROOT / "public/scripts/connector.py")

class ConnectorTests(unittest.TestCase):
    def setUp(self):
        self.parent = helpers.KIT_ROOT / "private-test-runs"
        self.parent.mkdir(exist_ok=True)
        self.temporary = tempfile.TemporaryDirectory(dir=self.parent)
        self.root = client.root_path(Path(self.temporary.name) / "data")
        self.state = {"uid": "synthetic_a", "organizationId": "synthetic_org_a", "owner": True,
            "profile": {"fullName": "Synthetic A"}, "organization": {"name": "Synthetic A", "plan": "pro_plus"}, "profileRevision": "1:0"}
    def tearDown(self):
        self.temporary.cleanup()
    def test_private_connection_roundtrip_and_exclusive_creation(self):
        session = {"api": "https://demo.invalid.cloudfunctions.net/qrclimaAssistantAPI", "credential": "a" * 43}
        client.save_session(self.root, session)
        self.assertEqual(client.load_session(self.root), session)
        with self.assertRaises(client.ConnectorError):
            client.save_session(self.root, session)
        if os.name == "nt":
            self.assertNotIn(session["credential"].encode(), client.session_path(self.root).read_bytes())
    def test_endpoint_refuses_cleartext_external_servers_and_redirects(self):
        for value in ["http://demo.cloudfunctions.net", "https://evil.example", "https://a.run.app/?redirect=x", "https://u:p@a.run.app/"]:
            with self.assertRaises(client.ConnectorError):
                client.endpoint(value)
        with self.assertRaises(client.ConnectorError):
            client.NoRedirect().redirect_request(None, None, 302, '', {}, 'https://other.run.app')
    def test_inicia_does_not_print_or_put_credential_in_browser_link(self):
        with patch.object(client, "request", return_value={"enabled": True, "api": "https://demo.cloudfunctions.net/qrclimaAssistantAPI"}), patch.object(client.webbrowser, "open") as opened:
            result = client.initiate(self.root)
        session = client.load_session(self.root)
        self.assertNotIn(session["credential"], json.dumps(result))
        self.assertNotIn(session["credential"], opened.call_args.args[0])
        self.assertEqual(result["code"], result["url"].split('=')[-1][:8].upper())
    def test_disabled_connector_does_not_create_credential(self):
        with patch.object(client, "request", return_value={"enabled": False}), self.assertRaises(client.ConnectorError):
            client.initiate(self.root, False)
        self.assertFalse(client.session_path(self.root).exists())
    def test_verified_identity_preserves_preferences_and_operation_policy(self):
        client.sync_identity(self.root, "principal", self.state)
        store, _ = client.stores()
        profile = store.load_profile(store.profile_path(self.root, "principal"), "principal")
        self.assertEqual(profile["qrclima"]["account_uid"]["status"], "verified")
        self.assertEqual(profile["qrclima"]["active_organization_id"], "synthetic_org_a")
        self.assertEqual(profile["operation_policy"]["sdk_writes"], "disabled")
        self.assertTrue(all(item["setting"]["value"] is None for item in profile["preferences"]))
    def test_identity_does_not_replace_another_account_profile(self):
        client.sync_identity(self.root, "principal", self.state)
        other = copy.deepcopy(self.state); other["uid"] = "synthetic_b"
        with self.assertRaises(client.ConnectorError):
            client.sync_identity(self.root, "principal", other)
    def test_context_sync_keeps_data_private_and_refuses_cross_org_page(self):
        def fake(root, body):
            if body["action"] == "status":
                return self.state
            return {"organizationId": "synthetic_org_a", "records": [{"id": "one", "name": "PRIVATE-SYNTHETIC-CACHE"}], "nextCursor": None}
        with patch.object(client, "call", side_effect=fake):
            result = client.synchronize(self.root, "principal", 1)
        self.assertEqual(len(result["categories"]), 7)
        self.assertNotIn("PRIVATE-SYNTHETIC-CACHE", json.dumps(result))
        self.assertTrue(any("PRIVATE-SYNTHETIC-CACHE" in file.read_text() for file in self.root.rglob("*.json")))
        def wrong(root, body):
            return self.state if body["action"] == "status" else {"organizationId": "synthetic_org_b", "records": [], "nextCursor": None}
        with patch.object(client, "call", side_effect=wrong), self.assertRaises(client.ConnectorError):
            client.synchronize(self.root, "principal", 1)

if __name__ == "__main__":
    unittest.main()
