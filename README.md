# Baton

Baton is a small handoff-quality prototype for GTM teams. It takes structured
Salesforce-style exports and notes, checks a Closed Won handoff, then produces
one account deck that keeps the customer context and unfinished work together.

The [example deck](examples/terrapin-account-deck.pptx) is the main output. It
follows a fictional account from Sales to Implementation, then Customer Success.

## What it solves

When ownership changes, the receiving person often has to reconstruct what the
customer expects and what is still open. Baton preserves that context as a dated
handoff record instead of relying on a current owner field or an edited slide.

## How it works

```text
CSV exports + notes → Python checks → skill assessment → saved handoff history → account deck
```

The CSVs represent five familiar CRM objects: Account, Opportunity, Contact,
Opportunity Contact Role, and Sales Notes. Python handles repeatable checks and
history safety; the skill reviews context and evidence; the deck renderer turns
the saved history into a presentation.

## Run the example

```sh
python3 scripts/analyze_handoff.py
python3 scripts/manage_handoffs.py view --history examples/handoffs/terrapin-history.json
```

To rebuild the supplied deck:

```sh
node scripts/build_deck.mjs --history examples/handoffs/terrapin-history.json --output account-deck.pptx --demo
```

The validator and history helper use Python with no additional packages. Deck
generation also needs Node.js and `@oai/artifact-tool`. Reviewers can open the
included deck directly.

## Scope

This is a local, CSV-backed POC. It does not monitor CRM ownership changes or
write to CRM. Each transfer is supplied explicitly, including the previous and
new owners, teams, and effective date.

Apollo is a **future enhancement**: a production version could retrieve
read-only account context or ownership history using least-privilege access. It
is deliberately not part of this demo, which keeps the data flow clear and
avoids real credentials or customer data.

## Assignment material

- [One-pager](docs/one-pager.pdf)
- [Loom walkthrough](docs/loom-walkthrough.md)
- [Interview prep](docs/interview-prep.md)
- [Submission checklist](docs/submission-checklist.md)

Record a Loom under five minutes and add its link here before submitting.

## Verify

```sh
python3 -B -m unittest discover -s tests -v
```

All names, records, dates, and results in this repository are fictional.
