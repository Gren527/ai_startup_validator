import streamlit as st
import re
from orchestrator import run_startup_validator
from pdf_report import generate_pdf


# ---------- SCORE EXTRACTION FUNCTION ----------
def extract_score(text):

    import re

    match = re.search(r"startup\s*score[^0-9]*([0-9]+(\.[0-9]+)?)", text, re.IGNORECASE)

    if match:
        return float(match.group(1))

    return 0


# ---------- PAGE CONFIG ----------
st.set_page_config(
    page_title="AI Startup Validator",
    layout="wide"
)

st.title("🚀 AI Startup Idea Validator")

st.write("""
Enter your startup idea and our AI agents will analyze:

• Market demand  
• Competitors  
• Technical feasibility  
• Business model  
• Startup viability  
• Improvement suggestions  
""")

st.divider()


# ---------- USER INPUT ----------
idea = st.text_area(
    "Enter your startup idea",
    placeholder="Example ideas: AI resume builder, smart diet planner, AI travel planner"
)


# ---------- RUN ANALYSIS ----------
if st.button("Validate Startup Idea"):

    if idea.strip() == "":
        st.warning("Please enter a startup idea")

    else:

        progress = st.progress(0)

        progress.progress(20)

        with st.spinner("AI agents analyzing your idea..."):

            result = run_startup_validator(idea)

        progress.progress(100)

        st.success("Analysis Complete")

        st.divider()

        # ---------- RESULTS DISPLAY ----------
        col1, col2 = st.columns(2)

        with col1:

            st.subheader("📊 Market Analysis")
            st.write(result["market_analysis"])

            st.subheader("⚙️ Technical Feasibility")
            st.write(result["feasibility_analysis"])

            st.subheader("📈 Startup Evaluation")
            st.write(result["startup_evaluation"])

        with col2:

            st.subheader("🏢 Competitor Analysis")
            st.write(result["competitor_analysis"])

            st.subheader("💰 Business Model")
            st.write(result["business_model"])

            st.subheader("💡 Suggested Improvements")
            st.write(result["suggested_improvements"])

        st.divider()


        # ---------- SCORE VISUALIZATION ----------
        st.subheader("📊 Startup Score")

        score = extract_score(result["startup_evaluation"])

        if score > 10:
            score = 10

        st.progress(score / 10)

        st.write(f"Estimated Startup Score: **{score}/10**")


        st.divider()


        # ---------- PDF REPORT ----------
        pdf_file = generate_pdf(result)

        with open(pdf_file, "rb") as file:

            st.download_button(
                label="📄 Download Full Startup Report",
                data=file,
                file_name="startup_validation_report.pdf",
                mime="application/pdf"
            )