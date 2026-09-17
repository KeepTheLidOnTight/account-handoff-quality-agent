# Logic review and validation

## What changed with the account deck

Baton now stores a sequence of handoffs for an account and renders one PowerPoint
from that history. Its opening view shows the latest recorded owner and all
outstanding actions. Dated sections preserve earlier assessments and facts.
The legacy sales validator and Markdown examples remain supporting checks.

The history helper validates event structure, IDs, source references, chronology,
account consistency and owner continuity. It ignores an identical retry, rejects
changed content under an existing event ID, and carries open actions forward
when later events omit them. It does not infer transfers from a current owner.

The Terrapin example has two events:

- September 16, 2026: Samson in Sales transfers to Ruben in Implementation.
  The sales assessment is Ready.
- December 1, 2026: Ruben transfers to Althea in Customer Success. This simulated
  future assessment is Needs Review because training and QBR dates are unconfirmed.
  The sales baseline does not apply to this later transfer.

The December event marks kickoff, identity notice and rollout verification done.
It omits the December 18 investigation-time action, so that action stays open
with Ruben. Althea owns the account, not automatically every action. The earlier
September section remains Ready with its original evidence.

## Original sales fixes retained

| Initial behavior | Revised behavior |
| --- | --- |
| Evaluate the first opportunity row | Select the only Closed Won deal or require an explicit choice. |
| Two blank fields block; any nonblank value passes | Any missing core prerequisite blocks. Known placeholders count as unconfirmed; other preparation gaps need review. |
| Invalid contact references produce blank stakeholders | Stop on invalid schemas, IDs, relationships, account links or role booleans. |
| Omit populated fields and source IDs | Preserve complete selected records and references for evidence review. |
| Unclear final readiness ownership | Treat Python's sales result as a structured baseline; contextual review can escalate Ready to Needs Review. |

The sponsor/timeline/success-criteria policy is a prototype business assumption.
It applies to initial sales handoffs, not automatically to later internal transfers.

## Verification evidence

- **All 56 Python tests passed: 27 sales-validator tests and 29 history tests.**
  The history checks include baseline type and no optimistic sales override,
  evidence dates at or before recording, stored snapshots, retries/conflicts,
  event order, owner continuity, and action carry-forward/closure.
- The original **27 sales-validator tests** cover selection, placeholders,
  required fields, malformed input, record links and evidence preservation.
- Five sales fixtures cover Blocked, Ready, Needs Review, contradictory notes,
  and an intentional input error. See [scenarios](scenarios.md).
- A separate agent reviewed two unnamed sales exports without the expected
  outcomes. It returned Ready for the complete case and Needs Review for the
  conflict, citing both CRM and the schedule-change note. This review predates
  the ongoing deck feature and does not validate later-transfer judgments.
- A new assessment-only check used raw December and September ownership snapshots
  plus the ready sales CSVs, without the prepared events, history or deck. It
  returned Needs Review with no sales baseline, Althea as the CS account owner,
  and the three supported open actions. It retained Ruben's December 18 action
  and did not claim that target was achieved. It also identified the missing
  recording timestamp in the raw inputs. This is one small behavioral check.
- The full suite passed under Python 3.9+: 56 tests in 13.759 seconds.
  Run it with `python3 -B -m unittest discover -s tests -v` on a supported
  Python version.
- Deck checks passed: the one-event deck has four slides, and the two-event deck
  has five. The additional transfer adds one dated record while the current pages
  refresh. The carried action stays visible. The final deck passed package,
  layout, font and import checks, and all five rendered slides were reviewed for
  readability.

## Limits of these checks

Tests validate specific code behavior, not source truth, authorization or broad
model accuracy. The two-export review is a small semantic check. The saved
history is a local file, not a tamper-proof audit system. The helper expects one
writer at a time; concurrent writes and reviewed corrections need further work.

Rendering rebuilds from stored history rather than editing an old PPTX. It
preserves earlier content, not necessarily identical slide positions or file
bytes. Manual PowerPoint edits do not update the saved records. If rendering
fails after an event is saved, that distinction must be reported.

All examples are fictional, and the later transfer is a simulated future case.
No time saving, revenue impact or real customer outcome has been measured.
