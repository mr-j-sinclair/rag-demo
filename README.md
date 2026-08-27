# rag-demo

## Development workflow

Run any module directly as a package (not as a bare script path) so imports resolve
the same way they will when used from elsewhere in the project:

```bash
uv run python -m rag_demo.<module_name>
```

For interactive exploration, use the VS Code Python REPL (select this project's
interpreter, then start a REPL) to import modules and call methods one at a time —
e.g. build a `KnowledgeBase`, call `kb.build_index("data")` once, then experiment with
`kb.as_retriever(...)` or `rag_pipeline.ask(...)` without re-running the whole app each time.
