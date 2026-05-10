from agents.market_agent import market_agent
from agents.competitor_agent import competitor_agent
from agents.feasibility_agent import feasibility_agent
from agents.business_agent import business_agent
from agents.evaluation_agent import evaluation_agent
from agents.improvement_agent import improvement_agent
from agents.critical_reviewer_agent import critical_reviewer_agent
from agents.innovation_agent import innovation_agent
from agents.local_context_agent import local_context_agent      # NEW
from agents.financial_math_agent import financial_math_agent    # NEW

from concurrent.futures import ThreadPoolExecutor


def run_startup_validator(idea, local_info=None, user_finance=None):

    # 🔹 Shared context
    context = {
        "idea": idea,
        "local_info": local_info or {},       # NEW: user's local details
        "user_finance": user_finance or {},   # NEW: user's financial situation
        "market_analysis": {},
        "competitor_analysis": {},
        "feasibility_analysis": {},
        "business_model": {},
        "innovation_analysis": {},
        "local_context": {},                  # NEW
        "financial_projection": {},           # NEW
        "startup_evaluation": {},
        "risk_analysis": {},
        "suggested_improvements": "",
        "final_score": 5
    }

    # 🔹 Phase 1: Base agents (parallel) — UNCHANGED
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

    # 🔹 Phase 2: Innovation — UNCHANGED
    try:
        context["innovation_analysis"] = innovation_agent(context)
    except:
        context["innovation_analysis"] = {"innovation_score": 5}

    # 🔹 Phase 3: NEW — Local Context Analysis
    if local_info:
        try:
            context["local_context"] = local_context_agent(context)
        except:
            context["local_context"] = {"local_opportunity_score": 5, "local_fit_verdict": "UNKNOWN"}
    else:
        context["local_context"] = {"local_opportunity_score": 5, "local_fit_verdict": "NOT PROVIDED"}

    # 🔹 Phase 4: Evaluation (summary only) — UNCHANGED
    try:
        context["startup_evaluation"] = evaluation_agent(
            context["market_analysis"],
            context["competitor_analysis"],
            context["feasibility_analysis"],
            context["business_model"]
        )
    except:
        context["startup_evaluation"] = {"verdict": "UNCERTAIN"}

    # 🔹 Phase 5: Risk Analysis — UNCHANGED
    try:
        context["risk_analysis"] = critical_reviewer_agent(context)
    except:
        context["risk_analysis"] = {"risk_score": 5}

    # 🔹 Phase 6: NEW — Financial Math & Growth Projection
    if user_finance:
        try:
            context["financial_projection"] = financial_math_agent(context)
        except:
            context["financial_projection"] = {}
    else:
        context["financial_projection"] = {}

    # 🔹 Phase 7: Improvements — UNCHANGED
    try:
        context["suggested_improvements"] = improvement_agent(
            context["idea"],
            context["startup_evaluation"]
        )
    except:
        context["suggested_improvements"] = "No suggestions available"

    # 🔹 Phase 8: FINAL SCORE — slightly updated to include local_context if available
    try:
        market_score = context["market_analysis"].get("score", 5)
        competitor_score = context["competitor_analysis"].get("score", 5)
        feasibility_score = context["feasibility_analysis"].get("score", 5)
        business_score = context["business_model"].get("score", 5)
        innovation_score = context["innovation_analysis"].get("innovation_score", 5)
        local_score = context["local_context"].get("local_opportunity_score", None)

        if local_score is not None and local_info:
            # Include local score when user provided local context
            final_score = (
                0.22 * market_score +
                0.18 * competitor_score +
                0.18 * feasibility_score +
                0.17 * business_score +
                0.13 * innovation_score +
                0.12 * local_score        # NEW weight
            )
        else:
            # Original weights
            final_score = (
                0.25 * market_score +
                0.20 * competitor_score +
                0.20 * feasibility_score +
                0.20 * business_score +
                0.15 * innovation_score
            )

        final_score = max(0, min(10, final_score))
        context["final_score"] = round(final_score, 2)

    except:
        context["final_score"] = 5

    return context