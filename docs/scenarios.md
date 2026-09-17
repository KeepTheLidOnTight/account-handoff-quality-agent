# Demo scenarios

## Main demo: one account, two handoffs

Open [Terrapin's account deck](../examples/terrapin-account-deck.pptx).
The [saved history](../examples/handoffs/terrapin-history.json) contains both
events and their evidence. The later event is a simulated future transfer.

| Date | Internal transfer | Assessment | What to look for |
| --- | --- | --- | --- |
| September 16, 2026 | Samson Delilah, Sales, to Ruben Cherise, Implementation | Ready under the sales policy | Agreed sponsor, timeline and measures support handoff. Implementation work remains to be completed. |
| December 1, 2026 | Ruben Cherise, Implementation, to Althea Cassidy, Customer Success | Needs Review under the generic transfer policy | Training and QBR dates are unconfirmed. The current overview changes, while the September section keeps its original assessment. |

Three actions in the first event become done in the second. The investigation-time
check due December 18 is absent from the second event and therefore carries
forward as open, with Ruben still responsible. The second event adds training
and QBR actions for Althea with unconfirmed dates. Customer contacts Scarlet,
Casey and Jack are distinct from those internal account owners.

View the saved history with:

```sh
python3 scripts/manage_handoffs.py view --history examples/handoffs/terrapin-history.json
```

Rebuild with the renderer and dependencies described in the [README](../README.md):

```sh
node scripts/build_deck.mjs --history examples/handoffs/terrapin-history.json --output account-deck.pptx --demo
```

An identical event retry is a no-op. Conflicting content under an existing ID,
out-of-order events, and a broken owner chain require corrected input. Use a
working copy for experiments; don't invent transfers to bypass a rejected event.

## Supporting sales-validation cases

These five isolated CSV folders exercise the original Closed Won profile.
The Markdown assessments are debugging examples, not the main product output.
Do not combine folders: IDs intentionally repeat to make changes easy to compare.

| Input folder | Purpose | Structured result | Contextual result |
| --- | --- | --- | --- |
| `data` | Sponsor, timeline and success criteria are blank | Blocked | Blocked; notes provide context without filling CRM fields |
| `scenarios/ready` | Required fields, stakeholders and agreements are complete | Ready | Ready after evidence review |
| `scenarios/needs-review` | CRM next step is blank, although a note mentions an action | Needs Review | Needs Review until the structured gap is resolved |
| `scenarios/conflicting-notes` | CRM pilot date is October 5; an approved note moves it to November 2 and requires replanning | Ready | Needs Review, citing the conflict |
| `scenarios/invalid-link` | Technical-buyer role references a missing contact | Input error, exit code 2 | No assessment until input is repaired |

```sh
python3 scripts/analyze_handoff.py
python3 scripts/analyze_handoff.py --data-dir scenarios/ready
python3 scripts/analyze_handoff.py --data-dir scenarios/needs-review
python3 scripts/analyze_handoff.py --data-dir scenarios/conflicting-notes
python3 scripts/analyze_handoff.py --data-dir scenarios/invalid-link
```

Blocked and Needs Review are valid analysis results. An input error is an
execution failure that stops assessment. Ready from the sales script is only
a baseline for contextual review, not approval to start implementation.

All companies, people, dates, notes and results are fictional. There are no real
customer records or personal data. IDs are mock relationship keys, not a claim
that these fixtures are Salesforce-import-ready. The `.example` domains are
reserved for examples.
