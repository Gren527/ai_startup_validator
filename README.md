# 🚀 AI Startup Idea Validator

An advanced **multi-agent AI system** that analyzes startup ideas and provides structured insights, scoring, and investment recommendations.

---

## 🧠 Overview

This project uses multiple AI agents to evaluate a startup idea across different dimensions such as:

- 📊 Market Analysis  
- 🏢 Competitor Analysis  
- ⚙️ Technical Feasibility  
- 💰 Business Model  
- 🚀 Innovation  
- 😈 Risk Assessment  

It combines all these into a **final score and investment decision**.

---

## ⚙️ Features

- ✅ Multi-agent architecture  
- ✅ Parallel processing using ThreadPoolExecutor  
- ✅ Explainable AI (WHY decision)  
- ✅ Final score (0–10)  
- ✅ Investment recommendation:
  - 🟢 INVEST  
  - 🟡 CONSIDER  
  - 🔴 REJECT  
- ✅ Interactive dashboard (Streamlit)  
- ✅ Radar chart visualization  
- ✅ Risk indicator  
- ✅ PDF report generation  

---

## 🧠 System Architecture
User Input
↓
Orchestrator
↓
| Market Agent |
| Competitor Agent |
| Feasibility Agent |
| Business Agent |
| Innovation Agent |
| Risk Agent |

↓
Final Score + Decision + Report


---

## 📊 Scoring Logic

Final score is computed using weighted contributions from:

- Market Score  
- Competitor Score  
- Feasibility Score  
- Business Score  
- Innovation Score  
- Risk Adjustment  

---

## 🖥️ UI

Built using **Streamlit**, featuring:

- Clean card-based layout  
- Radar chart visualization  
- Score progress bars  
- Risk level indicator  
- Explainable "Why this decision" section  

---

## 📄 PDF Report

Generates a structured multi-page report including:

- Full analysis of all agents  
- Risk breakdown  
- Final decision  
- Explanation  

---

## 🛠️ Tech Stack

- Python  
- Streamlit  
- Plotly  
- LangChain  
- Ollama (LLM - llama3)  
- ReportLab  

---
