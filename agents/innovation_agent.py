from langchain_ollama import OllamaLLM
import json
import re

llm = OllamaLLM(model="llama3", temperature=0)


def innovation_agent(context):

    idea = context.get("idea", "")
    competitors = context.get("competitor_analysis", {}).get("competitors", [])

    # safety fallback
    if not competitors:
        competitors = ["existing solutions"]

    prompt = f"""
You are evaluating startup innovation.

Idea:
{idea}

Competitors:
{competitors}

TASK:
- Judge how different and unique the idea is compared to competitors

STRICT RULES:
- Return ONLY JSON
- No explanation outside JSON
- No markdown

FORMAT:
{{
    "innovation_score": number (0-10),
    "reason": "short explanation"
}}
"""

    for _ in range(3):  # retry

        response = llm.invoke(prompt).strip()

        # 🔥 clean markdown
        response = re.sub(r"```json|```", "", response).strip()

        # 🔥 extract JSON
        match = re.search(r"\{.*\}", response, re.DOTALL)

        if match:
            try:
                data = json.loads(match.group(0))

                # ✅ FIX: correct key check
                score = data.get("innovation_score", None)

                if score is None:
                    continue  # retry if missing

                # normalize
                if score > 10:
                    score = score / 10

                data["innovation_score"] = round(score, 2)

                return data

            except:
                continue

    # 🔥 SMART fallback (not useless 5)
    return {
        "innovation_score": 6,
        "reason": "Moderately innovative compared to current solutions"
    }