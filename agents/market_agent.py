from langchain_ollama import OllamaLLM
from rag_fetcher import fetch_rag_context, filter_rag_context, inject_rag
import json

llm = OllamaLLM(model="llama3", temperature=0)


def market_agent(context):

    idea = context["idea"]

    # ── RAG: fetch → filter to top 6 most relevant sentences ─────────────
    rag_query   = f"market size industry trends {idea}"
    raw_rag     = fetch_rag_context(rag_query)
    rag_context = filter_rag_context(raw_rag, idea, top_n=6)   # ← NEW
    # ─────────────────────────────────────────────────────────────────────

    base_prompt = f"""
Analyze the market potential for this startup idea.

Idea: {idea}

STRICT INSTRUCTIONS:
- Score MUST be between 0 and 10
- Return ONLY valid JSON
- No explanation
- No markdown
- DO NOT skip any fields

FORMAT:
{{
    "target_users": "string",
    "market_demand": "string",
    "market_size": "string",
    "industry_growth": "string",
    "score": number
}}
"""

    prompt = inject_rag(base_prompt, rag_context)
    print("[market_agent] filtered RAG context:\n", rag_context)

    response = llm.invoke(prompt).strip()

    if response.startswith("```"):
        response = response.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(response)
        return {
            "target_users":    data.get("target_users", "Not identified"),
            "market_demand":   data.get("market_demand", "Unknown"),
            "market_size":     data.get("market_size", "Unknown"),
            "industry_growth": data.get("industry_growth", "Unknown"),
            "score":           float(data.get("score", 5))
        }
    except Exception:
        return {
            "target_users":    "Not identified",
            "market_demand":   "Unknown",
            "market_size":     "Unknown",
            "industry_growth": "Unknown",
            "score":           5
        }