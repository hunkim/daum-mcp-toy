# daum-mcp-toy

Mock MCP servers for **Daum Agent Portal** — Tier 0 (Day 1-7 demo gate).
**4 servers · 14 Korean-context tools · live at `https://daum-mcp.toy.x.upstage.ai`.**

> *Korea's Agent grounding layer. People's Portal → Agent's Portal.*

---

## ▶︎ Add to your Claude / Cursor / VS Code in 10 seconds

### Claude.ai (web, Pro / Team / Enterprise) — Custom Connectors

[![Open Claude.ai connector settings](https://img.shields.io/badge/Add%20to-Claude.ai-DA7756?logo=anthropic&logoColor=white&style=for-the-badge)](https://claude.ai/settings/connectors)

1. Click the badge → **"Add custom connector"**
2. Paste each URL below as a separate connector (name them anything):
   ```
   https://daum-mcp.toy.x.upstage.ai/meta/mcp
   https://daum-mcp.toy.x.upstage.ai/search/mcp
   https://daum-mcp.toy.x.upstage.ai/knowledge/mcp
   https://daum-mcp.toy.x.upstage.ai/solar/mcp
   ```
3. No auth required (toy server). All 14 tools appear in your chat tools tray.

### Claude Desktop (macOS / Windows)

Append the following block to `~/Library/Application Support/Claude/claude_desktop_config.json`
(macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows), then restart Claude:

```json
{
  "mcpServers": {
    "daum-meta":      { "type": "http", "url": "https://daum-mcp.toy.x.upstage.ai/meta/mcp" },
    "daum-search":    { "type": "http", "url": "https://daum-mcp.toy.x.upstage.ai/search/mcp" },
    "daum-knowledge": { "type": "http", "url": "https://daum-mcp.toy.x.upstage.ai/knowledge/mcp" },
    "daum-solar":     { "type": "http", "url": "https://daum-mcp.toy.x.upstage.ai/solar/mcp" }
  }
}
```

### Cursor — one-click install (4 buttons)

[![Add daum-meta to Cursor](https://img.shields.io/badge/Cursor-Add%20daum--meta-000?logo=cursor&style=flat-square)](cursor://anysphere.cursor-deeplink/mcp/install?name=daum-meta&config=eyJ1cmwiOiJodHRwczovL2RhdW0tbWNwLnRveS54LnVwc3RhZ2UuYWkvbWV0YS9tY3AifQ==)
[![Add daum-search to Cursor](https://img.shields.io/badge/Cursor-Add%20daum--search-000?logo=cursor&style=flat-square)](cursor://anysphere.cursor-deeplink/mcp/install?name=daum-search&config=eyJ1cmwiOiJodHRwczovL2RhdW0tbWNwLnRveS54LnVwc3RhZ2UuYWkvc2VhcmNoL21jcCJ9)
[![Add daum-knowledge to Cursor](https://img.shields.io/badge/Cursor-Add%20daum--knowledge-000?logo=cursor&style=flat-square)](cursor://anysphere.cursor-deeplink/mcp/install?name=daum-knowledge&config=eyJ1cmwiOiJodHRwczovL2RhdW0tbWNwLnRveS54LnVwc3RhZ2UuYWkva25vd2xlZGdlL21jcCJ9)
[![Add daum-solar to Cursor](https://img.shields.io/badge/Cursor-Add%20daum--solar-000?logo=cursor&style=flat-square)](cursor://anysphere.cursor-deeplink/mcp/install?name=daum-solar&config=eyJ1cmwiOiJodHRwczovL2RhdW0tbWNwLnRveS54LnVwc3RhZ2UuYWkvc29sYXIvbWNwIn0=)

### VS Code (1.99+ Copilot MCP) — one-click install (4 buttons)

[![Install daum-meta in VS Code](https://img.shields.io/badge/VS%20Code-Install%20daum--meta-007ACC?logo=visualstudiocode&style=flat-square)](vscode:mcp/install?%7B%22name%22%3A%22daum-meta%22%2C%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fdaum-mcp.toy.x.upstage.ai%2Fmeta%2Fmcp%22%7D)
[![Install daum-search in VS Code](https://img.shields.io/badge/VS%20Code-Install%20daum--search-007ACC?logo=visualstudiocode&style=flat-square)](vscode:mcp/install?%7B%22name%22%3A%22daum-search%22%2C%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fdaum-mcp.toy.x.upstage.ai%2Fsearch%2Fmcp%22%7D)
[![Install daum-knowledge in VS Code](https://img.shields.io/badge/VS%20Code-Install%20daum--knowledge-007ACC?logo=visualstudiocode&style=flat-square)](vscode:mcp/install?%7B%22name%22%3A%22daum-knowledge%22%2C%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fdaum-mcp.toy.x.upstage.ai%2Fknowledge%2Fmcp%22%7D)
[![Install daum-solar in VS Code](https://img.shields.io/badge/VS%20Code-Install%20daum--solar-007ACC?logo=visualstudiocode&style=flat-square)](vscode:mcp/install?%7B%22name%22%3A%22daum-solar%22%2C%22type%22%3A%22http%22%2C%22url%22%3A%22https%3A%2F%2Fdaum-mcp.toy.x.upstage.ai%2Fsolar%2Fmcp%22%7D)

### ChatGPT Desktop (Plus / Pro) · Gemini Enterprise · OpenClaw / agent SDKs

Any MCP-compliant client takes URLs directly. Paste the four `/mcp` URLs above
into the client's "MCP server" / "Connector" / "Tool extension" UI.

### Verify (no install)

```bash
curl -s https://daum-mcp.toy.x.upstage.ai/health
# → {"status":"ok","servers":["daum-meta","daum-search","daum-knowledge","daum-solar"],"mock":true}
```

### Try it (sample prompts)

> *"강남 날씨랑 환율 알려줘"* &nbsp;·&nbsp; *"'정산'을 영어로, 한자 어원도"*  &nbsp;·&nbsp; *"한강에 대해 한국어 격식체로 정리해줘"*

---

This package implements 4 MCP servers and 14 tools as defined in the
`daum_mcp_specification.md` v1.0 spec. The mock layer is response-shape
identical to the production schema — swap the `mocks/data.py` fixtures
with live calls to `api.daum.upstage.ai` when the upstream is provisioned.

| Server | Tools | Scopes |
|--------|-------|--------|
| `daum-meta` | `discover_servers`, `route_intent`, `bind_server` | `meta:*` |
| `daum-search` | `daum_search_web`, `daum_search_news`, `daum_search_realtime_panel`, `daum_search_voice`, `daum_search_image_query` | `search.*:read` |
| `daum-knowledge` | `dict_lookup`, `encyclopedia_lookup`, `translate_ko`, `korean_etymology` | `knowledge.*:read` |
| `daum-solar` | `solar_korean_chat`, `solar_korean_embed` | `solar.*:execute` |

All responses include the canonical `_meta` block (request_id, tenant_id,
consent_status, data_freshness_ts, rate_limit_remaining, tokens_billed,
korean_score, license).

---

## Quickstart

```bash
git clone <this-repo>
cd daum-mcp-wrapper

python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"

# smoke tests (25 cases)
pytest -q

# inspector / dev UI
mcp dev servers/search.py

# stdio launch (for embedding in a host)
python -m servers.search
python -m servers.knowledge
python -m servers.solar
python -m servers.meta

# HTTP launch — single host, all 4 servers under /{prefix}/mcp
python -m servers.http_app                # 0.0.0.0:8989  (default)
PORT=9000 python -m servers.http_app      # custom port

# Or with uvicorn directly (e.g. behind a reverse proxy)
uvicorn servers.http_app:app --host 0.0.0.0 --port 8989 --workers 4
```

## Server-side deployment (HTTP)

```bash
# Docker
docker build -t daum-mcp-wrapper:0.1.0 .
docker run --rm -p 8989:8989 daum-mcp-wrapper:0.1.0

# Compose
docker compose up -d
curl http://127.0.0.1:8989/health
```

Test deployment is provisioned at **`https://daum-mcp.toy.x.upstage.ai`**
(HTTPS reverse proxy in front of the container on port 8989).

Endpoints once running:

| Path | What it serves |
|------|----------------|
| `GET  /` | server inventory (id, endpoint, tool_count) |
| `GET  /health` | liveness — used by k8s / docker healthcheck |
| `POST /meta/mcp` | MCP JSON-RPC for daum-meta |
| `POST /search/mcp` | MCP JSON-RPC for daum-search |
| `POST /knowledge/mcp` | MCP JSON-RPC for daum-knowledge |
| `POST /solar/mcp` | MCP JSON-RPC for daum-solar |

### Connect a remote MCP client

```python
from mcp.client.streamable_http import streamablehttp_client
from mcp.client.session import ClientSession

async with streamablehttp_client("https://daum-mcp.toy.x.upstage.ai/search/mcp") as (r, w, _):
    async with ClientSession(r, w) as s:
        await s.initialize()
        result = await s.call_tool(
            "daum_search_realtime_panel",
            {"query": "강남 날씨"},
        )
```

### Claude Desktop with a remote endpoint

Once you have an HTTPS reverse proxy in front (nginx / caddy / cloudflare):

```json
{
  "mcpServers": {
    "daum-meta":      { "url": "https://daum-mcp.toy.x.upstage.ai/meta/mcp" },
    "daum-search":    { "url": "https://daum-mcp.toy.x.upstage.ai/search/mcp" },
    "daum-knowledge": { "url": "https://daum-mcp.toy.x.upstage.ai/knowledge/mcp" },
    "daum-solar":     { "url": "https://daum-mcp.toy.x.upstage.ai/solar/mcp" }
  }
}
```

## Wire up to Claude Desktop (local stdio)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "daum-meta": {
      "command": "/absolute/path/daum-mcp-wrapper/.venv/bin/python",
      "args": ["-m", "servers.meta"],
      "cwd": "/absolute/path/daum-mcp-wrapper"
    },
    "daum-search": {
      "command": "/absolute/path/daum-mcp-wrapper/.venv/bin/python",
      "args": ["-m", "servers.search"],
      "cwd": "/absolute/path/daum-mcp-wrapper"
    },
    "daum-knowledge": {
      "command": "/absolute/path/daum-mcp-wrapper/.venv/bin/python",
      "args": ["-m", "servers.knowledge"],
      "cwd": "/absolute/path/daum-mcp-wrapper"
    },
    "daum-solar": {
      "command": "/absolute/path/daum-mcp-wrapper/.venv/bin/python",
      "args": ["-m", "servers.solar"],
      "cwd": "/absolute/path/daum-mcp-wrapper"
    }
  }
}
```

Restart Claude Desktop. You should see all 14 tools available.

## Try it (sample agent prompts)

- *"Daum의 MCP 서버 목록을 한 번에 알려줘."* → `discover_servers`
- *"강남 날씨와 환율을 한 번에 보여줘."* → `daum_search_realtime_panel`
- *"'정산'을 영어로 옮기면? 어원도 같이."* → `dict_lookup` + `korean_etymology`
- *"한강에 대해 한국어로 정리해주고 출처를 달아줘."* → `solar_korean_chat(grounding=["knowledge"])`
- *"청계천 관련 최신 글 5개를 Tistory에서만."* → `daum_search_web(site_filter="tistory.com")`

## Architecture

```
daum-mcp-wrapper/
├── pyproject.toml          # package + entrypoints
├── servers/
│   ├── meta.py             # daum-meta — discovery + routing
│   ├── search.py           # daum-search — 5 tools (web/news/panel/voice/image)
│   ├── knowledge.py        # daum-knowledge — 4 tools (dict/wiki/translate/etymology)
│   └── solar.py            # daum-solar — 2 tools (chat/embed)
├── mocks/
│   └── data.py             # deterministic fixtures (swap with live HTTP)
└── tests/
    └── test_smoke.py       # 25 cases — every tool, happy + error paths
```

Each server uses **FastMCP** so adding a tool is one decorated function.
Response shapes mirror `tier0_openapi.yaml` exactly, including the
`_meta` envelope and standardized error paths (PII auto-block raises
`-32008 pii_redaction_required` on the wire equivalent).

## Going live

1. **Replace fixtures** in `mocks/data.py` with HTTP calls (httpx) to
   real Daum/Solar endpoints. Keep the function signatures identical.
2. **Add OAuth 2.1 + PKCE-S256 + RFC 8707** middleware (FastMCP
   exposes `mcp.run(transport="streamable-http")` for HTTP transport).
3. **Wire the audit log** — every `_meta.request_id` gets an
   HMAC-signed entry per `hitl_ux_specification.md` §4.
4. **Tighten PII**: replace the regex stub with KISA-grade patterns +
   Solar Korean PII classifier.
5. **Tier 1 onwards**: add the remaining 15 servers (101 more tools)
   following the same FastMCP shape.

## Acceptance criteria (Day 7 demo gate)

See `tier0_openapi.yaml` `x-acceptance-criteria` (AC-1 through AC-10).
Currently AC-1 to AC-5 are validated by `tests/test_smoke.py`; AC-6
through AC-10 require the OAuth + audit middleware (Tier 0 W2).

## License

Internal — Upstage / Daum. See `LICENSE`.
