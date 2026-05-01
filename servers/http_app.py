"""Server-side ASGI app — mounts all four Tier 0 MCP servers under a single
host on streamable-HTTP transport.

Endpoints (when bound to e.g. http://0.0.0.0:8000):

    GET  /                       → {"name": "daum-mcp-wrapper", ...}
    GET  /health                 → {"status": "ok", "servers": [...]}
    POST /meta/mcp               → MCP JSON-RPC for daum-meta
    POST /search/mcp             → MCP JSON-RPC for daum-search
    POST /knowledge/mcp          → MCP JSON-RPC for daum-knowledge
    POST /solar/mcp              → MCP JSON-RPC for daum-solar

Run locally:
    uvicorn servers.http_app:app --host 0.0.0.0 --port 8989

Or as a module (defaults to 0.0.0.0:8989):
    python -m servers.http_app

Public test endpoint (when fronted by HTTPS proxy):
    https://daum-mcp.toy.x.upstage.ai/{meta,search,knowledge,solar}/mcp
"""

from __future__ import annotations

import contextlib
import os
from typing import Any

from mcp.server.transport_security import TransportSecuritySettings
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route

from servers.knowledge import mcp as knowledge_mcp
from servers.meta import mcp as meta_mcp
from servers.search import mcp as search_mcp
from servers.solar import mcp as solar_mcp

ALL_SERVERS = [
    ("meta", meta_mcp),
    ("search", search_mcp),
    ("knowledge", knowledge_mcp),
    ("solar", solar_mcp),
]


def _build_security_settings() -> TransportSecuritySettings:
    """DNS-rebinding protection for MCP streamable-HTTP transport.

    The MCP SDK enables this by default and only allows localhost — when
    we're behind a reverse proxy on a public domain, the public Host header
    is rejected with HTTP 421 unless we explicitly allow it.

    Configure via env var:
      DAUM_MCP_ALLOWED_HOSTS="*"                          # disable check
      DAUM_MCP_ALLOWED_HOSTS="daum-mcp.toy.x.upstage.ai"  # pin one
      DAUM_MCP_ALLOWED_HOSTS="a.example.com,b.example.com,localhost:*"
    """
    raw = os.getenv("DAUM_MCP_ALLOWED_HOSTS", "*").strip()
    if raw == "*" or raw == "":
        return TransportSecuritySettings(enable_dns_rebinding_protection=False)
    hosts = [h.strip() for h in raw.split(",") if h.strip()]
    # Always include the local loopbacks so internal health/probe still work.
    for loop in ("127.0.0.1:*", "localhost:*", "[::1]:*"):
        if loop not in hosts:
            hosts.append(loop)
    return TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=hosts,
    )


async def root(_request) -> JSONResponse:
    return JSONResponse(
        {
            "name": "daum-mcp-wrapper",
            "version": "0.1.0",
            "transport": "streamable-http",
            "servers": [
                {
                    "id": f"daum-{prefix}",
                    "endpoint": f"/{prefix}/mcp",
                    "public_url": f"https://daum-mcp.toy.x.upstage.ai/{prefix}/mcp",
                    "tool_count": len(getattr(srv, "_tool_manager", srv)._tools)
                    if hasattr(srv, "_tool_manager")
                    else None,
                }
                for prefix, srv in ALL_SERVERS
            ],
            "docs": "https://github.com/hunkim/daum-mcp-toy",
        }
    )


async def health(_request) -> JSONResponse:
    return JSONResponse(
        {
            "status": "ok",
            "servers": [f"daum-{p}" for p, _ in ALL_SERVERS],
            "mock": True,
        }
    )


@contextlib.asynccontextmanager
async def lifespan(app: Starlette):
    """Forward lifespan to every mounted FastMCP session manager so
    streamable-HTTP state (sessions, SSE pumps) starts and stops cleanly."""
    async with contextlib.AsyncExitStack() as stack:
        for _prefix, srv in ALL_SERVERS:
            await stack.enter_async_context(srv.session_manager.run())
        yield


def build_app() -> Starlette:
    security = _build_security_settings()
    routes: list[Any] = [
        Route("/", root, methods=["GET"]),
        Route("/health", health, methods=["GET"]),
    ]
    for prefix, srv in ALL_SERVERS:
        # MUST set BEFORE streamable_http_app() — the session manager bakes
        # the security settings in at construction time.
        srv.settings.transport_security = security
        routes.append(Mount(f"/{prefix}", app=srv.streamable_http_app()))
    return Starlette(routes=routes, lifespan=lifespan)


app = build_app()


def main() -> None:
    import uvicorn

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8989"))
    uvicorn.run(
        "servers.http_app:app",
        host=host,
        port=port,
        log_level=os.getenv("LOG_LEVEL", "info"),
        reload=os.getenv("RELOAD", "0") == "1",
    )


if __name__ == "__main__":
    main()
