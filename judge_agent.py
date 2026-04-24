import os
import re
from dotenv import load_dotenv
load_dotenv()

from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
MODEL = "models/gemma-3-4b-it"

# ── Judge prompt ──────────────────────────────────────────────────────────────
JUDGE_PROMPT = """You are an expert consulting report evaluator.

Original business problem:
{problem}

Report to evaluate:
{report}

Score the report on a scale of 0–10 for each criterion, then give an overall score:

1. Structure (0–10): Does the report follow the required sections clearly?
2. Logical Reasoning (0–10): Are conclusions logically derived from the findings?
3. Relevance (0–10): Is the content directly relevant to the stated business problem?
4. Actionability (0–10): Are the recommendations specific, practical, and implementable?

Respond in EXACTLY this format (no extra text):
STRUCTURE: <score>
REASONING: <score>
RELEVANCE: <score>
ACTIONABILITY: <score>
OVERALL: <score>
FEEDBACK: <one or two sentences of the most important improvement needed>"""


def parse_judgment(raw: str) -> dict:
    result = {}
    patterns = {
        "structure":     r"STRUCTURE:\s*([\d.]+)",
        "reasoning":     r"REASONING:\s*([\d.]+)",
        "relevance":     r"RELEVANCE:\s*([\d.]+)",
        "actionability": r"ACTIONABILITY:\s*([\d.]+)",
        "score":         r"OVERALL:\s*([\d.]+)",
        "feedback":      r"FEEDBACK:\s*(.+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, raw, re.IGNORECASE | re.DOTALL)
        if match:
            result[key] = match.group(1).strip()

    if "score" not in result:
        sub_keys = ["structure", "reasoning", "relevance", "actionability"]
        sub_scores = [float(result[k]) for k in sub_keys if k in result]
        result["score"] = round(sum(sub_scores) / len(sub_scores), 1) if sub_scores else "N/A"

    if "feedback" not in result:
        result["feedback"] = "No specific feedback provided."

    return result


def evaluate_report(report: str, problem: str) -> dict:
    if not report.strip():
        return {"score": 0, "feedback": "Empty report — nothing to evaluate."}

    prompt = JUDGE_PROMPT.format(problem=problem, report=report)

    try:
        response = client.models.generate_content(model=MODEL, contents=prompt)
        return parse_judgment(response.text)
    except Exception as e:
        return {"score": "N/A", "feedback": f"Judge API call failed: {e}"}
