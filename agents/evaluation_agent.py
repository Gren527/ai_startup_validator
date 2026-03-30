from langchain_ollama import OllamaLLM

llm = OllamaLLM(model="llama3")

def evaluation_agent(market, competitor, feasibility, business):

    prompt = f"""
You are an expert startup analyst similar to a venture capitalist evaluating early-stage startup ideas.

Evaluate the following startup idea based on the analyses provided.

Market Analysis:
{market}

Competitor Analysis:
{competitor}

Technical Feasibility:
{feasibility}

Business Model:
{business}

Evaluate the idea using these criteria:

1. Market Demand (0–10)
   How strong is the demand for this solution?

2. Competitive Advantage (0–10)
   Does the startup have a clear advantage over competitors?

3. Technical Feasibility (0–10)
   Is the technology realistic and achievable?

4. Revenue Potential (0–10)
   How strong and scalable is the monetization model?

5. Innovation (0–10)
   How unique or differentiated is the idea?

Compute the final startup score using this formula:

Final Score =
(0.20 × Market Demand) +
(0.15 × Competitive Advantage) +
(0.20 × Technical Feasibility) +
(0.25 × Revenue Potential) +
(0.20 × Innovation)

Guidelines:

* Most startup ideas should score between 4 and 8.
* Only give 9 or 10 if the idea is exceptionally strong.
* Be realistic and critical like an investor.

Return your answer in this EXACT format:

Strengths:

* ...

Weaknesses:

* ...

Overall Viability:
...

Startup Score: X/10

"""

    response = llm.invoke(prompt)

    return response