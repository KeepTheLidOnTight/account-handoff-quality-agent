"""Black-box checks for recorded handoff history and evidence integrity.

All fixture mutations happen in isolated temporary copies. The tests exercise
the public CLI without importing the history manager's implementation.
"""

import copy
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "manage_handoffs.py"
FIXTURES = PROJECT_ROOT / "examples" / "handoffs"


class HandoffHistoryCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="handoff-history-test-")
        self.addCleanup(self.temp.cleanup)
        self.fixture_dir = Path(self.temp.name) / "handoffs"
        shutil.copytree(FIXTURES, self.fixture_dir)
        self.history_path = self.fixture_dir / "terrapin-history.json"
        self.history_path.unlink(missing_ok=True)
        self.first_path = self.fixture_dir / "01-sales-to-implementation.json"
        self.second_path = self.fixture_dir / "02-implementation-to-cs.json"
        self.first = self.read_json(self.first_path)
        self.second = self.read_json(self.second_path)

    @staticmethod
    def read_json(path):
        return json.loads(path.read_text(encoding="utf-8"))

    @staticmethod
    def write_json(path, value):
        path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")

    def run_cli(self, operation, event_path=None):
        command = [
            sys.executable, "-B", str(SCRIPT), operation,
            "--history", str(self.history_path),
        ]
        if event_path is not None:
            command += ["--event", str(event_path)]
        return subprocess.run(
            command, capture_output=True, text=True, check=False,
            cwd=self.temp.name,
        )

    def success(self, operation="add", event_path=None):
        if operation == "add" and event_path is None:
            event_path = self.first_path
        completed = self.run_cli(operation, event_path)
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertFalse(completed.stderr, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertIsInstance(result, dict)
        return result

    def input_error(self, event_path=None, operation="add"):
        if operation == "add" and event_path is None:
            event_path = self.first_path
        before = self.history_path.read_bytes() if self.history_path.exists() else None
        completed = self.run_cli(operation, event_path)
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        self.assertFalse(completed.stdout, completed.stdout)
        result = json.loads(completed.stderr)
        self.assertIsInstance(result.get("error"), dict)
        for key in ("code", "message"):
            self.assertIsInstance(result["error"].get(key), str)
            self.assertTrue(result["error"][key])
        after = self.history_path.read_bytes() if self.history_path.exists() else None
        self.assertEqual(after, before, "Rejected input must not alter history")
        return result

    def ownership_source(self, event, event_path):
        """Find the fixture's actual event record instead of assuming an ID."""
        for source in event["sources"]:
            path = event_path.parent / source["location"]
            if source["id"] in event["source_ids"] and path.suffix == ".json":
                record = self.read_json(path)
                if record.get("handoff_id") == event["handoff_id"]:
                    return source, path, record
        self.fail("Fixture must cite an ownership record for its event")

    def change_bound_event(self, event_path, changes, ownership_only=False):
        """Change metadata and its evidence together to reach sequence checks."""
        event = self.read_json(event_path)
        source, source_path, record = self.ownership_source(event, event_path)
        event.update(copy.deepcopy(changes))
        record.update(copy.deepcopy(changes))
        self.write_json(source_path, record)
        source.pop("sha256", None)
        source.pop("snapshot", None)
        if ownership_only:
            event["sources"] = [source]
            event["source_ids"] = [source["id"]]
            event["actions"] = []
            for section in ("goals", "stakeholders", "commitments", "gaps", "risks"):
                event["assessment"][section] = []
        self.write_json(event_path, event)
        return event

    def test_first_event_freezes_sources_and_sets_current_owner(self):
        result = self.success()
        self.assertEqual(result["account"]["id"], self.first["account_id"])
        self.assertEqual([event["handoff_id"] for event in result["events"]],
                         [self.first["handoff_id"]])
        self.assertEqual(result["current"]["owner"], self.first["to"])
        self.assertEqual(result["current"]["as_of"], self.first["effective_at"])
        self.assertEqual(result["current"]["readiness"], self.first["assessment"]["readiness"])
        supplied = {source["id"]: source for source in self.first["sources"]}
        for frozen in result["events"][0]["sources"]:
            original = supplied[frozen["id"]]
            source_path = self.first_path.parent / original["location"]
            self.assertEqual(frozen["sha256"], hashlib.sha256(source_path.read_bytes()).hexdigest())
            self.assertEqual(frozen["record_id"], original["record_id"])
            self.assertEqual(frozen["account_id"], self.first["account_id"])
            if source_path.suffix == ".json":
                expected = self.read_json(source_path)
            else:
                with source_path.open(newline="", encoding="utf-8-sig") as stream:
                    expected = next(row for row in csv.DictReader(stream)
                                    if row["Id"] == original["record_id"])
            self.assertEqual(frozen["snapshot"], expected)

    def test_identical_event_retry_is_byte_identical(self):
        first_result = self.success()
        first_bytes = self.history_path.read_bytes()
        repeated_result = self.success()
        self.assertEqual(self.history_path.read_bytes(), first_bytes)
        self.assertEqual(repeated_result, first_result)

    def test_view_reproduces_current_history_without_writing(self):
        added = self.success()
        before = self.history_path.read_bytes()
        viewed = self.success("view")
        self.assertEqual(viewed, added)
        self.assertEqual(self.history_path.read_bytes(), before)

    def test_changed_existing_event_is_rejected_without_rewriting_history(self):
        self.success()
        self.change_bound_event(self.first_path, {"reason": "A corrected Terrapin ownership explanation."})
        self.input_error()

    def test_second_event_carries_forward_omitted_open_actions(self):
        first_result = self.success()
        prior_open = first_result["current"]["open_actions"]
        self.assertTrue(prior_open, "Sample first event should demonstrate open actions")
        event = copy.deepcopy(self.second)
        event["actions"] = []
        self.write_json(self.second_path, event)
        result = self.success(event_path=self.second_path)
        self.assertEqual([item["handoff_id"] for item in result["events"]],
                         [self.first["handoff_id"], self.second["handoff_id"]])
        self.assertEqual(result["events"][0], first_result["events"][0])
        self.assertEqual(result["current"]["owner"], self.second["to"])
        self.assertEqual(result["current"]["open_actions"], prior_open)
        self.assertTrue(all(action["event_id"] == self.first["handoff_id"]
                            for action in result["current"]["open_actions"]))

    def test_explicit_action_closure_removes_only_that_action(self):
        first_result = self.success()
        prior_open = first_result["current"]["open_actions"]
        self.assertTrue(prior_open)
        action = {key: value for key, value in prior_open[0].items()
                  if key not in {"event_id", "updated_event_id", "sources"}}
        action.update(status="done", source_ids=self.second["source_ids"])
        event = copy.deepcopy(self.second)
        event["actions"] = [action]
        self.write_json(self.second_path, event)
        result = self.success(event_path=self.second_path)
        self.assertCountEqual([item["id"] for item in result["current"]["open_actions"]],
                              [item["id"] for item in prior_open[1:]])
        self.assertEqual(result["events"][0], first_result["events"][0])
        self.assertEqual(result["events"][1]["actions"][0]["status"], "done")

    def test_mixing_account_events_is_rejected(self):
        self.success()
        self.change_bound_event(self.second_path, {"account_id": "account-scarlet-begonia"},
                                ownership_only=True)
        self.input_error(self.second_path)

    def test_equal_effective_time_is_rejected(self):
        self.success()
        self.change_bound_event(self.second_path, {"effective_at": self.first["effective_at"]})
        self.input_error(self.second_path)

    def test_earlier_effective_time_is_rejected(self):
        self.success()
        self.change_bound_event(self.second_path, {"effective_at": "2000-01-01T00:00:00Z"})
        self.input_error(self.second_path)

    def test_unchanged_owner_and_team_is_rejected(self):
        self.change_bound_event(self.first_path, {"to": self.first["from"]})
        self.input_error()

    def test_owner_continuity_mismatch_is_rejected(self):
        self.success()
        new_from = dict(self.second["from"], owner_id="employee-casey-jones")
        self.change_bound_event(self.second_path, {"from": new_from})
        self.input_error(self.second_path)

    def test_team_only_change_is_a_valid_handoff(self):
        new_to = dict(self.first["from"], team="Terrapin specialist team")
        self.change_bound_event(self.first_path, {"to": new_to})
        result = self.success()
        self.assertEqual(result["current"]["owner"], new_to)

    def test_view_uses_frozen_evidence_when_source_file_is_gone(self):
        expected = self.success()
        _, source_path, _ = self.ownership_source(self.first, self.first_path)
        source_path.unlink()
        self.assertEqual(self.success("view"), expected)

    def test_unknown_cited_source_id_is_rejected(self):
        event = copy.deepcopy(self.first)
        event["source_ids"].append("missing-source-scarlet-begonia")
        self.write_json(self.first_path, event)
        self.input_error()

    def test_missing_ownership_evidence_is_rejected(self):
        event = copy.deepcopy(self.first)
        event["source_ids"] = []
        self.write_json(self.first_path, event)
        self.input_error()

    def test_missing_source_file_is_rejected(self):
        event = copy.deepcopy(self.first)
        event["sources"][0]["location"] = "missing-terrapin-evidence.json"
        self.write_json(self.first_path, event)
        self.input_error()

    def test_malformed_source_reference_is_rejected(self):
        event = copy.deepcopy(self.first)
        del event["sources"][0]["record_id"]
        self.write_json(self.first_path, event)
        self.input_error()

    def test_cross_account_snapshot_is_rejected(self):
        _, source_path, record = self.ownership_source(self.first, self.first_path)
        record["account_id"] = "account-other-terrapin"
        self.write_json(source_path, record)
        self.input_error()

    def test_unmatched_ownership_claim_is_rejected(self):
        event = copy.deepcopy(self.first)
        event["reason"] = "A claim absent from the cited ownership record."
        self.write_json(self.first_path, event)
        self.input_error()

    def test_invalid_event_timestamp_is_rejected(self):
        self.change_bound_event(self.first_path, {"effective_at": "not-a-date"})
        self.input_error()

    def test_timezone_free_event_timestamp_is_rejected(self):
        self.change_bound_event(self.first_path, {"effective_at": "2026-01-01T12:00:00"})
        self.input_error()

    def test_invalid_source_date_is_rejected(self):
        event = copy.deepcopy(self.first)
        event["sources"][0]["date"] = "2026-02-30"
        self.write_json(self.first_path, event)
        self.input_error()

    def test_internal_transfer_rejects_a_sales_baseline(self):
        self.success()
        event = copy.deepcopy(self.second)
        event["assessment"]["baseline"] = "Ready"
        self.write_json(self.second_path, event)
        self.input_error(self.second_path)

    def test_sales_baseline_requires_a_known_rating(self):
        for baseline in (None, "", "Unknown", "Ready (structured checks)"):
            with self.subTest(baseline=baseline):
                event = copy.deepcopy(self.first)
                event["assessment"]["baseline"] = baseline
                self.write_json(self.first_path, event)
                self.input_error()

    def test_final_sales_rating_cannot_improve_on_baseline(self):
        for baseline, final in (("Blocked", "Ready"), ("Blocked", "Needs Review"),
                                ("Needs Review", "Ready")):
            with self.subTest(baseline=baseline, final=final):
                event = copy.deepcopy(self.first)
                event["assessment"].update(baseline=baseline, readiness=final)
                self.write_json(self.first_path, event)
                self.input_error()

    def test_final_sales_rating_may_be_more_cautious_than_baseline(self):
        event = copy.deepcopy(self.first)
        event["assessment"].update(baseline="Ready", readiness="Needs Review")
        self.write_json(self.first_path, event)
        result = self.success()
        self.assertEqual(result["current"]["readiness"], "Needs Review")
        self.assertEqual(result["events"][0]["assessment"]["baseline"], "Ready")

    def test_future_evidence_cannot_support_an_earlier_assessment(self):
        for evidence_date in ("2026-09-17", "2026-09-16T10:01:00-05:00"):
            with self.subTest(date=evidence_date):
                event = copy.deepcopy(self.first)
                event["sources"][0]["date"] = evidence_date
                self.write_json(self.first_path, event)
                self.input_error()

    def test_malformed_event_json_is_rejected(self):
        self.first_path.write_text('{"handoff_id":', encoding="utf-8")
        self.input_error()

    def test_missing_event_file_is_rejected(self):
        self.first_path.unlink()
        self.input_error()


if __name__ == "__main__":
    unittest.main()
