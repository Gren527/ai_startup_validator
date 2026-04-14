from langchain_ollama import OllamaLLM
import json

llm = OllamaLLM(model="llama3")

def market_agent(context):

    idea = context["idea"]

    prompt = f"""
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

    response = llm.invoke(prompt).strip()

    # 🔥 Clean markdown
    if response.startswith("```"):
        response = response.replace("```json", "").replace("```", "").strip()

    try:
        data = json.loads(response)

        # 🔥 Ensure ALL keys exist (VERY IMPORTANT)
        return {
            "target_users": data.get("target_users", "Not identified"),
            "market_demand": data.get("market_demand", "Unknown"),
            "market_size": data.get("market_size", "Unknown"),
            "industry_growth": data.get("industry_growth", "Unknown"),
            "score": float(data.get("score", 5))
        }

    except:
        # 🔥 STRONG fallback (never empty)
        return {
            "target_users": "Not identified",
            "market_demand": "Unknown",
            "market_size": "Unknown",
            "industry_growth": "Unknown",
            "score": 5
        }