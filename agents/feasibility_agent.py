from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

def feasibility_agent(idea):

    prompt = f"""
    Evaluate the technical feasibility of this startup idea.

    Idea: {idea}

    Provide:
    - Required technologies
    - Development complexity
    - Estimated development timeline
    """

    response = llm.invoke(prompt)

    return response