"""daum-search MCP server (mock).

5 tools: daum_search_web, daum_search_news, daum_search_realtime_panel,
daum_search_voice, daum_search_image_query.
"""

from __future__ import annotations

import base64
from typing import Any, Literal

from mcp.server.fastmcp import FastMCP

from mocks.data import (
    NEWS_RESULTS,
    REALTIME_PANEL_FIXTURES,
    WEB_RESULTS,
    make_meta,
    pii_check,
)

mcp = FastMCP("daum-search")


@mcp.tool()
def daum_search_web(
    query: str,
    size: int = 10,
    cursor: str | None = None,
    freshness: Literal["any", "day", "week", "month", "year"] = "any",
    site_filter: str | None = None,
    korean_only: bool = False,
    safe_search: Literal["strict", "moderate", "off"] = "moderate",
) -> dict[str, Any]:
    """Search Korean web pages using Daum's 30-year Korean-optimized index.

    Use this when the query is in Korean, mentions Korea, or needs Korean
    primary sources. Outperforms Google/Bing on Tistory, 다음 카페, Korean
    news, and vernacular Korean. Returns korean_score per result.
    """
    if err := pii_check(query):
        raise ValueError(f"-32008 pii_redaction_required: {err}")
    if not 1 <= size <= 50:
        raise ValueError("size must be in [1, 50]")
    items = list(WEB_RESULTS["default"])[:size]
    if site_filter:
        if site_filter.startswith("!"):
            block = site_filter[1:]
            items = [i for i in items if block not in i["url"]]
        else:
            items = [i for i in items if site_filter in i["url"]]
    if korean_only:
        items = [i for i in items if i["korean_score"] >= 0.9]
    return {
        "items": items,
        "next_cursor": None if len(items) < size else "cursor_demo_2",
        "total_estimated": 1247,
        "query_echo": query,
        "freshness_applied": freshness,
        "_meta": make_meta("daum_search_web", query, billed=max(1, len(items) // 5)),
    }


@mcp.tool()
def daum_search_news(
    query: str,
    date_from: str | None = None,
    date_to: str | None = None,
    publishers: list[str] | None = None,
    region: Literal["national", "local", "international"] | None = None,
    summary: Literal["none", "short", "medium", "long"] = "short",
    include_sentiment: bool = True,
    size: int = 20,
) -> dict[str, Any]:
    """Search Korean news with publisher and date filters. Composite — each
    item includes Solar-generated Korean summary, sentiment, and entities,
    so the agent does NOT need follow-up fetch+summarize calls."""
    if err := pii_check(query):
        raise ValueError(f"-32008 pii_redaction_required: {err}")
    items = list(NEWS_RESULTS["default"])[:size]
    if publishers:
        items = [i for i in items if i["publisher"] in publishers]
    if summary == "none":
        for i in items:
            i = dict(i)
            i.pop("summary_ko", None)
    if not include_sentiment:
        for i in items:
            i.pop("sentiment", None)
    return {
        "items": items,
        "related_topics": ["Solar Pro4", "Daum Agent Portal", "한국어 LLM", "MCP"],
        "filters_applied": {
            "date_from": date_from,
            "date_to": date_to,
            "publishers": publishers,
            "region": region,
        },
        "_meta": make_meta("daum_search_news", query, billed=2 + len(items)),
    }


@mcp.tool()
def daum_search_realtime_panel(
    query: str,
    widgets: list[Literal["weather", "fx", "stock", "sports_score", "box_office", "news_box", "related_queries", "trends"]] | None = None,
) -> dict[str, Any]:
    """Daum 통합검색 widget panel — for a query, returns the live widgets
    Daum exposes (날씨, 환율, 주가, 스포츠 스코어, 박스오피스, 뉴스 박스,
    관련 검색어, 실시간 트렌드) in a single composite call. 1-stop grounding
    for everyday Korean queries."""
    selected = widgets or [
        "weather", "fx", "stock", "sports_score", "box_office", "news_box", "related_queries",
    ]
    fixtures = REALTIME_PANEL_FIXTURES["default_widgets"]
    out: dict[str, Any] = {w: fixtures[w] for w in selected if w in fixtures}
    return {
        "query_echo": query,
        "widgets": out,
        "_meta": make_meta("daum_search_realtime_panel", query, billed=len(selected)),
    }


@mcp.tool()
def daum_search_voice(
    audio_base64: str,
    audio_format: Literal["wav", "mp3", "m4a", "webm", "flac"],
    sample_rate_hz: int = 16000,
    search_after_transcription: bool = True,
) -> dict[str, Any]:
    """Korean speech audio → query transcription → web/news search results
    in one composite call. Solar Korean ASR (vernacular, dialect, code-switch)."""
    try:
        raw = base64.b64decode(audio_base64, validate=False)
    except Exception as e:
        raise ValueError(f"audio_base64 decode failed: {e}") from None
    duration_s_est = max(0.1, len(raw) / max(sample_rate_hz, 1) / 2)
    transcript = "오늘 강남 날씨 어때?"  # mock
    result: dict[str, Any] = {
        "transcript": transcript,
        "confidence": 0.93,
        "duration_sec_estimated": round(duration_s_est, 2),
        "format": audio_format,
        "_meta": make_meta("daum_search_voice", transcript, billed=3),
    }
    if search_after_transcription:
        result["search_results"] = WEB_RESULTS["default"][:3]
    return result


@mcp.tool()
def daum_search_image_query(
    image_base64: str,
    mode: Literal["similar", "identify_plant", "identify_object", "ocr", "product_match"] = "similar",
    max_results: int = 10,
) -> dict[str, Any]:
    """Image-as-query search. Modes — similar / identify_plant (다음 '꽃검색'
    일반화) / identify_object / OCR / product_match. Korean products,
    plants, landmarks indexed."""
    try:
        raw = base64.b64decode(image_base64, validate=False)
    except Exception as e:
        raise ValueError(f"image_base64 decode failed: {e}") from None
    payload_size = len(raw)
    if mode == "identify_plant":
        results = [
            {"name": "벚꽃 (Prunus serrulata)", "confidence": 0.91, "common_names_ko": ["벚꽃", "사쿠라"]},
            {"name": "겹벚꽃 (Prunus serrulata 'Kanzan')", "confidence": 0.06},
        ]
    elif mode == "ocr":
        results = [{"text": "강남구 테헤란로 123\n2층 카페 라떼", "confidence": 0.97, "blocks": 2}]
    elif mode == "product_match":
        results = [
            {"product_id": "kakao_makers_4823", "title": "수제 도자기 머그", "merchant": "카카오메이커스", "price_krw": 28000, "match_score": 0.88},
        ]
    elif mode == "identify_object":
        results = [
            {"label_ko": "남산타워", "label_en": "N Seoul Tower", "confidence": 0.95},
        ]
    else:  # similar
        results = [
            {"image_url": "https://img.daum.net/example/abc1.jpg", "page_url": "https://travel.daum.net/page/x", "similarity": 0.83},
            {"image_url": "https://img.daum.net/example/abc2.jpg", "page_url": "https://blog.tistory.com/y", "similarity": 0.79},
        ]
    return {
        "mode": mode,
        "results": results[:max_results],
        "image_bytes_received": payload_size,
        "_meta": make_meta("daum_search_image_query", f"{mode}:{payload_size}", billed=4),
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()
