"""Record explicit handoff events and view account history; no CRM writes."""

import argparse
import copy
import csv
from datetime import date, datetime, timezone
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import tempfile


class HistoryError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def require(condition, code, message):
    if not condition:
        raise HistoryError(code, message)


def nonblank(value):
    return isinstance(value, str) and bool(value.strip())


def text_field(obj, key):
    require(isinstance(obj, dict) and nonblank(obj.get(key)), "invalid_event", f"{key} must be nonblank text.")
    return obj[key]


def timestamp(value, label):
    require(nonblank(value), "invalid_date", f"{label} requires an ISO timestamp with timezone.")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise HistoryError("invalid_date", f"Invalid {label}: {value!r}.") from error
    require(parsed.tzinfo is not None, "invalid_date", f"{label} requires an explicit timezone.")
    return parsed.astimezone(timezone.utc)


def source_date(value):
    require(nonblank(value), "invalid_date", "Evidence dates must be explicit.")
    if len(value) == 10:
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    return timestamp(value, "source date")


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise HistoryError("unreadable_json", f"Cannot read {path}: {error}") from error


def csv_records(content, label):
    try:
        reader = csv.DictReader(io.StringIO(content.decode("utf-8-sig")), strict=True)
        headers = reader.fieldnames or []
        require("Id" in headers and len(headers) == len(set(headers)), "invalid_source", f"{label}: missing Id or duplicate headers.")
        result = {}
        for row in reader:
            require(None not in row and all(v is not None for v in row.values()), "invalid_source", f"{label}: malformed CSV row.")
            record_id = row["Id"]
            require(nonblank(record_id) and record_id not in result, "invalid_source", f"{label}: empty or duplicate Id.")
            result[record_id] = row
        return result
    except (UnicodeError, csv.Error) as error:
        raise HistoryError("invalid_source", f"{label}: {error}") from error


def load_csv(path):
    try:
        return csv_records(path.read_bytes(), str(path))
    except OSError as error:
        raise HistoryError("missing_source", f"Cannot read evidence {path}: {error}") from error


