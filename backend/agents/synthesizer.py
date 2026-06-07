import os
from agents.graph import ResearchState
from rag.qdrant_client import upsert_docs, search_similar

reranker = None


def _get_reranker():
    global reranker
    if reranker is None:
        from sentence_transformers import CrossEncoder
        reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
    return reranker


async def synthesizer_node(state: ResearchState) -> dict:
    count = upsert_docs(state["raw_docs"])
    print(f"\n[SYNTHESIZER] Upserted {count} chunks into Qdrant")

    candidates = search_similar(state["query"], limit=20)
    print(f"[SYNTHESIZER] Retrieved {len(candidates)} candidates")

    if not candidates:
        return {"top_chunks": []}

    # Skip re-ranking in production to save memory
    use_reranker = os.environ.get("USE_RERANKER", "true").lower() == "true"

    if use_reranker:
        try:
            rr = _get_reranker()
            pairs = [(state["query"], c["text"]) for c in candidates]
            scores = rr.predict(pairs)
            for i, c in enumerate(candidates):
                c["rerank_score"] = float(scores[i])
            ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
            top_chunks = ranked[:8]
            print(f"[SYNTHESIZER] Re-ranked to top {len(top_chunks)}")
        except Exception as e:
            print(f"[SYNTHESIZER] Re-ranker failed, using dense scores: {e}")
            top_chunks = candidates[:8]
    else:
        top_chunks = candidates[:8]
        print(f"[SYNTHESIZER] Using top {len(top_chunks)} by dense score (re-ranker disabled)")

    return {"top_chunks": top_chunks}