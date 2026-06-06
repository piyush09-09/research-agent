from sentence_transformers import CrossEncoder
from agents.graph import ResearchState
from rag.qdrant_client import upsert_docs, search_similar

# Load cross-encoder once at startup (~50MB download on first run)
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


async def synthesizer_node(state: ResearchState) -> dict:
    # Step 1: Store all researcher docs in Qdrant
    count = upsert_docs(state["raw_docs"])
    print(f"\n[SYNTHESIZER] Upserted {count} chunks into Qdrant")

    # Step 2: Retrieve top 20 via dense search (cast a wide net)
    candidates = search_similar(state["query"], limit=20)
    print(f"[SYNTHESIZER] Retrieved {len(candidates)} candidates from Qdrant")

    if not candidates:
        return {"top_chunks": []}

    # Step 3: Re-rank with cross-encoder (the upgrade)
    pairs = [(state["query"], c["text"]) for c in candidates]
    scores = reranker.predict(pairs)

    # Attach re-ranker scores and sort
    for i, candidate in enumerate(candidates):
        candidate["rerank_score"] = float(scores[i])

    ranked = sorted(candidates, key=lambda x: x["rerank_score"], reverse=True)
    top_chunks = ranked[:8]

    print(f"[SYNTHESIZER] Re-ranked to top {len(top_chunks)} chunks:")
    for i, r in enumerate(top_chunks):
        print(f"  [{i+1}] (dense: {r['score']:.3f}, rerank: {r['rerank_score']:.3f}) {r['text'][:80]}...")

    return {"top_chunks": top_chunks}