from langchain_ollama import OllamaLLM
import json
import re

# 🔥 Use low randomness for consistency
llm = OllamaLLM(model="llama3", temperature=0)


def competitor_agent(context):

    idea = context["idea"]

    prompt = f"""
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

    # 🔁 Retry mechanism
    for _ in range(3):

        response = llm.invoke(prompt).strip()

        # 🔥 Remove markdown if present
        response = re.sub(r"```json|```", "", response).strip()

        # 🔥 Extract JSON block
        match = re.search(r"\{.*\}", response, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(0))

                # ✅ Validate competitors
                competitors = data.get("competitors", [])

                if not competitors or len(competitors) < 1:
                    continue  # retry if empty

                # ✅ Normalize score
                score = data.get("score", 5)
                if isinstance(score, (int, float)):
                    if score > 10:
                        score = score / 10
                else:
                    score = 5

                data["score"] = round(score, 2)

                return data

            except:
                continue  # retry if parsing fails

    # 🔥 Smart fallback (never broken UI)
    return {
        "competitors": ["Generic competitors in this domain"],
        "features": "Common features in similar platforms",
        "strengths": "Established players with user base",
        "weaknesses": "High competition and low differentiation",
        "score": 6
    }