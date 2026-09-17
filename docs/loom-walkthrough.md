# Loom walkthrough

Aim for **4 minutes 30 seconds**, with a hard limit of five minutes. This is your
recording plan, not a finished Loom. Record your voice and screen; the camera
bubble is optional. The interview date is still TBD.

## Before recording

Open these at a readable zoom:

1. [The project summary slide](demo-slide.pptx).
2. [Terrapin's account deck](../examples/terrapin-account-deck.pptx).
3. [SKILL.md](../SKILL.md), especially the two readiness policies.
4. [Saved handoff history](../examples/handoffs/terrapin-history.json).
5. [Validation notes](validation-notes.md).

The deck is the main demonstration. Avoid touring every file. Close unrelated
windows and notifications, then rehearse once with a timer. Find the latest
overview, outstanding actions, and both dated sections before you start.

If you want a fresh rebuild without typing terminal commands, ask your coding agent:

> Follow SKILL.md. Read examples/handoffs/terrapin-history.json and rebuild the
> Terrapin account deck using the existing history. Show the latest owner,
> outstanding actions, and both dated handoffs. Explain which action carried
> forward. Use the demo rendering option to keep the fictional and simulated
> labels visible. Do not change source records or add events.

Run that before recording so you can check the result. Call it a saved example
or prepared rebuild. Do not present it as a live model assessment. The PPTX
renderer needs the environment described in the README, not Python alone.

## 0:00-0:35 - The problem

**Show:** the project summary slide.

I built Baton because every time an account changes teams, the next person has
to rebuild the story. What did the customer want? What did we promise? What's
still open? Baton keeps one account deck with the current context at the front
and dated handoffs behind it. I want to reduce preparation and dropped
commitments. I haven't measured that impact yet.

## 0:35-1:20 - The first handoff

**Show:** Terrapin's September 16 Sales to Implementation section.

This is a fictional customer. In September, Samson in Sales hands the account
to Ruben in Implementation. The supplied CRM records and notes support Ready:
there's a sponsor, an agreed plan, and measurable outcomes. Ready means the
handoff evidence meets this policy. It doesn't mean the rollout has happened.
This section records what the team knew at that point, including an
investigation-time target due December 18.

## 1:20-2:25 - The deck grows

**Show:** the December 1 section, then the current overview and action list.

The second transfer is a simulated future case. Implementation hands the account
to Althea in Customer Success. The front now shows Althea and Needs Review,
because training and the first QBR still need confirmed dates. The earlier
September section still says Ready. It hasn't been rewritten using later facts.

Here's the detail I care most about: the December 18 investigation-time check
is still open, even though the new transfer doesn't mention that action. It
carries forward with Ruben as its action owner. Althea owns the account now,
but that alone doesn't reassign Ruben's work. A recorded update needs evidence.

## 2:25-3:10 - How it works

**Show:** the history file briefly, then the workflow in SKILL.md.

The initial handoff uses five Salesforce-style CSVs. Later transfers also need
explicit owner and team metadata plus operational notes. Python checks the data
and protects the history. The model reads the evidence and explains gaps.
The renderer rebuilds the deck from the stored events. It doesn't use an old
PowerPoint as the source of truth. Repeating the same event doesn't add another
section, and a changed event with the same ID is rejected.

## 3:10-3:50 - What AI got wrong

**Show:** validation-notes.md.

I used AI to draft the project and then review it. The first sales validator
selected the first opportunity, accepted TBD, and could hide a broken contact
link. Those behaviors were corrected and tested. All 56 Python tests pass.
The history checks also cover
ordering, owner continuity, duplicate events and carried actions. The automated
tests check code behavior. A separate agent's two-case review gives a small
check of evidence interpretation, not a guarantee that the model is accurate.

## 3:50-4:30 - Scope and production work

**Show:** the summary slide or the account deck's current overview.

This runs when someone supplies a handoff. It doesn't detect CRM ownership
changes or write anything back. For production, I'd connect to actual ownership
history, agree on each receiving team's rules, and add access controls and a
reviewed correction process. I'd also test real handoffs for missed gaps and
false alarms. The main idea is that a team change updates the current view
without losing what earlier teams knew or leaving unfinished work behind.

## After recording

- Watch the full recording. Confirm readable screens, clear audio, and a duration
  of five minutes or less. Trim waiting and repeated explanations.
- Check the hiring team can open the link. Add the Loom URL to the public repo's
  README. A walkthrough document alone does not fulfill the recording option.
- Publish the updated project package and check the public files match the demo.
- Submit at least 24 hours before the interview once its date is set. No recruiter
  message has been sent.

If you choose a live demo instead, use the same sequence and keep the saved
account deck available as a clearly labeled fallback.