def resolve_source(source, event, event_dir, history_dir):
    require(isinstance(source, dict), "invalid_source", "Each source must be an object.")
    for field in ("id", "kind", "location", "record_id", "date", "excerpt"):
        text_field(source, field)
    source_date(source["date"])
    path = (event_dir / source["location"]).resolve()
    try:
        content = path.read_bytes()
    except OSError as error:
        raise HistoryError("missing_source", f"Cannot read evidence {path}: {error}") from error
    record_id = source["record_id"]
    if path.suffix.lower() == ".csv":
        records = csv_records(content, str(path))
        require(record_id in records, "unknown_record", f"Evidence record {record_id} is absent from {path.name}.")
        record = records[record_id]
        if path.name == "Account.csv":
            account_id = record["Id"]
        elif "AccountId" in record:
            account_id = record["AccountId"]
        elif "OpportunityId" in record:
            opportunities = load_csv(path.parent / "Opportunity.csv")
            opportunity = opportunities.get(record["OpportunityId"])
            require(opportunity is not None, "broken_source_reference", f"{path.name}: opportunity reference does not resolve.")
            account_id = opportunity.get("AccountId")
            if "ContactId" in record:
                contact = load_csv(path.parent / "Contact.csv").get(record["ContactId"])
                require(contact is not None and contact.get("AccountId") == account_id, "cross_account_source", "Evidence role has an invalid or cross-account contact.")
        else:
            raise HistoryError("invalid_source", f"Cannot identify the account for {path.name}.")
    elif path.suffix.lower() == ".json":
        try:
            record = json.loads(content.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as error:
            raise HistoryError("invalid_source", f"{path.name}: malformed JSON.") from error
        require(isinstance(record, dict) and record.get("id") == record_id, "unknown_record", f"JSON evidence must identify record {record_id}.")
        account_id = record.get("account_id")
    else:
        raise HistoryError("invalid_source", "Evidence must be a CSV export or a JSON record.")
    require(account_id == event["account_id"], "cross_account_source", f"Evidence {source['id']} belongs to another or unknown account.")
    digest = hashlib.sha256(content).hexdigest()
    require(source.get("sha256", digest) == digest, "changed_source", "Evidence file differs from its supplied digest.")
    require(source.get("snapshot", record) == record, "changed_source", "Evidence record differs from its supplied snapshot.")
    normalized = {key: source[key] for key in ("id", "kind", "location", "record_id", "date", "excerpt")}
    normalized.update(location=os.path.relpath(path, history_dir), account_id=account_id,
                      sha256=digest, snapshot=record)
    return normalized


def citations(value, known, label):
    require(isinstance(value, list) and value and all(nonblank(item) for item in value), "invalid_citation", f"{label} needs a nonempty source_ids list.")
    require(len(value) == len(set(value)) and set(value) <= known, "unknown_citation", f"{label} contains duplicate or unknown source IDs.")


def validate_event(event, frozen=False, event_dir=None, history_dir=None):
    require(isinstance(event, dict), "invalid_event", "Event must be an object.")
    event = copy.deepcopy(event)
    for key in ("handoff_id", "account_id", "account_name", "reason"):
        text_field(event, key)
    effective = timestamp(event.get("effective_at"), "effective_at")
    recorded = timestamp(event.get("recorded_at"), "recorded_at")
    require(recorded >= effective, "invalid_date", "An occurred handoff cannot be recorded before its effective time.")
    require(event.get("handoff_type") in {"sales_to_implementation", "internal_transfer"}, "invalid_event", "Unknown handoff_type.")
    for side in ("from", "to"):
        for field in ("owner_id", "owner_name", "team"):
            text_field(event.get(side), field)
    require((event["from"]["owner_id"], event["from"]["team"]) != (event["to"]["owner_id"], event["to"]["team"]), "unchanged_ownership", "A handoff must change its internal owner or team.")
    require(isinstance(event.get("sources"), list) and event["sources"], "invalid_source", "Sources are required.")
    normalized = []
    for source in event["sources"]:
        if not frozen:
            normalized.append(resolve_source(source, event, event_dir, history_dir))
            continue
        for field in ("id", "kind", "location", "record_id", "date", "excerpt", "sha256", "account_id"):
            text_field(source, field)
        source_date(source["date"])
        require(source["account_id"] == event["account_id"], "cross_account_source", "Frozen evidence belongs to another account.")
        snapshot = source.get("snapshot")
        require(isinstance(snapshot, dict) and snapshot.get("Id", snapshot.get("id")) == source["record_id"], "invalid_source", "Frozen source record does not match its ID.")
        require(len(source["sha256"]) == 64 and all(ch in "0123456789abcdef" for ch in source["sha256"]), "invalid_source", "Frozen source digest is malformed.")
        normalized.append(source)
    event["sources"] = normalized
    recorded_local_date = datetime.fromisoformat(event["recorded_at"].replace("Z", "+00:00")).date()
    for source in normalized:
        evidence_date = source_date(source["date"])
        not_future = evidence_date <= recorded if isinstance(evidence_date, datetime) else evidence_date <= recorded_local_date
        require(not_future, "future_evidence", "Evidence cannot be dated after the handoff assessment was recorded.")
    known = {source["id"] for source in normalized}
    require(len(known) == len(normalized), "invalid_source", "Source IDs must be unique within an event.")
    citations(event.get("source_ids"), known, "Event ownership/date/reason")
    event_records = [source["snapshot"] for source in normalized if source["id"] in event["source_ids"]]
    ownership_keys = ("handoff_id", "account_id", "effective_at", "handoff_type", "from", "to", "reason")
    require(any(all(record.get(key) == event[key] for key in ownership_keys) for record in event_records), "unsupported_event", "An event citation must point to an ownership record matching its ID, account, date, type, from/to and reason.")
    assessment = event.get("assessment")
    require(isinstance(assessment, dict) and assessment.get("readiness") in {"Ready", "Needs Review", "Blocked"}, "invalid_assessment", "Assessment readiness is required.")
    require("baseline" in assessment and (assessment["baseline"] is None or nonblank(assessment["baseline"])), "invalid_assessment", "baseline must be text or null.")
    if event["handoff_type"] == "internal_transfer":
        require(assessment["baseline"] is None, "invalid_baseline", "Internal transfers do not use the sales baseline; baseline must be null.")
    else:
        severity = {"Ready": 0, "Needs Review": 1, "Blocked": 2}
        require(assessment["baseline"] in severity, "invalid_baseline", "A sales handoff baseline must be Ready, Needs Review or Blocked.")
        require(severity[assessment["readiness"]] >= severity[assessment["baseline"]], "baseline_override", "Final readiness cannot improve on the structured sales baseline.")
    text_field(assessment, "summary")
    for section in ("goals", "stakeholders", "commitments", "gaps", "risks"):
        require(isinstance(assessment.get(section), list), "invalid_assessment", f"{section} must be a list.")
        for statement in assessment[section]:
            text_field(statement, "text")
            citations(statement.get("source_ids"), known, section)
    require(isinstance(event.get("actions"), list), "invalid_action", "actions must be a list.")
    action_ids = set()
    for action in event["actions"]:
        for key in ("id", "text", "owner"):
            text_field(action, key)
        require(action["id"] not in action_ids, "invalid_action", "Action IDs must be unique within an event.")
        action_ids.add(action["id"])
        require(action.get("status") in {"open", "done", "cancelled"}, "invalid_action", "Action status must be open, done or cancelled.")
        require("due" in action, "invalid_action", "Action due date is required; use null if not confirmed.")
        if action["due"] is not None:
            try:
                date.fromisoformat(action["due"])
            except (TypeError, ValueError) as error:
                raise HistoryError("invalid_action", "Action due must be YYYY-MM-DD or null.") from error
        citations(action.get("source_ids"), known, f"Action {action['id']}")
    return event


def validate_sequence(history):
    require(isinstance(history, dict) and history.get("schema_version") == 1, "invalid_history", "Unsupported history schema.")
    for field in ("id", "name"):
        text_field(history.get("account"), field)
    require(isinstance(history.get("events"), list) and history["events"], "invalid_history", "History must contain at least one event.")
    seen = set()
    previous = None
    for event in history["events"]:
        require(event["account_id"] == history["account"]["id"] and event["account_name"] == history["account"]["name"], "account_mismatch", "One history can contain only one account identity.")
        require(event["handoff_id"] not in seen, "duplicate_event", "History contains duplicate event IDs.")
        seen.add(event["handoff_id"])
        if previous:
            require(timestamp(event["effective_at"], "effective_at") > timestamp(previous["effective_at"], "effective_at"), "chronology", "New effective_at must be later than the last handoff.")
            require((event["from"]["owner_id"], event["from"]["team"]) == (previous["to"]["owner_id"], previous["to"]["team"]), "ownership_discontinuity", "Incoming owner/team must match the previous receiving owner/team.")
        previous = event


def load_history(path):
    history = read_json(path)
    require(isinstance(history, dict) and isinstance(history.get("events"), list), "invalid_history", "Malformed history.")
    history["events"] = [validate_event(event, frozen=True) for event in history["events"]]
    validate_sequence(history)
    return history


def with_current(history):
    result = copy.deepcopy(history)
    actions = {}
    for event in history["events"]:
        sources = {source["id"]: source for source in event["sources"]}
        for action in event["actions"]:
            origin = actions.get(action["id"], {}).get("event_id", event["handoff_id"])
            actions[action["id"]] = dict(copy.deepcopy(action), event_id=origin,
                updated_event_id=event["handoff_id"],
                sources=[copy.deepcopy(sources[source_id]) for source_id in action["source_ids"]])
    last = history["events"][-1]
    result["current"] = {
        "owner": copy.deepcopy(last["to"]), "as_of": last["effective_at"],
        "readiness": last["assessment"]["readiness"],
        "open_actions": [action for action in actions.values() if action["status"] == "open"],
        "latest_handoff_id": last["handoff_id"],
    }
    return result


def atomic_write(path, history):
    pending = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            pending = Path(stream.name)
            json.dump(history, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(pending, path)
    finally:
        if pending is not None and pending.exists():
            pending.unlink()


def add(history_path, event_path):
    event = validate_event(read_json(event_path), event_dir=event_path.parent, history_dir=history_path.parent)
    require(history_path.parent.is_dir(), "missing_directory", "History parent directory must already exist.")
    # This local POC supports one writer per history. Atomic replacement avoids
    # partial files; it does not coordinate simultaneous writers.
    history = load_history(history_path) if history_path.exists() else {
        "schema_version": 1, "account": {"id": event["account_id"], "name": event["account_name"]}, "events": [],
    }
    for prior in history["events"]:
        if prior["handoff_id"] == event["handoff_id"]:
            require(prior == event, "event_conflict", "This event ID already exists with different content; prior events are immutable.")
            return with_current(history)
    history["events"].append(event)
    validate_sequence(history)
    atomic_write(history_path, history)
    return with_current(history)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    add_parser = commands.add_parser("add", help="Record one explicitly supplied, occurred handoff.")
    add_parser.add_argument("--history", type=Path, required=True)
    add_parser.add_argument("--event", type=Path, required=True)
    view_parser = commands.add_parser("view", help="Read frozen events and derive current owner/actions.")
    view_parser.add_argument("--history", type=Path, required=True)
    args = parser.parse_args()
    try:
        history_path = args.history.resolve()
        result = add(history_path, args.event.resolve()) if args.command == "add" else with_current(load_history(history_path))
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (HistoryError, OSError) as error:
        print(json.dumps({"error": {"code": getattr(error, "code", "io_error"), "message": str(error)}}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
