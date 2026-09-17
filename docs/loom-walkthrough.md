# Loom walkthrough

Aim for **4 minutes 30 seconds**, with a hard limit of five minutes. This is your
recording plan, not a finished Loom. Record your voice and screen; the camera
bubble is optional. The interview date is still TBD.

## Before recording

Open these at a readable zoom:

1. [The one-pager](one-pager.pdf).
2. [Terrapin's account deck](../examples/terrapin-account-deck.pptx).
3. [SKILL.md](../SKILL.md), especially the two readiness policies.
4. [Saved handoff history](../examples/handoffs/terrapin-history.json).
5. [Validation notes](validation-notes.md).

The deck is the main demonstration. It has two slides: a current account brief and clear next steps. Avoid touring every file.
Close unrelated windows and notifications, then rehearse once with a timer.

If you want a fresh rebuild without typing terminal commands, ask your coding agent:

> Follow SKILL.md. Read examples/handoffs/terrapin-history.json and rebuild the
> Terrapin account deck using the existing history. Show the latest owner,
> outstanding actions, and both dated handoffs. Explain which action carried
> forward. Use the demo rendering option to keep the fictional and simulated
> labels visible. Do not change source records or add events.

Run that before recording so you can check the result. Call it a saved example
or prepared rebuild. Do not present it as a live model assessment. The PPTX
renderer needs the environment described in the README, not Python alone.

## 0:00-0:55 - The problem, current state, and advice

**Show:** slide 1, the current account record.

I built Baton because every time an account changes teams, the next person has
to rebuild the story. What did the customer want? What did we promise? What's
still open? Baton keeps one account deck with the current context at the front
and dated handoffs behind it. It gives the next team one place to begin and makes open work visible.

The front makes the current situation legible in a few seconds. Six venues report to one dashboard, 96% of priority alerts arrive within 15 minutes, and the 42-minute investigation target remains due December 18. The recommendation is explicit: keep the handoff open until training, QBR, and the measurement are recorded.

## 0:55-1:35 - Recommended next steps

**Show:** slide 2.

The open-action slide separates account ownership from action ownership. Althea
owns Customer Success, but Ruben still owns the December 18 investigation-time
check because no recorded update reassigned it. Althea owns the two date-confirmation
follow-ups. The deck shows the text, owner, and due date for each item.

## 1:35-2:20 - How it works

**Show:** the history file briefly, then the workflow in SKILL.md.

The initial handoff uses five Salesforce-style CSVs. Later transfers also need
explicit owner and team metadata plus operational notes. Python checks the data
and protects the history. The model reads the evidence and explains gaps.
The renderer rebuilds the deck from the stored events. It doesn't use an old
PowerPoint as the source of truth. Repeating the same event doesn't add another
section, and a changed event with the same ID is rejected.

## 2:20-3:05 - What AI got wrong

**Show:** validation-notes.md.

I used AI to draft the project and then review it. The first sales validator
selected the first opportunity, accepted TBD, and could hide a broken contact
link. Those behaviors were corrected and tested. All 56 Python tests pass.
The history checks also cover
ordering, owner continuity, duplicate events and carried actions. The automated
tests check code behavior. A separate agent's two-case review gives a small
check of evidence interpretation, not a guarantee that the model is accurate.

## 3:05-3:45 - Scope and production work

**Show:** the account deck's current overview.

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
