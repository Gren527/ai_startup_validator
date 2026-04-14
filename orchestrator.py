from agents.market_agent import market_agent
from agents.competitor_agent import competitor_agent
from agents.feasibility_agent import feasibility_agent
from agents.business_agent import business_agent
from agents.evaluation_agent import evaluation_agent
from agents.improvement_agent import improvement_agent
from agents.critical_reviewer_agent import critical_reviewer_agent
from agents.innovation_agent import innovation_agent

from concurrent.futures import ThreadPoolExecutor


def run_startup_validator(idea):

    # 🔹 Shared context
    context = {
        "idea": idea,
        "market_analysis": {},
        "competitor_analysis": {},
        "feasibility_analysis": {},
        "business_model": {},
        "innovation_analysis": {},
        "startup_evaluation": {},
        "risk_analysis": {},
        "suggested_improvements": "",
        "final_score": 5
    }

    # 🔹 Phase 1: Base agents (parallel)
    with ThreadPoolExecutor() as executor:

        market_future = executor.submit(market_agent, context)
        competitor_future = executor.submit(competitor_agent, context)
        feasibility_future = executor.submit(feasibility_agent, context)
        business_future = executor.submit(business_agent, context)

        try:
            context["market_analysis"] = market_future.result() or {"score": 5}
        except:
            context["market_analysis"] = {"score": 5}

        try:
            context["competitor_analysis"] = competitor_future.result() or {"score": 5}
        except:
            context["competitor_analysis"] = {"score": 5}

        try:
            context["feasibility_analysis"] = feasibility_future.result() or {"score": 5}
        except:
            context["feasibility_analysis"] = {"score": 5}

        try:
            context["business_model"] = business_future.result() or {"score": 5}
        except:
            context["business_model"] = {"score": 5}

    # 🔹 Phase 2: Innovation
    try:
        context["innovation_analysis"] = innovation_agent(context)
    except:
        context["innovation_analysis"] = {"innovation_score": 5}

    # 🔹 Phase 3: Evaluation (summary only)
    try:
        context["startup_evaluation"] = evaluation_agent(
            context["market_analysis"],
            context["competitor_analysis"],
            context["feasibility_analysis"],
            context["business_model"]
        )
    except:
        context["startup_evaluation"] = {"verdict": "UNCERTAIN"}

    # 🔹 Phase 4: Risk Analysis (SEPARATE)
    try:
        context["risk_analysis"] = critical_reviewer_agent(context)
    except:
        context["risk_analysis"] = {"risk_score": 5}

    # 🔹 Phase 5: Improvements
    try:
        context["suggested_improvements"] = improvement_agent(
            context["idea"],
            context["startup_evaluation"]
        )
    except:
        context["suggested_improvements"] = "No suggestions available"

    # 🔹 Phase 6: FINAL SCORE (IDEA QUALITY ONLY ✅)
    try:
        market_score = context["market_analysis"].get("score", 5)
        competitor_score = context["competitor_analysis"].get("score", 5)
        feasibility_score = context["feasibility_analysis"].get("score", 5)
        business_score = context["business_model"].get("score", 5)
        innovation_score = context["innovation_analysis"].get("innovation_score", 5)

        # ✅ PURE IDEA QUALITY SCORE (NO RISK MIXING)
        final_score = (
            0.25 * market_score +
            0.20 * competitor_score +
            0.20 * feasibility_score +
            0.20 * business_score +
            0.15 * innovation_score
        )

        # clamp
        final_score = max(0, min(10, final_score))

        context["final_score"] = round(final_score, 2)

    except:
        context["final_score"] = 5

    return context