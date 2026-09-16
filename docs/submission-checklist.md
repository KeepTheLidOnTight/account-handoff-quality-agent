# Apollo submission checklist

Checked against the supplied **Senior Business Systems Analyst, GTM Technical
Exercise**, especially the Requirements and Deliverable sections. This checklist
separates prepared materials from actions still needed before submission.

| Assignment criterion | Status | Evidence or remaining action |
| --- | --- | --- |
| Working agent skill with YAML frontmatter | Done | [SKILL.md](../SKILL.md) and [validator](../scripts/analyze_handoff.py). |
| At least one external data source | Done | Five CSV exports in `data/`. The assignment explicitly accepts structured files and mock data. |
| Public GitHub repository | Done | [Account Handoff Quality Agent](https://github.com/KeepTheLidOnTight/account-handoff-quality-agent) contains the skill, validator, fictional data, examples, and demo materials. |
| Short README with setup and run instructions | Done | [README](../README.md). |
| Clear GTM problem and business impact | Prepared | [One-pager](one-pager.md) explains the handoff problem and intended benefit. Savings have not been measured. |
| Use AI tooling and explain how it helped | Done and documented | [Validation notes](validation-notes.md) and [interview prep](interview-prep.md) explain the AI-assisted build and review. |
| Free tooling and no confidential data | Project meets the scope | Python standard library, fictional CSV data, and no paid API dependency. Use your available recording tool without purchasing an upgrade. |
| One-pager OR single slide | Prepared | [One-pager PDF](one-pager.pdf) and [editable summary slide](demo-slide.pptx). Both were requested for this project. |
| Live demo OR Loom of no more than 5 minutes linked in repo | Recording pending | [Walkthrough](loom-walkthrough.md) and saved [example assessment](../examples/blocked-assessment.md) are prepared. Record your voice and screen, check duration/access, then add the video URL to the README. A walkthrough document alone does not fulfill the recording option. |
| Cover all five discussion topics | Prepared | [Interview prep](interview-prep.md): problem, assumptions, design decisions, AI trust/checks, production hardening. Rehearsal is still needed. |
| Return to recruiter at least 24 hours before interview | Pending | Interview date is TBD. Once scheduled, calculate the deadline and send the final public repo and materials. No recruiter message has been sent. |

## Final check before sending

- Open the public repository without relying on a signed-in account.
- Follow the README from a fresh copy and verify the expected demo results.
- Watch the full recording. Confirm it is readable, audible, and at most five minutes.
- Check the hiring team can open the recording link and supporting files.
- Confirm the recording describes saved outputs honestly and makes no unsupported
  claims about model accuracy or measured business results.
- Send at least 24 hours before the interview.

Apollo asks for a focused prototype and clear thinking. The recorded demo can
use the default and conflicting-notes cases; there is no need to tour every file
or add more features to explain the work.
