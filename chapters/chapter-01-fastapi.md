# Chapter 1 — Turn the RAG project into a small API

Right now `main.py` only exposes the RAG pipeline through a terminal input loop — nothing else can call it. Before anything can be containerized or deployed, it needs a **callable interface**: a well-defined door that other programs (a browser, a curl command, a load balancer, Cloud Run's own health checker) can knock on over HTTP.

```
today:            terminal ──stdin──> main.py ──stdout──> terminal
after Chapter 1:   HTTP client ──request──> FastAPI app ──JSON──> HTTP client
```

**FastAPI** is a Python web framework that turns plain Python functions into HTTP endpoints, using type hints to auto-generate request/response validation (via **Pydantic** models) and interactive docs at `/docs`. You declare a route, FastAPI handles parsing the request, calling your function, and serializing the response.

### The challenge

Create `src/rag_demo/api.py`. It should build **one shared `FastAPI` app object**, and at startup construct the `KnowledgeBase` + `RAGPipeline` exactly the way `main.py` already does (reuse those classes unchanged — don't touch `knowledge_base.py` or `pipeline.py`). Then define these routes:

| Method | Path | Behavior |
|---|---|---|
| GET | `/health` | Returns something simple confirming the app is alive (e.g. `{"status": "ok"}`) |
| POST | `/query` | Takes a question, returns the RAG answer |
| GET | `/documents` | Lists the filenames currently in `data/` |
| POST | `/documents` | Accepts a new `.txt` document, saves it into `data/`, rebuilds the index |
| DELETE | `/documents/{filename}` | Removes a file from `data/` |

A skeleton to start from:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# build kb / retriever / llm / rag_pipeline here, once, at import time
# (same steps main.py already does)

class QueryRequest(BaseModel):
    question: str

class QueryResponse(BaseModel):
    answer: str

@app.get("/health")
def health():
    ...

@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    ...

# GET /documents, POST /documents, DELETE /documents/{filename} below
```

Hints:
- `POST /documents` receiving a file upload needs FastAPI's `UploadFile` type — worth looking up in the FastAPI docs if you haven't used it before.
- After adding/deleting a document, you'll need to call `kb.build_index("data")` again to refresh the retriever — think about where that call needs to live so `rag_pipeline` picks up the new retriever.
- To run it: `uv add fastapi "uvicorn[standard]"`, then `uv run uvicorn src.rag_demo.api:app --reload` (from the project root). Visit `http://127.0.0.1:8000/docs` for the interactive Swagger UI.

One open design question for you to decide (not a right/wrong answer, just tell me your call when you're done): should the old `main.py` CLI loop stay as-is, get deleted, or get adapted? I'll leave that to you.

Take your time — ping me when you've got something to look at, or if you want a hint on any piece.
