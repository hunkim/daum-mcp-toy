"""HTTP smoke test — boots the ASGI app in-process and probes via the
official MCP streamable-HTTP client. Validates that all four servers are
reachable under their mounted prefixes."""

from __future__ import annotations

import asyncio
import threading
import time

import pytest
import uvicorn

from servers.http_app import app


@pytest.fixture(scope="module")
def server():
    config = uvicorn.Config(app, host="127.0.0.1", port=8771, log_level="warning")
    srv = uvicorn.Server(config)
    thread = threading.Thread(target=srv.run, daemon=True)
    thread.start()
    for _ in range(40):
        if srv.started:
            break
        time.sleep(0.1)
    assert srv.started, "uvicorn failed to start in time"
    yield "http://127.0.0.1:8771"
    srv.should_exit = True
    thread.join(timeout=5)


def test_health(server):
    import urllib.request, json
    body = json.loads(urllib.request.urlopen(f"{server}/health", timeout=2).read())
    assert body["status"] == "ok"
    assert set(body["servers"]) == {"daum-meta", "daum-search", "daum-knowledge", "daum-solar"}


def test_root_inventory(server):
    import urllib.request, json
    body = json.loads(urllib.request.urlopen(f"{server}/", timeout=2).read())
    counts = {s["id"]: s["tool_count"] for s in body["servers"]}
    assert counts == {"daum-meta": 3, "daum-search": 5, "daum-knowledge": 4, "daum-solar": 2}


def test_mcp_initialize_and_call(server):
    from mcp.client.streamable_http import streamablehttp_client
    from mcp.client.session import ClientSession

    async def go():
        async with streamablehttp_client(f"{server}/knowledge/mcp") as (r, w, _):
            async with ClientSession(r, w) as s:
                await s.initialize()
                tools = await s.list_tools()
                assert {t.name for t in tools.tools} == {
                    "dict_lookup", "encyclopedia_lookup", "translate_ko", "korean_etymology",
                }
                res = await s.call_tool(
                    "dict_lookup", {"word": "정산", "direction": "ko-en"},
                )
                assert any("settlement" in c.text.lower() for c in res.content)

    asyncio.run(go())
