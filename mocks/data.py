"""Static mock fixtures for Tier 0 Daum MCP servers.

These are NOT real Daum data — they are deterministic stand-ins shaped
exactly like the production response schemas. Swap with live calls
to api.daum.upstage.ai once provisioned.
"""

from __future__ import annotations

import hashlib
from datetime import datetime, timezone

# ---------------------------------------------------------------
# Server registry (used by daum-meta.discover_servers)
# ---------------------------------------------------------------
TIER0_SERVERS = [
    {
        "server_id": "daum-search",
        "base_url": "https://mcp.daum.upstage.ai/search",
        "description": "30년 한국어 인덱스 + 멀티모달 검색",
        "tool_count": 5,
        "scopes_required": [
            "search.web:read", "search.news:read", "search.image:read",
        ],
        "health": "healthy",
        "latency_p50_ms": 180,
    },
    {
        "server_id": "daum-knowledge",
        "base_url": "https://mcp.daum.upstage.ai/knowledge",
        "description": "사전 + 백과 6종 + 번역 + 어원",
        "tool_count": 4,
        "scopes_required": [
            "knowledge.dict:read", "knowledge.encyclopedia:read",
            "knowledge.translate:read",
        ],
        "health": "healthy",
        "latency_p50_ms": 90,
    },
    {
        "server_id": "daum-solar",
        "base_url": "https://mcp.daum.upstage.ai/solar",
        "description": "Solar Pro 한국어 reasoning 게이트웨이",
        "tool_count": 2,
        "scopes_required": ["solar.korean:execute", "solar.embed:execute"],
        "health": "healthy",
        "latency_p50_ms": 720,
    },
    {
        "server_id": "daum-meta",
        "base_url": "https://mcp.daum.upstage.ai/meta",
        "description": "Federated discovery & routing",
        "tool_count": 3,
        "scopes_required": ["meta:discover", "meta:route", "meta:bind"],
        "health": "healthy",
        "latency_p50_ms": 30,
    },
]

# Routing hints used by route_intent
ROUTING_RULES = [
    # (keywords, plan)
    (
        ["검색", "찾아", "search", "뉴스", "news"],
        [
            ("daum-search", "daum_search_web", "한국어 검색에 최적"),
            ("daum-search", "daum_search_news", "최신 보도 보강"),
        ],
    ),
    (
        ["뜻", "의미", "단어", "사전", "dictionary", "translate", "번역"],
        [
            ("daum-knowledge", "dict_lookup", "표제어 lookup"),
            ("daum-knowledge", "translate_ko", "필요 시 번역"),
        ],
    ),
    (
        ["인물", "역사", "백과", "encyclopedia", "정의"],
        [
            ("daum-knowledge", "encyclopedia_lookup", "백과 6종 조회"),
        ],
    ),
    (
        ["요약", "분석", "한국어로 답해", "정리해줘", "reasoning"],
        [
            ("daum-solar", "solar_korean_chat", "한국어 reasoning 위임"),
        ],
    ),
    (
        ["임베딩", "embedding", "유사도"],
        [
            ("daum-solar", "solar_korean_embed", "Korean embedding"),
        ],
    ),
    (
        ["날씨", "환율", "주가", "박스오피스"],
        [
            ("daum-search", "daum_search_realtime_panel", "위젯 1-stop"),
        ],
    ),
]

# ---------------------------------------------------------------
# Search fixtures
# ---------------------------------------------------------------
WEB_RESULTS = {
    "default": [
        {
            "title": "청계천 산책 후기 — 2026년 봄",
            "url": "https://walk-seoul.tistory.com/2026/04/cheonggye",
            "snippet": "지난 주말 청계천을 따라 종로에서 동대문까지 걸었다. 벚꽃은 거의 끝났고...",
            "source_type": "blog",
            "published_at": "2026-04-14T10:23:00Z",
            "korean_score": 0.96,
            "freshness_score": 0.85,
        },
        {
            "title": "[현장] 청계광장 분수대 재가동 — 2026 시즌 개막",
            "url": "https://news.daum.net/article/202604231201",
            "snippet": "서울시는 23일 청계광장 분수대를 올해 시즌 처음으로 가동했다고 밝혔다.",
            "source_type": "news",
            "published_at": "2026-04-23T03:01:00Z",
            "korean_score": 0.99,
            "freshness_score": 0.92,
        },
        {
            "title": "청계천 맛집 BEST 10 (현지인 추천)",
            "url": "https://cafe.daum.net/seoulfoodies/post/1294",
            "snippet": "종로 직장인이 추천하는 청계천 인근 점심 맛집을 정리합니다...",
            "source_type": "cafe",
            "published_at": "2026-03-30T07:45:00Z",
            "korean_score": 0.94,
            "freshness_score": 0.7,
        },
    ],
}

