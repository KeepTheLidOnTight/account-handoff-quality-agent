# Interview prep

Use these as speaking notes, not a script to memorize. Describe the actual
AI-assisted process. Add personal experience only when it is something you did.

## Your 30-second introduction

I built Baton to keep an account's story together when ownership changes.
It produces one deck with the current owner and outstanding work at the front,
then a dated section for each handoff. Earlier sections keep the facts and
assessment from that time. The skill reviews the evidence, Python protects the
records, and the deck rebuilds from saved history. The demo follows a fictional
account through Sales, Implementation, and Customer Success.

## 1. Why does this matter to a GTM team?

Each team change can make someone reconstruct the customer story. A receiving
teammate needs more than a name in an owner field. They need to know what the
customer expects and which work is still open. I wanted that context to survive
the transfer instead of creating another disconnected document.

**Show:** Althea owns the account in the latest view, while Ruben's investigation
check is still open. Account ownership and action ownership are separate.

**If they ask about value:** I haven't measured it yet. I would compare handoff
preparation time, clarification requests and dropped follow-up work on similar
accounts. I would also ask receiving teams whether the deck helped them find
the right evidence. Faster onboarding alone would not prove this tool caused it.

## 2. What did you assume?

A person supplies the transfer date, the old and new internal owners and teams,
and the supporting records. The prototype does not infer a transfer from today's
CRM owner or detect one automatically. Internal employees are distinct from
customer contacts such as Scarlet and Casey.

The sales profile assumes a Closed Won deal and requires a documented sponsor,
timeline and success criteria. Those rules don't automatically apply to Customer
Success. Later transfers get a generic review of responsibilities, commitments,
risks and next actions. I'd agree on team-specific requirements before production.

**Why CSVs?** The assignment accepts structured files. Five Salesforce-style
exports give repeatable external inputs without real credentials or employer
data. The object relationships are recognizable, but these are mock keys and
custom fields, not a promised Salesforce import package.

**Why is December in the deck?** It's a simulated future transfer that lets me
demonstrate how a second handoff changes the current view. No real December
event or customer outcome is being claimed.

## 3. Why a skill, Python, and saved history?

Different parts need different checks. Python can reliably select a deal,
validate links, reject a duplicate or conflicting event, and keep an open action
visible. The model adds context: a filled date might disagree with an approved
change in the notes, and rollout completion doesn't prove every success goal.
The skill tells it how to distinguish those facts and cite evidence.

The saved history is the source for rendering. Each event includes owners,
timestamps, an assessment, actions and source references. The front of the deck
uses the latest event and all outstanding work. Dated sections use their original
events. A rebuild preserves earlier content even if pagination changes.

**Why not edit the old PowerPoint?** Manual edits are hard to reconcile with
sources and can erase past context. Here the deck is an output. Editing a slide
does not change the saved history, and the next rebuild uses that history.

**What do I need to run it?** Python 3 runs the validator and history helper with
no extra packages. Rendering the PPTX also needs Node.js and `@oai/artifact-tool`,
which the demo's Codex environment supplies. That library is not bundled with
the repo. A reviewer can open the saved deck without rebuilding it. I would not
claim Python alone builds the deck or that every public environment includes
the presentation library.

**What is deliberately out of scope?** Live ownership triggers, CRM writeback,
concurrent users, an automatic correction workflow, and a policy for every team.
This is a local prototype with one writer at a time.

## 4. Where did AI help, and where didn't you trust it?

I used AI for the skill, code, fictional cases and supporting materials, then
asked it to review the work and test failures. The original sales validator
selected the first opportunity, accepted TBD, and could hide a broken contact
link. The fixes made deal selection explicit, recognized placeholders, and
stopped on invalid relationships. Changing the rule from two missing fields to
any missing core prerequisite was also a business-policy choice, not just a bug fix.

**The checks mean different things:**

- All 56 Python tests pass: 27 for the sales validator and 29 for handoff history.
- The original 27 sales tests check deterministic code behavior. Five sales
  fixtures cover complete, incomplete, review, conflicting and invalid inputs.
- A separate agent assessed two unnamed exports without their expected answers.
  It returned Ready for complete evidence and Needs Review for conflicting notes.
  That is a small behavioral check, not a broad evaluation of model accuracy.
- The history tests check record order, stable IDs, owner continuity and action
  carry-forward. They do not prove a recorded statement is true or authorized.
- The rendered deck needs visual review too. A structurally valid PPTX can still
  have unreadable text or omit context.
- A separate assessment-only check of the raw later-transfer inputs returned
  Needs Review, the correct CS owner and three open actions. It kept the
  investigation goal outstanding and flagged missing recording metadata.
  That is one additional case, not a general accuracy result.

**A useful evidence example:** CRM says the pilot starts October 5. A note records
an approved move to November 2 and says the remaining milestones need re-planning.
The original sales checks say Ready because the fields are populated. The skill
returns Needs Review and cites both sources. This remains a supporting test case,
separate from the two-transfer account-deck demonstration.

**Avoid claiming:** that you hand-wrote all code, manually checked every test, or
proved the AI is accurate. Explain the AI-assisted review and its limits.

## 5. What would you harden for production?

| Area | What I would do |
| --- | --- |
| Reliability | Connect to real transfer history, monitor failed runs, add safe retries and concurrent-write handling, and design a reviewed correction process. |
| Security | Use least-privilege access, protect notes and decks, set retention rules, and treat source text as evidence rather than instructions. |
| Scale | Fetch relevant account changes instead of whole exports, handle API limits, and rebuild only affected accounts. |
| Accuracy | Agree on team policies, evaluate labeled real handoffs, measure missed gaps and false alarms, and keep a person responsible for unresolved commitments. |

The local history file is not tamper-proof. The helper prevents certain bad
updates through its interface; someone with file access can still edit it.
Any future CRM writeback needs authorization and a traceable review process.

## Questions they may push on

**Why does Ruben still own an action after Althea gets the account?**

The action had Ruben as its explicit owner. The later event did not close or
reassign it, so it remains open with him. Account ownership does not silently
change action responsibility. The receiving team can review and record a supported update.

**What if the same handoff arrives twice?**

An identical event ID and content is a no-op. Different content with the same ID
is a conflict. A retry must reuse the recorded timestamps. This protects local
append behavior; it does not solve concurrent writes across a production system.

**What if the owner chain is broken or the events are out of order?**

The helper rejects it. The user needs to correct the input or use a reviewed
history-correction process. The skill must not invent a missing transfer.

**Does Needs Review stop an ownership change?**

No. It describes the supplied handoff evidence. Baton does not approve, execute,
or reverse ownership changes in CRM. The receiving team's process decides what
to do with the finding.

**Why keep a September Ready section if December Needs Review?**

They assess different transfers using the evidence available at those times.
Changing the old status would erase that distinction. The latest overview makes
the current recorded situation clear while dated sections preserve the history.

**What does the legacy sales validator still do?**

It checks initial Closed Won readiness. Missing core fields block that sales
handoff, notes cannot silently fill CRM gaps, and broken inputs stop assessment.
It does not determine the readiness of a later internal transfer.

## Rehearse

Explain the problem in 30 seconds without mentioning implementation tools.
Then show the current owner, a carried action and the preserved September section.
Be able to name one failure AI introduced and the check added for it. Finish
with one production improvement and one honest limit of the prototype.
