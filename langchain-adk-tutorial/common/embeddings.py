"""Turn text into vectors (embeddings), with the same Gemini / local switch as common/models.py.

EMBEDDING_PROVIDER=gemini (default) uses Gemini on Vertex AI with the GOOGLE_* settings from .env.
EMBEDDING_PROVIDER=local uses an embedding model loaded in LM Studio (same server as the chat model).
Env vars: GEMINI_EMBEDDING_MODEL, LOCAL_EMBEDDING_MODEL, LOCAL_API_BASE.
"""
import os

import numpy as np
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_openai import OpenAIEmbeddings

import common.models  # noqa: F401  (loads the root .env and the Vertex AI setting)


def embedding_provider() -> str:
    return os.environ.get("EMBEDDING_PROVIDER", "gemini").lower()


# Remembers vectors already computed in this run, so repeating a text costs no new API call.
# Key: (provider, model, kind, text). Lost when the program ends.
_CACHE: dict[tuple, np.ndarray] = {}


def _model_name(provider: str) -> str:
    if provider == "gemini":
        return os.environ.get("GEMINI_EMBEDDING_MODEL", "text-embedding-005")
    return os.environ.get("LOCAL_EMBEDDING_MODEL", "text-embedding-embeddinggemma-300m")


def embed_texts(texts: list[str], kind: str = "document") -> np.ndarray:
    """Return one vector per text, as a 2D numpy array (rows = texts).

    Args:
        texts: The strings to embed.
        kind: "document" for text you search IN, "query" for the question you search WITH.
            Gemini embeddings are tuned differently for the two. Local models ignore it.
    """
    if not texts:
        return np.zeros((0, 0))
    provider = embedding_provider()
    keys = [(provider, _model_name(provider), kind, t) for t in texts]
    missing = [t for t, k in zip(texts, keys) if k not in _CACHE]
    if missing:
        fresh = _embed_uncached(list(dict.fromkeys(missing)), kind, provider)  # dict.fromkeys drops duplicates
        for text, vector in zip(dict.fromkeys(missing), fresh):
            _CACHE[(provider, _model_name(provider), kind, text)] = vector
    return np.array([_CACHE[k] for k in keys])


def _embed_uncached(texts: list[str], kind: str, provider: str) -> np.ndarray:
    """The real call to the embedding model. Use embed_texts, which adds the cache."""

    if provider == "gemini":
        embedder = GoogleGenerativeAIEmbeddings(model=_model_name(provider))  # reads the GOOGLE_* variables, like the Gemini chat agents
        task = "RETRIEVAL_QUERY" if kind == "query" else "RETRIEVAL_DOCUMENT"
        return np.array(embedder.embed_documents(texts, task_type=task), dtype=float)   # sent in batches of 100

    if provider == "local":
        embedder = OpenAIEmbeddings(
            model=_model_name(provider),
            base_url=os.environ.get("LOCAL_API_BASE", "http://127.0.0.1:1234/v1"),
            api_key=os.environ.get("LOCAL_API_KEY", "lm-studio"),
            # The OpenAI class normally splits text into OpenAI's own tokens first. A local model has different tokens, so send plain text.
            check_embedding_ctx_length=False,
            timeout=120,
        )
        return np.array(embedder.embed_documents(texts), dtype=float)

    raise ValueError(f"EMBEDDING_PROVIDER must be 'gemini' or 'local', got {provider!r}")
