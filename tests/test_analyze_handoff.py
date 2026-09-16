"""Black-box checks for readiness policy, selection, integrity and evidence.

Every change to fixture data is confined to a temporary directory. Tests invoke
the public command-line interface and do not import validator implementation.
"""

import csv
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = PROJECT_ROOT / "scripts" / "analyze_handoff.py"
TABLES = (
    "Account.csv",
    "Opportunity.csv",
    "Contact.csv",
    "OpportunityContactRole.csv",
    "SalesNotes.csv",
)
BLOCKERS = {
    "Executive_Sponsor__c": "Executive sponsor",
    "Implementation_Timeline__c": "Implementation timeline",
    "Success_Criteria__c": "Success criteria",
}
PLACEHOLDERS = (
    "", "TBD", "TBC", "N/A", "NA", "none", "null", "unknown",
    "not confirmed", "not provided", "pending", "-", "?",
)


class HandoffCliTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="handoff-test-")
        self.addCleanup(self.temp.cleanup)
        self.data_dir = Path(self.temp.name) / "data"
        shutil.copytree(PROJECT_ROOT / "data", self.data_dir)
        self.original = {name: self.read_table(name) for name in TABLES}
        self.opp_id = self.original["Opportunity.csv"][0]["Id"]

    def read_table(self, name):
        with (self.data_dir / name).open(newline="", encoding="utf-8-sig") as file:
            return list(csv.DictReader(file))

    def write_table(self, name, rows, fieldnames=None):
        if fieldnames is None:
            with (self.data_dir / name).open(newline="", encoding="utf-8-sig") as file:
                fieldnames = next(csv.reader(file))
        with (self.data_dir / name).open("w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    def update_opportunity(self, **values):
        rows = self.read_table("Opportunity.csv")
        rows[0].update(values)
        self.write_table("Opportunity.csv", rows)

    def make_ready(self):
        self.update_opportunity(
            Executive_Sponsor__c="Scarlet Begonia",
            Implementation_Timeline__c="Kickoff 2026-10-05; corporate rollout first.",
            Success_Criteria__c="Publish a monthly executive security report.",
            NextStep="Schedule implementation kickoff with Casey Jones.",
            Technical_Owner__c="Casey Jones",
        )

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--data-dir", str(self.data_dir), *args],
            capture_output=True,
            text=True,
            check=False,
        )

    def success(self, *args):
        completed = self.run_cli(*args)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertFalse(completed.stderr, completed.stderr)
        result = json.loads(completed.stdout)
        self.assertEqual(result["readiness_scope"], "structured_checks_only")
        self.assertIsInstance(result["issues"], list)
        for issue in result["issues"]:
            self.assertTrue({"code", "severity", "message"}.issubset(issue))
            self.assertTrue(issue.get("source") or issue.get("sources"), issue)
        return result

    def input_error(self, *args):
        completed = self.run_cli(*args)
        self.assertEqual(completed.returncode, 2, completed.stdout + completed.stderr)
        self.assertFalse(completed.stdout, completed.stdout)
        result = json.loads(completed.stderr)
        self.assertIsInstance(result.get("error"), dict)
        for key in ("code", "message"):
            self.assertIsInstance(result["error"].get(key), str)
            self.assertTrue(result["error"][key])
        return result

    def assert_readiness(self, expected):
        result = self.success()
        self.assertEqual(result["handoff_readiness"], expected)
        if expected != "Ready":
            self.assertTrue(result["issues"])
        return result

    def test_original_fixture_is_blocked_and_preserves_record_evidence(self):
        result = self.assert_readiness("Blocked")
        self.assertEqual(result["opportunity_id"], self.opp_id)
        self.assertEqual(result["opportunity_name"], self.original["Opportunity.csv"][0]["Name"])
        self.assertCountEqual(result["missing_structured_fields"], BLOCKERS.values())
        self.assertEqual(result["opportunity"], self.original["Opportunity.csv"][0])
        self.assertEqual(result["account"], self.original["Account.csv"][0])
        self.assertCountEqual(result["sales_notes"], self.original["SalesNotes.csv"])

        contacts = {row["Id"]: row for row in self.original["Contact.csv"]}
        roles = {row["Id"]: row for row in self.original["OpportunityContactRole.csv"]}
        self.assertEqual(len(result["stakeholders"]), len(roles))
        for stakeholder in result["stakeholders"]:
            role = roles[stakeholder["role_id"]]
            contact = contacts[stakeholder["contact_id"]]
            self.assertEqual(stakeholder["contact_id"], role["ContactId"])
            self.assertEqual(stakeholder["contact"], contact)
            self.assertEqual(stakeholder["opportunity_contact_role"], role)
            self.assertEqual(stakeholder["name"], f'{contact["FirstName"]} {contact["LastName"]}')
            self.assertEqual(stakeholder["title"], contact["Title"])
            self.assertEqual(stakeholder["role"], role["Role"])
            self.assertIsInstance(stakeholder["is_primary"], bool)
            self.assertEqual(stakeholder["is_primary"], role["IsPrimary"].casefold() == "true")

    def test_complete_fixture_passes_structured_checks(self):
        self.make_ready()
        result = self.assert_readiness("Ready")
        self.assertEqual(result["missing_structured_fields"], [])

    def test_each_single_required_blocker_is_enough(self):
        for field, label in BLOCKERS.items():
            with self.subTest(field=field):
                self.make_ready()
                self.update_opportunity(**{field: ""})
                result = self.assert_readiness("Blocked")
                self.assertEqual(result["missing_structured_fields"], [label])

    def test_placeholder_values_do_not_pass_blocking_checks(self):
        for placeholder in PLACEHOLDERS:
            with self.subTest(placeholder=placeholder):
                self.make_ready()
                self.update_opportunity(Executive_Sponsor__c=f"  {placeholder.swapcase()}  ")
                result = self.assert_readiness("Blocked")
                self.assertIn("Executive sponsor", result["missing_structured_fields"])

    def test_incomplete_stakeholder_cites_the_actual_source_field(self):
        for filename, field in (("Contact.csv", "LastName"), ("OpportunityContactRole.csv", "Role")):
            with self.subTest(filename=filename, field=field):
                for name, original_rows in self.original.items():
                    self.write_table(name, original_rows)
                self.make_ready()
                rows = self.read_table(filename)
                rows[0][field] = "TBD"
                self.write_table(filename, rows)
                result = self.assert_readiness("Needs Review")
                expected = {"file": filename, "record_id": rows[0]["Id"], "field": field}
                self.assertIn(expected, [issue.get("source") for issue in result["issues"]])

    def test_next_step_gap_requires_review(self):
        self.make_ready()
        self.update_opportunity(NextStep="  TBD  ")
        result = self.assert_readiness("Needs Review")
        self.assertIn("Next step", result["missing_structured_fields"])

    def test_technical_owner_gap_requires_review(self):
        self.make_ready()
        self.update_opportunity(Technical_Owner__c="")
        self.assert_readiness("Needs Review")

    def test_no_contact_roles_requires_review(self):
        self.make_ready()
        self.write_table("OpportunityContactRole.csv", [])
        result = self.assert_readiness("Needs Review")
        self.assertEqual(result["stakeholders"], [])

    def test_no_sales_notes_requires_review(self):
        self.make_ready()
        self.write_table("SalesNotes.csv", [])
        result = self.assert_readiness("Needs Review")
        self.assertEqual(result["sales_notes"], [])

    def test_only_blank_note_bodies_require_review(self):
        self.make_ready()
        rows = self.read_table("SalesNotes.csv")
        for row in rows:
            row["Body"] = " \t "
        self.write_table("SalesNotes.csv", rows)
        self.assert_readiness("Needs Review")

    def test_zero_or_multiple_primary_roles_require_review(self):
        self.make_ready()
        for primary_count in (0, 2):
            with self.subTest(primary_count=primary_count):
                rows = self.read_table("OpportunityContactRole.csv")
                for index, row in enumerate(rows):
                    row["IsPrimary"] = "TRUE" if index < primary_count else "FALSE"
                self.write_table("OpportunityContactRole.csv", rows)
                self.assert_readiness("Needs Review")

    def test_blocker_takes_priority_over_review_gaps(self):
        self.update_opportunity(NextStep="", Technical_Owner__c="")
        self.write_table("SalesNotes.csv", [])
        self.assert_readiness("Blocked")

    def test_auto_selection_ignores_first_nonclosed_opportunity(self):
        rows = self.read_table("Opportunity.csv")
        other = dict(rows[0], Id="terrapin-open-opportunity", StageName="Prospecting")
        rows[0]["StageName"] = "  cLoSeD wOn  "
        self.write_table("Opportunity.csv", [other, *rows])
        self.assertEqual(self.success()["opportunity_id"], self.opp_id)

    def test_multiple_closed_won_records_require_selection(self):
        rows = self.read_table("Opportunity.csv")
        other = dict(rows[0], Id="franklins-tower-won", Name="Franklin's Tower rollout")
        self.write_table("Opportunity.csv", [*rows, other])
        self.input_error()
        selected = self.success("--opportunity-id", other["Id"])
        self.assertEqual(selected["opportunity_id"], other["Id"])
        self.assertEqual(selected["stakeholders"], [])
        self.assertEqual(selected["sales_notes"], [])

    def test_explicit_nonclosed_record_is_rejected(self):
        self.update_opportunity(StageName="Closed Lost")
        self.input_error("--opportunity-id", self.opp_id)

    def test_no_closed_won_records_is_selection_error(self):
        self.update_opportunity(StageName="Prospecting")
        self.input_error()

    def test_unknown_opportunity_id_is_selection_error(self):
        self.input_error("--opportunity-id", "no-such-opportunity")

    def test_empty_opportunity_export_is_selection_error(self):
        self.write_table("Opportunity.csv", [])
        self.input_error()

    def test_broken_foreign_keys_are_input_errors(self):
        cases = (
            ("Opportunity.csv", "AccountId"),
            ("Contact.csv", "AccountId"),
            ("OpportunityContactRole.csv", "OpportunityId"),
            ("OpportunityContactRole.csv", "ContactId"),
            ("SalesNotes.csv", "OpportunityId"),
        )
        for name, field in cases:
            with self.subTest(table=name, field=field):
                rows = [dict(row) for row in self.original[name]]
                rows[0][field] = "nonexistent-record"
                self.write_table(name, rows)
                self.input_error()
                self.write_table(name, self.original[name])

    def test_role_contact_must_belong_to_opportunity_account(self):
        accounts = self.read_table("Account.csv")
        accounts.append(dict(accounts[0], Id="ripple-account", Name="Terrapin Touring Co."))
        self.write_table("Account.csv", accounts)
        contacts = self.read_table("Contact.csv")
        contacts[0]["AccountId"] = "ripple-account"
        self.write_table("Contact.csv", contacts)
        self.input_error()

    def test_duplicate_ids_are_rejected_in_each_export(self):
        for name in TABLES:
            with self.subTest(table=name):
                self.write_table(name, [*self.original[name], self.original[name][0]])
                self.input_error()
                self.write_table(name, self.original[name])

    def test_empty_record_ids_are_rejected_in_each_export(self):
        for name in TABLES:
            with self.subTest(table=name):
                rows = [dict(row) for row in self.original[name]]
                rows[0]["Id"] = " "
                self.write_table(name, rows)
                self.input_error()
                self.write_table(name, self.original[name])

    def test_missing_required_headers_are_input_errors(self):
        cases = (
            ("Account.csv", "Name"),
            ("Opportunity.csv", "Executive_Sponsor__c"),
            ("Contact.csv", "Title"),
            ("OpportunityContactRole.csv", "IsPrimary"),
            ("SalesNotes.csv", "Body"),
        )
        for name, field in cases:
            with self.subTest(table=name, field=field):
                original_fields = list(self.original[name][0])
                rows = [{key: value for key, value in row.items() if key != field}
                        for row in self.original[name]]
                self.write_table(name, rows, [key for key in original_fields if key != field])
                self.input_error()
                self.write_table(name, self.original[name], original_fields)

    def test_malformed_csv_row_width_is_input_error(self):
        name = "Contact.csv"
        fields = list(self.original[name][0])
        values = [self.original[name][0][field] for field in fields]
        for malformed in (values[:-1], [*values, "extra-value"]):
            with self.subTest(column_count=len(malformed)):
                with (self.data_dir / name).open("w", newline="", encoding="utf-8") as file:
                    writer = csv.writer(file)
                    writer.writerow(fields)
                    writer.writerow(malformed)
                self.input_error()

    def test_malformed_primary_boolean_is_input_error(self):
        rows = self.read_table("OpportunityContactRole.csv")
        rows[0]["IsPrimary"] = "maybe"
        self.write_table("OpportunityContactRole.csv", rows)
        self.input_error()

    def test_unselected_records_are_still_integrity_checked(self):
        rows = self.read_table("Opportunity.csv")
        rows.append(dict(rows[0], Id="terrapin-unselected-open-deal", StageName="Prospecting",
                         AccountId="missing-account"))
        self.write_table("Opportunity.csv", rows)
        self.input_error("--opportunity-id", self.opp_id)

    def test_conflicting_crm_and_note_evidence_is_retained_for_review(self):
        self.make_ready()
        self.update_opportunity(Implementation_Timeline__c="Deployment begins in November 2026.")
        notes = self.read_table("SalesNotes.csv")
        notes[0]["Body"] = "Terrapin Touring Co. says deployment must begin in early October 2026."
        self.write_table("SalesNotes.csv", notes)
        result = self.assert_readiness("Ready")
        self.assertEqual(result["opportunity"], self.read_table("Opportunity.csv")[0])
        self.assertCountEqual(result["sales_notes"], notes)
        # Ready covers structural checks only; no semantic conflict detection is
        # claimed. Both incompatible statements must remain available to review.


if __name__ == "__main__":
    unittest.main()
