# Grateful Dead-themed demo scenarios

Every company, person, address, domain, deal, and note in these datasets is fictional. The theme uses playful names, not real band biographies, lyrics, customers, or personal data. IDs are mock relationship keys; these fixtures are not represented as Salesforce-import-ready. The `.example` domain is reserved for examples.

Each folder contains a complete, isolated set of the five CSVs. IDs intentionally repeat between folders so a single changed condition is easy to compare. Do not combine the folders into one input directory.

The fictional customer is **Terrapin Touring Co.**, an entertainment and venue-operations company buying **Wall of Sound Security** for its corporate environment and six acquired venues. Scarlet Begonia is the primary decision-maker; Casey Jones owns technical rollout; Jack Straw handles procurement.

| Input folder | Purpose | Expected validator baseline | Expected final assessment |
| --- | --- | --- | --- |
| `data` | Main demo: sponsor, timeline, and success criteria are blank. Notes contain useful goals and dependencies but do not establish complete agreements. | Blocked | Blocked |
| `scenarios/ready` | Confirmed sponsor, dated rollout plan, feasible identity-team notice, measurable outcomes, and one primary contact. | Ready | Ready after evidence review |
| `scenarios/needs-review` | Identical to Ready except the CRM next step is blank. Notes still describe an action, exposing a structured-field gap. | Needs Review | Needs Review until CRM correction |
| `scenarios/conflicting-notes` | Complete structured fields, but a newer note supersedes the corporate pilot date and requires remaining milestones to be re-planned. | Ready | Needs Review: evidence conflict, with both sources cited |
| `scenarios/invalid-link` | The technical-buyer role references `003TerrapinMissing`, which has no Contact row. | Input error; exit code 2 | No assessment; repair the input first |

## Run the fixtures

Run from the project folder with Python 3:

```bash
python3 scripts/analyze_handoff.py
python3 scripts/analyze_handoff.py --data-dir scenarios/ready
python3 scripts/analyze_handoff.py --data-dir scenarios/needs-review
python3 scripts/analyze_handoff.py --data-dir scenarios/conflicting-notes
python3 scripts/analyze_handoff.py --data-dir scenarios/invalid-link
```

The validator checks structured completeness and relationship integrity. It does not interpret note meaning or detect contradictory dates. `Ready` from the validator is a baseline for the skill's evidence review, not an approval to begin implementation. The conflicting-notes case deliberately demonstrates that division of work.

An assessment with Blocked or Needs Review is a successful analysis, not an execution failure. The invalid-link fixture intentionally fails before assessment so an unreliable join cannot look like a healthy handoff.
