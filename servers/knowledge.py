"""daum-knowledge MCP server (mock).

4 tools: dict_lookup, encyclopedia_lookup, translate_ko, korean_etymology.
"""

from __future__ import annotations

from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from mocks.data import (
    DICT_FIXTURES,
    ENCYCLOPEDIA_FIXTURES,
    ETYMOLOGY_FIXTURES,
    TRANSLATE_FIXTURES,
    make_meta,
    pii_check,
)

mcp = FastMCP("daum-knowledge")


@mcp.tool()
def dict_lookup(
    word: str,
    direction: Literal["ko-en", "en-ko", "en-en", "ko-ja", "ja-ko", "ko-zh", "zh-ko", "ko-ko"],
    include_examples: bool = True,
    include_etymology: bool = False,
    domain: Literal["general", "legal", "medical", "IT", "finance"] = "general",
) -> dict[str, Any]:
    """Multi-language dictionary lookup. Supports ko↔en, en↔en, ko↔ja, ko↔zh,
    ko↔ko. Returns senses, examples, IPA, audio URL, frequency band, hanja
    etymology if applicable. CANONICAL Korean lexical grounding tool —
    invoke before translating Korean idioms or domain jargon."""
    if err := pii_check(word):
        raise ValueError(f"-32008 pii_redaction_required: {err}")
    key = (word.strip().lower() if direction.startswith("en") else word.strip(), direction)
    entry = DICT_FIXTURES.get(key)
    if not entry:
        # graceful degraded mock for unknown words
        entry = {
            "senses": [{"pos": "n.", "gloss": f"[mock] no fixture for '{word}' ({direction})", "register": "formal", "examples": []}],
            "pron_ipa": "",
            "audio_url": "",
            "frequency_band": 5,
            "hanja": "",
        }
    out = dict(entry)
    if not include_examples:
        out["senses"] = [{**s, "examples": []} for s in out["senses"]]
    if not include_etymology:
        out.pop("hanja", None)
    out["domain_applied"] = domain
    out["_meta"] = make_meta("dict_lookup", f"{word}|{direction}", billed=1)
    return out


@mcp.tool()
def encyclopedia_lookup(
    entity: str,
    type: Literal["person", "place", "event", "term", "organization", "work", "auto"] = "auto",
    sources: list[Literal["daum_baekgwa", "korean_culture", "disease", "yesform_legal", "eduwill_current_affairs", "korea_local"]] | None = None,
    fields: list[Literal["summary", "infobox", "related", "images", "sources", "license"]] | None = None,
) -> dict[str, Any]:
    """Korean entity lookup across 6 encyclopedias. Caller scopes which
    encyclopedias to query — license-transparent."""
    if err := pii_check(entity):
        raise ValueError(f"-32008 pii_redaction_required: {err}")
    sources = sources or ["daum_baekgwa", "korean_culture"]
    fields = fields or ["summary", "infobox", "related", "license"]
    entry: dict[str, Any] | None = None
    for src in sources:
        candidate = ENCYCLOPEDIA_FIXTURES.get((entity.strip().lower(), src))
        if candidate:
            entry = candidate
            break
    if not entry:
        entry = {
            "title": entity,
            "summary": f"[mock] '{entity}'에 대한 백과 항목 (sources={sources})",
            "infobox": {},
            "related": [],
            "sources_used": sources[:1],
            "license": "mock-license",
        }
    out = {k: entry[k] for k in entry if k in {"title", *fields, "sources_used"}}
    out["entity_id"] = f"ent_{abs(hash((entity, tuple(sources)))) % 10**8:08d}"
    out["type_applied"] = type
    out["_meta"] = make_meta("encyclopedia_lookup", f"{entity}|{','.join(sources)}", billed=2)
    return out


@mcp.tool()
def translate_ko(
    text: str,
    direction: Literal["ko-en", "en-ko", "ko-ja", "ja-ko", "ko-zh", "zh-ko"],
    domain: Literal["general", "business", "legal", "medical", "casual", "literary"] = "general",
    formality: Literal["formal_polite", "polite", "casual", "very_casual"] = "polite",
    preserve_terms: list[str] | None = None,
) -> dict[str, Any]:
    """Solar-Pro powered translation, Korean-anchored. Combines dictionary
    lookup + LLM translation in one composite call. Domain-aware, with
    formality / honorific control."""
    if err := pii_check(text):
        raise ValueError(f"-32008 pii_redaction_required: {err}")
    if len(text) > 10000:
        raise ValueError("text exceeds 10000 char limit")
    fixture = TRANSLATE_FIXTURES.get((text.strip(), direction))
    if not fixture:
        # generic mock — pretend Solar Pro4 translated
        if direction == "ko-en":
            translation = f"[mock-en] {text}"
        elif direction == "en-ko":
            translation = f"[mock-ko] {text}"
        else:
            translation = f"[mock-{direction}] {text}"
        fixture = {
            "translation": translation,
            "confidence": 0.82,
            "alternatives": [],
            "terminology_notes": [],
        }
    out = dict(fixture)
    out["direction"] = direction
    out["domain_applied"] = domain
    out["formality_applied"] = formality
    out["preserve_terms_applied"] = preserve_terms or []
    out["_meta"] = make_meta("translate_ko", f"{direction}|{text[:20]}", billed=max(1, len(text) // 100))
    return out


@mcp.tool()
def korean_etymology(
    word: str,
    time_window: Literal["contemporary", "modern", "premodern", "all"] = "all",
) -> dict[str, Any]:
    """한자/외래어 어원, 동음이의어 disambiguation, 시대별 의미 변화.
    Surface Sino-Korean roots, Japanese loanwords, recent neologisms."""
    if err := pii_check(word):
        raise ValueError(f"-32008 pii_redaction_required: {err}")
    fixture = ETYMOLOGY_FIXTURES.get(word.strip())
    if not fixture:
        fixture = {
            "hanja": "",
            "origin_lang": "native_korean",
            "history": [{"era": "modern", "note": f"[mock] '{word}' 어원 정보 미수록"}],
            "homophones": [],
        }
    out = dict(fixture)
    if time_window != "all":
        out["history"] = [h for h in out["history"] if h["era"] == time_window]
    out["_meta"] = make_meta("korean_etymology", word, billed=1)
    return out


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
