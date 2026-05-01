"""Smoke tests — exercise every Tier 0 tool end-to-end.

Run: pytest -q from daum_mcp_mock/
"""

from __future__ import annotations

import base64

import pytest

from servers import meta as meta_mod
from servers import search as search_mod
from servers import knowledge as kn_mod
from servers import solar as solar_mod


def _call(server_module, tool_name: str, **kwargs):
    """Invoke a FastMCP-registered tool by name on a server module."""
    mcp = server_module.mcp
    # FastMCP keeps a registry of tools; fetch the underlying callable.
    # The decorator preserves the original function on the module, so we
    # prefer that path for sync invocation.
    fn = getattr(server_module, tool_name)
    return fn(**kwargs)


# ─────────────────────────── meta ───────────────────────────

def test_meta_discover_servers():
    out = _call(meta_mod, "discover_servers")
    assert "servers" in out and len(out["servers"]) == 4
    ids = {s["server_id"] for s in out["servers"]}
    assert ids == {"daum-search", "daum-knowledge", "daum-solar", "daum-meta"}
    assert out["_meta"]["mock"] is True


def test_meta_route_intent_korean():
    out = _call(meta_mod, "route_intent", task="강남 날씨 알려줘")
    assert out["plan"], "plan must not be empty"
    assert out["plan"][0]["server_id"] == "daum-search"
    assert any(p["tool_name"] == "daum_search_realtime_panel" for p in out["plan"])


def test_meta_route_intent_dictionary():
    out = _call(meta_mod, "route_intent", task="'정산'의 영어 뜻이 뭐야?")
    tools = [p["tool_name"] for p in out["plan"]]
    assert "dict_lookup" in tools


def test_meta_bind_server_known():
    out = _call(meta_mod, "bind_server", server_id="daum-search")
    assert out["server_id"] == "daum-search"
    assert out["expires_at"].endswith("Z")


def test_meta_bind_server_unknown():
    with pytest.raises(ValueError):
        _call(meta_mod, "bind_server", server_id="nonexistent")


# ─────────────────────────── search ─────────────────────────

def test_search_web():
    out = _call(search_mod, "daum_search_web", query="청계천", size=5)
    assert out["items"], "should return items"
    assert out["query_echo"] == "청계천"
    assert all(0 <= i["korean_score"] <= 1 for i in out["items"])


def test_search_web_pii_blocks():
    with pytest.raises(ValueError, match="pii_redaction_required"):
        _call(search_mod, "daum_search_web", query="홍길동 주민번호 901010-1234567")


def test_search_web_site_filter():
    out = _call(search_mod, "daum_search_web", query="청계천", site_filter="tistory.com")
    assert all("tistory.com" in i["url"] for i in out["items"])


def test_search_news_composite():
    out = _call(search_mod, "daum_search_news", query="Solar Pro4")
    assert out["items"]
    assert all("summary_ko" in i for i in out["items"])
    assert all("sentiment" in i for i in out["items"])


def test_search_realtime_panel_default():
    out = _call(search_mod, "daum_search_realtime_panel", query="강남 날씨")
    assert "weather" in out["widgets"]
    assert "fx" in out["widgets"]
    assert "related_queries" in out["widgets"]


def test_search_realtime_panel_subset():
    out = _call(
        search_mod, "daum_search_realtime_panel",
        query="환율", widgets=["fx", "stock"],
    )
    assert set(out["widgets"].keys()) == {"fx", "stock"}


def test_search_voice():
    audio = base64.b64encode(b"\x00" * 32000).decode()
    out = _call(
        search_mod, "daum_search_voice",
        audio_base64=audio, audio_format="wav",
    )
    assert "transcript" in out
    assert out["confidence"] > 0
    assert "search_results" in out


def test_search_image_query_plant():
    img = base64.b64encode(b"\x89PNG\r\n\x1a\n" + b"\x00" * 256).decode()
    out = _call(search_mod, "daum_search_image_query", image_base64=img, mode="identify_plant")
    assert out["mode"] == "identify_plant"
    assert out["results"][0]["confidence"] >= 0.5


# ─────────────────────────── knowledge ──────────────────────

def test_dict_lookup_known():
    out = _call(kn_mod, "dict_lookup", word="정산", direction="ko-en", include_etymology=True)
    assert any("settlement" in s["gloss"].lower() for s in out["senses"])
    assert out["hanja"] == "精算"


def test_dict_lookup_unknown_returns_mock():
    out = _call(kn_mod, "dict_lookup", word="없는단어아주이상한", direction="ko-en")
    assert out["senses"][0]["gloss"].startswith("[mock]")


def test_encyclopedia_korean_culture():
    out = _call(
        kn_mod, "encyclopedia_lookup",
        entity="한강", sources=["korean_culture"],
    )
    assert "한강" in out["title"]
    assert "korean_culture" in out["sources_used"]


def test_translate_known():
    out = _call(
        kn_mod, "translate_ko",
        text="월말까지 정산을 마감해 주세요.",
        direction="ko-en",
    )
    assert "settlement" in out["translation"].lower()
    assert out["confidence"] > 0.9


def test_translate_too_long():
    with pytest.raises(ValueError):
        _call(kn_mod, "translate_ko", text="가" * 10001, direction="ko-en")


def test_etymology_known():
    out = _call(kn_mod, "korean_etymology", word="정산")
    assert out["hanja"] == "精算"
    assert out["origin_lang"] == "sino_korean"


def test_etymology_time_window_filter():
    out = _call(kn_mod, "korean_etymology", word="정산", time_window="modern")
    assert all(h["era"] == "modern" for h in out["history"])


# ─────────────────────────── solar ──────────────────────────

def test_solar_chat_known_match():
    out = _call(
        solar_mod, "solar_korean_chat",
        messages=[{"role": "user", "content": "한강에 대해 알려줘"}],
        grounding=["knowledge"],
    )
    assert "한강" in out["content"]
    assert out["grounding_citations"], "grounding requested → citations"
    assert out["korean_quality_score"] > 0.9


def test_solar_chat_no_grounding_no_citations():
    out = _call(
        solar_mod, "solar_korean_chat",
        messages=[{"role": "user", "content": "정산"}],
    )
    assert out["grounding_citations"] == []


def test_solar_chat_empty_raises():
    with pytest.raises(ValueError):
        _call(solar_mod, "solar_korean_chat", messages=[])


def test_solar_embed_shape():
    out = _call(
        solar_mod, "solar_korean_embed",
        texts=["안녕하세요", "Daum Agent Portal"],
        task_type="retrieval_document",
    )
    assert out["dim"] == 1024
    assert len(out["embeddings"]) == 2
    assert len(out["embeddings"][0]) == 1024
    # unit-normalized
    norm = sum(x * x for x in out["embeddings"][0]) ** 0.5
    assert abs(norm - 1.0) < 1e-6


def test_solar_embed_too_many_raises():
    with pytest.raises(ValueError):
        _call(
            solar_mod, "solar_korean_embed",
            texts=["x"] * 257, task_type="similarity",
        )
