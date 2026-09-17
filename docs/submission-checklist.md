# Assignment submission checklist

The working product is now **one account deck with dated handoffs**. The one-pager explains the project; the account deck shows the customer-specific output.

| Assignment criterion | Status | Evidence or remaining action |
| --- | --- | --- |
| Working agent skill with YAML frontmatter | Prepared locally | [SKILL.md](../SKILL.md), [sales validator](../scripts/analyze_handoff.py), [history helper](../scripts/manage_handoffs.py), and [deck renderer](../scripts/build_deck.mjs). |
| At least one external data source | Prepared | Five Salesforce-style CSV exports, plus explicit transfer records and notes. The assignment accepts structured files and mock data. |
| Public GitHub repository | Published and verified | [Baton](https://github.com/KeepTheLidOnTight/baton) contains the account-deck implementation and artifacts. |
| Short README with setup and run instructions | Prepared | [README](../README.md) explains both Python helpers and PPTX renderer requirements. |
| Clear GTM problem and business impact | Prepared | [One-pager](one-pager.pdf) explains retained account context and unfinished work. |
| Use AI and explain its role | Documented | [Validation notes](validation-notes.md) and [interview prep](interview-prep.md) describe drafts, failures, checks and limits. |
| Tooling and confidential-data requirements | Dependency qualification needed | Python helpers use the standard library. PPTX generation also requires Node.js and `@oai/artifact-tool` supplied by the demo's Codex environment. It is not bundled here. No renderer API charge or real customer data is involved, but don't claim universal free access to that library. Reviewers can open the saved deck directly. |
| One-pager OR single project-summary slide | Prepared | [One-pager PDF](one-pager.pdf). |
| Live demo OR Loom of no more than 5 minutes linked in repo | Recording pending | [Loom walkthrough](loom-walkthrough.md) uses the [account deck](../examples/terrapin-account-deck.pptx). Record, check duration/access, and add the URL to README. A script alone does not fulfill the recording option. |
| Cover all five discussion topics | Prepared; rehearse | [Interview prep](interview-prep.md) covers the problem, assumptions, design, AI checks and production hardening. |
| Submit at least 24 hours before interview | Pending | Interview date is TBD. No recruiter message has been sent. |

## Before sending

- Open the public repo without relying on a signed-in account before sending.
- Open the saved account deck. Check that September is Ready, December is Needs Review, and the future case is labeled simulated.
- Check the latest owner, carried investigation-time action and preserved earlier
  content. The deck must match its saved history.
- Follow the README from a fresh copy. If rebuilding PPTX, use the documented
  presentation dependency; Python-only checks are not a renderer check.
- Watch the full recording and confirm readable screens, clear sound, an
  accessible link, and a duration of no more than five minutes.
- Verify that claims about tests, AI accuracy and business impact are qualified.
- Once the interview is scheduled, submit the repository and materials at least
  24 hours beforehand.

The remaining submission actions are publishing/verifying the revised package,
recording or choosing a live demo, rehearsing, and sending the materials on time.
