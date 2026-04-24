import os
from dotenv import load_dotenv
load_dotenv()

import streamlit as st
from research_agent import run_research
from judge_agent import evaluate_report
from google import genai

# ── Config ────────────────────────────────────────────────────────────────────
client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "models/gemma-3-4b-it"

st.set_page_config(
    page_title="ConsultGenie",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;600;700&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@300;400&display=swap');

:root {
    --bg:       #07090f;
    --bg2:      #0c1018;
    --bg3:      #111820;
    --border:   #1c2a3a;
    --border2:  #243348;
    --cyan:     #00c2d4;
    --violet:   #8b6fff;
    --green:    #00d68f;
    --text:     #d0dce8;
    --muted:    #526070;
    --faint:    #1e2e3e;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif !important;
    background: var(--bg) !important;
    color: var(--text) !important;
}
.stApp { background: var(--bg) !important; }

/* subtle dot grid */
.stApp::before {
    content: '';
    position: fixed; inset: 0;
    background-image: radial-gradient(circle, rgba(0,194,212,0.06) 1px, transparent 1px);
    background-size: 28px 28px;
    pointer-events: none;
    z-index: 0;
}

/* ── Header ── */
.cg-header {
    padding: 2.8rem 0 2rem;
    text-align: center;
}
.cg-eyebrow {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.68rem;
    letter-spacing: 0.28em;
    color: var(--cyan);
    text-transform: uppercase;
    margin-bottom: 0.7rem;
    opacity: 0;
    animation: riseIn 0.6s ease 0.1s forwards;
}
.cg-title {
    font-family: 'Playfair Display', serif !important;
    font-size: 3.6rem;
    font-weight: 700;
    letter-spacing: -0.5px;
    color: #eaf2ff;
    margin: 0;
    line-height: 1.1;
    opacity: 0;
    animation: riseIn 0.7s ease 0.2s forwards;
}
.cg-title span {
    background: linear-gradient(120deg, var(--cyan) 0%, var(--violet) 60%, var(--green) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.cg-tagline {
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.88rem;
    font-weight: 300;
    color: var(--muted);
    margin-top: 0.7rem;
    letter-spacing: 0.04em;
    opacity: 0;
    animation: riseIn 0.7s ease 0.35s forwards;
}
.cg-rule {
    width: 60px; height: 1px;
    background: linear-gradient(90deg, var(--cyan), var(--violet));
    margin: 1.2rem auto 0;
    opacity: 0;
    animation: riseIn 0.6s ease 0.45s forwards;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] label {
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.7rem !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    color: var(--muted) !important;
}
section[data-testid="stSidebar"] .stTextArea textarea {
    background: var(--bg) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.85rem !important;
    line-height: 1.65 !important;
    resize: none !important;
}
section[data-testid="stSidebar"] .stTextArea textarea:focus {
    border-color: var(--cyan) !important;
    box-shadow: 0 0 0 3px rgba(0,194,212,0.1) !important;
    outline: none !important;
}
section[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: var(--bg) !important;
    border-color: var(--border) !important;
    border-radius: 6px !important;
    color: var(--text) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.85rem !important;
}

/* ── Generate button ── */
.stButton > button[kind="primary"] {
    width: 100% !important;
    background: transparent !important;
    border: 1px solid var(--cyan) !important;
    color: var(--cyan) !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.78rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    border-radius: 6px !important;
    padding: 0.65rem 1rem !important;
    transition: all 0.25s ease !important;
    position: relative !important;
    overflow: hidden !important;
}
.stButton > button[kind="primary"]:hover {
    background: rgba(0,194,212,0.08) !important;
    box-shadow: 0 0 20px rgba(0,194,212,0.2) !important;
    transform: translateY(-1px) !important;
}

/* ── Step tracker ── */
.steps-wrap {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 0;
    margin: 2rem 0 1rem;
}
.step-node {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 6px;
}
.step-circle {
    width: 36px; height: 36px;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 400;
    transition: all 0.4s ease;
}
.step-circle.done {
    background: linear-gradient(135deg, var(--cyan), var(--violet));
    color: #000;
    font-weight: 600;
    box-shadow: 0 0 16px rgba(0,194,212,0.4);
}
.step-circle.active {
    background: transparent;
    border: 1.5px solid var(--cyan);
    color: var(--cyan);
    animation: stepPulse 2s infinite;
}
.step-circle.idle {
    background: var(--bg3);
    border: 1px solid var(--border);
    color: var(--muted);
}
.step-text {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: var(--muted);
}
.step-text.active { color: var(--cyan); }
.step-line {
    width: 56px; height: 1px;
    background: var(--border);
    margin-bottom: 22px;
    transition: background 0.5s ease;
}
.step-line.done { background: linear-gradient(90deg, var(--cyan), var(--violet)); }

/* ── Section label ── */
.section-label {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: var(--cyan);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 8px;
}
.section-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: var(--border);
}

/* ── Report card ── */
.report-wrap {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 2.2rem 2.6rem;
    position: relative;
    animation: riseIn 0.5s ease both;
    line-height: 1.75;
}
.report-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    border-radius: 12px 12px 0 0;
    background: linear-gradient(90deg, var(--cyan), var(--violet), var(--green));
}
.report-wrap h2 {
    font-family: 'Playfair Display', serif !important;
    font-size: 1.35rem !important;
    font-weight: 600 !important;
    color: #eaf2ff !important;
    margin: 1.6rem 0 0.5rem !important;
    padding-bottom: 0.4rem !important;
    border-bottom: 1px solid var(--border) !important;
    letter-spacing: 0 !important;
}
.report-wrap h3 {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    color: var(--cyan) !important;
    margin: 1.2rem 0 0.3rem !important;
    letter-spacing: 0.02em !important;
}
.report-wrap p {
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 300 !important;
    color: #a8bccf !important;
    line-height: 1.8 !important;
    margin-bottom: 0.8rem !important;
}
.report-wrap ul, .report-wrap ol {
    font-size: 0.88rem !important;
    font-weight: 300 !important;
    color: #a8bccf !important;
    line-height: 1.8 !important;
    padding-left: 1.4rem !important;
}
.report-wrap li { margin-bottom: 0.3rem !important; }
.report-wrap strong {
    color: var(--text) !important;
    font-weight: 500 !important;
}

/* ── Score panel ── */
.score-wrap {
    background: var(--bg2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 1.8rem 1.6rem;
    position: relative;
    animation: riseIn 0.5s ease 0.15s both;
}
.score-wrap::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0; height: 2px;
    border-radius: 12px 12px 0 0;
    background: linear-gradient(90deg, var(--violet), var(--green));
}
.score-big {
    font-family: 'Playfair Display', serif;
    font-size: 5.5rem;
    font-weight: 700;
    line-height: 1;
    text-align: center;
    background: linear-gradient(135deg, var(--cyan) 30%, var(--green) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.score-denom {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    color: var(--muted);
    text-align: center;
    text-transform: uppercase;
    margin-top: 0.2rem;
}
.bar-track {
    background: var(--bg3);
    border-radius: 3px;
    height: 4px;
    margin: 1.2rem 0 0.25rem;
    overflow: hidden;
}
.bar-fill {
    height: 100%;
    border-radius: 3px;
    background: linear-gradient(90deg, var(--cyan), var(--green));
    transition: width 1.8s cubic-bezier(0.22, 1, 0.36, 1);
}
.crit-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid var(--faint);
}
.crit-row:last-child { border-bottom: none; }
.crit-name {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
}
.crit-val {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.78rem;
    color: var(--cyan);
}
.feedback-card {
    background: var(--bg3);
    border-left: 2px solid var(--violet);
    border-radius: 0 6px 6px 0;
    padding: 0.9rem 1rem;
    margin-top: 1.2rem;
    font-family: 'IBM Plex Sans', sans-serif;
    font-size: 0.78rem;
    font-weight: 300;
    color: #7a94a8;
    line-height: 1.7;
}
.feedback-card strong {
    display: block;
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.62rem;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: var(--violet);
    margin-bottom: 0.4rem;
    font-weight: 400;
}

/* ── Sidebar info block ── */
.info-block {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.66rem;
    line-height: 2;
    color: var(--muted);
    letter-spacing: 0.06em;
}
.info-block .tag {
    display: inline-block;
    padding: 1px 7px;
    border-radius: 3px;
    font-size: 0.6rem;
    font-weight: 400;
    margin-right: 4px;
}
.tag-cyan  { background: rgba(0,194,212,0.12); color: var(--cyan); }
.tag-vio   { background: rgba(139,111,255,0.12); color: var(--violet); }
.tag-green { background: rgba(0,214,143,0.12); color: var(--green); }

/* ── Misc ── */
.streamlit-expanderHeader {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 6px !important;
    font-family: 'IBM Plex Mono', monospace !important;
    font-size: 0.72rem !important;
    color: var(--muted) !important;
    letter-spacing: 0.08em !important;
}
.stStatus {
    background: var(--bg2) !important;
    border-color: var(--border) !important;
    font-family: 'IBM Plex Sans', sans-serif !important;
    font-size: 0.84rem !important;
}
hr { border-color: var(--border) !important; }
.stAlert { border-radius: 6px !important; }

/* ── Animations ── */
@keyframes riseIn {
    from { opacity: 0; transform: translateY(12px); }
    to   { opacity: 1; transform: translateY(0); }
}
@keyframes stepPulse {
    0%, 100% { box-shadow: 0 0 0 0 rgba(0,194,212,0.35); }
    50%       { box-shadow: 0 0 0 7px rgba(0,194,212,0); }
}
</style>
""", unsafe_allow_html=True)

# ── Prompts ───────────────────────────────────────────────────────────────────
SYSTEM_PROMPT = """You are a senior management consultant.
Given a business problem and research findings, produce a structured consulting report with exactly these sections:

## Problem Framing
## Root Cause Analysis
## Key Findings
## Recommendations

Be specific, concise, and actionable. Use data from research where available."""

DECOMPOSE_PROMPT = """You are an AI task planner for a consulting firm.

Business Problem: {problem}
Industry: {industry}

Step 1 — Decide if web research is needed (answer YES or NO, then explain briefly).
Step 2 — If YES, write 2–3 focused search queries (one per line, prefixed with QUERY:).
Step 3 — List the consulting frameworks you will apply (e.g. SWOT, RCA, Porter's Five Forces).

Keep your response short and structured."""

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="cg-header">
    <div class="cg-eyebrow">Agentic AI System &nbsp;·&nbsp; v2.0</div>
    <div class="cg-title">Consult<span>Genie</span></div>
    <div class="cg-tagline">Strategy-grade consulting reports, generated by AI agents</div>
    <div class="cg-rule"></div>
</div>
""", unsafe_allow_html=True)

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.65rem;
letter-spacing:0.2em;text-transform:uppercase;color:#00c2d4;
padding:0.6rem 0 1.2rem;">// Problem Input</div>
""", unsafe_allow_html=True)

    business_problem = st.text_area(
        "Business Problem",
        placeholder="Describe the core challenge your organisation is facing. Be specific about symptoms, context, and goals.",
        height=170,
        label_visibility="collapsed",
    )
    st.markdown("""
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;
letter-spacing:0.14em;color:#526070;margin:-6px 0 8px;">
BUSINESS PROBLEM
</div>""", unsafe_allow_html=True)

    industry = st.selectbox(
        "Industry",
        ["Retail / E-commerce", "Healthcare", "Finance / Banking",
         "Manufacturing", "SaaS / Technology", "Logistics", "Education", "Other"],
        label_visibility="collapsed",
    )
    st.markdown("""
<div style="font-family:'IBM Plex Mono',monospace;font-size:0.62rem;
letter-spacing:0.14em;color:#526070;margin:-6px 0 14px;">
INDUSTRY SECTOR
</div>""", unsafe_allow_html=True)

    generate_btn = st.button("⚡  Generate Report", type="primary", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("""
<div class="info-block">
<span class="tag tag-cyan">Gemini</span> LLM Reasoning<br>
<span class="tag tag-vio">Tavily</span> Web Research<br>
<span class="tag tag-green">Judge</span> Report Evaluation<br>
</div>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def gemini(prompt: str) -> str:
    response = client.models.generate_content(model=MODEL, contents=prompt)
    return response.text


def render_steps(current: int):
    labels = ["Decompose", "Research", "Report", "Judge"]
    html = '<div class="steps-wrap">'
    for i, label in enumerate(labels):
        if i < current:
            circle_cls = "done"
            text_cls = ""
            symbol = "✓"
        elif i == current:
            circle_cls = "active"
            text_cls = "active"
            symbol = str(i + 1)
        else:
            circle_cls = "idle"
            text_cls = ""
            symbol = str(i + 1)

        html += f"""
<div class="step-node">
    <div class="step-circle {circle_cls}">{symbol}</div>
    <div class="step-text {text_cls}">{label}</div>
</div>"""
        if i < len(labels) - 1:
            line_cls = "done" if i < current else ""
            html += f'<div class="step-line {line_cls}"></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)


def decide_and_search(problem, industry):
    decompose_response = gemini(DECOMPOSE_PROMPT.format(problem=problem, industry=industry))
    queries = [
        line.replace("QUERY:", "").strip()
        for line in decompose_response.splitlines()
        if line.strip().startswith("QUERY:")
    ]
    research_summary = run_research(queries) if queries else ""
    return decompose_response, research_summary


def generate_report(problem, industry, research):
    prompt = f"""{SYSTEM_PROMPT}

Business Problem: {problem}
Industry: {industry}

Research Findings:
{research if research else "No external research conducted — use domain knowledge only."}

Now write the full consulting report:"""
    return gemini(prompt)


def render_report(md: str) -> str:
    """Convert basic markdown to styled HTML for the report card."""
    import re
    lines = md.split("\n")
    out = []
    for line in lines:
        line = line.rstrip()
        if line.startswith("## "):
            out.append(f"<h2>{line[3:]}</h2>")
        elif line.startswith("### "):
            out.append(f"<h3>{line[4:]}</h3>")
        elif line.startswith("- ") or line.startswith("* "):
            out.append(f"<li>{line[2:]}</li>")
        elif line == "":
            out.append("<br>")
        else:
            line = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', line)
            out.append(f"<p>{line}</p>")
    return "\n".join(out)


# ── Main flow ─────────────────────────────────────────────────────────────────
if generate_btn:
    if not business_problem.strip():
        st.warning("Please enter a business problem before generating.")
        st.stop()

    step_ph = st.empty()

    with st.status("Running ConsultGenie agent…", expanded=True) as status:

        with step_ph.container():
            render_steps(0)
        st.write("Decomposing the problem and deciding on research strategy…")
        try:
            decompose_text, research_summary = decide_and_search(business_problem, industry)
        except Exception as e:
            st.error(f"Decomposition failed: {e}")
            st.stop()

        with st.expander("View agent planning output"):
            st.code(decompose_text, language=None)

        with step_ph.container():
            render_steps(1)
        if research_summary:
            st.write("Web research completed via Tavily.")
            with st.expander("View research findings"):
                st.markdown(research_summary)
        else:
            st.write("Web research not required — proceeding with domain knowledge.")

        with step_ph.container():
            render_steps(2)
        st.write("Generating structured consulting report…")
        try:
            report = generate_report(business_problem, industry, research_summary)
        except Exception as e:
            st.error(f"Report generation failed: {e}")
            st.stop()

        with step_ph.container():
            render_steps(3)
        st.write("Evaluating report quality with LLM Judge…")
        try:
            judgment = evaluate_report(report, business_problem)
        except Exception as e:
            judgment = {"score": "N/A", "feedback": f"Judge failed: {e}"}

        with step_ph.container():
            render_steps(4)
        status.update(label="Report generated successfully.", state="complete")

    # ── Output ────────────────────────────────────────────────────────────────
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1], gap="large")

    with col1:
        st.markdown('<div class="section-label">Consulting Report</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="report-wrap">{render_report(report)}</div>', unsafe_allow_html=True)

    with col2:
        score        = judgment.get("score", "N/A")
        feedback     = judgment.get("feedback", "No feedback available.")
        structure    = judgment.get("structure", "–")
        reasoning    = judgment.get("reasoning", "–")
        relevance    = judgment.get("relevance", "–")
        actionability = judgment.get("actionability", "–")

        try:
            pct = float(score) * 10
        except (ValueError, TypeError):
            pct = 0

        st.markdown('<div class="section-label">Evaluation</div>', unsafe_allow_html=True)
        st.markdown(f"""
<div class="score-wrap">
    <div class="score-big">{score}</div>
    <div class="score-denom">Overall Score / 10</div>
    <div class="bar-track">
        <div class="bar-fill" style="width:{pct}%"></div>
    </div>
    <br>
    <div class="crit-row">
        <span class="crit-name">Structure</span>
        <span class="crit-val">{structure} / 10</span>
    </div>
    <div class="crit-row">
        <span class="crit-name">Reasoning</span>
        <span class="crit-val">{reasoning} / 10</span>
    </div>
    <div class="crit-row">
        <span class="crit-name">Relevance</span>
        <span class="crit-val">{relevance} / 10</span>
    </div>
    <div class="crit-row">
        <span class="crit-name">Actionability</span>
        <span class="crit-val">{actionability} / 10</span>
    </div>
    <div class="feedback-card">
        <strong>Judge Feedback</strong>
        {feedback}
    </div>
</div>
""", unsafe_allow_html=True)