NEWS_RESULTS = {
    "default": [
        {
            "headline": "Upstage, Solar Pro4 공개 — 한국어 reasoning 격차 GPT-4 대비 +6pt",
            "url": "https://news.daum.net/article/202604300921",
            "publisher": "전자신문",
            "published_at": "2026-04-30T00:21:00Z",
            "summary_ko": "업스테이지가 Solar Pro4를 공개하며 한국어 추론 벤치마크에서 GPT-4를 6점 차로 상회했다고 발표.",
            "sentiment": "positive",
            "entities": [
                {"text": "Upstage", "type": "org", "confidence": 0.99},
                {"text": "Solar Pro4", "type": "product", "confidence": 0.97},
            ],
        },
        {
            "headline": "다음, Upstage 인수 후 첫 개편 — 'Agent Portal' 비전 발표",
            "url": "https://news.daum.net/article/202604280505",
            "publisher": "한국경제",
            "published_at": "2026-04-28T05:05:00Z",
            "summary_ko": "Upstage가 인수한 Daum이 'Agent Portal' 비전을 공식 발표하고 13개 MCP 서버 로드맵을 공개.",
            "sentiment": "positive",
            "entities": [
                {"text": "Daum", "type": "org", "confidence": 0.99},
                {"text": "Agent Portal", "type": "product", "confidence": 0.9},
            ],
        },
    ],
}

REALTIME_PANEL_FIXTURES = {
    "default_widgets": {
        "weather": {
            "location": "서울특별시 강남구",
            "temp_c": 19.4,
            "condition": "구름조금",
            "pm10": 32,
            "pm25": 18,
            "uv_index": 5,
            "updated_at": "2026-05-01T11:30:00Z",
        },
        "fx": {
            "USD_KRW": 1326.40,
            "EUR_KRW": 1452.10,
            "JPY_100_KRW": 884.20,
            "CNY_KRW": 184.30,
            "as_of": "2026-05-01T11:25:00Z",
        },
        "stock": {
            "KOSPI": {"index": 2814.22, "change_pct": 0.54},
            "KOSDAQ": {"index": 871.05, "change_pct": -0.21},
        },
        "sports_score": {
            "KBO": [{"home": "두산", "away": "LG", "score": "3-5", "status": "8회"}],
        },
        "box_office": [
            {"rank": 1, "title": "갤러틱 뷰로", "audience_share_pct": 28.4},
            {"rank": 2, "title": "서울의 봄2", "audience_share_pct": 19.1},
        ],
        "news_box": [
            "Upstage Solar Pro4 발표",
            "다음 Agent Portal 공개",
            "KOSPI 0.5% 상승 마감",
        ],
        "related_queries": ["서울 날씨", "강남 미세먼지", "오늘 날씨 예보"],
        "trends": ["박동빈", "S&P500", "양세종"],
    }
}

