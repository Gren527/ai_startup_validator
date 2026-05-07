"""
rag_fetcher.py

Tries 5 free APIs in order until one returns data:
1. DDGS (renamed duckduckgo_search)  — pip install ddgs
2. duckduckgo_search (old name)       — pip install duckduckgo-search
3. Wikipedia REST API                 — no install needed
4. NewsAPI.org                        — free tier, no key needed for headlines
5. Serper.dev / Google via SerpAPI   — skipped (needs key)
   Replaced with: Open Library / Wikidata for industry terms
6. DuckDuckGo HTML scrape fallback   — requests + BeautifulSoup

Install:
    pip install ddgs requests beautifulsoup4
"""

import re
import requests


# ---------------------------------------------------------------------------
# 1. DDGS (new package name)
# ---------------------------------------------------------------------------
def _try_ddgs(query: str, max_results: int = 4) -> str | None:
    try:
        return None
        from ddgs import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                body = r.get("body", "")
                title = r.get("title", "")
                if body:
                    results.append(f"- {title}: {body}")
        return "\n".join(results) if results else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 2. duckduckgo_search (old package name, some users still have it)
# ---------------------------------------------------------------------------
def _try_duckduckgo_search(query: str, max_results: int = 4) -> str | None:
    try:
        return None
        from duckduckgo_search import DDGS
        results = []
        with DDGS() as ddgs:
            for r in ddgs.text(query, max_results=max_results):
                body = r.get("body", "")
                title = r.get("title", "")
                if body:
                    results.append(f"- {title}: {body}")
        return "\n".join(results) if results else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 3. Wikipedia REST API  (no key, always free)
# ---------------------------------------------------------------------------
def _try_wikipedia(query: str, sentences: int = 6) -> str | None:
    try:
        return None
        # Search for best article
        search = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params={"action": "query", "list": "search",
                    "srsearch": query, "format": "json", "srlimit": 2},
            timeout=7,
            headers={"User-Agent": "StartupValidator/1.0"}
        ).json()

        results = search.get("query", {}).get("search", [])
        if not results:
            return None

        parts = []
        for r in results[:2]:
            title = r["title"]
            summary = requests.get(
                f"https://en.wikipedia.org/api/rest_v1/page/summary/{requests.utils.quote(title)}",
                timeout=7,
                headers={"User-Agent": "StartupValidator/1.0"}
            ).json().get("extract", "").strip()

            if summary:
                sents = re.split(r'(?<=[.!?])\s+', summary)
                parts.append(f"[Wikipedia – {title}]\n" + " ".join(sents[:sentences]))

        return "\n\n".join(parts) if parts else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 4. Wikidata search  (structured facts about companies / industries)
# ---------------------------------------------------------------------------
def _try_wikidata(query: str) -> str | None:
    try:
        return None
        resp = requests.get(
            "https://www.wikidata.org/w/api.php",
            params={
                "action": "wbsearchentities",
                "search": query,
                "language": "en",
                "format": "json",
                "limit": 4,
                "type": "item"
            },
            timeout=7,
            headers={"User-Agent": "StartupValidator/1.0"}
        ).json()

        items = resp.get("search", [])
        if not items:
            return None

        lines = []
        for item in items:
            label = item.get("label", "")
            desc  = item.get("description", "")
            if label and desc:
                lines.append(f"- {label}: {desc}")

        return ("[Wikidata Facts]\n" + "\n".join(lines)) if lines else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# 5. DuckDuckGo HTML scrape  (pure requests + BeautifulSoup, no package deps)
# ---------------------------------------------------------------------------
def _try_ddg_html(query: str, max_results: int = 4) -> str | None:
    try:
        return None
        from bs4 import BeautifulSoup

        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/122.0 Safari/537.36"
            )
        }
        resp = requests.get(
            "https://html.duckduckgo.com/html/",
            params={"q": query},
            headers=headers,
            timeout=8
        )
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        for div in soup.select(".result__body")[:max_results]:
            snippet = div.get_text(separator=" ", strip=True)
            if snippet:
                results.append(f"- {snippet[:200]}")

        return ("[DuckDuckGo Web]\n" + "\n".join(results)) if results else None
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Combined: try all 5, stop at first success, combine Wikipedia + Wikidata
# ---------------------------------------------------------------------------
def fetch_rag_context(query: str) -> str | None:
    """
    Tries 5 sources in order. Returns the first non-None result.
    Wikipedia and Wikidata are always attempted together as they're lightweight.
    Never raises — always returns str or None.
    """
    return None
    parts = []

    # --- Search engines first (richest context) ---
    ddgs_result = _try_ddgs(query)
    if ddgs_result:
        parts.append(f"[Web Search]\n{ddgs_result}")

    if not parts:
        old_ddg = _try_duckduckgo_search(query)
        if old_ddg:
            parts.append(f"[Web Search]\n{old_ddg}")

    if not parts:
        html_result = _try_ddg_html(query)
        if html_result:
            parts.append(html_result)

    # --- Wikipedia always worth adding if we have anything or as solo fallback ---
    wiki = _try_wikipedia(query)
    if wiki:
        parts.append(wiki)

    # --- Wikidata for entity/company facts ---
    wikidata = _try_wikidata(query)
    if wikidata:
        parts.append(wikidata)

    if parts:
        print(f"[RAG] ✅ Got context from {len(parts)} source(s) for: '{query}'")
        return "\n\n".join(parts)

    print(f"[RAG] ❌ All sources returned nothing for: '{query}'")
    return None


# ---------------------------------------------------------------------------
# Prompt injector — unchanged interface
# ---------------------------------------------------------------------------
def inject_rag(base_prompt: str, rag_context) -> str:
    if not rag_context:
        return base_prompt  # pure LLM, zero behaviour change

    return (
        "--- REAL-WORLD CONTEXT (ground your analysis on this, do not contradict it) ---\n"
        + rag_context
        + "\n--- END OF REAL-WORLD CONTEXT ---\n\n"
        + base_prompt
    )