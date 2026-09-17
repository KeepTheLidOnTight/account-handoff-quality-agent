# Baton

An account changes hands, and the next team has to piece the story together again.
Baton keeps one deck with the account: two current-state pages at the front, a
short handoff history, then one dated page per recorded transfer. Open work
stays visible until someone closes it.

The [example deck](examples/terrapin-account-deck.pptx) follows **Terrapin Touring
Co.** from Sales to Implementation, then to Customer Success. All names, dates and
results are fictional. The later transfer is a simulated future case.

## What it does

For each supplied transfer, the skill reviews the records and notes, saves a
sourced assessment, and rebuilds the deck. Earlier handoffs keep their original
facts and readiness. The front reflects the latest recorded transfer. Unfinished
actions carry forward even when the newest handoff doesn't mention them.

Python checks the records and protects the saved history. The model reviews what
the evidence means. A filled CRM date can still disagree with a later agreement,
and a Customer Success handoff needs different checks from a sales one.

This prototype runs when someone supplies a handoff. It does not detect ownership
changes in Salesforce or write back to CRM. A current-owner field cannot tell it
who owned the account before or when the change happened.

## Try it in your coding agent

Open this project and use:

> Follow SKILL.md. Read the Terrapin history in examples/handoffs and rebuild its
> account deck. Show the latest owner, outstanding actions and both dated
> handoffs. Explain which actions carried forward. Don't change source data.

To record another handoff, provide the existing account history, a transfer
record with the old and new internal owners/teams and date, and relevant notes.
Baton needs those facts explicitly. [The schema](references/handoff-schema.md)
defines the saved record.

## Setup and commands

The validator and history helper use **Python 3.9+ with no extra packages**:

```sh
python3 scripts/analyze_handoff.py
python3 scripts/manage_handoffs.py view --history examples/handoffs/terrapin-history.json
```

The first command runs the original Closed Won checks. The second shows the
handoffs and current outstanding work. To add a prepared event to a working copy:

```sh
python3 scripts/manage_handoffs.py add --history account-history.json --event new-handoff.json
```

Adding the same event twice won't duplicate its section. Changing an existing
event ID is rejected. This is a local workflow for one writer at a time.

**Deck generation also needs Node.js and an installed `@oai/artifact-tool`.**
The Codex environment used for this demo supplies that presentation library.
Set `BATON_NODE_MODULES` to its Node modules folder if needed, and `BATON_PYTHON`
if Python isn't available as `python3`. There is no paid API call in the renderer.
The library is not bundled here; Python alone cannot rebuild the PPTX. Reviewers
can open the saved example deck directly.

```sh
node scripts/build_deck.mjs --history examples/handoffs/terrapin-history.json --output account-deck.pptx --demo
```

The included Project Kickoff template provides the layout. See
[deck output guidance](references/deck-output.md) for the evidence rules.
Corrections to saved history need an explicit reviewed process. Manual
PowerPoint edits won't update the history used for the next rebuild.

## Checks and examples

```sh
python3 -B -m unittest discover -s tests -v
```

Tests cover the sales validator and handoff-history behavior. The original
[five data scenarios](docs/scenarios.md) still exercise missing fields, complete
records, conflicting notes and broken links. The saved Markdown
[assessments](examples/blocked-assessment.md) show the reasoning behind those
checks. The account deck is now the main output.

## Demo and write-up

The [one-pager](docs/one-pager.pdf) and [single summary slide](docs/demo-slide.pptx)
explain the project. They are separate from the account handoff deck.
The [Loom walkthrough](docs/loom-walkthrough.md), [interview prep](docs/interview-prep.md)
and [submission checklist](docs/submission-checklist.md) cover the presentation.
The recording is still to come.

## What I'd do next in production

Agree on each receiving team's requirements, connect to account ownership
history with limited permissions, and handle concurrent updates and retries.
I'd add reviewed corrections, access controls and retention for customer
records, then evaluate more real handoffs for missed gaps and false alarms.
I haven't measured time savings or customer impact.
