# Baton

Baton keeps one account handoff deck current as an account moves between internal
owners or teams. The opening pages show the current owner, context and unfinished
work. Each transfer adds one dated page, so the original handoff record stays
easy to find.

Open the [example deck](examples/terrapin-account-deck.pptx). It follows a
fictional account from Sales to Implementation, then Customer Success.

## Start here

Ask your coding agent to follow [SKILL.md](SKILL.md) and rebuild the Terrapin
deck from the history in `examples/handoffs`. It will review the account, show
the current owner and open actions, and preserve both dated handoffs.

The project has two small helpers:

```sh
python3 scripts/analyze_handoff.py
python3 scripts/manage_handoffs.py view --history examples/handoffs/terrapin-history.json
```

The first checks a Closed Won sales handoff. The second reads the saved history
and derives the current owner and open work. To record a new, prepared transfer:

```sh
python3 scripts/manage_handoffs.py add --history account-history.json --event new-handoff.json
```

Then rebuild the deck:

```sh
node scripts/build_deck.mjs --history account-history.json --output account-deck.pptx --demo
```

Deck creation needs Node.js and `@oai/artifact-tool`; the saved example deck is
ready to open without any setup.

## Optional Apollo connection

Baton can retrieve a **read-only current account snapshot** from Apollo. It
checks the key, searches your saved Apollo accounts, and fetches the account you
choose. It does not write to Apollo, detect a historical transfer, or add one to
Baton automatically.

Create a scoped Apollo API key with access to account search and account view,
then keep it in your local environment as `APOLLO_API_KEY`. Do not put the key or
real account snapshots in this public repository.

```sh
python3 scripts/apollo_snapshot.py health
python3 scripts/apollo_snapshot.py search --name "Account name"
python3 scripts/apollo_snapshot.py snapshot --account-id APOLLO_ACCOUNT_ID --out apollo/account.json
```

Use the saved snapshot as current-account evidence when preparing a transfer.
The prior owner, new owner and effective date still need to be supplied and
reviewed explicitly. See [Apollo integration notes](references/apollo-integration.md).

## Demo material

The [one-pager](docs/one-pager.pdf), [single summary slide](docs/demo-slide.pptx),
[Loom walkthrough](docs/loom-walkthrough.md) and
[interview prep](docs/interview-prep.md) are ready for the assignment. Record a
Loom under five minutes, then add its link here before submitting.

## Check it

```sh
python3 -B -m unittest discover -s tests -v
```

All included records are fictional. See [the handoff schema](references/handoff-schema.md)
for the event format and [deck guidance](references/deck-output.md) for what the
deck preserves.
