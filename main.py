import streamlit as st
import plotly.graph_objects as go
from orchestrator import run_startup_validator
from pdf_report import generate_pdf

st.set_page_config(page_title="AI Startup Validator", layout="wide")

# ---------- CSS ----------
st.markdown("""
<style>
.big-title {
    font-size: 44px;
    font-weight: 800;
    background: linear-gradient(90deg, #00C9FF, #92FE9D);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.card {
    background: #111;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #222;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# ---------- HEADER ----------
st.markdown('<div class="big-title">🚀 AI Startup Validator</div>', unsafe_allow_html=True)
st.write("Analyze your startup idea using AI agents")
st.divider()

# ---------- INPUT ----------
idea = st.text_area("Enter your startup idea")

# ---------- RADAR ----------
def radar(result):
    vals = [
        result.get("market_analysis", {}).get("score", 5),
        result.get("competitor_analysis", {}).get("score", 5),
        result.get("feasibility_analysis", {}).get("score", 5),
        result.get("business_model", {}).get("score", 5),
        result.get("innovation_analysis", {}).get("innovation_score", 5)
    ]
    cats = ["Market","Competition","Feasibility","Business","Innovation"]

    vals += vals[:1]
    cats += cats[:1]

    fig = go.Figure(go.Scatterpolar(r=vals, theta=cats, fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,10])), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ---------- RUN ----------
if st.button("Validate Startup Idea"):

    if not idea.strip():
        st.warning("Enter idea")
        st.stop()

    try:
        with st.spinner("Analyzing..."):
            result = run_startup_validator(idea)
    except Exception as e:
        st.error(f"Error: {e}")
        st.stop()

    st.success("Analysis Complete")

    col1, col2 = st.columns(2)

    # ---------- LEFT ----------
    with col1:
        m = result.get("market_analysis", {})

        st.markdown(f"""
        <div class="card">
        <h3>📊 Market</h3>
        {m.get('target_users','Not available')}<br>
        Demand: {m.get('market_demand','N/A')}<br>
        Size: {m.get('market_size','N/A')}<br>
        Growth: {m.get('industry_growth','N/A')}
        </div>
        """, unsafe_allow_html=True)

        st.progress(m.get("score",5)/10)

        f = result.get("feasibility_analysis", {})

        st.markdown(f"""
        <div class="card">
        <h3>⚙️ Feasibility</h3>
        {f.get('technologies','N/A')}<br>
        Complexity: {f.get('complexity','N/A')}<br>
        Timeline: {f.get('timeline','N/A')}
        </div>
        """, unsafe_allow_html=True)

        st.progress(f.get("score",5)/10)

    # ---------- RIGHT ----------
    with col2:
        c = result.get("competitor_analysis", {})
        comp = ", ".join(c.get("competitors", [])) if c.get("competitors") else "Not found"

        st.markdown(f"""
        <div class="card">
        <h3>🏢 Competitors</h3>
        {comp}<br>
        Features: {c.get('features','N/A')}
        </div>
        """, unsafe_allow_html=True)

        st.progress(c.get("score",5)/10)

        b = result.get("business_model", {})

        st.markdown(f"""
        <div class="card">
        <h3>💰 Business</h3>
        Revenue: {b.get('revenue_model','N/A')}<br>
        Pricing: {b.get('pricing_strategy','N/A')}<br>
        Scalability: {b.get('scalability','N/A')}
        </div>
        """, unsafe_allow_html=True)

        st.progress(b.get("score",5)/10)

    # ---------- INNOVATION ----------
    i = result.get("innovation_analysis", {})

    st.markdown(f"""
    <div class="card">
    <h3>🚀 Innovation</h3>
    {i.get('reason','N/A')}
    </div>
    """, unsafe_allow_html=True)

    st.progress(i.get("innovation_score",5)/10)

    # ---------- RADAR ----------
    st.subheader("📊 Startup Profile")
    radar(result)

    # ---------- RISK ----------
    r = result.get("risk_analysis", {})
    risk_score = r.get("risk_score",5)

    if risk_score >= 7:
        st.error(f"🔴 High Risk ({risk_score}/10)")
    elif risk_score >= 4:
        st.warning(f"🟡 Moderate Risk ({risk_score}/10)")
    else:
        st.success(f"🟢 Low Risk ({risk_score}/10)")

    # ---------- FINAL ----------
    score = result.get("final_score",5)

    st.markdown(f"""
    <h2 style='text-align:center;'>📊 Final Score</h2>
    <h1 style='text-align:center;color:#00C9FF'>{score}/10</h1>
    """, unsafe_allow_html=True)

    st.progress(score/10)

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

    if m.get("score",5) >= 8:
        reasons.append("Strong market demand")
    if risk_score >= 7:
        reasons.append("High risk reduces confidence")
    if i.get("innovation_score",5) < 7:
        reasons.append("Low innovation")

    if not reasons:
        reasons.append("Balanced across all metrics")

    for reason in reasons:
        st.write(f"• {reason}")

    # ---------- PDF ----------
    pdf = generate_pdf(result)
    with open(pdf, "rb") as f:
        st.download_button("📄 Download Report", f, "report.pdf")