# ---------------------------------------------------------------
# Knowledge fixtures
# ---------------------------------------------------------------
DICT_FIXTURES = {
    ("정산", "ko-en"): {
        "senses": [
            {
                "pos": "명사",
                "gloss": "settlement; reconciliation; clearing of accounts",
                "register": "formal",
                "examples": [
                    "월말에 정산을 마감했다.",
                    "거래 정산은 영업일 기준 3일 이내 완료된다.",
                ],
            },
            {
                "pos": "명사",
                "gloss": "calculation; computation",
                "register": "formal",
                "examples": ["보조금 정산 내역을 확인했다."],
            },
        ],
        "pron_ipa": "/t͡ɕʌŋ.san/",
        "audio_url": "https://dic.daum.net/audio/jeongsan.mp3",
        "frequency_band": 7,
        "hanja": "精算",
    },
    ("agent", "en-ko"): {
        "senses": [
            {
                "pos": "noun",
                "gloss": "에이전트; 대리인; (소프트웨어) 자율적으로 작업을 수행하는 프로그램",
                "register": "formal",
                "examples": [
                    "AI agent가 일정을 자동으로 관리한다.",
                    "이번 분쟁은 양측 agent를 통해 해결되었다.",
                ],
            },
        ],
        "pron_ipa": "/ˈeɪ.dʒənt/",
        "audio_url": "https://dic.daum.net/audio/agent.mp3",
        "frequency_band": 9,
        "hanja": "",
    },
    ("연어", "ko-ko"): {
        "senses": [
            {"pos": "명사", "gloss": "(동물) 연어과 회유성 어류", "register": "formal", "examples": ["연어는 강에서 태어나 바다로 내려간다."]},
            {"pos": "명사", "gloss": "(언어학) 함께 자주 어울려 쓰이는 단어 결합", "register": "formal", "examples": ["'시간을 보내다'는 한국어의 대표적 연어이다."]},
        ],
        "pron_ipa": "/jʌn.ʌ/",
        "audio_url": "https://dic.daum.net/audio/yeoneo.mp3",
        "frequency_band": 6,
        "hanja": "鰱魚 / 連語",
    },
}

ENCYCLOPEDIA_FIXTURES = {
    ("한강", "korean_culture"): {
        "title": "한강 (漢江)",
        "summary": (
            "한강은 한반도 중부를 동에서 서로 흐르는 강으로, 길이 약 514km에 이르며 "
            "서울특별시를 관통한다. 북한강과 남한강이 양수리에서 합류해 본류를 이루며, "
            "조선시대 한양 천도(1394) 이후 한국 정치·경제·문화의 중심 축이 되어 왔다."
        ),
        "infobox": {
            "길이": "514km",
            "유역면적": "26,219 km²",
            "발원": "강원도 태백산 검룡소 (남한강) / 금강산 (북한강)",
            "하구": "강화만 (서해)",
        },
        "related": ["북한강", "남한강", "임진강", "한양", "한강 르네상스"],
        "sources_used": ["korean_culture"],
        "license": "한국학중앙연구원 한국민족문화대백과사전 (CC BY-NC-SA)",
    },
    ("solar pro", "daum_baekgwa"): {
        "title": "Solar Pro",
        "summary": (
            "Solar Pro는 Upstage가 개발한 한국어 특화 대형 언어 모델 시리즈이다. "
            "한국어 추론 능력에서 다국어 모델 대비 우수한 성능을 보이며, 2026년 "
            "Daum 인수 이후 Daum 코퍼스를 활용한 학습으로 한국어 격차를 추가 축소했다."
        ),
        "infobox": {"개발사": "Upstage", "공개": "2024", "최신 버전": "Solar Pro4 (2026-04)"},
        "related": ["Upstage", "Daum", "Solar Embedding", "한국어 LLM"],
        "sources_used": ["daum_baekgwa"],
        "license": "다음백과",
    },
}

ETYMOLOGY_FIXTURES = {
    "정산": {
        "hanja": "精算",
        "origin_lang": "sino_korean",
        "history": [
            {"era": "modern", "note": "근대 일본을 거쳐 한국 회계용어로 정착 (20세기 초)"},
            {"era": "contemporary", "note": "디지털 결제 시대 '정산일', '정산내역' 등 확장"},
        ],
        "homophones": [{"word": "정산", "hanja": "淨山", "gloss": "(불교) 깨끗한 산"}],
    },
    "연어": {
        "hanja": "鰱魚 / 連語",
        "origin_lang": "sino_korean",
        "history": [
            {"era": "premodern", "note": "어류 鰱魚는 중국 한자 어휘에서 차용"},
            {"era": "modern", "note": "언어학 용어 連語(collocation)는 일본 학계 차용 후 정착"},
        ],
        "homophones": [],
    },
}

