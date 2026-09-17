"""Read a selected Apollo account into a local Baton evidence snapshot."""

import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import sys
import tempfile
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


API_BASE = "https://api.apollo.io/api/v1"


class ApolloError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


def api_key(environment=None):
    key = (environment or os.environ).get("APOLLO_API_KEY", "").strip()
    if not key:
        raise ApolloError("missing_api_key", "Set APOLLO_API_KEY locally before connecting to Apollo.")
    return key


def now():
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def safe_detail(raw):
    try:
        value = json.loads(raw)
        if isinstance(value, dict):
            return str(value.get("message") or value.get("error") or "")[:240]
    except json.JSONDecodeError:
        pass
    return raw.strip().replace("\n", " ")[:240]


class ApolloClient:
    def __init__(self, key, opener=urlopen):
        self.key, self.opener = key, opener

    def request(self, path, method="GET", payload=None):
        data = json.dumps(payload).encode("utf-8") if payload is not None else None
        request = Request(API_BASE + path, data=data, method=method, headers={
            "Accept": "application/json", "Content-Type": "application/json", "x-api-key": self.key,
        })
        try:
            with self.opener(request, timeout=20) as response:
                raw = response.read().decode("utf-8")
        except HTTPError as error:
            detail = safe_detail(error.read().decode("utf-8", errors="replace"))
            raise ApolloError("apollo_http_error", f"Apollo returned HTTP {error.code}. {detail}".rstrip()) from error
        except (URLError, OSError) as error:
            raise ApolloError("apollo_connection_error", "Could not reach Apollo. Check your connection and try again.") from error
        try:
            return json.loads(raw)
        except json.JSONDecodeError as error:
            raise ApolloError("invalid_apollo_response", "Apollo returned an unreadable response.") from error

    def health(self):
        return self.request("/auth/health")

    def search_accounts(self, name):
        return self.request("/accounts/search", "POST", {"q_organization_name": name, "page": 1, "per_page": 10})

    def account(self, account_id):
        return self.request(f"/accounts/{account_id}")


def summary(response):
    accounts = response.get("accounts", []) if isinstance(response, dict) else []
    matches = []
    for account in accounts[:10] if isinstance(accounts, list) else []:
        if isinstance(account, dict):
            matches.append({key: account.get(key) for key in ("id", "name", "domain", "website_url")})
    return {"matches": matches, "selection_required": True}


def snapshot(account_id, record, output_path):
    retrieved_at = now()
    account = record.get("account", record) if isinstance(record, dict) else {}
    name = account.get("name") if isinstance(account, dict) else None
    return {
        "schema_version": 1, "retrieved_at": retrieved_at,
        "api": {"service": "Apollo", "endpoint": f"/accounts/{account_id}", "read_only": True},
        "source": {"id": f"apollo-account-{account_id}-{retrieved_at[:10]}", "kind": "Apollo account snapshot",
                   "location": str(output_path), "record_id": account_id, "date": retrieved_at[:10],
                   "excerpt": f"Current Apollo account snapshot for {name or account_id}."},
        "record": record,
    }


def atomic_write(path, value):
    path, pending = Path(path), None
    if not path.parent.is_dir():
        raise ApolloError("missing_output_directory", f"Create the output folder first: {path.parent}")
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False) as stream:
            pending = Path(stream.name)
            json.dump(value, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(pending, path)
    finally:
        if pending is not None and pending.exists():
            pending.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("health")
    search = commands.add_parser("search")
    search.add_argument("--name", required=True)
    save = commands.add_parser("snapshot")
    save.add_argument("--account-id", required=True)
    save.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    try:
        client = ApolloClient(api_key())
        if args.command == "health":
            result = client.health()
        elif args.command == "search":
            result = summary(client.search_accounts(args.name))
        else:
            value = snapshot(args.account_id, client.account(args.account_id), args.out)
            atomic_write(args.out, value)
            result = {"saved": str(args.out), "source": value["source"], "read_only": True}
        print(json.dumps(result, indent=2, ensure_ascii=False))
        return 0
    except (ApolloError, OSError) as error:
        print(json.dumps({"error": {"code": getattr(error, "code", "io_error"), "message": str(error)}}), file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
