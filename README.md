# Local RAG API

A local Retrieval-Augmented Generation (RAG) application built with LangChain and exposed through a FastAPI API.

Documents are embedded locally, while OpenAI generates answers using the retrieved document context.

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- An OpenAI API key

## Setup

Install the project dependencies:

```bash
uv sync
```

Create a `.env` file based on `.env.example`:

```env
OPENAI_API_KEY=your-openai-api-key
```

Do not commit the `.env` file.

## Run the API

From the project root, start the FastAPI development server:

```bash
uv run uvicorn rag_demo.api:app --reload
```

The API will be available at:

- API: http://127.0.0.1:8000
- Interactive documentation: http://127.0.0.1:8000/docs

The application builds its initial vector index from the `.txt` files in `data/`.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| `GET` | `/health` | Check that the API is running |
| `POST` | `/query` | Ask a question using the RAG pipeline |
| `GET` | `/documents` | List available documents |
| `POST` | `/documents` | Upload a `.txt` document |
| `DELETE` | `/documents/{filename}` | Delete a document |

Example query:

```bash
curl -X POST http://127.0.0.1:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "Who was Ada Lovelace?"}'
```

## Run the tests

These include unit and integration tests. They use test data and avoid making real OpenAI chat requests.

```bash
uv run pytest -v
```

## Optional terminal interface

The original command-line interface remains available:

```bash
uv run python main.py
```