"""Tests voor de sparql_text_errors/sparql_dict_errors-decorators: moeten
zowel sync als async functies correct wrappen (nodig voor tools die
ctx.report_progress() awaiten), en moeten fouten loggen in plaats van ze
stilletjes te verbergen.
"""

import io
import logging
import urllib.error

from rce_cho_mcp.sparql import sparql_dict_errors, sparql_text_errors


def _http_error(code=504, url="https://example.org/sparql", body=b"boom"):
    return urllib.error.HTTPError(url, code, "fout", {}, io.BytesIO(body))


def test_sync_text_errors_happy_path():
    @sparql_text_errors()
    def ok() -> str:
        return "resultaat"

    assert ok() == "resultaat"


def test_sync_text_errors_http_error_logged(caplog):
    @sparql_text_errors()
    def boom() -> str:
        raise _http_error()

    with caplog.at_level(logging.ERROR):
        out = boom()
    assert "HTTP 504" in out
    assert any("boom" in r.message for r in caplog.records)


def test_sync_text_errors_generic_exception(caplog):
    @sparql_text_errors()
    def boom() -> str:
        raise ValueError("kapot")

    with caplog.at_level(logging.ERROR):
        out = boom()
    assert "Onverwachte fout: ValueError" in out


def test_sync_text_errors_include_body():
    @sparql_text_errors(include_body=True)
    def boom() -> str:
        raise _http_error(body=b"een rauwe foutmelding")

    out = boom()
    assert "Ruwe foutmelding" in out
    assert "een rauwe foutmelding" in out


def test_sync_dict_errors_happy_path():
    @sparql_dict_errors
    def ok() -> dict:
        return {"ok": True}

    assert ok() == {"ok": True}


def test_sync_dict_errors_http_error():
    @sparql_dict_errors
    def boom() -> dict:
        raise _http_error(code=500)

    out = boom()
    assert out["status"] == 500


def test_sync_dict_errors_generic_exception():
    @sparql_dict_errors
    def boom() -> dict:
        raise RuntimeError("kapot")

    out = boom()
    assert out["error"] == "unexpected_error"


async def test_async_text_errors_happy_path():
    @sparql_text_errors()
    async def ok() -> str:
        return "async-resultaat"

    assert await ok() == "async-resultaat"


async def test_async_text_errors_http_error():
    @sparql_text_errors()
    async def boom() -> str:
        raise _http_error(code=502)

    out = await boom()
    assert "HTTP 502" in out


async def test_async_dict_errors_happy_path():
    @sparql_dict_errors
    async def ok() -> dict:
        return {"ok": True}

    assert await ok() == {"ok": True}
