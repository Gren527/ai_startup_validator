from langchain_ollama import OllamaLLM
import json
import re

llm = OllamaLLM(model="llama3")

def critical_reviewer_agent(context):

    idea = context["idea"]

    market_score = context["market_analysis"].get("score", 5)
    competitor_score = context["competitor_analysis"].get("score", 5)
    feasibility_score = context["feasibility_analysis"].get("score", 5)
    business_score = context["business_model"].get("score", 5)

    prompt = f"""
You are a critical startup investor.

Your job is to find why this startup idea might FAIL.

Startup Idea:
{idea}

Scores:
Market: {market_score}
Competition: {competitor_score}
Feasibility: {feasibility_score}
Business: {business_score}

STRICT INSTRUCTIONS:
- Be critical and realistic
- Identify real risks
- No positive bias
- Return ONLY valid JSON

FORMAT:
{{
    "biggest_risk": "short sentence",
    "risk_factors": ["risk1", "risk2", "risk3"],
    "risk_score": number (0-10),
    "verdict": "SAFE / MODERATE RISK / HIGH RISK"
}}
"""

    response = llm.invoke(prompt).strip()

    # 🔥 clean markdown
    if response.startswith("```"):
        response = re.sub(r"```json|```", "", response).strip()

    # 🔥 extract JSON
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        response = match.group(0)

    try:
        data = json.loads(response)

        # normalize score
        score = data.get("risk_score", 5)
        if score > 10:
            score = score / 10

        data["risk_score"] = round(score, 2)

        return data

    except:
        return {
            "biggest_risk": "Unknown risk",
            "risk_factors": ["Parsing failed"],
            "risk_score": 5,
            "verdict": "UNCERTAIN"
        }