TRANSLATE_FIXTURES = {
    ("월말까지 정산을 마감해 주세요.", "ko-en"): {
        "translation": "Please finalize the settlement by the end of the month.",
        "confidence": 0.97,
        "alternatives": [
            "Please close out the reconciliation by month-end.",
        ],
        "terminology_notes": [
            {"source": "정산", "target": "settlement", "rationale": "회계 도메인 일반 용례"},
        ],
    },
    ("Let me delegate this to a Korean agent.", "en-ko"): {
        "translation": "이 작업은 한국어 에이전트에게 위임하겠습니다.",
        "confidence": 0.96,
        "alternatives": ["이 일은 한국어 agent에게 맡기겠습니다."],
        "terminology_notes": [
            {"source": "agent", "target": "에이전트", "rationale": "기술 도메인 표준 표기"},
        ],
    },
}

# ---------------------------------------------------------------
# Solar fixtures
# ---------------------------------------------------------------
SOLAR_CHAT_FIXTURES = [
    # Match heuristic: substring of last user message
    {
        "match": "한강",
        "content": (
            "한강은 한반도 중부를 가로지르는 약 514km의 강으로, 서울특별시를 관통합니다. "
            "북한강과 남한강이 양수리에서 합류해 본류를 이루며, 조선 한양 천도 이래 "
            "한국 정치·경제·문화의 중심축 역할을 해 왔습니다."
        ),
        "citations": [
            {"source": "knowledge.encyclopedia_lookup", "url": "https://100.daum.net/encyclopedia/view/35XXXXXXX", "span": "한강은 한반도 중부..."},
        ],
        "score": 0.94,
    },
    {
        "match": "정산",
        "content": (
            "'정산(精算)'은 회계·결제 맥락에서 'settlement' 또는 'reconciliation'으로 옮길 수 있습니다. "
            "공식 문서에서는 settlement, 일상에서는 close-out 표현이 자연스럽습니다."
        ),
        "citations": [
            {"source": "knowledge.dict_lookup", "url": "https://dic.daum.net/word/view.do?wordid=ekw000XXX", "span": "정산: settlement; reconciliation"},
        ],
        "score": 0.93,
    },
    {
        "match": "Daum",
        "content": (
            "Daum은 Upstage가 2026년에 인수한 한국 포털입니다. 인수 후 'Agent Portal' 비전 아래 "
            "13개 영역의 MCP 서버를 단계적으로 출시하고 있으며, 한국어 grounding 인프라로 "
            "재포지셔닝되고 있습니다."
        ),
        "citations": [
            {"source": "search.daum_search_news", "url": "https://news.daum.net/article/202604280505", "span": "다음, Upstage 인수 후 첫 개편..."},
        ],
        "score": 0.95,
    },
]


# ---------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------
def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def _stable_uuid(seed: str) -> str:
    h = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return f"{h[:8]}-{h[8:12]}-{h[12:16]}-{h[16:20]}-{h[20:32]}"


def make_meta(tool_name: str, args_signature: str, *, korean_score: float = 0.95, billed: int = 1) -> dict:
    """Standard ResponseMeta block — same shape as production schema."""
    return {
        "request_id": _stable_uuid(f"{tool_name}:{args_signature}:{_now_iso()}"),
        "tenant_id": "ten_demo_001",
        "consent_status": "explicit",
        "data_freshness_ts": _now_iso(),
        "rate_limit_remaining": 998,
        "tokens_billed": billed,
        "korean_score": korean_score,
        "license": "daum-agent-portal-v1",
        "mock": True,  # mock 표시 — production 응답에는 없음
    }


def pii_check(text: str) -> str | None:
    """Return error message if PII pattern detected. Mirrors §3.2 of HITL spec."""
    import re
    if re.search(r"\b\d{6}-\d{7}\b", text):  # 주민번호
        return "주민번호 패턴 감지 — 입력 거부"
    if re.search(r"\b(?:\d[ -]*?){13,16}\b", text):  # card-ish
        # heuristic; production does Luhn check
        return "카드번호 의심 패턴 감지 — 입력 거부"
    return None
