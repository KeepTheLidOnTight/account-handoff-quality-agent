# Account Handoff Quality Agent

A deal can be Closed Won and still be a messy handoff. The CRM has a few blank
fields, the rollout plan is buried in call notes, and the implementation team
has to piece it all together before kickoff.

I built this skill to review that information and give the receiving team a
brief they can work from: customer goals, stakeholders, commitments, missing
details, and questions to resolve.

The demo customer is **Terrapin Touring Co.** All the data is fictional and
Grateful Dead themed. I used Salesforce-style CSVs so the demo can run without
setting up a Salesforce org.

## Try it

You'll need Python 3. There are no packages to install. From the project folder:

```sh
python3 scripts/analyze_handoff.py
```

This runs the data checks and prints the results as JSON. To get the full handoff
assessment, open the project in your coding agent and use this prompt:

> Follow SKILL.md and assess the Closed Won deal in the data folder. Run the
> validator, review the CRM records and sales notes, and return the handoff
> assessment with source references. Don't change the data.

To try the complete handoff example:

```sh
python3 scripts/analyze_handoff.py --data-dir scenarios/ready
```

If your data contains more than one Closed Won deal, add `--opportunity-id` and
the deal's ID. The script will list the choices if you leave it out.

## How it works

Python handles the repeatable checks: selecting the right deal, joining records,
checking required fields, and catching broken links or placeholders like `TBD`.
It reads five files: Account, Opportunity, Contact, OpportunityContactRole, and
SalesNotes.

The [skill](SKILL.md) tells the model how to read the notes, compare them with the
CRM, and write the brief. For example, wanting to start in October doesn't mean
both teams agreed to an October start. Being the primary contact doesn't make
someone the executive sponsor.

For this demo, a missing sponsor, timeline, or success criteria blocks the
handoff. Other gaps need review. The model also checks for conflicting evidence,
so a deal that passes the Python checks can still need review. Nothing is written
back to the source data.

## Scenarios and checks

There are five [demo cases](docs/scenarios.md): an incomplete handoff, a complete
one, a missing next step, conflicting notes, and a broken contact link. The
conflicting-notes case is useful to walk through: all the CRM fields are filled,
but the rollout dates no longer agree with the notes.

Run the tests with:

```sh
python3 -B -m unittest discover -s tests -v
```

The tests check deal selection, missing fields, placeholders, bad input, and
record links. The [validation notes](docs/validation-notes.md) cover what broke
in the first version, what changed, and how I checked the model's assessment.

## Demo and write-up

The [one-pager](docs/one-pager.pdf) explains the design decisions and what I'd
change for production. The [summary slide](docs/demo-slide.pptx) covers the
workflow and the conflicting-dates example.
There's also a [slide image](docs/demo-slide.png) you can open for screen sharing.

Saved examples include an [incomplete handoff](examples/blocked-assessment.md)
and a [handoff with conflicting notes](examples/conflicting-notes-assessment.md).
These are outputs from example runs, not live results.

The recording is still to come. The [demo walkthrough](docs/loom-walkthrough.md)
sets out what to show in under five minutes. The
[interview notes](docs/interview-prep.md) cover the discussion questions, and the
[submission checklist](docs/submission-checklist.md) tracks what's left to send.

## What's still missing

This is a prototype. The fields and readiness rules are assumptions for the
exercise, and the IDs are mock keys. Before a real team used it, I'd agree on
their handoff requirements, connect their systems with the right access controls,
and test against a wider set of deals. Any future CRM updates would need human
review. I haven't measured time savings or business impact yet.
