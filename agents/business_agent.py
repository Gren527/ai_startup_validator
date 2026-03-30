from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

def business_agent(idea):

    prompt = f"""
    Suggest a business model for this startup idea.

    Idea: {idea}

    Provide:
    - Revenue model
    - Pricing strategy
    - Scalability potential
    """

    response = llm.invoke(prompt)

    return response