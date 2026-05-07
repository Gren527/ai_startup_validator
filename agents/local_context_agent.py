from langchain_ollama import OllamaLLM
import json
import re

llm = OllamaLLM(model="llama3", temperature=0)


def local_context_agent(context):
    """
    Evaluates how the startup idea fits the LOCAL context provided by the user:
    - Location type (village, town, city, metro)
    - Existing infrastructure / competitors in that location
    - Local demographics and buying behavior
    - Cultural/mentality fit

    This is separate from the global competitor_agent which looks at the world market.
    """

    idea = context.get("idea", "")
    local_info = context.get("local_info", {})

    location_type = local_info.get("location_type", "unknown")
    location_desc = local_info.get("location_description", "")
    existing_businesses = local_info.get("existing_businesses", "")
    local_population = local_info.get("local_population", "")
    local_demand_notes = local_info.get("local_demand_notes", "")

    prompt = f"""
You are a LOCAL MARKET ANALYST. You evaluate startup ideas based on local ground-level realities,
NOT global trends.

Startup Idea:
{idea}

Local Context Provided by User:
- Location Type: {location_type}
- Location Description: {location_desc}
- Existing businesses nearby: {existing_businesses}
- Approximate population: {local_population}
- User's notes on local demand: {local_demand_notes}

YOUR TASK:
1. Assess if this idea fits this SPECIFIC local context
2. Identify local demand signals (e.g., "no gaming centers but many youth = strong unmet demand")
3. Identify local risks (e.g., "small village, low purchasing power, idea may be premature")
4. Give a local opportunity score (0-10) where 10 = perfect local fit

RULES:
- Think like a local investor who knows the ground reality
- A bad global idea can be great locally (e.g., first mall in a growing town)
- A great global idea can fail locally (e.g., luxury spa in a low-income village)
- Return ONLY valid JSON, no markdown, no extra text

FORMAT:
{{
    "local_opportunity_score": number (0-10),
    "local_demand_assessment": "short paragraph",
    "unmet_local_needs": ["need1", "need2"],
    "local_risks": ["risk1", "risk2"],
    "local_fit_verdict": "STRONG FIT / MODERATE FIT / WEAK FIT / PREMATURE"
}}
"""

    for _ in range(3):
        response = llm.invoke(prompt).strip()
        response = re.sub(r"```json|```", "", response).strip()
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                data = json.loads(match.group(0))
                score = data.get("local_opportunity_score", 5)
                if score > 10:
                    score = score / 10
                data["local_opportunity_score"] = round(float(score), 2)
                return data
            except:
                continue

    return {
        "local_opportunity_score": 5,
        "local_demand_assessment": "Could not assess local context",
        "unmet_local_needs": ["Insufficient local data provided"],
        "local_risks": ["Unknown local risks"],
        "local_fit_verdict": "MODERATE FIT"
    }