# Logic review and validation

## Changes from the initial prototype

| Initial behavior | Revised behavior |
| --- | --- |
| Evaluate the first opportunity row. | Select the only Closed Won deal, or require an explicit ID when several exist. Reject non-Closed Won selections. |
| Two missing fields mean Blocked; any nonblank text passes. | Any missing core prerequisite (sponsor, timeline, success criteria) blocks the handoff. Known placeholder tokens count as unconfirmed. Other preparation gaps require review. |
| Unresolved contact references silently produce blank stakeholders. | Validate input schemas, unique IDs, record relationships, same-account role links, and role booleans. Stop with an attributable input error when data is unreliable. |
| JSON omits account context, populated opportunity fields, and source IDs. | Preserve complete selected records and original IDs so the model can compare CRM fields with note evidence. |
| Final status ownership is unclear. | Treat the validator result as a structured baseline. The skill reviews meaning and can escalate Ready to Needs Review; notes never silently fill CRM fields. |

The core-field policy is a deliberate POC business assumption. It is more
conservative than the original count-of-blanks rule and must be agreed with the
receiving team before real use.

## Verification performed

- **27 automated CLI tests passed**, including parameterized cases for
  placeholders, missing columns, duplicate IDs, broken references, selection,
  readiness, source preservation, and exact attribution of stakeholder issues.
- Default fixture: **Blocked**, with the three intended core gaps.
- Complete fixture: structured baseline **Ready**.
- Missing-next-step fixture: **Needs Review**, even though notes contain an action.
- Conflicting-notes fixture: structured baseline **Ready**, with both conflicting
  source records retained for review.
- Invalid-link fixture: **input error, exit code 2**, with no assessment.
- An independent agent used the revised skill on two unnamed input exports
  without seeing the scenario guide or expected outcomes. It assessed the
  complete export as **Ready** and the conflicting export as **Needs Review**,
  citing the stale CRM timeline and the explicit rescheduling note.

All named accounts, contacts, deals, and notes are fictional.
Tests use disposable input copies. The revised project does not change
source records during an assessment.

## What these checks do not prove

The automated tests validate deterministic behavior, not the truth or adequacy of
arbitrary customer statements. The independent review is a small behavioral
check, not a large model evaluation. Production would need more labeled cases,
organization-specific business rules, checks of unusual data formats, and human
review of unresolved commitments and contradictions. No time-saving or revenue
impact has been measured.
