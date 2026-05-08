"""
rag_fetcher.py

Tries 5 free APIs in order until one returns data:
1. DDGS (renamed duckduckgo_search)  — pip install ddgs
2. duckduckgo_search (old name)       — pip install duckduckgo-search
3. Wikipedia REST API                 — no install needed
4. Wikidata                           — no install needed
5. DuckDuckGo HTML scrape fallback   — requests + BeautifulSoup

NEW: filter_rag_context(raw_rag, idea, top_n)
  — Scores every sentence in the raw RAG output by keyword overlap
    with the idea string, then returns only the top-N most relevant
    sentences.  This keeps the injected context tight and on-topic.

Install:
    pip install ddgs requests beautifulsoup4
"""

import re
import math
import requests


# ──────────────────────────────────────────────────────────────────────────────
# RAG FILTERING  (new)
# ──────────────────────────────────────────────────────────────────────────────

def _tokenize(text: str) -> set[str]:
    """Lowercase words, strip punctuation, drop 1-char tokens."""
    return {
        w for w in re.findall(r"[a-zA-Z0-9]+", text.lower())
        if len(w) > 1
    }


# Common English stopwords — we down-weight these so content words dominate
_STOPWORDS = {
    "the", "is", "in", "it", "of", "and", "to", "a", "an", "for",
    "on", "at", "by", "as", "or", "be", "this", "that", "are",
    "was", "with", "from", "its", "also", "has", "have", "been",
    "their", "they", "which", "who", "more", "can", "we", "he",
    "she", "you", "not", "but", "so", "about", "will", "other"
}


def _score_sentence(sentence: str, query_tokens: set[str]) -> float:
    """
    TF-IDF-lite: score = overlap of content words between sentence and query,
    weighted by inverse sentence length so short sharp sentences rank higher.

    Returns a float; higher = more relevant.
    """
    sent_tokens = _tokenize(sentence) - _STOPWORDS
    query_content = query_tokens - _STOPWORDS

    if not sent_tokens or not query_content:
        return 0.0

    overlap = sent_tokens & query_content
    # Jaccard-like with a length penalty for very long sentences
    score = len(overlap) / (1 + math.log1p(len(sent_tokens)))
    return score


def filter_rag_context(
    raw_rag: str,
    idea: str,
    top_n: int = 6,
    min_len: int = 30
) -> str:
    """
    Given raw multi-source RAG text and the startup idea string,
    return only the top_n most relevant sentences.

    Parameters
    ----------
    raw_rag  : str   — full text returned by fetch_rag_context()
    idea     : str   — the startup idea (used as the relevance query)
    top_n    : int   — how many sentences to keep   (default: 6)
    min_len  : int   — ignore sentences shorter than this (chars)

    Returns
    -------
    A compact string of the top-N sentences, one per line,
    ready to inject into a prompt.
    """
    if not raw_rag:
        return ""

    # Split on sentence boundaries (keep header lines like "[Wikipedia – X]")
    raw_sentences = re.split(r"(?<=[.!?])\s+|\n", raw_rag)
    query_tokens = _tokenize(idea)

    scored = []
    for sent in raw_sentences:
        sent = sent.strip()
        if len(sent) < min_len:
            continue  # skip very short / header fragments
        score = _score_sentence(sent, query_tokens)
        scored.append((score, sent))

    # Sort descending, take top N
    scored.sort(key=lambda x: x[0], reverse=True)
    top_sentences = [s for _, s in scored[:top_n]]

    return "\n".join(top_sentences)


# ──────────────────────────────────────────────────────────────────────────────
# SOURCE FETCHERS  (unchanged)
# ──────────────────────────────────────────────────────────────────────────────

def _try_ddgs(query: str, max_results: int = 4) -> str | None:
    try:
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


def _try_duckduckgo_search(query: str, max_results: int = 4) -> str | None:
    try:
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


def _try_wikipedia(query: str, sentences: int = 6) -> str | None:
    try:
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


def _try_wikidata(query: str) -> str | None:
    try:
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


def _try_ddg_html(query: str, max_results: int = 4) -> str | None:
    try:
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


# ──────────────────────────────────────────────────────────────────────────────
# COMBINED FETCHER
# ──────────────────────────────────────────────────────────────────────────────

def fetch_rag_context(query: str) -> str | None:
    """
    Tries all sources, returns combined raw text.
    Use filter_rag_context() afterwards to trim to what matters.
    """
    parts = []

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

    wiki = _try_wikipedia(query)
    if wiki:
        parts.append(wiki)

    wikidata = _try_wikidata(query)
    if wikidata:
        parts.append(wikidata)

    if parts:
        print(f"[RAG] ✅ Got context from {len(parts)} source(s) for: '{query}'")
        return "\n\n".join(parts)

    print(f"[RAG] ❌ All sources returned nothing for: '{query}'")
    return None


# ──────────────────────────────────────────────────────────────────────────────
# PROMPT INJECTOR
# ──────────────────────────────────────────────────────────────────────────────

def inject_rag(base_prompt: str, rag_context: str | None) -> str:
    if not rag_context:
        return base_prompt

    return (
        "--- REAL-WORLD CONTEXT (ground your analysis on this, do not contradict it) ---\n"
        + rag_context
        + "\n--- END OF REAL-WORLD CONTEXT ---\n\n"
        + base_prompt
    )