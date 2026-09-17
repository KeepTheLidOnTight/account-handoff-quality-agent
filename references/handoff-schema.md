# Handoff history contract

Baton records explicitly supplied ownership changes and rebuilds an account deck from their frozen assessments. It does not detect CRM changes, schedule transfers, or update account ownership in another system. Each event describes an already-occurred change; its readiness rating records outstanding handoff quality concerns, not whether that past change was allowed.

The supplied example is entirely fictional. Its September 16, 2026 event uses the existing ready-scenario Salesforce-style CSV facts. Its December 1, 2026 event and internal employees are invented evidence for demonstrating a later transfer. Customer contacts Scarlet Begonia, Casey Jones and Jack Straw are separate from internal owners Samson Delilah, Ruben Cherise and Althea Cassidy.

## Commands and runtimes

The history helper and sales validator use Python 3.9+ and its standard library. They run independently of the presentation runtime.

```sh
python3 scripts/manage_handoffs.py add \
  --history examples/handoffs/terrapin-history.json \
  --event examples/handoffs/01-sales-to-implementation.json

python3 scripts/manage_handoffs.py add \
  --history examples/handoffs/terrapin-history.json \
  --event examples/handoffs/02-implementation-to-cs.json

python3 scripts/manage_handoffs.py view \
  --history examples/handoffs/terrapin-history.json
```

The example history already contains both events. Running those additions again with unchanged evidence is a no-op. Use a different history filename to demonstrate building it from scratch. The history parent folder must already exist.

Successful `add` and `view` commands return the same normalized view shape on stdout and exit with code 0. Invalid event, evidence or history inputs return JSON of the form `{"error":{"code":"...","message":"..."}}` on stderr and exit with code 2. Command-line usage errors use the standard argument parser's usage output.

`scripts/build_deck.mjs` consumes the `view` command's JSON. Creating a PowerPoint additionally requires Node.js and the configured `@oai/artifact-tool` runtime; passing the Python checks does not establish that the presentation runtime is installed. See the project README for rendering setup.

## Stored history

One history file contains one account and an ordered list of immutable events:

```json
{
  "schema_version": 1,
  "account": {"id": "0015g00002ABCDeAAH", "name": "Terrapin Touring Co."},
  "events": ["event objects described below"]
}
```

`account.id` and `account.name` must match every event. Event IDs are unique. Effective timestamps must strictly increase; the next event's `from.owner_id` and `from.team` must match the previous event's `to.owner_id` and `to.team`. Display names are descriptive; owner IDs and team names determine continuity. Changing only the team is valid. An event that changes neither the internal owner nor the team is rejected.

There is one writer per history file in this local POC. The helper validates before replacing the history with a complete temporary file, flushes it, and uses atomic replacement. This prevents partial JSON files; it does **not** coordinate simultaneous writers. There is no platform-specific locking dependency.

An identical event-ID retry returns the existing history without rewriting it. Different content under an existing ID is rejected, including changed source snapshots. Earlier handoffs cannot be inserted retroactively. Corrections and account renames need a separately reviewed migration; this POC has no overwrite or revision command. Do not invent a new ownership change to conceal a correction.

## Event fields

| Field | Required value |
|---|---|
| `handoff_id` | Stable, nonblank event identifier. |
| `account_id`, `account_name` | Identity of the account that owns the history. |
| `effective_at` | ISO timestamp including timezone, when ownership changed. |
| `recorded_at` | ISO timestamp including timezone, no earlier than `effective_at`. |
| `handoff_type` | `sales_to_implementation` or `internal_transfer`. |
| `from`, `to` | Objects with nonblank `owner_id`, `owner_name` and `team`. |
| `reason` | Explanation of this ownership/team change. |
| `source_ids` | Nonempty list of IDs from this event's `sources`, supporting ownership, date and reason. |
| `assessment` | Assessment object below. |
| `actions` | Action changes recorded at this event, possibly an empty list. |
| `sources` | Nonempty list of attributable evidence objects. |

An event citation must reference a JSON ownership record whose `handoff_id`, `account_id`, `effective_at`, `handoff_type`, `from`, `to` and `reason` exactly match the event. The source record also has its own `id`. This binds the transfer metadata to an explicit mock or supplied record. It does not authenticate a live CRM transaction.

## Assessment and readiness

```json
{
  "readiness": "Needs Review",
  "baseline": null,
  "summary": "Concise assessment of this transfer.",
  "goals": [{"text": "A supported customer goal.", "source_ids": ["source-id"]}],
  "stakeholders": [],
  "commitments": [],
  "gaps": [],
  "risks": []
}
```

The five section lists are required and may be empty. Each listed statement has nonblank `text` and at least one valid `source_ids` reference. `summary` is required. Section text and the summary are supplied by the assessment workflow; this helper does not generate prose or determine whether it is semantically supported.

