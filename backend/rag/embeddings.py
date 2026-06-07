_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def embed_text(text: str) -> list[float]:
    return _get_model().encode(text).tolist()


def embed_texts(texts: list[str]) -> list[list[float]]:
    return _get_model().encode(texts).tolist()