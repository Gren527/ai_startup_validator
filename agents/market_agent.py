from langchain_ollama import OllamaLLM
from rag_fetcher import fetch_rag_context, inject_rag
import json

llm = OllamaLLM(model="llama3", temperature=0)

def market_agent(context):

    idea = context["idea"]

    # ── RAG: fetch real-world market context ──────────────────────────────
    # Query is intentionally broad to get industry-level data
    rag_query = f"market size industry trends {idea}"
    rag_context = fetch_rag_context(rag_query)
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

    # ── Inject RAG if available, else use base prompt as-is ───────────────
    prompt = inject_rag(base_prompt, rag_context)
    print(rag_context)
    
    response = llm.invoke(prompt).strip()

    # 🔥 Clean markdown
    if response.startswith("```"):
        response = response.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(response)

        return {
            "target_users": data.get("target_users", "Not identified"),
            "market_demand": data.get("market_demand", "Unknown"),
            "market_size": data.get("market_size", "Unknown"),
            "industry_growth": data.get("industry_growth", "Unknown"),
            "score": float(data.get("score", 5))
        }

    except:
        return {
            "target_users": "Not identified",
            "market_demand": "Unknown",
            "market_size": "Unknown",
            "industry_growth": "Unknown",
            "score": 5
        }