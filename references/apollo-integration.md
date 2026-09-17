# Apollo integration

This optional connection brings a current Apollo account record into Baton as
evidence. It is deliberately narrow: read-only, user-selected and local.

## What it does

1. Checks that the locally configured Apollo key works.
2. Searches saved Apollo accounts by name and shows a small list of possible
   matches.
3. Fetches one account only after its ID is chosen and saves a source snapshot.

Use the snapshot to confirm current account context while preparing a handoff.
It does not establish who owned the account before, when a transfer took effect,
or whether the transfer was approved. Those facts still belong in the explicit
handoff event.

## Set it up

Create a **scoped** Apollo API key that can search and view accounts. Save it in
your local environment as `APOLLO_API_KEY`; do not add it to a file in this repo.
The script reads only the account search and account-view endpoints. It never
writes to Apollo.

```sh
python3 scripts/apollo_snapshot.py health
python3 scripts/apollo_snapshot.py search --name "Terrapin Touring Co."
python3 scripts/apollo_snapshot.py snapshot --account-id APOLLO_ACCOUNT_ID --out apollo/account.json
```

The `apollo/` folder is ignored by Git because a real response can contain
customer data. Keep the fictional example data in this repository and keep live
snapshots local.

## Why the selection step matters

Account names are often similar. Baton shows search matches but will not silently
choose one. Supply the correct Apollo account ID to save the snapshot.

The workflow uses Apollo's saved-account search and account-view endpoints. It
does not use person or organization enrichment, so Baton avoids those
credit-consuming calls for this use case.
