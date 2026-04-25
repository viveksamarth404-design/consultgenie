# 🧠 ConsultGenie — Agentic AI Consulting Report Generator

> AI Agent System · Semester IV ECE · B.Tech ECE-B · 2025–26

A production-grade agentic AI system that takes a business problem and industry as input, autonomously decides whether to search the web for real-world data, applies consulting frameworks, generates a structured professional report, and evaluates its own output using an LLM-as-Judge — all in one pipeline.

**Live Demo →** [web-production-537f9.up.railway.app](https://web-production-537f9.up.railway.app)

---

## 👥 Team

| Role | Member | Roll No. |
|------|--------|----------|
| Role A — Architect & Integrator | Vivek Samarth | 16 |
| Role B — Builder & Deployer | Dipanshu Sule | 15 |

**Semester:** IV · B.Tech ECE-B  
**Department:** Electronics and Communication Engineering  
**Date:** 24/04/2026

---

## 📋 Table of Contents

1. [Problem Statement](#-problem-statement)
2. [Why an Agentic Approach](#-why-an-agentic-approach)
3. [System Architecture](#-system-architecture)
4. [Agent Workflow](#-agent-workflow)
5. [Task Decomposition](#-task-decomposition)
6. [LLM-as-Judge](#️-llm-as-judge)
7. [Technology Stack](#-technology-stack)
8. [Key Features](#-key-features)
9. [Setup & Installation](#-setup--installation)
10. [Deployment](#-deployment)
11. [Example Output](#-example-output)
12. [Project Structure](#️-project-structure)

---

## 🎯 Problem Statement

**Consulting Report Writer**

Given a business problem and industry, the agent autonomously researches best practices, precedent cases, and expert frameworks via Tavily Search, then produces a structured consulting-style report covering:

- **Problem Framing** — understanding the core issue in context
- **Root Cause Analysis** — identifying underlying causes, not just symptoms
- **Key Findings** — insights drawn from real-world research and frameworks
- **Actionable Recommendations** — concrete steps the business can implement

The pipeline involves three coordinated agents:

| Agent | Role |
|-------|------|
| **Framework Researcher** | Decides which consulting frameworks apply and what to search |
| **Analysis Agent** | Processes Tavily search results and applies SWOT / RCA / Gap Analysis |
| **Report Writer** | Generates the full structured consulting report |

A separate **LLM-as-Judge** then evaluates the report on structure, logical reasoning, and actionability — scoring each dimension independently before the output is shown to the user.

---

## 🤖 Why an Agentic Approach

| Requirement | Why a Single Prompt Fails | Why the Agent Works |
|-------------|--------------------------|---------------------|
| Current best practices | LLM training cutoff — data is stale | Agent calls Tavily at query time for live data |
| Problem-specific reasoning | Generic output, no contextualisation | Gemini decomposes the problem before deciding what to search |
| Consulting frameworks | No structured methodology | Agent applies SWOT, Root Cause Analysis, Gap Analysis |
| Quality assurance | No self-checking | Separate LLM-as-Judge evaluates the report independently |
| Multi-step coordination | Cannot research + analyse + report in one pass | Each stage is a discrete, verifiable step in the pipeline |

The key agentic property is the autonomous decision at Step 2: the agent reads the problem, reasons about whether real-world search would improve the output, and decides whether to invoke Tavily or skip it — without being told which to do.

---

## 🔄 Agent Workflow

**Step 1 — User Input**  
User enters a business problem and selects an industry via the Streamlit sidebar.

**Step 2 — Problem Decomposition (Agentic Decision Point)**  
Gemini reads the problem and decides:
- Is real-world web research needed? (YES / NO)
- If YES → outputs `QUERY:` prefixed search strings
- Which consulting frameworks apply (SWOT, RCA, Gap Analysis, Porter's Five Forces)

This is the core agentic behaviour — the agent reasons about what it needs before acting.

**Step 3 — Tavily Research (Conditional)**  
If `QUERY:` lines were produced:
- Each query is sent to Tavily Search API
- Results are filtered (minimum 80 characters, no duplicate URLs)
- Filtered results are summarised into a markdown research block

If no queries were produced → step is skipped entirely.

**Step 4 — Framework Analysis**  
Gemini receives the problem + research summary and applies the selected consulting frameworks to extract structured insights.

**Step 5 — Report Generation**  
Gemini generates a full consulting report in exactly this structure:
```
## Problem Framing
## Root Cause Analysis
## Key Findings
## Recommendations
```

**Step 6 — LLM-as-Judge Evaluation**  
A separate Gemini call (acting as an independent evaluator) scores the report:
```
STRUCTURE:     x/10
REASONING:     x/10
RELEVANCE:     x/10
ACTIONABILITY: x/10
OVERALL:       x/10
FEEDBACK:      <specific improvement suggestion>
```

**Step 7 — Final Output**  
Streamlit displays the full report alongside the judge's score panel. If the overall score is below 5, a warning prompts the user to refine the problem statement.

---

## 📊 Task Decomposition

| Stage | Input | Decision / Logic | Tool Used | Output |
|-------|-------|-----------------|-----------|--------|
| 1. User input | Business problem text + industry | Always executes | Streamlit UI | Raw problem string |
| 2. Decomposition | Problem string | Gemini decides: search needed? Outputs QUERY: lines if yes | Gemini API | Plan text + 0–3 search queries |
| 3. Research | QUERY: lines | Triggered only if ≥1 QUERY: line exists. Skipped otherwise | Tavily Search API | Filtered markdown: best practices, expert data |
| 4. Analysis | Problem + research summary | Always executes. Applies SWOT / RCA / Gap Analysis | Gemini API | Structured analytical context |
| 5. Report gen | Analytical context + problem | Always executes. Produces 4-section report | Gemini API | Full consulting report (markdown) |
| 6. Judge eval | Report + original problem | Always executes. Independent quality check | Gemini API (Judge) | Score per criterion + overall + feedback |
| 7. Display | Report + judgment dict | Score < 5 → show warning. Always render report + panel | Streamlit UI | Final rendered output in browser |

**Agent Decision Logic:**
```
Problem received
      │
      ▼
Does it involve current practices,
market data, or recent industry events?
      │
   YES → Gemini outputs QUERY: lines → Tavily fires
   NO  → Gemini skips search → uses domain knowledge only
      │
      ▼
Tavily returns results
      │
Are results meaningful? (>80 chars, not duplicate)
   YES → Include in research summary
   NO  → Filter out, proceed without that result
      │
      ▼
Judge scores the report
      │
Score ≥ 7 → Green indicator, output accepted ✅
Score 5–6 → Orange indicator, review recommended ⚠️
Score < 5 → Red warning, refine and regenerate ❌
```

---

## ⚖️ LLM-as-Judge

The Judge is a completely separate Gemini call with its own system prompt. It has no memory of generating the report — it evaluates it as an independent reviewer would.

### Scoring Criteria

| Criterion | What It Checks | Score Interpretation |
|-----------|---------------|---------------------|
| Structure (0–10) | Are all 4 sections present and clearly separated? | 8–10: Complete; 5–7: Partial; <5: Unstructured |
| Logical Reasoning (0–10) | Do conclusions follow from the root cause and findings? | 8–10: Tight logic; 5–7: Some gaps; <5: Non-sequitur |
| Relevance (0–10) | Is the report specific to the stated problem, not generic? | 8–10: Highly specific; 5–7: Partially generic; <5: Off-topic |
| Actionability (0–10) | Can someone actually implement the recommendations? | 8–10: Concrete steps; 5–7: Vague; <5: Aspirational only |

### Judge Prompt Format
```
STRUCTURE:     <score>
REASONING:     <score>
RELEVANCE:     <score>
ACTIONABILITY: <score>
OVERALL:       <score>
FEEDBACK:      <one or two sentences on the most important improvement>
```

---

## 🛠 Technology Stack

| Layer | Technology | Purpose |
|-------|------------|---------|
| UI | Streamlit | Input sidebar, step tracker, report display, score panel |
| LLM | Google Gemini API (google-genai) | Decomposition, analysis, report generation, Judge evaluation |
| Search Tool | Tavily Search API | Live web research — best practices, expert frameworks, precedent cases |
| Language | Python 3.11+ | All backend logic, agent orchestration |
| Environment | python-dotenv | Secure API key loading from .env |
| Deployment | Railway | Cloud hosting with public live URL via Procfile |

---

## ✨ Key Features

- **Agentic search decision** — the agent reasons about whether to search before acting, not blindly every time
- **Real-time research data** — Tavily fetches live best practices and expert frameworks at query time
- **Consulting framework application** — SWOT, Root Cause Analysis, and Gap Analysis applied automatically
- **LLM-as-Judge quality gate** — independent evaluation with per-criterion scoring before output is shown
- **Step-by-step transparency** — animated step tracker shows which stage the agent is in
- **Low-score warnings** — if the Judge scores below 5, user is prompted to refine the problem
- **Dark professional UI** — Playfair Display + IBM Plex typography, dark theme, gradient score panel

---

## 🚀 Setup & Installation

### Prerequisites
- Python 3.11 or higher
- A Google Gemini API key
- A Tavily API key

### 1. Clone the repository
```bash
git clone https://github.com/viveksamarth404-design/consultgenie.git
cd consultgenie
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create your .env file
Create a file named `.env` in the project root:
```env
GEMINI_API_KEY=your_gemini_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

> ⚠️ **Never commit this file to GitHub.** It is already listed in `.gitignore`.

### 4. Run the app
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`

---

## 🌐 Deployment

The application is deployed on Railway and publicly accessible at:  
**[web-production-537f9.up.railway.app](https://web-production-537f9.up.railway.app)**

### Deploy your own instance on Railway

1. Push the repository to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
3. Select your repository
4. In the **Variables** tab, add:
   - `GEMINI_API_KEY`
   - `TAVILY_API_KEY`
5. Railway auto-detects the Procfile and deploys automatically

**Procfile contents:**
```
web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
```

### Common Deployment Errors

| Error | Fix |
|-------|-----|
| `KeyError: GEMINI_API_KEY` | Add the variable in Railway's Variables tab |
| `ModuleNotFoundError` | Ensure requirements.txt is in the root directory |
| Blank page on load | Check Railway logs — usually a missing env var |
| `429 RESOURCE_EXHAUSTED` | Gemini free tier quota hit — wait 24 hrs or create a new API key |

---

## 📄 Example Output

**Input:**
```
Business Problem: Our team struggles to identify root causes when product quality drops.
Manual investigation takes weeks and relies on tribal knowledge.
Industry: Manufacturing / Operations
```

**Generated Report (excerpt):**
```markdown
## Problem Framing
The organisation faces a systemic gap in its quality management process —
investigations are unstructured, slow, and dependent on individual expertise
rather than repeatable methodology...

## Root Cause Analysis
The bottleneck is the absence of a standardised diagnostic framework.
Without a shared language for problem-solving, each investigation
restarts from zero...

## Key Findings
- Industry benchmarks show structured RCA reduces recurrence by 60–70%
- Cross-functional visibility gaps are the leading driver of delayed root cause identification
- Digital traceability tools reduce investigation time from weeks to hours

## Recommendations
1. Implement the 5-Why + Fishbone methodology as the standard investigation protocol
2. Deploy a lightweight digital traceability layer on the production line
3. Run quarterly cross-functional reviews to capture systemic patterns
```

**Judge Score: 8.5 / 10**  
*Feedback: Recommendations would benefit from specific implementation timelines and cost estimates.*

---

## 🎥 Demo Video

📹 Loom walkthrough: https://www.loom.com/share/3f3eb1f2e07141a98be6c76385b58ad1

The video covers:
- Problem statement and motivation
- End-to-end demo with a real business problem
- LLM-as-Judge evaluation in action

---

## 🗂 Project Structure

```
consultgenie/
├── app.py                  # Streamlit UI + agent orchestration
├── research_agent.py       # Tavily integration + result filtering
├── judge_agent.py          # LLM-as-Judge evaluation logic
├── requirements.txt        # Python dependencies
├── Procfile                # Railway deployment config
├── architecture.svg        # System architecture diagram
├── .gitignore              # Excludes .env from version control
└── README.md               # This file
```

---

## 📦 Requirements

```
streamlit>=1.40.0
google-genai>=1.0.0
tavily-python>=0.3.3
python-dotenv>=1.0.0
```

---

## 🔒 Environment Variables

| Variable | Description | Where to Get |
|----------|-------------|--------------|
| `GEMINI_API_KEY` | Google Gemini API key | [aistudio.google.com](https://aistudio.google.com) |
| `TAVILY_API_KEY` | Tavily Search API key | [app.tavily.com](https://app.tavily.com) |

---

*ConsultGenie · ECE Semester IV Project · B.Tech ECE-A · 2025–26*
