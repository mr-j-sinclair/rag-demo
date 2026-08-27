# Chapter 2 — Automated testing

Right now there's no automated way to know if a change broke anything — the only verification has been manual (running the server, eyeballing responses). **Automated tests** are code that checks other code, run with one command, repeatable forever. Two flavors you'll use here:

- **Unit test**: tests one small piece in isolation — a pure function, no network/filesystem/DB. Fast, deterministic.
- **Integration test**: tests several pieces wired together (e.g. the real embedding model + real vector store) — slower, but catches wiring bugs a unit test can't see.

**pytest** is the test runner: you write plain functions named `test_*`, use Python's `assert` for checks, run `pytest`, it collects and executes every `test_*` function and reports pass/fail with a diff on failure.

```
test_format_docs()
      │
      ▼
  assert format_docs([...]) == "expected string"
      │
      ├─ true  → pytest reports PASSED
      └─ false → pytest reports FAILED + shows the actual vs expected diff
```

**Why LLM calls are harder to test:** `rag_pipeline.ask()` ultimately calls the real OpenAI API. That's non-deterministic (wording varies between runs even at `temperature=0`... not guaranteed identical), costs money per test run, requires network + a valid API key, and has no single "correct" string to assert equality against. So CI must never make a real LLM call — you either test around it (assert the retriever/formatting/wiring is correct, and stop before the LLM) or substitute a **fake/stub LLM** that returns a canned response so you're testing that `RAGPipeline` calls it correctly, not what OpenAI says.

## The challenge

Create a `tests/` directory at the project root, add `pytest` as a dev dependency, and write a small, focused set of tests:

1. **Unit test** — `tests/test_formatting.py`: test `format_docs()` from `src/rag_demo/formatting.py` with a small hand-built list of `Document` objects (you construct these directly with known `page_content`, no file loading needed) and assert the joined-string output is exactly what you expect.
2. **Unit test** — `tests/test_documents.py`: test `load_documents()` from `src/rag_demo/documents.py` against the real `data/` folder — assert you get back the expected number of documents and that `metadata["source"]` looks right for at least one of them.
3. **Integration test** — `tests/test_knowledge_base.py`: build a real `KnowledgeBase`, call `build_index("data")`, get a retriever, and assert that `retriever.invoke("Who was Ada Lovelace?")` returns documents whose `metadata["source"]` is `"adalovelace.txt"` — this automates the manual retrieval check from Steps D/E of the RAG course. This test will be slow (real embedding model) — that's expected and fine for now.
4. **Your call, with reasoning**: decide whether to write a test for `RAGPipeline.ask()` using a stub LLM (a fake object with an `.invoke()` method that returns a canned `AIMessage`-like response, swapped in instead of `ChatOpenAI`), or to explicitly skip testing that path and note why in a comment. Either is a valid answer here — I want to see you reason about it, not guess what I want.

Commands, explained:

```bash
uv add --dev pytest
```
`--dev` marks it as a development-only dependency — needed to run tests, not needed to run the app in production. Adds it to `pyproject.toml` under a dev group and updates `uv.lock`.

```bash
uv run pytest
```
Runs the test runner, which auto-discovers files named `test_*.py` and functions named `test_*` inside them, and prints a pass/fail summary.

```bash
uv run pytest -v
```
Same, but verbose — lists each test by name with its individual result, useful while you're building these out.

Hints:
- `Document` comes from `langchain_core.documents` — same import you've already used elsewhere in this project.
- pytest doesn't need a class or any special setup for simple cases — a bare `def test_something():` with an `assert` inside is a complete, valid test.
- For the integration test, don't assert on the *exact* retrieved text (that's brittle and will break the moment `data/adalovelace.txt` changes) — assert on the metadata/source, which is the stable, meaningful thing.

Take your time. Ping me when you (or Codex) are done, and I'll run `uv run pytest` myself and inspect the actual test files before we move on.
