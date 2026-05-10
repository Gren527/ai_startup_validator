from langchain_ollama import OllamaLLM
import json
import re
import math

llm = OllamaLLM(model="llama3", temperature=0)


def _compute_growth_curve(initial_revenue, growth_rate_monthly, months=24):
    """
    Simple compound growth model.
    Returns list of monthly revenue projections.
    """
    curve = []
    rev = initial_revenue
    for m in range(1, months + 1):
        rev = rev * (1 + growth_rate_monthly)
        curve.append(round(rev, 2))
    return curve


def _loan_risk_verdict(user_finance):
    """
    Pure math: if user is taking a loan and startup has slow returns,
    flag as HIGH LOAN RISK.
    """
    funding_type = user_finance.get("funding_type", "").lower()
    return_speed = user_finance.get("expected_return_speed", "").lower()  # slow/medium/fast
    monthly_obligation = user_finance.get("monthly_loan_obligation", 0)
    savings_runway_months = user_finance.get("savings_runway_months", 6)

    if "loan" in funding_type:
        if return_speed == "slow":
            return "CRITICAL — Loan + Slow Returns is dangerous. You must hit revenue before savings run out."
        elif return_speed == "medium":
            if savings_runway_months < 12:
                return "HIGH RISK — Loan with medium returns requires at least 12 months runway."
            return "MODERATE — Manageable if you have 12+ months runway."
        else:
            return "ACCEPTABLE — Fast returns can service the loan if demand holds."
    elif "savings" in funding_type or "self" in funding_type:
        return "LOWER RISK — Self-funded. No loan pressure."
    elif "investor" in funding_type:
        return "MODERATE — Investor expectations may pressure early growth."
    return "UNKNOWN — Provide funding type for better assessment."


def financial_math_agent(context):
    """
    Computes:
    - Break-even timeline (math-based)
    - Revenue growth curve (slow/medium/fast startup types)
    - Loan risk verdict based on user's financial situation
    - ROI estimate at 12 and 24 months
    - Recommendation: suited for loan-taker vs wealthy investor
    """

    idea = context.get("idea", "")
    user_finance = context.get("user_finance", {})
    market_score = context.get("market_analysis", {}).get("score", 5)
    feasibility_score = context.get("feasibility_analysis", {}).get("score", 5)
    business_score = context.get("business_model", {}).get("score", 5)
    local_score = context.get("local_context", {}).get("local_opportunity_score", 5)

    investment_amount = float(user_finance.get("investment_amount", 100000))
    monthly_costs = float(user_finance.get("monthly_operational_cost", 10000))
    funding_type = user_finance.get("funding_type", "savings")
    risk_appetite = user_finance.get("risk_appetite", "medium").lower()

    # --- Ask LLM for startup type (slow/medium/fast ramp) ---
    llm_prompt = f"""
You are a financial analyst evaluating startup economics.

Startup Idea: {idea}

Context Scores (0-10):
- Market: {market_score}
- Feasibility: {feasibility_score}
- Business Model: {business_score}
- Local Fit: {local_score}

Classify this startup's revenue ramp profile and estimate:

RULES:
- Return ONLY valid JSON
- No markdown, no extra text
- All numbers must be realistic

FORMAT:
{{
    "ramp_type": "SLOW / MEDIUM / FAST",
    "ramp_reasoning": "1-2 sentences why",
    "estimated_monthly_revenue_month1": number (in same currency as investment),
    "estimated_monthly_growth_rate": number (0.0 to 0.3, monthly percentage as decimal),
    "break_even_months_estimate": number,
    "revenue_risk_factors": ["factor1", "factor2"]
}}
"""

    llm_result = {}
    for _ in range(3):
        response = llm.invoke(llm_prompt).strip()
        response = re.sub(r"```json|```", "", response).strip()
        match = re.search(r"\{.*\}", response, re.DOTALL)
        if match:
            try:
                llm_result = json.loads(match.group(0))
                break
            except:
                continue

    # Safe defaults if LLM fails
    ramp_type = llm_result.get("ramp_type", "MEDIUM")
    ramp_reasoning = llm_result.get("ramp_reasoning", "Standard growth assumed.")
    initial_monthly_rev = float(llm_result.get("estimated_monthly_revenue_month1", investment_amount * 0.05))
    growth_rate = float(llm_result.get("estimated_monthly_growth_rate", 0.08))
    llm_breakeven = llm_result.get("break_even_months_estimate", 18)
    revenue_risk_factors = llm_result.get("revenue_risk_factors", [])

    # Clamp growth rate
    growth_rate = max(0.01, min(0.30, growth_rate))

    # --- Math: Growth Curve ---
    curve_24m = _compute_growth_curve(initial_monthly_rev, growth_rate, months=24)
    cumulative_revenue = [round(sum(curve_24m[:i+1]), 2) for i in range(24)]

    # --- Math: Break-even ---
    # Find month where cumulative revenue >= investment_amount
    total_costs_so_far = 0
    breakeven_month = None
    for i, monthly_rev in enumerate(curve_24m):
        total_costs_so_far += monthly_costs
        if cumulative_revenue[i] >= (investment_amount + total_costs_so_far):
            breakeven_month = i + 1
            break

    if breakeven_month is None:
        # Estimate beyond 24 months using formula
        # C * (1+r)^n >= Investment + n * monthly_cost
        # Approximation:
        breakeven_month = int(llm_breakeven)  # fall back to LLM estimate

    # --- ROI Math ---
    roi_12m = None
    roi_24m = None
    total_ops_12m = monthly_costs * 12
    total_ops_24m = monthly_costs * 24
    if len(cumulative_revenue) >= 12:
        roi_12m = round(((cumulative_revenue[11] - investment_amount - total_ops_12m) / investment_amount) * 100, 1)
    if len(cumulative_revenue) >= 24:
        roi_24m = round(((cumulative_revenue[23] - investment_amount - total_ops_24m) / investment_amount) * 100, 1)

    # --- Loan Risk ---
    loan_verdict = _loan_risk_verdict(user_finance)

    # --- Who should take this idea? ---
    if ramp_type == "SLOW":
        suited_for = "Wealthy investors / long-term thinkers. NOT recommended for loan-funded founders."
    elif ramp_type == "FAST":
        suited_for = "Loan-funded or time-pressured founders. Fast returns reduce financial risk."
    else:
        suited_for = "Suitable for self-funded or investor-backed founders with 12+ months runway."

    # --- Risk appetite alignment ---
    if risk_appetite == "low" and ramp_type == "SLOW":
        appetite_match = "MISMATCH — Slow returns conflict with low risk appetite. Reconsider."
    elif risk_appetite == "high" and ramp_type == "FAST":
        appetite_match = "ALIGNED — High risk appetite suits this fast-moving startup."
    else:
        appetite_match = "MODERATE MATCH — Proceed with careful cash flow planning."

    return {
        "ramp_type": ramp_type,
        "ramp_reasoning": ramp_reasoning,
        "break_even_months": breakeven_month,
        "roi_at_12_months_pct": roi_12m,
        "roi_at_24_months_pct": roi_24m,
        "monthly_revenue_curve_24m": curve_24m,
        "cumulative_revenue_24m": cumulative_revenue,
        "loan_risk_verdict": loan_verdict,
        "suited_for": suited_for,
        "risk_appetite_match": appetite_match,
        "revenue_risk_factors": revenue_risk_factors,
        "investment_amount": investment_amount,
        "monthly_costs": monthly_costs,
    }