`readiness` is exactly `Ready`, `Needs Review` or `Blocked`.

- For `sales_to_implementation`, `baseline` must be one of those same three ratings, copied from the structured sales validator. The final rating may be more cautious but cannot be less cautious: `Ready` < `Needs Review` < `Blocked`. The helper checks this relationship; the assessment workflow is responsible for supplying the actual validator result.
- For `internal_transfer`, `baseline` must be `null`. The original sales-only gates do not determine readiness for a later owner or team change. The assessment workflow reviews receiving ownership, open obligations, customer context and transition-specific gaps.

Neither a structured `Ready` result nor successful event validation proves that targets were achieved. In the example, six reporting venues and 96% of priority alerts arriving within 15 minutes do not establish achievement of the separate December 18 investigation-time target.

## Actions and carry-forward

```json
{
  "id": "terrapin-investigation-target",
  "text": "Verify mean investigation time against the agreed target.",
  "owner": "Ruben Cherise (Implementation)",
  "due": "2026-12-18",
  "status": "open",
  "source_ids": ["confirmation", "ownership-september"]
}
```

IDs are stable across events and unique within each event. `text` and `owner` are nonblank. `due` is a date in `YYYY-MM-DD` format or `null` for a date that is not confirmed. Status is `open`, `done` or `cancelled`. Every new action and every update requires valid citations in the event recording it.

Event actions are updates, not a replacement task list. Omitted earlier open actions remain open, with their existing owner, due date and evidence. A later entry with the same ID replaces the current action state; `done` or `cancelled` removes it from current open actions while preserving both historical entries. An ownership transfer does not silently reassign outstanding tasks.

In the sample, the December event closes kickoff, identity notice and rollout verification. It omits the still-open investigation target, so that target carries forward under Ruben. Training and QBR follow-ups are new tasks for Althea, with unconfirmed due dates.

## Evidence sources and snapshots

Event input sources require these fields:

```json
{
  "id": "ownership-september",
  "kind": "Fictional internal handoff record",
  "location": "snapshots/2026-09-16-ownership.json",
  "record_id": "mock-ownership-2026-09-16",
  "date": "2026-09-16",
  "excerpt": "A readable excerpt of the ownership evidence."
}
```

Source IDs are unique within their event, and every citation must resolve within that event. `kind` is descriptive text. Evidence dates must be valid dates or timestamps with timezones, and cannot be later than `recorded_at`. Date-only evidence is compared with the recorded timestamp's local calendar date; timestamp evidence is compared as an absolute instant. This is a check of the supplied dates, not independent authentication of document chronology.

On `add`, locations resolve relative to the input event file. The helper accepts:

- Salesforce-style CSV rows identified by `Id`. Account membership is checked through `AccountId`, or through a sibling `Opportunity.csv` for opportunity-linked rows. Contact-role sources also verify their contact through sibling `Contact.csv`.
- A single JSON record whose `id` matches `record_id` and whose `account_id` matches the event. The sample ownership records use this format.

Missing files, unknown records, malformed CSV rows, unresolved or cross-account joins, duplicate source IDs and unknown citations fail before the history is written. The helper does not validate arbitrary document formats.

Normalized sources keep the original fields and add:

| Field | Meaning |
|---|---|
| `account_id` | Account resolved from the source record or its relationships. |
| `sha256` | SHA-256 of the complete source-file bytes at ingestion. |
| `snapshot` | Full extracted CSV row or JSON record as an object. |

`location` is rewritten relative to the history folder. This makes the supplied example portable with its snapshots. The file hash is provenance for the ingested file, not a signature or a tamper-proof history mechanism.

`view` uses embedded snapshots rather than reopening external sources. Historical context remains available if original source files move or change. `add` rereads supplied source files; a changed retry is rejected. Excerpts are supplied prose and are not automatically checked for exact quotations or semantic entailment. Source presence is not a substitute for the assessment's evidence review.

## Renderer view

`view` returns the stored history plus a derived `current` object:

```json
{
  "current": {
    "owner": {"owner_id": "005MOCKCSALTHEA", "owner_name": "Althea Cassidy", "team": "Customer Success"},
    "as_of": "2026-12-01T09:00:00-06:00",
    "readiness": "Needs Review",
    "latest_handoff_id": "terrapin-2026-12-01-implementation-cs",
    "open_actions": ["derived action objects"]
  }
}
```

Each derived open action has its action fields plus `event_id` for its originating event, `updated_event_id` for its latest update, and `sources` containing resolved evidence objects from that update. Its `source_ids` are interpreted in `updated_event_id`, not automatically in the latest handoff. This prevents carried tasks from losing their earlier provenance.

The stored history has no derived `current` field. The renderer rebuilds its current overview and all dated sections from `view`; it does not append slides to an old PowerPoint or mutate historical assessment content. PowerPoint edits are not synchronized back into history.
