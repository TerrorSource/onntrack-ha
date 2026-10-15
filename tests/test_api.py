"""Tests voor de Onntrack API-client (zonder Home Assistant, met nep-sessie).

Draaien met:  pytest tests/  -of-  python3 tests/test_api.py
Vereist: aiohttp (voor de imports in api.py).
"""
from __future__ import annotations

import asyncio
import hashlib
import importlib.util
import sys
import types
from pathlib import Path

_BASE = Path(__file__).resolve().parent.parent / "custom_components" / "onntrack"

# api.py gebruikt relatieve imports; laad const en api als nep-package.
_pkg = types.ModuleType("onntrack_pkg")
_pkg.__path__ = [str(_BASE)]
sys.modules["onntrack_pkg"] = _pkg
for _name in ("const", "api"):
    _spec = importlib.util.spec_from_file_location(
        f"onntrack_pkg.{_name}", _BASE / f"{_name}.py"
    )
    _mod = importlib.util.module_from_spec(_spec)
    sys.modules[f"onntrack_pkg.{_name}"] = _mod
    _spec.loader.exec_module(_mod)

api = sys.modules["onntrack_pkg.api"]


class FakeResponse:
    """Nep aiohttp-respons."""

    def __init__(self, payload=None, status=200, invalid_json=False):
        self._payload = payload
        self.status = status
        self._invalid_json = invalid_json

    async def json(self, content_type=None):
        if self._invalid_json:
            raise ValueError("geen JSON")
        return self._payload


class FakeSession:
    """Nep aiohttp-sessie die geprogrammeerde responses teruggeeft."""

    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    async def post(self, url, json=None, headers=None):
        self.calls.append({"url": url, "json": json, "headers": headers or {}})
        return self.responses.pop(0)


def _login_ok(token="een-heel-lang-token-van-de-api"):
    return FakeResponse({"code": 10000, "data": {"token": token}})


def test_login_success_and_md5_password():
    session = FakeSession([_login_ok()])
    client = api.OnntrackApi(session, "gebruiker", "geheim")
    asyncio.run(client.login())
    sent = session.calls[0]["json"]
    assert sent["password"] == hashlib.md5(b"geheim").hexdigest()
    assert sent["account"] == "gebruiker"


def test_login_token_as_plain_string():
    session = FakeSession(
        [FakeResponse({"code": 10000, "data": "x" * 32})]
    )
    client = api.OnntrackApi(session, "u", "p")
    asyncio.run(client.login())  # geen exceptie = token geaccepteerd


def test_login_wrong_credentials_raises_auth_error():
    session = FakeSession(
        [FakeResponse({"code": 20001, "msg": "AccountPasswordInvalid"})]
    )
    client = api.OnntrackApi(session, "u", "fout")
    try:
        asyncio.run(client.login())
        raise AssertionError("verwachtte OnntrackAuthError")
    except api.OnntrackAuthError:
        pass


def test_login_without_token_raises():
    session = FakeSession([FakeResponse({"code": 10000, "data": {}})])
    client = api.OnntrackApi(session, "u", "p")
    try:
        asyncio.run(client.login())
        raise AssertionError("verwachtte OnntrackAuthError")
    except api.OnntrackAuthError:
        pass


def test_monitor_relogs_in_when_token_expired():
    session = FakeSession([
        _login_ok("token-1-xxxxxxxxxxxxxxxxxxxxx"),       # eerste login
        FakeResponse({"code": 10005}),                     # token verlopen
        _login_ok("token-2-xxxxxxxxxxxxxxxxxxxxx"),       # nieuwe login
        FakeResponse({"code": 10000, "data": [{"modeleName": "basic"}]}),
    ])
    client = api.OnntrackApi(session, "u", "p")
    data = asyncio.run(client.get_monitor_info("12345"))
    assert data == [{"modeleName": "basic"}]
    assert len(session.calls) == 4


def test_http_error_raises_onntrack_error():
    session = FakeSession([FakeResponse({"whatever": 1}, status=502)])
    client = api.OnntrackApi(session, "u", "p")
    try:
        asyncio.run(client.login())
        raise AssertionError("verwachtte OnntrackError")
    except api.OnntrackAuthError:
        raise AssertionError("moet OnntrackError zijn, geen auth-fout")
    except api.OnntrackError:
        pass


def test_invalid_json_raises_onntrack_error():
    session = FakeSession([FakeResponse(invalid_json=True)])
    client = api.OnntrackApi(session, "u", "p")
    try:
        asyncio.run(client.login())
        raise AssertionError("verwachtte OnntrackError")
    except api.OnntrackError:
        pass


def test_non_dict_response_raises_onntrack_error():
    session = FakeSession([FakeResponse(payload=["lijst", "ipv", "dict"])])
    client = api.OnntrackApi(session, "u", "p")
    try:
        asyncio.run(client.login())
        raise AssertionError("verwachtte OnntrackError")
    except api.OnntrackError:
        pass


if __name__ == "__main__":
    fouten = 0
    for naam, fn in sorted(globals().items()):
        if naam.startswith("test_") and callable(fn):
            try:
                fn()
                print(f"OK   {naam}")
            except AssertionError as err:
                fouten += 1
                print(f"FAIL {naam}: {err}")
    raise SystemExit(fouten)
