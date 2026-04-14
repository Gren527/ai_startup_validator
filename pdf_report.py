from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase.pdfmetrics import stringWidth
import re

def generate_pdf(result):

    c = canvas.Canvas("startup_report.pdf", pagesize=letter)
    width, height = letter
    y = height - 50

    def check():
        nonlocal y
        if y < 80:
            c.showPage()
            y = height - 50

    def wrap(text, max_width=450):
        words = str(text).split()
        lines, cur = [], ""
        for w in words:
            test = cur + " " + w if cur else w
            if stringWidth(test, "Helvetica", 11) < max_width:
                cur = test
            else:
                lines.append(cur)
                cur = w
        if cur:
            lines.append(cur)
        return lines

    def draw(text):
        nonlocal y
        text = re.sub(r"\*\*", "", str(text))
        for line in wrap(text):
            check()
            c.drawString(60, y, line)
            y -= 14

    def title(text):
        nonlocal y
        c.setFont("Helvetica-Bold", 18)
        c.setFillColor(colors.HexColor("#00C9FF"))
        c.drawString(140, y, text)
        c.setFillColor(colors.black)
        y -= 30

    def section(text):
        nonlocal y
        check()
        c.setFont("Helvetica-Bold", 13)
        c.setFillColor(colors.HexColor("#4CAF50"))
        c.drawString(50, y, text)
        c.setFillColor(colors.black)
        y -= 20

    def line(label, val):
        nonlocal y
        check()
        c.setFont("Helvetica-Bold", 11)
        c.drawString(60, y, f"{label}:")
        y -= 14
        c.setFont("Helvetica", 11)
        draw(val)
        y -= 5

    def bullets(arr):
        for item in arr:
            draw("• " + str(item))

    # ---------- TITLE ----------
    title("Startup Validation Report")

    # ---------- IDEA ----------
    section("💡 Idea")
    draw(result.get("idea", ""))

    # ---------- MARKET ----------
    m = result.get("market_analysis", {})
    section("📊 Market Analysis")
    line("Target Users", m.get("target_users", ""))
    line("Demand", m.get("market_demand", ""))
    line("Market Size", m.get("market_size", ""))
    line("Growth", m.get("industry_growth", ""))
    line("Score", f"{m.get('score',5)}/10")

    # ---------- COMPETITOR ----------
    cpt = result.get("competitor_analysis", {})
    section("🏢 Competitor Analysis")
    line("Competitors", ", ".join(cpt.get("competitors", [])))
    line("Features", cpt.get("features", ""))
    line("Strengths", cpt.get("strengths", ""))
    line("Weaknesses", cpt.get("weaknesses", ""))
    line("Score", f"{cpt.get('score',5)}/10")

    # ---------- FEASIBILITY ----------
    f = result.get("feasibility_analysis", {})
    section("⚙️ Feasibility")
    line("Technologies", f.get("technologies", ""))
    line("Complexity", f.get("complexity", ""))
    line("Timeline", f.get("timeline", ""))
    line("Score", f"{f.get('score',5)}/10")

    # ---------- BUSINESS ----------
    b = result.get("business_model", {})
    section("💰 Business Model")
    line("Revenue", b.get("revenue_model", ""))
    line("Pricing", b.get("pricing_strategy", ""))
    line("Scalability", b.get("scalability", ""))
    line("Score", f"{b.get('score',5)}/10")

    # ---------- INNOVATION ----------
    i = result.get("innovation_analysis", {})
    section("🚀 Innovation")
    line("Score", f"{i.get('innovation_score',5)}/10")
    draw(i.get("reason", ""))

    # ---------- RISK ----------
    r = result.get("risk_analysis", {})
    section("😈 Risk Analysis")
    line("Risk Score", f"{r.get('risk_score',5)}/10")
    line("Verdict", r.get("verdict", ""))

    if "risk_factors" in r:
        section("Risk Factors")
        bullets(r.get("risk_factors", []))

    # ---------- IMPROVEMENTS ----------
    section("💡 Improvements")
    improvements = result.get("suggested_improvements", "").split("\n")
    bullets([i for i in improvements if i.strip()])

    # ---------- FINAL ----------
    score = result.get("final_score", 5)
    section("📊 Final Score")
    draw(f"{score}/10")

    # ---------- DECISION ----------
    section("💰 Decision")

    if score >= 8 and r.get("risk_score",5) <= 6:
        decision = "INVEST"
    elif score >= 6:
        decision = "CONSIDER"
    else:
        decision = "REJECT"

    draw(decision)

    # ---------- WHY ----------
    section("🧠 Why This Decision")

    reasons = []

    if m.get("score",5) >= 8:
        reasons.append("Strong market demand")
    if r.get("risk_score",5) >= 7:
        reasons.append("High risk reduces confidence")
    if i.get("innovation_score",5) < 7:
        reasons.append("Low innovation compared to competitors")

    if not reasons:
        reasons.append("Balanced performance across all areas")

    bullets(reasons)

    c.save()
    return "startup_report.pdf"