from langchain_ollama import OllamaLLM
import json
import re

llm = OllamaLLM(model="llama3")

def evaluation_agent(market, competitor, feasibility, business):

    market_score = market.get("score", 5)
    competitor_score = competitor.get("score", 5)
    feasibility_score = feasibility.get("score", 5)
    business_score = business.get("score", 5)

    prompt = f"""
Evaluate this startup.

Scores:
Market: {market_score}
Competition: {competitor_score}
Feasibility: {feasibility_score}
Business: {business_score}

STRICT:
- ONLY JSON
- No explanation
- No markdown

FORMAT:
{{
    "market_score": {market_score},
    "competition_score": {competitor_score},
    "feasibility_score": {feasibility_score},
    "business_score": {business_score},
    "strengths": ["point1", "point2"],
    "weaknesses": ["point1", "point2"],
    "verdict": "GO or NO-GO"
}}
"""

    response = llm.invoke(prompt).strip()

    # 🔥 CLEAN markdown
    response = re.sub(r"```json|```", "", response).strip()

    # 🔥 EXTRACT JSON ONLY
    match = re.search(r"\{.*\}", response, re.DOTALL)

    if match:
        cleaned = match.group(0)
    else:
        cleaned = response

    try:
        return json.loads(cleaned)

    except:
        # 🔥 SMART FALLBACK (NO MORE ALL 5s)
        return {
            "market_score": market_score,
            "competition_score": competitor_score,
            "feasibility_score": feasibility_score,
            "business_score": business_score,
            "strengths": [
                "Strong potential based on analysis",
                "Viable business direction"
            ],
            "weaknesses": [
                "Parsing issue occurred",
                "Needs deeper evaluation"
            ],
            "verdict": "MODERATE"
        }