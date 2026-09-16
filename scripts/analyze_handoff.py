"""Prepare attributable CRM evidence and check handoff prerequisites (stdlib only)."""

import argparse
import csv
import json
import sys
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# POC policy: notes enrich the handoff but do not fill these CRM fields.
BLOCKING_FIELDS = {
    "Executive_Sponsor__c": "Executive sponsor",
    "Implementation_Timeline__c": "Implementation timeline",
    "Success_Criteria__c": "Success criteria",
}
REVIEW_FIELDS = {"NextStep": "Next step", "Technical_Owner__c": "Technical owner"}
PLACEHOLDERS = {
    "", "tbd", "tbc", "n/a", "na", "none", "null", "unknown",
    "not confirmed", "not provided", "pending", "-", "?",
}
REQUIRED_COLUMNS = {
    "Account.csv": {"Id", "Name"},
    "Opportunity.csv": {
        "Id", "AccountId", "Name", "StageName", *BLOCKING_FIELDS, *REVIEW_FIELDS,
    },
    "Contact.csv": {"Id", "AccountId", "FirstName", "LastName", "Title"},
    "OpportunityContactRole.csv": {
        "Id", "OpportunityId", "ContactId", "Role", "IsPrimary",
    },
    "SalesNotes.csv": {"Id", "OpportunityId", "NoteDate", "Body"},
}


class InputError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def unconfirmed(value):
    return value is None or value.strip().casefold() in PLACEHOLDERS


def read_table(data_dir, filename):
    try:
        with (data_dir / filename).open(newline="", encoding="utf-8-sig") as stream:
            reader = csv.DictReader(stream, strict=True)
            headers = reader.fieldnames or []
            if len(headers) != len(set(headers)):
                raise InputError("invalid_schema", f"{filename}: duplicate column names.")
            missing = REQUIRED_COLUMNS[filename] - set(headers)
            if missing:
                raise InputError("invalid_schema", f"{filename}: missing columns: {', '.join(sorted(missing))}.")
            rows = []
            for row in reader:
                if None in row or any(value is None for value in row.values()):
                    raise InputError("malformed_csv", f"{filename}: incorrect column count near line {reader.line_num}.")
                rows.append(row)
            return rows
    except (OSError, UnicodeError, csv.Error) as error:
        raise InputError("unreadable_data", f"{filename}: {error}") from error


def index_rows(rows, filename):
    indexed = {}
    for row in rows:
        record_id = row["Id"].strip()
        if unconfirmed(record_id):
            raise InputError("invalid_id", f"{filename}: a record has no usable Id.")
        if record_id in indexed:
            raise InputError("duplicate_id", f"{filename}: duplicate Id {record_id}.")
        indexed[record_id] = row
    return indexed


def validate_relationships(tables, indexes):
    # Validate the full export, so malformed records cannot be hidden by selection.
    links = (
        ("Opportunity.csv", "AccountId", "Account.csv"),
        ("Contact.csv", "AccountId", "Account.csv"),
        ("OpportunityContactRole.csv", "OpportunityId", "Opportunity.csv"),
        ("OpportunityContactRole.csv", "ContactId", "Contact.csv"),
        ("SalesNotes.csv", "OpportunityId", "Opportunity.csv"),
    )
    for filename, field, target in links:
        for row in tables[filename]:
            if row[field].strip() not in indexes[target]:
                raise InputError("broken_reference", f"{filename} {row['Id']}: {field} {row[field]!r} does not resolve to {target}.")
    seen_roles = set()
    for role in tables["OpportunityContactRole.csv"]:
        opportunity = indexes["Opportunity.csv"][role["OpportunityId"].strip()]
        contact = indexes["Contact.csv"][role["ContactId"].strip()]
        if opportunity["AccountId"].strip() != contact["AccountId"].strip():
            raise InputError("cross_account_contact", f"OpportunityContactRole.csv {role['Id']}: contact belongs to another account.")
        pair = (role["OpportunityId"].strip(), role["ContactId"].strip())
        if pair in seen_roles:
            raise InputError("duplicate_contact_role", f"OpportunityContactRole.csv: repeated contact/opportunity pair {pair}.")
        seen_roles.add(pair)
        if role["IsPrimary"].strip().casefold() not in {"true", "false"}:
            raise InputError("invalid_boolean", f"OpportunityContactRole.csv {role['Id']}: IsPrimary must be TRUE or FALSE.")


