import os, glob
from typing import List
from chromadb import PersistentClient
from chromadb.utils import embedding_functions
from models.schema import SemanticAnswer

# Persist under assignment data folder
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "chroma")

# Use OpenAI embeddings (reliable & no extra local deps)
_OPENAI_EMBED = embedding_functions.OpenAIEmbeddingFunction(
    api_key=os.getenv("OPENAI_API_KEY"),
    model_name="text-embedding-3-small",
)

def ensure_index_from_sample() -> None:
    """Create a tiny collection from sample docs if not exists."""
    os.makedirs(PERSIST_DIR, exist_ok=True)
    client = PersistentClient(path=PERSIST_DIR)
    colname = "sample_docs"

    try:
        col = client.get_collection(colname)
    except Exception:
        col = client.create_collection(colname, embedding_function=_OPENAI_EMBED)

    # If collection exists but has no embedding_function, set it
    try:
        # if it didn't allow updating , I just re-create texts below.
        col._embedding_function = _OPENAI_EMBED  # type: ignore[attr-defined]
    except Exception:
        pass

    # If already populated, skip
    try:
        if col.count() > 0:
            return
    except Exception:
        # If .count() failed, just proceed to (re)build
        pass

    # Build from sample files
    samples_dir = os.path.join(os.path.dirname(__file__), "..", "data", "sample_docs")
    files = sorted(glob.glob(os.path.join(samples_dir, "*.txt")))
    docs, ids = [], []
    for i, fp in enumerate(files, start=1):
        with open(fp, "r", encoding="utf-8") as f:
            docs.append(f.read().strip())
            ids.append(f"doc-{i}")

    # Add with OpenAI embeddings (handled by embedding_function)
    col.add(documents=docs, ids=ids)

def semantic_query(question: str, k: int = 3) -> SemanticAnswer:
    ensure_index_from_sample()
    client = PersistentClient(path=PERSIST_DIR)
    # re-attach the embedding function (defensive)
    col = client.get_collection("sample_docs", embedding_function=_OPENAI_EMBED)

    # Standard Chroma query (embeddings computed via _OPENAI_EMBED)
    res = col.query(query_texts=[question], n_results=k)
    passages: List[str] = res.get("documents", [[]])[0] if res.get("documents") else []

    # Naive synthesis from top passages
    answer = " ".join(passages[:2])[:600] if passages else "No results were found."
    return SemanticAnswer(query=question, top_passages=passages, answer=answer)
