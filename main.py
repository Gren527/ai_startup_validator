import streamlit as st
import plotly.graph_objects as go
from orchestrator import run_startup_validator
from pdf_report import generate_pdf

import warnings
import logging

# Hide python deprecation warnings
warnings.filterwarnings("ignore", category=UserWarning, module="transformers")

# Lower transformers logging level
logging.getLogger("transformers").setLevel(logging.ERROR)

st.set_page_config(page_title="AI Startup Validator", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>

.section {
    background: rgba(255,255,255,0.04);
    padding: 16px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.08);
    box-shadow: 0 4px 12px rgba(0,0,0,0.2);
    margin-bottom: 16px;
    transition: 0.2s ease;
}

.section:hover {
    transform: translateY(-2px);
    border: 1px solid rgba(0,201,255,0.3);
}

.section h3 {
    color: #00C9FF;
    margin-bottom: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="big-title">🚀 AI Startup Validator</div>', unsafe_allow_html=True)
st.caption("Evaluate your startup idea like an investor")

st.divider()

# ---------- INPUT FORM ----------
st.subheader("🧠 Startup Details")

col1, col2 = st.columns(2)

with col1:
    idea = st.text_area("💡 Startup Idea", placeholder="Explain what your startup does")

    problem = st.text_area(
        "⚠️ Problem Statement",
        placeholder="What problem are you solving?"
    )

with col2:
    stage = st.selectbox(
        "📍 Startup Stage",
        [
            "Just an idea",
            "Research phase",
            "Building MVP",
            "Early users",
            "Scaling",
            "Revenue generating"
        ]
    )

    target_users = st.text_input(
        "🎯 Target Users",
        placeholder="Students, businesses, developers..."
    )

value = st.text_area(
    "🚀 Unique Value Proposition",
    placeholder="What makes your idea different?"
)

st.divider()

# ---------- NEW: LOCAL CONTEXT ----------
st.subheader("📍 Local Context (Optional but Recommended)")
st.caption("Help the AI understand your local market ground reality")

use_local = st.checkbox("I want local market analysis")

local_info = {}

if use_local:
    lc1, lc2 = st.columns(2)
    with lc1:
        location_type = st.selectbox(
            "Location Type",
            ["Village", "Small Town", "Medium City", "Large City", "Metro/Capital"]
        )
        location_desc = st.text_input(
            "Describe your location",
            placeholder="e.g. Growing town near highway, 50km from city"
        )
        existing_businesses = st.text_input(
            "What businesses already exist nearby?",
            placeholder="e.g. Small shops, no malls, 2 restaurants, no theatres"
        )
    with lc2:
        local_population = st.text_input(
            "Approximate population",
            placeholder="e.g. 20,000 people"
        )
        local_demand_notes = st.text_area(
            "What do you observe about local demand?",
            placeholder="e.g. Many young people with no entertainment options, people travel 30km to the city for malls"
        )

    local_info = {
        "location_type": location_type,
        "location_description": location_desc,
        "existing_businesses": existing_businesses,
        "local_population": local_population,
        "local_demand_notes": local_demand_notes
    }

st.divider()

# ---------- NEW: FINANCIAL INPUTS ----------
st.subheader("💰 Your Financial Situation (Optional)")
st.caption("Required for ROI, break-even, and loan risk analysis")

use_finance = st.checkbox("I want financial math & growth projection")

user_finance = {}

if use_finance:
    fc1, fc2 = st.columns(2)
    with fc1:
        investment_amount = st.number_input(
            "Total Investment Amount (₹ or your currency)",
            min_value=1000,
            value=500000,
            step=10000
        )
        monthly_operational_cost = st.number_input(
            "Monthly Operational Cost",
            min_value=0,
            value=30000,
            step=1000
        )
        funding_type = st.selectbox(
            "How are you funding this?",
            ["Personal Savings", "Bank Loan", "Family Loan", "Angel Investor", "VC / External Investor", "Mixed"]
        )
    with fc2:
        risk_appetite = st.selectbox(
            "Your Risk Appetite",
            ["Low — I need returns fast", "Medium — I can wait 1-2 years", "High — I'm in for the long game"]
        )
        expected_return_speed = st.selectbox(
            "What return speed do you expect?",
            ["Fast (within 6 months)", "Medium (6-18 months)", "Slow (18+ months)"]
        )
        savings_runway_months = st.slider(
            "How many months can you survive without revenue?",
            min_value=1, max_value=36, value=12
        )
        monthly_loan_obligation = 0
        if "Loan" in funding_type:
            monthly_loan_obligation = st.number_input(
                "Monthly Loan EMI",
                min_value=0,
                value=10000,
                step=1000
            )

    # normalize values for agent
    return_speed_map = {
        "Fast (within 6 months)": "fast",
        "Medium (6-18 months)": "medium",
        "Slow (18+ months)": "slow"
    }
    risk_map = {
        "Low — I need returns fast": "low",
        "Medium — I can wait 1-2 years": "medium",
        "High — I'm in for the long game": "high"
    }

    user_finance = {
        "investment_amount": investment_amount,
        "monthly_operational_cost": monthly_operational_cost,
        "funding_type": funding_type.lower(),
        "risk_appetite": risk_map[risk_appetite],
        "expected_return_speed": return_speed_map[expected_return_speed],
        "savings_runway_months": savings_runway_months,
        "monthly_loan_obligation": monthly_loan_obligation
    }

st.divider()

# ---------- RADAR ----------
def radar(result):
    vals = [
        result.get("market_analysis", {}).get("score", 5),
        result.get("competitor_analysis", {}).get("score", 5),
        result.get("feasibility_analysis", {}).get("score", 5),
        result.get("business_model", {}).get("score", 5),
        result.get("innovation_analysis", {}).get("innovation_score", 5)
    ]
    # Add local score if available
    local_score = result.get("local_context", {}).get("local_opportunity_score")
    cats = ["Market", "Competition", "Feasibility", "Business", "Innovation"]
    if local_score is not None:
        vals.append(local_score)
        cats.append("Local Fit")

    vals += vals[:1]
    cats += cats[:1]

    fig = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0, 10])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


