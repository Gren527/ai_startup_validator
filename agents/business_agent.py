from langchain_ollama import OllamaLLM
import json
import re

llm = OllamaLLM(model="llama3")

def business_agent(context):

    idea = context["idea"]

    prompt = f"""
Analyze and suggest a business model for this startup idea.

Idea: {idea}

STRICT INSTRUCTIONS:
- Return ONLY valid JSON
- Score MUST be between 0 and 10
- No explanation
- No markdown
- No extra text

FORMAT:
{{
    "revenue_model": "short text",
    "pricing_strategy": "short text",
    "scalability": "short text",
    "score": number
}}
"""

    response = llm.invoke(prompt).strip()

    # 🔥 CLEAN EVERYTHING
    if response.startswith("```"):
        response = re.sub(r"```json|```", "", response).strip()

    # 🔥 EXTRACT JSON ONLY
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        response = match.group(0)

    try:
        return json.loads(response)
    except:
        return {
            "revenue_model": "",
            "pricing_strategy": "",
            "scalability": "",
            "score": 5
        }