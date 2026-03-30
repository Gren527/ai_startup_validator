from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

def competitor_agent(idea):

    prompt = f"""
    Identify competitors for this startup idea.

    Idea: {idea}

    Provide:
    - Top competitors
    - Their key features
    - Strengths and weaknesses
    """

    response = llm.invoke(prompt)

    return response