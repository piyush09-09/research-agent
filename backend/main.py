import json
import re
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from contextlib import asynccontextmanager
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from agents.graph import build_graph, ResearchState
from agents.writer import llm as writer_llm
from core.database import init_db
from core.config import settings
from auth import create_user, login_user, decode_token


# ── Rate Limiter ──
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app):
    await init_db()
    yield


app = FastAPI(title="AI Research Agent", lifespan=lifespan)
app.state.limiter = limiter


# ── Rate limit error handler ──
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    return HTTPException(status_code=429, detail="Too many requests. Please wait before trying again.")


# ── CORS — lock to your frontend URLs ──
app.add_middleware(
    CORSMiddleware,
 allow_origins=[
    "http://localhost:5173",
    "http://localhost:4173",
    # Add after Vercel deploy:
    # "https://research-agent-yourusername.vercel.app",
],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type", "Authorization"],
)

graph = build_graph()


# ── Input sanitization ──
def sanitize_query(query: str) -> str:
    """Clean user input to prevent injection and abuse."""
    # Strip HTML tags
    query = re.sub(r'<[^>]+>', '', query)
    # Remove control characters
    query = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', query)
    # Collapse excessive whitespace
    query = re.sub(r'\s+', ' ', query).strip()
    return query


# ── Auth dependency ──
async def get_current_user(request: Request) -> dict:
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid token")

    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Token expired or invalid")

    return payload


# ── Request models with validation ──
class SignupRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=6, max_length=128)


class LoginRequest(BaseModel):
    email: str = Field(min_length=5, max_length=200)
    password: str = Field(min_length=1, max_length=128)


class ResearchRequest(BaseModel):
    query: str = Field(min_length=3, max_length=1000)
    word_limit: int = Field(default=500, ge=100, le=5000)