def select_opportunity(opportunities, opportunity_id):
    if opportunity_id is not None:
        matches = [row for row in opportunities if row["Id"].strip() == opportunity_id.strip()]
        if not matches:
            raise InputError("opportunity_not_found", f"No opportunity matches {opportunity_id!r}.")
        if matches[0]["StageName"].strip().casefold() != "closed won":
            raise InputError("not_closed_won", "The selected opportunity is not Closed Won.")
        return matches[0]
    matches = [row for row in opportunities if row["StageName"].strip().casefold() == "closed won"]
    if not matches:
        raise InputError("no_closed_won", "No Closed Won opportunity found.")
    if len(matches) > 1:
        ids = ", ".join(row["Id"] for row in matches)
        raise InputError("ambiguous_opportunity", f"Multiple Closed Won opportunities: {ids}. Select one with --opportunity-id.")
    return matches[0]


def analyze(data_dir=DATA_DIR, opportunity_id=None):
    data_dir = Path(data_dir)
    tables = {name: read_table(data_dir, name) for name in REQUIRED_COLUMNS}
    indexes = {name: index_rows(rows, name) for name, rows in tables.items()}
    validate_relationships(tables, indexes)
    opportunity = select_opportunity(tables["Opportunity.csv"], opportunity_id)
    opp_id = opportunity["Id"].strip()
    account = indexes["Account.csv"][opportunity["AccountId"].strip()]
    notes = [row for row in tables["SalesNotes.csv"] if row["OpportunityId"].strip() == opp_id]
    roles = [row for row in tables["OpportunityContactRole.csv"] if row["OpportunityId"].strip() == opp_id]
    issues = []
    missing = []

    def add_issue(code, severity, message, filename, record_id, field):
        issues.append({
            "code": code, "severity": severity, "message": message,
            "source": {"file": filename, "record_id": record_id, "field": field},
        })

    for fields, severity in ((BLOCKING_FIELDS, "blocker"), (REVIEW_FIELDS, "review")):
        for field, label in fields.items():
            if unconfirmed(opportunity[field]):
                missing.append(label)
                add_issue("unconfirmed_field", severity, f"{label} is blank or a placeholder.", "Opportunity.csv", opp_id, field)

    stakeholders = []
    for role in roles:
        contact = indexes["Contact.csv"][role["ContactId"].strip()]
        stakeholders.append({
            "contact_id": contact["Id"], "role_id": role["Id"],
            "name": f"{contact['FirstName']} {contact['LastName']}".strip(),
            "title": contact["Title"], "role": role["Role"],
            "is_primary": role["IsPrimary"].strip().casefold() == "true",
            "contact": contact, "opportunity_contact_role": role,
        })
        if unconfirmed(contact["LastName"]):
            add_issue("incomplete_stakeholder", "review", "A linked stakeholder needs a last name.", "Contact.csv", contact["Id"], "LastName")
        if unconfirmed(role["Role"]):
            add_issue("incomplete_stakeholder", "review", "A linked stakeholder needs an opportunity role.", "OpportunityContactRole.csv", role["Id"], "Role")

    if not roles:
        add_issue("no_stakeholders", "review", "No opportunity contact roles are recorded.", "Opportunity.csv", opp_id, "Id")
    elif sum(person["is_primary"] for person in stakeholders) != 1:
        add_issue("primary_contact_count", "review", "Exactly one primary opportunity contact is expected for this POC.", "Opportunity.csv", opp_id, "Id")
    if not any(not unconfirmed(note["Body"]) for note in notes):
        add_issue("no_sales_notes", "review", "No substantive sales notes are recorded.", "Opportunity.csv", opp_id, "Id")

    if any(issue["severity"] == "blocker" for issue in issues):
        readiness = "Blocked"
    else:
        readiness = "Needs Review" if issues else "Ready"
    return {
        "opportunity_id": opportunity["Id"],
        "opportunity_name": opportunity["Name"],
        "handoff_readiness": readiness,
        "readiness_scope": "structured_checks_only",
        "readiness_reasons": [issue["message"] for issue in issues],
        "missing_structured_fields": missing,
        "issues": issues,
        "opportunity": opportunity,
        "account": account,
        "stakeholders": stakeholders,
        "sales_notes": notes,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", type=Path, default=DATA_DIR, help="Folder containing the five CSV exports.")
    parser.add_argument("--opportunity-id", help="Required when more than one Closed Won opportunity exists.")
    args = parser.parse_args()
    try:
        result = analyze(args.data_dir, args.opportunity_id)
    except InputError as error:
        print(json.dumps({"error": {"code": error.code, "message": str(error)}}), file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
