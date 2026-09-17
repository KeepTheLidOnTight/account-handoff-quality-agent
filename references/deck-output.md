# Account deck output

Generate one editable PowerPoint deck per account from the saved handoff history.
Rebuild it when a new transfer is recorded. Keep the prior events' assessments,
sources and actions as they were recorded.

The first two slides show the latest recorded owner/team, latest transfer date,
customer context and outstanding actions. A short history follows. Add one dated
slide for every recorded transfer. Label the as-of date and use the latest
handoff's readiness. Each dated slide explains the ownership/team change,
assessment, commitments, gaps, risks and follow-up actions.

Keep internal employees separate from customer stakeholders. Preserve source IDs
beside claims and complete citations in speaker notes. Add continuation pages when
needed instead of truncating content. Open actions carry forward until a cited
update closes or cancels them.

## Runtime

`scripts/build_deck.mjs` requires Node.js and an installed `@oai/artifact-tool`.
The Codex environment used for this demo supplies that library. It is not part
of Python or bundled with this repository. If needed, set `BATON_NODE_MODULES`
to the existing Node modules directory, and `BATON_PYTHON` to the Python executable.

In Codex, use the workspace-dependencies tool to locate those paths. Do not
hardcode a previous user's computer paths or claim a package is installed when
it is unavailable.

```sh
node scripts/build_deck.mjs --history examples/handoffs/terrapin-history.json --output account-deck.pptx --demo
```

The `--demo` flag labels the fictional example. Omit it for real account histories.

Inspect every rendered slide before delivery. If the presentation dependency is
unavailable, report that the deck could not be rebuilt. The saved sample PPTX
remains viewable and the Python history helper remains usable, but an outline or
history file is not a generated deck.

Manual PowerPoint edits do not flow back into the saved history. The account deck is Baton's customer-specific output; the one-pager is the separate assignment write-up.
