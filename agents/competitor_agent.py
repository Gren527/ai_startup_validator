from langchain_ollama import OllamaLLM
from rag_fetcher import fetch_rag_context, filter_rag_context, inject_rag
import json
import re

llm = OllamaLLM(model="llama3", temperature=0)


def competitor_agent(context):

    idea = context["idea"]

    # ── RAG: fetch → filter to top 5 most relevant sentences ─────────────
    rag_query   = f"top competitors companies {idea}"
    raw_rag     = fetch_rag_context(rag_query)
    rag_context = filter_rag_context(raw_rag, idea, top_n=5)   # ← NEW
    # ─────────────────────────────────────────────────────────────────────

    base_prompt = f"""
You are a startup analyst.

Find REAL competitors for this startup idea.

Idea: {idea}

IMPORTANT:
- Always give at least 2 competitors
- If unsure, give similar products/platforms
- Do NOT leave competitors empty

STRICT:
- Return ONLY valid JSON
- No explanation
- No markdown

FORMAT:
{{
    "competitors": ["name1", "name2"],
    "features": "short text",
    "strengths": "short text",
    "weaknesses": "short text",
    "score": number (0-10)
}}
"""

    prompt = inject_rag(base_prompt, rag_context)
    print("[competitor_agent] filtered RAG context:\n", rag_context)

    for _ in range(3):

        response = llm.invoke(prompt).strip()
        response = re.sub(r"```json|```", "", response).strip()
        match    = re.search(r"\{.*\}", response, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(0))

                competitors = data.get("competitors", [])
                if not competitors or len(competitors) < 1:
                    continue

                score = data.get("score", 5)
                if isinstance(score, (int, float)):
                    if score > 10:
                        score = score / 10
                else:
                    score = 5

                data["score"] = round(score, 2)
                return data

            except Exception:
                continue

    return {
        "competitors": ["Generic competitors in this domain"],
        "features":    "Common features in similar platforms",
        "strengths":   "Established players with user base",
        "weaknesses":  "High competition and low differentiation",
        "score":       6
    }