# ---------- GROWTH CHART ----------
def growth_chart(fp):
    curve = fp.get("monthly_revenue_curve_24m", [])
    cumulative = fp.get("cumulative_revenue_24m", [])
    if not curve:
        return

    months = list(range(1, len(curve) + 1))
    investment = fp.get("investment_amount", 0)
    monthly_costs = fp.get("monthly_costs", 0)
    cost_line = [investment + monthly_costs * m for m in months]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=curve, name="Monthly Revenue", mode="lines+markers",
                             line=dict(color="#00C9FF")))
    fig.add_trace(go.Scatter(x=months, y=cumulative, name="Cumulative Revenue", mode="lines",
                             line=dict(color="#92FE9D", dash="dot")))
    fig.add_trace(go.Scatter(x=months, y=cost_line, name="Investment + Ops Cost", mode="lines",
                             line=dict(color="#FF6B6B", dash="dash")))

    be = fp.get("break_even_months")
    if be and be <= len(curve):
        fig.add_vline(x=be, line_color="orange", annotation_text=f"Break-even ~month {be}")

    fig.update_layout(
        title="24-Month Revenue Projection",
        xaxis_title="Month",
        yaxis_title="Revenue",
        template="plotly_dark"
    )
    st.plotly_chart(fig, use_container_width=True)


