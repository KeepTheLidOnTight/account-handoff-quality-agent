import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("apollo_snapshot", ROOT / "scripts" / "apollo_snapshot.py")
apollo = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(apollo)


class Response:
    def __init__(self, value): self.value = value
    def read(self): return json.dumps(self.value).encode("utf-8")
    def __enter__(self): return self
    def __exit__(self, *unused): return False


class ApolloSnapshotTests(unittest.TestCase):
    def test_missing_key_never_connects(self):
        with self.assertRaisesRegex(apollo.ApolloError, "APOLLO_API_KEY"): apollo.api_key({})

    def test_health_is_read_only(self):
        calls = []
        def opener(request, timeout):
            calls.append(request); return Response({"healthy": True})
        self.assertTrue(apollo.ApolloClient("secret", opener).health()["healthy"])
        self.assertEqual(calls[0].full_url, apollo.API_BASE + "/auth/health")
        self.assertEqual(calls[0].get_method(), "GET")

    def test_search_caps_and_requires_selection(self):
        calls = []
        def opener(request, timeout):
            calls.append(request); return Response({"accounts": [{"id": "a1", "name": "Example"}]})
        result = apollo.summary(apollo.ApolloClient("secret", opener).search_accounts("Example"))
        self.assertTrue(result["selection_required"])
        self.assertEqual(json.loads(calls[0].data.decode())["per_page"], 10)

    def test_snapshot_never_contains_key(self):
        value = apollo.snapshot("a1", {"account": {"name": "Example"}}, Path("apollo/a.json"))
        self.assertTrue(value["api"]["read_only"])
        self.assertNotIn("secret", json.dumps(value))

    def test_safe_http_error(self):
        def opener(request, timeout):
            raise HTTPError(request.full_url, 403, "", {}, io.BytesIO(b'{"message":"Not authorized"}'))
        with self.assertRaisesRegex(apollo.ApolloError, "HTTP 403. Not authorized"):
            apollo.ApolloClient("secret", opener).health()

    def test_missing_folder_writes_nothing(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "missing" / "a.json"
            with self.assertRaises(apollo.ApolloError): apollo.atomic_write(path, {})
            self.assertFalse(path.exists())
