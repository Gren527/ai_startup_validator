from langchain_ollama import OllamaLLM
import json
import re

llm = OllamaLLM(model="llama3")

def feasibility_agent(context):

    idea = context["idea"]

    prompt = f"""
Evaluate the technical feasibility of this startup idea.

Idea: {idea}

STRICT INSTRUCTIONS:
- Return ONLY valid JSON
- Score MUST be between 0 and 10
- No explanation
- No markdown
- No extra text

FORMAT:
{{
    "technologies": "short text",
    "complexity": "Low / Medium / High",
    "timeline": "X months",
    "score": number
}}
"""

    response = llm.invoke(prompt).strip()

    # 🔥 Remove markdown
    if response.startswith("```"):
        response = re.sub(r"```json|```", "", response).strip()

    # 🔥 Extract JSON block
    match = re.search(r"\{.*\}", response, re.DOTALL)
    if match:
        response = match.group(0)

    try:
        return json.loads(response)
    except:
        return {
            "technologies": "",
            "complexity": "",
            "timeline": "",
            "score": 5
        }