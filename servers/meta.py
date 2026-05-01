"""daum-meta MCP server (mock).

3 tools: discover_servers, route_intent, bind_server.
"""

from __future__ import annotations

from typing import Any
from datetime import datetime, timedelta, timezone

from mcp.server.fastmcp import FastMCP

from mocks.data import TIER0_SERVERS, ROUTING_RULES, make_meta, _stable_uuid

mcp = FastMCP("daum-meta")


@mcp.tool()
def discover_servers(tenant_id: str = "ten_demo_001", include_health: bool = True) -> dict[str, Any]:
    """List Daum MCP servers available to this tenant + tools each exposes.

    Use AS THE FIRST CALL to plan tool routing for any Korean-context task.
    Returns server_id, base_url, description, tool_count, scopes_required,
    health, and latency_p50_ms for each available server.
    """
    servers = [dict(s) for s in TIER0_SERVERS]
    if not include_health:
        for s in servers:
            s.pop("health", None)
            s.pop("latency_p50_ms", None)
    return {
        "servers": servers,
        "_meta": make_meta("discover_servers", tenant_id, billed=1),
    }


@mcp.tool()
def route_intent(task: str, max_tools: int = 5, allowed_servers: list[str] | None = None) -> dict[str, Any]:
    """Given a natural-language task in Korean or English, return the recommended
    sequence of MCP server.tool calls to fulfill it. Avoids tool overload —
    load only the recommended servers."""
    if not task or len(task) < 3:
        raise ValueError("task must be at least 3 characters")
    plan: list[dict[str, Any]] = []
    matched_keywords: list[str] = []
    for keywords, suggestions in ROUTING_RULES:
        if any(k.lower() in task.lower() for k in keywords):
            matched_keywords.extend(k for k in keywords if k.lower() in task.lower())
            for server, tool, rationale in suggestions:
                if allowed_servers and server not in allowed_servers:
                    continue
                if any(p["server_id"] == server and p["tool_name"] == tool for p in plan):
                    continue
                plan.append({
                    "step": len(plan) + 1,
                    "server_id": server,
                    "tool_name": tool,
                    "rationale_ko": rationale,
                    "expected_inputs": {"task": task},
                })
                if len(plan) >= max_tools:
                    break
        if len(plan) >= max_tools:
            break
    if not plan:
        plan.append({
            "step": 1,
            "server_id": "daum-search",
            "tool_name": "daum_search_web",
            "rationale_ko": "기본 fallback — 웹 검색으로 시작",
            "expected_inputs": {"query": task},
        })
    confidence = 0.6 + 0.1 * len(matched_keywords)
    confidence = min(confidence, 0.98)
    return {
        "plan": plan,
        "matched_keywords": sorted(set(matched_keywords)),
        "confidence": confidence,
        "_meta": make_meta("route_intent", task, korean_score=0.92, billed=2),
    }


@mcp.tool()
def bind_server(server_id: str, scopes: list[str] | None = None) -> dict[str, Any]:
    """Dynamically attach a child server to the active session. Performs
    handshake + token derivation under the parent's OAuth grant. Returns a
    session-scoped tool catalog the agent can immediately call."""
    target = next((s for s in TIER0_SERVERS if s["server_id"] == server_id), None)
    if not target:
        raise ValueError(f"server '{server_id}' not in Tier 0 catalog")
    granted = scopes or target["scopes_required"]
    expires = datetime.now(timezone.utc) + timedelta(hours=1)
    return {
        "session_id": _stable_uuid(f"bind:{server_id}"),
        "server_id": server_id,
        "base_url": target["base_url"],
        "granted_scopes": granted,
        "expires_at": expires.isoformat().replace("+00:00", "Z"),
        "bound_tools_preview": [
            {"name": "(see tools/list of bound server)", "annotations": {"readOnlyHint": True}},
        ],
        "_meta": make_meta("bind_server", server_id),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
