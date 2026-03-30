from agents.market_agent import market_agent
from agents.competitor_agent import competitor_agent
from agents.feasibility_agent import feasibility_agent
from agents.business_agent import business_agent
from agents.evaluation_agent import evaluation_agent
from agents.improvement_agent import improvement_agent

from concurrent.futures import ThreadPoolExecutor


def run_startup_validator(idea):

    # Run agents in parallel
    with ThreadPoolExecutor() as executor:

        market_future = executor.submit(market_agent, idea)
        competitor_future = executor.submit(competitor_agent, idea)
        feasibility_future = executor.submit(feasibility_agent, idea)
        business_future = executor.submit(business_agent, idea)

        market = market_future.result()
        competitor = competitor_future.result()
        feasibility = feasibility_future.result()
        business = business_future.result()

    # Evaluation after analysis agents finish
    evaluation = evaluation_agent(
        market,
        competitor,
        feasibility,
        business
    )

    # Improvement suggestions
    improvement = improvement_agent(idea, evaluation)

    return {
        "market_analysis": market,
        "competitor_analysis": competitor,
        "feasibility_analysis": feasibility,
        "business_model": business,
        "startup_evaluation": evaluation,
        "suggested_improvements": improvement
    }