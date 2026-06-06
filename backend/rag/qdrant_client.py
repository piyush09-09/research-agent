import uuid
import hashlib
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from rag.embeddings import embed_text, embed_texts
from core.config import settings

client = QdrantClient(path = settings.qdrant_path)

COLLECTION = "research_docs"
VECTOR_SIZE = 384

def ensure_collection():
    collections = [c.name for c in client.get_collections().collections]
    if COLLECTION not in collections:
        client.create_collection(
            collection_name = COLLECTION,
            vectors_config = VectorParams(size = VECTOR_SIZE, distance = Distance.COSINE)

        )

def chunk_text(text: str, chunk_size:int=400)->list[str]:
    """Split text into chunks of roughly chunk_size words."""
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size):
        chunk = " ".join(words[i:i+chunk_size])
        if chunk.strip():
            chunks.append(chunk)
    return chunks

def deterministic_id(text: str) -> str:
    """Same text always gets same ID — prevents duplicate upserts."""
    return hashlib.md5(text.encode()).hexdigest()


def upsert_docs(docs: list[dict])->int:
    """Chunk and store documents. Returns number of points upserted."""
    ensure_collection()

    all_chunks = []
    for doc in docs:
        chunks = chunk_text(doc["content"])
        for chunk in chunks:
            all_chunks.append({
                "text": chunk,
                "task": doc.get("task", "")
            })
    
    if not all_chunks:
        return 0

    texts = [c["text"] for c in all_chunks]
    vectors = embed_texts(texts)

    points = [
        PointStruct(
            id=deterministic_id(texts[i]),
            vector = vectors[i],
            payload = all_chunks[i]
        )
        for i in range(len(all_chunks))
    ]

    client.upsert(collection_name=COLLECTION, points = points)
    return len(points)


def search_similar(query: str, limit: int = 20)->list[dict]:
    """Dense vector search."""
    ensure_collection()
    query_vector = embed_text(query)

    results = client.query_points(
        collection_name = COLLECTION,
        query = query_vector,
        limit = limit
    )

    return [
        {"text": r.payload["text"], "task": r.payload.get("task", ""), "score":r.score}
        for r in results.points
    ]