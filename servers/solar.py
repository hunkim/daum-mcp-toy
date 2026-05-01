"""daum-solar MCP server (mock).

2 tools: solar_korean_chat, solar_korean_embed.
"""

from __future__ import annotations

import hashlib
import math
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from mocks.data import SOLAR_CHAT_FIXTURES, make_meta, pii_check

mcp = FastMCP("daum-solar")


def _embed(text: str, dim: int = 1024) -> list[float]:
    """Deterministic mock embedding — hash-derived, unit-normalized."""
    h = hashlib.sha256(text.encode("utf-8")).digest()
    raw = [(b - 128) / 128.0 for b in h]
    while len(raw) < dim:
        h = hashlib.sha256(h).digest()
        raw.extend((b - 128) / 128.0 for b in h)
    raw = raw[:dim]
    norm = math.sqrt(sum(x * x for x in raw)) or 1.0
    return [x / norm for x in raw]


@mcp.tool()
def solar_korean_chat(
    messages: list[dict[str, str]],
    grounding: list[Literal["search", "news", "knowledge", "local", "trends"]] | None = None,
    output_lang: Literal["ko", "en", "mixed"] = "ko",
    formality: Literal["formal_polite", "polite", "casual"] = "polite",
    max_tokens: int = 1024,
    temperature: float = 0.3,
) -> dict[str, Any]:
    """Delegate Korean-language reasoning to Solar Pro. Use when the calling
    LLM (Claude/GPT/Gemini) needs Korean nuance — honorifics, legal/medical
    Korean, idiom interpretation, sajeo (사자성어). Solar internally accesses
    Daum knowledge/local/news MCP for grounding."""
    if not messages:
        raise ValueError("messages must contain at least one entry")
    last = next((m for m in reversed(messages) if m.get("role") == "user"), messages[-1])
    last_content = str(last.get("content", ""))
    if err := pii_check(last_content):
        raise ValueError(f"-32008 pii_redaction_required: {err}")
    chosen = next((f for f in SOLAR_CHAT_FIXTURES if f["match"] in last_content), None)
    if chosen:
        content = chosen["content"]
        citations = chosen["citations"] if grounding else []
        score = chosen["score"]
    else:
        content = (
            "[mock Solar Pro4] 죄송합니다. 본 mock 인스턴스에는 해당 질문에 대한 "
            "정형 응답 fixture가 없습니다. 프로덕션에서는 Solar Pro4가 한국어 reasoning과 "
            f"grounding({', '.join(grounding or []) or '없음'})을 결합하여 답합니다."
        )
        citations = []
        score = 0.7
    if output_lang == "en":
        content = "[mock Solar Pro4 EN translation] " + content
    elif output_lang == "mixed":
        content = content + "\n\n[EN summary] mock summary in English."
    return {
        "content": content,
        "grounding_citations": citations,
        "korean_quality_score": score,
        "finish_reason": "stop",
        "model": "solar-pro4-mock",
        "settings": {
            "output_lang": output_lang,
            "formality": formality,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "grounding": grounding or [],
        },
        "_meta": make_meta("solar_korean_chat", last_content[:32], korean_score=score, billed=max(8, len(content) // 4)),
    }


@mcp.tool()
def solar_korean_embed(
    texts: list[str],
    task_type: Literal["retrieval_query", "retrieval_document", "classification", "clustering", "similarity"],
    normalize: bool = True,
) -> dict[str, Any]:
    """Korean-optimized embedding (Solar Embedding-1-Large-Korean).
    Returns 1024-dim vectors. Critical for any RAG over Korean corpora —
    outperforms multilingual embeddings on Korean by significant margin."""
    if not texts:
        raise ValueError("texts must be non-empty")
    if len(texts) > 256:
        raise ValueError("texts exceeds 256 batch limit")
    for t in texts:
        if err := pii_check(t):
            raise ValueError(f"-32008 pii_redaction_required: {err}")
    vectors = [_embed(t) for t in texts]
    return {
        "embeddings": vectors,
        "dim": 1024,
        "task_type_applied": task_type,
        "normalized": normalize,
        "model_version": "solar-embedding-1-large-korean-mock",
        "_meta": make_meta("solar_korean_embed", f"n={len(texts)}|{task_type}", billed=len(texts)),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
