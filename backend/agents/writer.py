from langchain_groq import ChatGroq
from agents.graph import ResearchState
from core.config import settings

llm = ChatGroq(
    api_key=settings.groq_api_key,
    model="llama-3.3-70b-versatile",
    max_tokens=8192
)


def build_context(top_chunks):
    context = ""
    for i, chunk in enumerate(top_chunks, 1):
        context += f"[Source {i}]: {chunk['text']}\n\n"
    return context


async def writer_node(state: ResearchState) -> dict:
    context = build_context(state["top_chunks"])
    response = await llm.ainvoke(
        f"Write a research report on: {state['query']}\nSources:\n{context}"
    )
    return {"report": response.content}