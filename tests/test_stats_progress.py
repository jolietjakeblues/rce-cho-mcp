"""Test voor de progress-callback in stats.dataset_totals().

Mockt execute_sparql() om geen netwerk nodig te hebben en dataset_statistics()
niet de ~1-2 minuten te laten duren die de live full-dataset scans kosten.
"""

import rce_cho_mcp.stats as stats_module


async def test_dataset_totals_without_on_step(monkeypatch):
    monkeypatch.setattr(
        stats_module,
        "execute_sparql",
        lambda query, timeout=0: {"results": {"bindings": [{"n": {"value": "42"}}]}},
    )
    totals = await stats_module.dataset_totals()
    assert totals == {"triples": 42, "entiteiten": 42, "klassen": 42, "properties": 42}


async def test_dataset_totals_reports_progress_for_each_step_plus_final(monkeypatch):
    monkeypatch.setattr(
        stats_module,
        "execute_sparql",
        lambda query, timeout=0: {"results": {"bindings": [{"n": {"value": "1"}}]}},
    )

    calls = []

    async def on_step(progress, total, message):
        calls.append((progress, total, message))

    await stats_module.dataset_totals(on_step=on_step)

    assert len(calls) == 5  # 4 deelqueries + 1 "Klaar."-melding
    assert calls[0] == (0, 4, "Tellen van triples...")
    assert calls[-1] == (4, 4, "Klaar.")


async def test_dataset_statistics_tool_reports_progress_via_context(monkeypatch):
    import rce_cho_mcp.server as server

    monkeypatch.setattr(
        stats_module,
        "execute_sparql",
        lambda query, timeout=0: {"results": {"bindings": [{"n": {"value": "7"}}]}},
    )

    seen = []

    class FakeContext:
        async def report_progress(self, progress, total=None, message=None):
            seen.append((progress, total, message))

    out = await server.dataset_statistics(ctx=FakeContext())
    assert "7" in out
    assert len(seen) == 5