# ---------- RUN ----------
if st.button("🚀 Validate Startup Idea"):

    if not idea.strip():
        st.warning("Please enter your startup idea")
        st.stop()

    user_input = f"""
    Idea: {idea}
    Stage: {stage}
    Target Users: {target_users}
    Problem: {problem}
    Unique Value: {value}
    """

    try:
        with st.spinner("🤖 AI agents analyzing your startup..."):
            result = run_startup_validator(
                user_input,
                local_info=local_info if use_local else None,
                user_finance=user_finance if use_finance else None
            )
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    st.success("✅ Analysis Complete")

    st.markdown(f"### 📍 Startup Stage: **{stage}**")

    col1, col2 = st.columns(2)

    # ---------- LEFT ----------
    with col1:
        m = result.get("market_analysis", {})

        st.markdown(f"""
        <div class="section">
        <h3>📊 Market</h3>
        {m.get('target_users','Not available')}<br>
        Demand: {m.get('market_demand','N/A')}<br>
        Size: {m.get('market_size','N/A')}<br>
        Growth: {m.get('industry_growth','N/A')}
        </div>
        """, unsafe_allow_html=True)

        st.progress(m.get("score", 5) / 10)

        f = result.get("feasibility_analysis", {})

        st.markdown(f"""
        <div class="section">
        <h3>⚙️ Feasibility</h3>
        {f.get('technologies','N/A')}<br>
        Complexity: {f.get('complexity','N/A')}<br>
        Timeline: {f.get('timeline','N/A')}
        </div>
        """, unsafe_allow_html=True)

        st.progress(f.get("score", 5) / 10)

    # ---------- RIGHT ----------
    with col2:
        c = result.get("competitor_analysis", {})
        comp = ", ".join(c.get("competitors", [])) if c.get("competitors") else "Not found"

        st.markdown(f"""
        <div class="section">
        <h3>🏢 Competitors</h3>
        {comp}<br>
        Features: {c.get('features','N/A')}
        </div>
        """, unsafe_allow_html=True)

        st.progress(c.get("score", 5) / 10)

        b = result.get("business_model", {})

        st.markdown(f"""
        <div class="section">
        <h3>💰 Business</h3>
        Revenue: {b.get('revenue_model','N/A')}<br>
        Pricing: {b.get('pricing_strategy','N/A')}<br>
        Scalability: {b.get('scalability','N/A')}
        </div>
        """, unsafe_allow_html=True)

        st.progress(b.get("score", 5) / 10)

    # ---------- INNOVATION ----------
    i = result.get("innovation_analysis", {})

    st.markdown(f"""
    <div class="section">
    <h3>🚀 Innovation</h3>
    {i.get('reason','N/A')}
    </div>
    """, unsafe_allow_html=True)

    st.progress(i.get("innovation_score", 5) / 10)

    # ---------- NEW: LOCAL CONTEXT ----------
    lc = result.get("local_context", {})
    if lc and lc.get("local_fit_verdict") not in ("NOT PROVIDED", None):
        verdict_color = {
            "STRONG FIT": "#4CAF50",
            "MODERATE FIT": "#FFC107",
            "WEAK FIT": "#FF5722",
            "PREMATURE": "#9C27B0",
            "UNKNOWN": "#888"
        }.get(lc.get("local_fit_verdict", ""), "#888")

        unmet = "".join([f"• {n}<br>" for n in lc.get("unmet_local_needs", [])])
        local_risks = "".join([f"• {r}<br>" for r in lc.get("local_risks", [])])

        st.markdown(f"""
        <div class="section">
        <h3>📍 Local Market Fit</h3>
        <span style="color:{verdict_color};font-weight:bold">{lc.get('local_fit_verdict','N/A')}</span><br><br>
        {lc.get('local_demand_assessment','')}<br><br>
        <b>Unmet Local Needs:</b><br>{unmet}
        <b>Local Risks:</b><br>{local_risks}
        </div>
        """, unsafe_allow_html=True)

        st.progress(lc.get("local_opportunity_score", 5) / 10)

    # ---------- NEW: FINANCIAL PROJECTION ----------
    fp = result.get("financial_projection", {})
    if fp:
        st.subheader("📈 Financial Projection")

        ramp_color = {"SLOW": "#FF5722", "MEDIUM": "#FFC107", "FAST": "#4CAF50"}.get(fp.get("ramp_type", ""), "#888")

        loan_verdict = fp.get("loan_risk_verdict", "N/A")
        loan_color = "#4CAF50" if "LOWER" in loan_verdict or "ACCEPTABLE" in loan_verdict else \
                     "#FFC107" if "MODERATE" in loan_verdict else "#FF5722"

        fc1, fc2, fc3 = st.columns(3)
        with fc1:
            st.metric("Break-even", f"Month {fp.get('break_even_months', 'N/A')}")
        with fc2:
            roi12 = fp.get("roi_at_12_months_pct")
            st.metric("ROI @ 12 months", f"{roi12}%" if roi12 is not None else "N/A")
        with fc3:
            roi24 = fp.get("roi_at_24_months_pct")
            st.metric("ROI @ 24 months", f"{roi24}%" if roi24 is not None else "N/A")

        st.markdown(f"""
        <div class="section">
        <h3>📊 Growth Profile</h3>
        <b>Ramp Type:</b> <span style="color:{ramp_color};font-weight:bold">{fp.get('ramp_type','N/A')}</span><br>
        {fp.get('ramp_reasoning','')}<br><br>
        <b>Suited For:</b> {fp.get('suited_for','N/A')}<br>
        <b>Risk Appetite Match:</b> {fp.get('risk_appetite_match','N/A')}<br><br>
        <b>Loan Risk:</b> <span style="color:{loan_color}">{loan_verdict}</span>
        </div>
        """, unsafe_allow_html=True)

        growth_chart(fp)

    # ---------- RADAR ----------
    st.subheader("📊 Startup Profile")
    radar(result)

    # ---------- RISK ----------
    r = result.get("risk_analysis", {})
    risk_score = r.get("risk_score", 5)

    if risk_score >= 7:
        st.error(f"🔴 High Risk ({risk_score}/10)")
    elif risk_score >= 4:
        st.warning(f"🟡 Moderate Risk ({risk_score}/10)")
    else:
        st.success(f"🟢 Low Risk ({risk_score}/10)")

    # ---------- FINAL ----------
    score = result.get("final_score", 5)

    st.markdown(f"""
    <h2 style='text-align:center;'>📊 Final Score</h2>
    <h1 style='text-align:center;color:#00C9FF'>{score}/10</h1>
    """, unsafe_allow_html=True)

    st.progress(score / 10)

    # ---------- DECISION ----------
    st.subheader("💰 Investment Recommendation")

    if score >= 8 and risk_score <= 6:
        st.success("🟢 INVEST")
    elif score >= 6:
        st.warning("🟡 CONSIDER")
    else:
        st.error("🔴 REJECT")

    # ---------- WHY ----------
    st.subheader("🧠 Why this decision?")

    reasons = []

    if m.get("score", 5) >= 8:
        reasons.append("Strong market demand")
    if risk_score >= 7:
        reasons.append("High risk reduces confidence")
    if i.get("innovation_score", 5) < 7:
        reasons.append("Low innovation")
    if lc.get("local_fit_verdict") == "STRONG FIT":
        reasons.append("Excellent local market opportunity")
    elif lc.get("local_fit_verdict") == "PREMATURE":
        reasons.append("Local market may not be ready yet")
    if fp.get("ramp_type") == "SLOW" and fp.get("loan_risk_verdict", "").startswith("CRITICAL"):
        reasons.append("Slow returns with loan funding is critical risk")

    if not reasons:
        reasons.append("Balanced across all metrics")

    for reason in reasons:
        st.write(f"• {reason}")

    # ---------- PDF ----------
    pdf = generate_pdf(result)
    with open(pdf, "rb") as f:
        st.download_button("📄 Download Report", f, "report.pdf")