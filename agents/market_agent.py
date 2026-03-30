from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

def market_agent(idea):

    prompt = f"""
    Analyze the market potential for this startup idea.

    Idea: {idea}

    Provide:
    - Target users
    - Market demand
    - Market size estimate
    - Industry growth
    """

    response = llm.invoke(prompt)

    return response