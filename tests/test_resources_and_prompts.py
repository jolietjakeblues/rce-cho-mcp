"""Tests voor de MCP Resources en Prompts in server.py."""

import rce_cho_mcp.server as server


def test_static_resources_registered():
    keys = set(server.mcp._resource_manager._resources.keys())
    assert keys == {
        "rce-cho://graphs",
        "rce-cho://ontology/statistics",
        "rce-cho://semantics/topics",
    }


def test_semantics_topic_template_registered():
    assert "rce-cho://semantics/{topic}" in server.mcp._resource_manager._templates


async def test_read_graphs_resource():
    result = await server.mcp.read_resource("rce-cho://graphs")
    content = list(result)[0].content
    assert "CHO-KENNIS graphs" in content


async def test_read_ontology_statistics_resource():
    result = await server.mcp.read_resource("rce-cho://ontology/statistics")
    content = list(result)[0].content
    assert "Classes:" in content
    assert "Properties:" in content


async def test_read_semantics_topics_resource():
    result = await server.mcp.read_resource("rce-cho://semantics/topics")
    content = list(result)[0].content
    assert "monument_aard" in content


async def test_read_semantics_topic_template_resource():
    result = await server.mcp.read_resource("rce-cho://semantics/maritime")
    content = list(result)[0].content
    assert "MASS" in content
    assert "query_sparql_mass" in content


def test_prompts_registered():
    assert set(server.mcp._prompt_manager._prompts.keys()) == {
        "zoek_monumenten_in_gemeente",
        "zoek_scheepswrak",
    }


async def test_zoek_monumenten_prompt_renders():
    messages = await server.mcp.get_prompt("zoek_monumenten_in_gemeente", {"gemeente": "Zwolle"})
    text = messages.messages[0].content.text
    assert "Zwolle" in text
    assert "monumenten_in_gemeente" in text


async def test_zoek_scheepswrak_prompt_renders():
    messages = await server.mcp.get_prompt("zoek_scheepswrak", {"naam": "Hendrika"})
    text = messages.messages[0].content.text
    assert "Hendrika" in text
    assert "query_sparql_mass" in text
