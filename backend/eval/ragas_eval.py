import json
import re
from langchain_groq import ChatGroq
from core.config import settings

eval_llm = ChatGroq(
    api_key=settings.groq_api_key,
    model="llama-3.1-8b-instant",
    temperature=0.3
)

GRADE_MAP = {
    "A": 0.95,
    "B": 0.78,
    "C": 0.55,
    "D": 0.35,
    "F": 0.15
}


async def _call_judge(prompt: str) -> float:
    try:
        response = await eval_llm.ainvoke(prompt)
        text = response.content.strip().upper()
        # Find the letter grade
        for grade in ["A", "B", "C", "D", "F"]:
            if f"GRADE: {grade}" in text or f'"GRADE":"{grade}"' in text.replace(" ", "") or f"GRADE:{grade}" in text.replace(" ", ""):
                return GRADE_MAP[grade]
        # Fallback: find any standalone letter grade
        match = re.search(r'\b([ABCDF])\b', text)
        if match:
            return GRADE_MAP.get(match.group(1), 0.55)
        return 0.55
    except Exception as e:
        print(f"[EVAL] Judge call failed: {e}")
        return -1.0


async def score_faithfulness(report: str, sources: str) -> float:
    prompt = f"""Grade the FAITHFULNESS of this report. Does it only state things the sources support?

Sources:
{sources[:2000]}

Report:
{report[:2000]}

Pick ONE grade:
A = every claim is in the sources
B = most claims supported, 1-2 minor extras
C = several unsupported claims
D = many fabricated details
F = mostly made up

Write your reasoning in 2 sentences, then write GRADE: followed by the letter."""

    return await _call_judge(prompt)


async def score_relevancy(report: str, query: str) -> float:
    prompt = f"""Grade the ANSWER RELEVANCY. Does the report actually answer this query?

Query: {query}

Report:
{report[:2000]}

Pick ONE grade:
A = directly and thoroughly answers the query
B = answers the main question but misses a minor aspect
C = partially answers, some parts are off-topic
D = barely related to the query
F = completely off-topic

Write your reasoning in 2 sentences, then write GRADE: followed by the letter."""

    return await _call_judge(prompt)


async def score_context_precision(query: str, sources: str) -> float:
    prompt = f"""Grade the CONTEXT PRECISION. Are these retrieved sources relevant to the query?

Query: {query}

Sources:
{sources[:2000]}

Pick ONE grade:
A = all sources are directly relevant
B = most relevant, 1-2 are tangential
C = about half are relevant
D = most are irrelevant noise
F = none relate to the query

Write your reasoning in 2 sentences, then write GRADE: followed by the letter."""

    return await _call_judge(prompt)


async def run_evaluation(query: str, report: str, top_chunks: list) -> dict:
    sources = "\n\n".join([f"[{i+1}]: {c['text']}" for i, c in enumerate(top_chunks)])

    print("\n[EVAL] Running RAGAS evaluation...")

    faithfulness = await score_faithfulness(report, sources)
    relevancy = await score_relevancy(report, query)
    precision = await score_context_precision(query, sources)

    scores = {
        "faithfulness": round(faithfulness, 2),
        "answer_relevancy": round(relevancy, 2),
        "context_precision": round(precision, 2),
    }

    valid = [v for v in scores.values() if v >= 0]
    scores["overall"] = round(sum(valid) / len(valid), 2) if valid else -1.0

    print(f"[EVAL] Scores: {scores}")
    return scores