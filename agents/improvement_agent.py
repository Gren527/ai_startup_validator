from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

def improvement_agent(idea, evaluation):

    prompt = f"""
    A startup idea has been evaluated.

    Idea:
    {idea}

    Evaluation:
    {evaluation}

    Suggest improvements for this startup idea.

    Provide:
    - Product improvements
    - Differentiation strategies
    - Better revenue opportunities
    """

    response = llm.invoke(prompt)

    return response