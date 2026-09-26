# Local RAG API

A local Retrieval-Augmented Generation (RAG) application built with LangChain and exposed through a FastAPI API.

Documents are embedded locally, while OpenAI generates answers using the retrieved document context.

## Requirements

- Python 3.11
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

These include unit and integration tests. Some use dummy data; retrieval integration tests use the documents in `data/` and retrieval components. The tests do not make real OpenAI chat requests.

```bash
uv run pytest -v
```

## Optional terminal interface

The original command-line interface remains available:

```bash
uv run python main.py
```


## Contributing changes

Make changes on a feature branch and submit a pull request targeting `main`.

Feature branch --> Pull request --> CI passes + reviewer approves --> Squash-merge

Before merging:

- The required `test` CI check must pass.
- At least one reviewer with write access must approve.
- The branch must be up to date with `main`.
- New code changes dismiss previous approvals and require another review.

Manually request a review from a repository collaborator with write access.

Direct pushes to `main` are blocked by branch protection.

## Continuous integration (CI)

CI runs automated checks on pull requests targeting `main` and on pushes to `main`, including merged pull requests. The workflow is defined in [ci.yml](.github/workflows/ci.yml).

The workflow:

- Installs the dependencies recorded in `uv.lock`.
- Restores the embedding model from cache or downloads it if needed.
- Runs `uv run ruff check .` to check code quality.
- Runs `uv run ruff format --check .` to check formatting without modifying files.
- Runs `uv run mypy .` to check for type errors without running the application.
- Runs `uv run pytest` to check application behaviour.

The required `test` check must pass before a pull request can merge.

Run the same checks locally before pushing:

```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy .
uv run pytest
```

Run these commands directly with `uv`. This project does not use a Makefile.

## Continuous deployment (CD)

The [CD workflow](.github/workflows/cd.yml) runs whenever changes are pushed to `main`, including when a pull request is merged.

The workflow:

- Authenticates to Google Cloud using Workload Identity Federation (WIF). This provides temporary credentials without storing a Google Cloud service-account key in GitHub.
- Uses Cloud Build to build a container image following [cloudbuild.yaml](cloudbuild.yaml).
- Stores the image in Artifact Registry, Google Cloud's container image registry.
- Deploys the image to the `rag-demo-api` service on Cloud Run in `europe-west2`.

The OpenAI API key is supplied from a GitHub Actions secret.

### After merging

Merge --> CD starts --> Cloud Build builds and stores the image --> Cloud Run deploys it.

Check the CD run in the repository's Actions tab to confirm deployment succeeded. Routine changes do not need a manual deployment.

CI also runs again on `main`. The CD workflow runs independently of that post-merge CI run; branch protection requires CI to pass on the PR before merging.

## Deployed service

- [API health check](https://rag-demo-api-j5o6qpnbta-nw.a.run.app/health)
- [Interactive API documentation](https://rag-demo-api-j5o6qpnbta-nw.a.run.app/docs)
