import importlib.util
import pathlib
import unittest
from unittest import mock

MODULE_PATH = pathlib.Path(__file__).with_name("publication_gate.py")
SPEC = importlib.util.spec_from_file_location("atlas_publication_gate", MODULE_PATH)
gate = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(gate)


def valid_preflight():
    return {
        "status": "FULL_RUNTIME_READY",
        "corePreviewReady": True,
        "fullRuntimeReady": True,
        "identity": {
            "schemaVersion": 3,
            "chunkSize": 128,
            "chunks": 3494,
            "mapSha256": gate.EXPECTED_MAP_SHA256,
        },
        "viewer": {"status": "CURRENT"},
        "spatial": {"status": "READY"},
        "tileInspector": {"status": "READY"},
        "creatures": {"status": "READY"},
        "environmentAnimations": {"status": "READY"},
        "verification": {"ok": True},
    }


def approval(scope):
    return {
        "schemaVersion": 1,
        "approved": True,
        "requirement": "ATLAS-PR-009",
        "scope": scope,
        "atlasVersion": 3,
        "mapSha256": gate.EXPECTED_MAP_SHA256,
        "approvedBy": "owner-reviewed",
        "approvedAt": "2026-08-17T10:30:00+02:00",
        "decision": "Recorded redistribution review decision.",
    }


class PublicationGateTests(unittest.TestCase):
    def test_private_local_full_runtime_does_not_require_redistribution_approval(self):
        report = gate.evaluate_publication(valid_preflight(), mode="private-local")
        self.assertEqual(report["status"], "READY")
        self.assertFalse(report["approval"]["required"])

    def test_authenticated_internet_mode_fails_closed_without_atlas_pr_009(self):
        report = gate.evaluate_publication(valid_preflight(), mode="internet-authenticated")
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIn("ATLAS-PR-009 Internet-facing redistribution approval is required", report["reasons"])

    def test_public_internet_mode_rejects_false_template(self):
        denied = approval("internet-public")
        denied["approved"] = False
        report = gate.evaluate_publication(valid_preflight(), mode="internet-public", approval=denied)
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIn("approval must explicitly set approved=true", report["reasons"])

    def test_internet_approval_scope_must_match_exactly(self):
        report = gate.evaluate_publication(
            valid_preflight(),
            mode="internet-public",
            approval=approval("internet-authenticated"),
        )
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIn("approval scope must exactly match internet-public", report["reasons"])

    def test_internet_mode_accepts_exact_approved_scope(self):
        report = gate.evaluate_publication(
            valid_preflight(),
            mode="internet-authenticated",
            approval=approval("internet-authenticated"),
        )
        self.assertEqual(report["status"], "READY")
        self.assertTrue(report["approval"]["valid"])

    def test_core_preview_is_not_enough_for_user_facing_distribution(self):
        preflight = valid_preflight()
        preflight["status"] = "CORE_PREVIEW_READY"
        preflight["fullRuntimeReady"] = False
        preflight["environmentAnimations"]["status"] = "MISSING"
        report = gate.evaluate_publication(preflight, mode="private-local")
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIn("deployment preflight status must be FULL_RUNTIME_READY", report["reasons"])
        self.assertIn("environment animations must be READY", report["reasons"])

    def test_wrong_world_identity_blocks_every_mode(self):
        preflight = valid_preflight()
        preflight["identity"]["mapSha256"] = "0" * 64
        report = gate.evaluate_publication(preflight, mode="private-local")
        self.assertEqual(report["status"], "BLOCKED")
        self.assertIn("Atlas map SHA-256 is not the certified canonical world", report["reasons"])

    def test_evaluate_atlas_runs_fresh_full_preflight_on_real_root(self):
        atlas = pathlib.Path("build/full-map-atlas")
        with mock.patch.object(gate, "deployment_preflight", return_value=valid_preflight()) as preflight:
            report = gate.evaluate_atlas(atlas, mode="private-local")
        preflight.assert_called_once_with(
            atlas,
            verify_chunks=True,
            require_environment_animations=True,
        )
        self.assertEqual(report["status"], "READY")


if __name__ == "__main__":
    unittest.main()
