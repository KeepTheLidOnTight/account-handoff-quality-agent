# Loom walkthrough

Aim for about **4 minutes 30 seconds**. Apollo allows a recording of no more
than five minutes. Record your own voice and screen; a camera bubble is optional.
This is a recording plan, not a finished Loom.

## Set up before recording

Open the project in your coding agent. Have these ready to show at a readable zoom:

1. `docs/demo-slide.pptx` or the screen-friendly `docs/demo-slide.png`.
2. `SKILL.md` and the five files in `data/`.
3. `examples/blocked-validation.json` and `examples/blocked-assessment.md`.
4. `examples/conflicting-notes-validation.json` and `examples/conflicting-notes-assessment.md`.
5. `docs/validation-notes.md`.

Close unrelated windows and notifications. Rehearse once with a timer. Use the
recording controls to pause while switching files if needed.

You can show saved outputs to keep the recording short. Say they are saved runs.
If you want a fresh run, paste the prompts below into your coding agent before
recording; you don't need to type terminal commands yourself. Keep the responses
available on screen. Don't present a saved assessment as a live model run.

**Default example prompt**

> Follow SKILL.md. Run the validator on the default data folder and assess the
> Closed Won opportunity. Show the validator result, then the full handoff brief
> with source references. Do not edit any files.

**Conflict example prompt**

> Follow SKILL.md using scenarios/conflicting-notes as the data folder. Run the
> validator, compare the CRM timeline with the notes, and return the handoff
> assessment. Explain any difference between the validator result and the final
> result. Do not edit any files.

## What to show and say

### 0:00-0:35 — The problem

**Show:** the summary slide.

I built an account handoff quality skill for the transition from sales to
implementation or customer success. The problem is that the receiving team can
have a closed deal without a clear picture of what was promised or what's still
missing. This reviews CRM records and sales notes together and produces a brief
the team can use before kickoff. The goal is less preparation and fewer missed
expectations. I haven't measured that impact yet.

### 0:35-1:10 — How it works

**Show:** the data folder, then the workflow and policy in SKILL.md.

The demo uses five Salesforce-style CSVs for a fictional customer, Terrapin
Touring. Python selects the Closed Won deal, joins its records, and checks the
required fields. The skill then has the model read the notes and compare them
with the CRM. I used CSVs so the inputs are repeatable and the demo doesn't need
credentials. This version only reads data. It doesn't update Salesforce.

### 1:10-2:00 — The incomplete handoff

**Show:** the saved default JSON result, then the missing information and
commitments sections in blocked-assessment.md.

Here's a saved run of the incomplete handoff. The sponsor, implementation
timeline, and success criteria are blank, so the validator returns Blocked.
The notes still help: Casey owns the technical rollout, SSO is required before
broad rollout, and the identity team needs two weeks' notice. But an early-October
preference isn't an agreed timeline, and Scarlet being the primary decision-maker
doesn't automatically make her the sponsor. The brief keeps those distinctions
and cites where each finding came from.

### 2:00-3:00 — Why the model is useful

**Show:** the conflict JSON's Ready result, then the conflicting-notes assessment
and its two source references.

This second saved example has all the structured fields filled, so Python
returns Ready. But CRM still lists an October 5 pilot. A note records an approved
move to November 2 and says the remaining milestones need replanning. The skill
changes the final assessment to Needs Review and cites both sources. That's the
part the model adds: it can explain why populated fields still leave the receiving
team with an unreliable plan. A person needs to reconcile that plan before
the handoff is relied on.

### 3:00-3:45 — What AI got wrong and how it was checked

**Show:** validation-notes.md.

I used AI to draft the project and review it. The first version had real
problems: it picked the first opportunity, let TBD pass as a completed field,
and could hide broken contact links. Those behaviors were corrected and tested.
There are now 27 automated tests for the script, plus five demo scenarios.
An independent agent also assessed two cases without their expected answers.
That's useful evidence for this prototype, but it isn't a large evaluation of
model accuracy.

### 3:45-4:30 — Assumptions and production work

**Show:** the policy or one-pager, then finish on the summary slide.

The readiness rules are assumptions for this exercise. I'd agree on them with
the receiving team before using this in production. I'd also add a live connector
with limited permissions, better operational logging, and a larger evaluation
set with real handoff edge cases. Any CRM updates would need human review.
The demo shows the decision process: identify the gaps, recover useful context,
and make it clear what someone still needs to confirm.

## After recording

- Watch the recording once. Check the screen is readable and your audio is clear.
- Keep the final video at or below five minutes. Trim waiting and repeated explanations.
- Check the link's viewing permissions so the hiring team can open it.
- Add the Loom URL to the README. A script or a local video without an accessible
  link does not complete the recorded-demo requirement.
- Send the public repo and supporting materials to the recruiter at least 24 hours
  before the interview. The interview date is currently TBD.

If you choose a live demo instead, use the same sequence and keep the saved
outputs available as a clearly labeled fallback.