def sse_event(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


# ── Auth endpoints ──
@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/auth/signup")
@limiter.limit("5/minute")
async def signup(request: Request, body: SignupRequest):
    result = await create_user(body.name, body.email, body.password)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@app.post("/auth/login")
@limiter.limit("10/minute")
async def login(request: Request, body: LoginRequest):
    result = await login_user(body.email, body.password)
    if "error" in result:
        raise HTTPException(status_code=401, detail=result["error"])
    return result


# ── Protected research endpoint ──
@app.post("/research")
@limiter.limit("5/hour")
async def research(request: Request, body: ResearchRequest, user: dict = Depends(get_current_user)):
    async def event_generator():
        query = sanitize_query(body.query)
        word_limit = body.word_limit

        if len(query) < 3:
            yield sse_event({"type": "step", "label": "Query too short. Please ask a longer question."})
            yield sse_event({"type": "done", "report": ""})
            return

        print(f"\n[SERVER] User: {user.get('email')} | Query: {query} | Limit: {word_limit}")

        # Step 1: Planner
        yield sse_event({"type": "step", "label": "Planner breaking down your query..."})

        from agents.planner import planner_node
        state: ResearchState = {
            "query": query,
            "tasks": [],
            "raw_docs": [],
            "top_chunks": [],
            "report": "",
            "eval_scores": {}
        }

        result = await planner_node(state)
        state["tasks"] = result["tasks"]

        task_names = [t["task"] for t in state["tasks"]]
        yield sse_event({"type": "step", "label": f"Created {len(task_names)} research tasks"})
        yield sse_event({"type": "tasks", "tasks": task_names})

        # Step 2: Researcher
        yield sse_event({"type": "step", "label": "Researcher investigating sources..."})

        from agents.researcher import researcher_node
        result = await researcher_node(state)
        state["raw_docs"] = result["raw_docs"]

        yield sse_event({"type": "step", "label": f"Collected {len(state['raw_docs'])} documents"})

        # Step 3: Synthesizer
        yield sse_event({"type": "step", "label": "Synthesizer finding relevant chunks..."})

        from agents.synthesizer import synthesizer_node
        result = await synthesizer_node(state)
        state["top_chunks"] = result["top_chunks"]

        yield sse_event({"type": "step", "label": f"Selected top {len(state['top_chunks'])} chunks"})

        # Step 4: Writer
        yield sse_event({"type": "step", "label": "Writer generating report..."})

        context = ""
        for i, chunk in enumerate(state["top_chunks"], 1):
            context += f"[Source {i}]: {chunk['text']}\n\n"

        full_report = ""

        if word_limit <= 1000:
            prompt = f"""You are a research report writer. Write a well-structured markdown report.
Cite sources as [1], [2], etc.

Query: {state['query']}

Sources:
{context}

STRICT LENGTH: Write approximately {word_limit} words total.
{"Maximum 2-3 short sections. Be very concise. No filler." if word_limit <= 300 else "Cover key points in 4-5 sections."}"""

            async for chunk in writer_llm.astream(prompt):
                token = chunk.content
                if token:
                    full_report += token
                    yield sse_event({"type": "token", "content": token})

        else:
            words_per_section = 400 if word_limit <= 2500 else 700
            num_sections = max(4, word_limit // words_per_section)

            yield sse_event({"type": "step", "label": f"Planning {num_sections}-section outline..."})

            outline_prompt = f"""Create an outline for a research report on: {state['query']}
Generate exactly {num_sections} section titles (NOT including Introduction and Conclusion).
Return ONLY a numbered list."""

            outline_response = await writer_llm.ainvoke(outline_prompt)
            sections = []
            for line in outline_response.content.strip().split("\n"):
                line = line.strip()
                if line and line[0].isdigit():
                    title = line.split(".", 1)[-1].strip() if "." in line else line
                    if title:
                        sections.append(title)

            if not sections or len(sections) < 3:
                sections = ["Background", "Key Findings", "Analysis", "Discussion", "Implications"]

            sections = sections[:num_sections]
            yield sse_event({"type": "step", "label": f"Writing {len(sections) + 2} sections..."})

            # Introduction
            yield sse_event({"type": "step", "label": "Writing: Introduction"})
            intro_prompt = f"""Write ONLY the Introduction ({words_per_section} words) for a research report on:
Query: {state['query']}
Sources: {context}
Start with: # Introduction
Cite as [1], [2]. Do NOT write any other section."""

            async for chunk in writer_llm.astream(intro_prompt):
                token = chunk.content
                if token:
                    full_report += token
                    yield sse_event({"type": "token", "content": token})

            full_report += "\n\n"
            yield sse_event({"type": "token", "content": "\n\n"})

            # Body sections
            for idx, section_title in enumerate(sections):
                yield sse_event({"type": "step", "label": f"Writing section {idx + 1}/{len(sections)}: {section_title}"})

                section_prompt = f"""Write ONLY the section "{section_title}" ({words_per_section} words) for a research report.
Topic: {state['query']}
Sources: {context}
Start with: ## {section_title}
Cite sources. Be detailed. Do NOT write introduction or conclusion."""

                async for chunk in writer_llm.astream(section_prompt):
                    token = chunk.content
                    if token:
                        full_report += token
                        yield sse_event({"type": "token", "content": token})

                full_report += "\n\n"
                yield sse_event({"type": "token", "content": "\n\n"})

            # Conclusion
            yield sse_event({"type": "step", "label": "Writing: Conclusion"})
            conclusion_prompt = f"""Write ONLY the Conclusion ({words_per_section} words) for a research report on:
Query: {state['query']}
Summary: {full_report[:2000]}
Start with: ## Conclusion
Summarize key findings, cite sources."""

            async for chunk in writer_llm.astream(conclusion_prompt):
                token = chunk.content
                if token:
                    full_report += token
                    yield sse_event({"type": "token", "content": token})

        # Step 5: RAGAS Evaluation
        yield sse_event({"type": "step", "label": "Running RAGAS evaluation..."})

        from eval.ragas_eval import run_evaluation
        try:
            eval_scores = await run_evaluation(
                query=state["query"],
                report=full_report,
                top_chunks=state["top_chunks"]
            )
            yield sse_event({"type": "eval", "scores": eval_scores})
        except Exception as e:
            print(f"[EVAL] Failed: {e}")
            yield sse_event({"type": "eval", "scores": {"overall": -1}})

        yield sse_event({"type": "done", "report": full_report})

    return StreamingResponse(event_generator(), media_type="text/event-stream")