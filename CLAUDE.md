# rag-demo — learning project status

## What this project is

A guided learning exercise: a small LangChain LCEL RAG app built from the 3 data files
and local `all-MiniLM-L6-v2` embedding model reused from a prior take-home project
(`/Users/sinclairmacbook/code_b/ai-engineer-coding-task-uk`). The goal is to internalise
`RunnableSequence` / `RunnableParallel` / `RunnablePassthrough` / `RunnableLambda` by
building a real retriever to replace a fake one seen in `/Users/sinclairmacbook/code/langc-course/chains_v1.py`.

**Full original plan** (phases, architecture rationale, file layout, what's out of scope):
`/Users/sinclairmacbook/.claude/plans/elegant-stargazing-kay.md`

## IMPORTANT — standing instruction: keep this file current

The user works in short, irregular sessions (roughly one step per day) and may close
the machine without warning. **Update this file's progress-checklist and "Session log"
sections immediately after each step/chapter is completed** — don't wait to be asked,
and don't batch updates. This applies to *both* courses tracked in this file: the RAG
course's "Progress against the plan" checklist, and the CI/CD course's "COURSE 2"
chapter checklist. If a step is only partially done (explained + skeleton given, but
not yet implemented/verified by the user), say so explicitly rather than marking it
done — the checklist must be resumable cold after a shutdown, with no ambiguity about
what's actually finished vs. just handed off.

## IMPORTANT — standing instruction: per-chapter files for Codex handoff (CI/CD course)

The user works on the actual CI/CD-course implementation with Codex in parallel, in this
same repo. Codex has filesystem access but no visibility into this conversation, so each
chapter's instructions need to exist as a file, not just as chat text. Rule: whenever a
chapter's teaching content is presented to the user in this conversation (explain →
challenge → named file(s) → skeleton → hints), **write that content verbatim — the exact
text posted on screen, not a paraphrase or summary — into its own file at
`chapters/chapter-<N>-<slug>.md`** in the project root that same turn (create `chapters/`
if it doesn't exist yet). If a chapter's guidance is later extended in conversation
(more hints, a correction, a follow-up), update that chapter's file to match rather than
letting it go stale — Codex should always be able to read the current ask straight from
the file.

## IMPORTANT — teaching constraint, read before doing anything

**Do not write the application code for the user.** This is a guided lesson, not a
build-it-for-them task. For each step: explain the concept, explain why it exists,
name the file/class/method to create, give a skeleton (signature + docstring/comment,
not a body), ask the user to implement it themselves, then review what they write and
help debug. Only give a full implementation if explicitly asked. Get the user to predict
data types/shapes before running code, then inspect the real output together. Keep
`main.py` thin — RAG logic lives in `src/rag_demo/`.

See the full constraint list and phase-by-phase teaching sequence in the plan file linked above
(Phases 5–12: Load docs → Chunk → Embeddings → Vector store → Retriever → LCEL chain →
inspect data at every stage → REPL workflow → main.py → verification → batch/stream → production context).

## Environment (done)

- `uv init --name rag-demo --python 3.11` (pinned — system Python is 3.14.x, too new for
  reliable `torch`/`sentence-transformers` wheels at time of writing)
- Dependencies added: `langchain`, `langchain-core`, `langchain-huggingface`, `langchain-openai`,
  `python-dotenv` (and whatever `langchain-text-splitters` transitively pulled in for chunking)
- `.env` (gitignored, real `OPENAI_API_KEY`) + `.env.example` (committed template) both exist
- `.gitignore` covers `.venv`, `.env`, and `models/all-MiniLM-L6-v2` (174MB, not source-controlled)
- `data/` (3 `.txt` files) and `models/all-MiniLM-L6-v2/` copied in from the take-home project

## Progress against the plan

- [x] **Step A — Load documents**: `src/rag_demo/documents.py` — `load_documents(folder_path) -> list[Document]`.
      Implemented, verified: 3 docs, metadata `{"source": filename}` correct, `page_content` lengths checked
      against file byte sizes (discussed UTF-8 char-vs-byte discrepancy).
- [x] **Step B — Chunk documents**: `src/rag_demo/knowledge_base.py` — `KnowledgeBase.__init__` builds
      `self.text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)`;
      `split_documents()` wraps it. Verified: 415 chunks total.
- [x] **Step C — Embeddings**: `KnowledgeBase.__init__` also builds
      `self.embeddings = HuggingFaceEmbeddings(model_name="models/all-MiniLM-L6-v2")`.
      Verified: `embed_query()` returns a `list[float]` of length 384. Discussed and *decided against*
      `encode_kwargs={"normalize_embeddings": True}` — redundant since `InMemoryVectorStore` uses
      cosine similarity, which is scale-invariant.
- [x] **Step D — Vector store**: `KnowledgeBase.build_index(self, folder_path: str) -> None` implemented —
      calls `load_documents()`, then `self.split_documents()`, then
      `self.vector_store = InMemoryVectorStore.from_documents(documents=chunks, embedding=self.embeddings)`.
      Verified (user's run + independently re-run by assistant): `similarity_search("Who was Ada Lovelace?", k=3)`
      returns 3 `Document`s, all `metadata["source"] == "adalovelace.txt"` — doubles as the Phase 10
      "Ada retrieval test". Module-level test/print code was correctly removed from `knowledge_base.py`
      (it was originally at import scope, which would have re-run on every import — fixed).
      Two small non-blocking cleanups still outstanding, left to the user's discretion: unused
      `from pprint import pprint` import, and the `if not documents: return None` guard in `build_index`
      runs after the load/split work it's meant to guard against (should move earlier, or just be dropped).
- [x] **Step E — Real retriever**: `KnowledgeBase.as_retriever(self, k: int = 5)` implemented, wrapping
      `self.vector_store.as_retriever(search_kwargs={"k": k})`. Verified: `retriever.invoke(...)` output
      matches `similarity_search()` exactly; `retriever.batch([...])` correctly routed 3 different
      questions (Jupiter/CRISPR/Ada) to their respective source documents — all three Phase 10
      per-document retrieval tests effectively passed. Also caught and fixed a real bug along the way:
      `from documents import load_documents` worked when running `knowledge_base.py` directly as a
      script (script's own dir goes on `sys.path`) but broke under package import (`from
      rag_demo.knowledge_base import KnowledgeBase`, as `main.py` will do) — fixed by using the
      absolute import `from rag_demo.documents import load_documents`, confirmed working both ways.
      The two minor Step D cleanups (unused `pprint` import, `if not documents` guard ordering) are
      still outstanding/optional — not revisited.
- [ ] **Phase 6 — LCEL chain (IN PROGRESS)**: building this incrementally, in sub-steps:
      - [x] `src/rag_demo/formatting.py` — `format_docs(docs: list[Document]) -> str` implemented and
            verified (joins `page_content` with `"\n\n"`; tested via `uv run python -m rag_demo.formatting`,
            confirmed the project is a properly installable package — `-m` module execution works cleanly).
      - [x] Prompt template — built and tested standalone (not yet moved into `pipeline.py`, which doesn't
            exist yet). `ChatPromptTemplate.from_template("...")` with `{context}`/`{question}` placeholders
            and "answer only from context, say you don't know otherwise" instructions (mirrors old `rag.py`'s
            system prompt). Verified: `.invoke({...})` → `ChatPromptValue` → `.to_messages()` → a list of
            exactly one `HumanMessage` (noted as a discussion point: `.from_template()` bundles everything —
            instructions + both placeholders — into a single Human message, unlike the old code's separate
            system/human messages; `ChatPromptTemplate.from_messages([("system", ...), ("human", ...)])` is
            the alternative if a system/human split is wanted later — optional, not required, not decided).
      - [x] **RunnableParallel + RunnablePassthrough deep dive**: user built
            `context_chain = retriever | RunnableLambda(format_docs)` and
            `parallel = RunnableParallel(context=context_chain, question=RunnablePassthrough())`, then ran both
            `parallel.invoke("Tell me about Jupiter")` (succeeded: `{"context": <str>, "question": <str>}`, both
            correctly shaped) and `parallel.invoke({"question": "Tell me about Jupiter"})` (user reported it
            errored; assistant reproduced independently to get exact traceback: `AttributeError: 'dict' object
            has no attribute 'replace'`). Explained why: `RunnableParallel` sends the *identical* raw input to
            every branch — with a dict input, the `question` passthrough branch would've echoed back the whole
            nested dict (wrong shape), and the `context` branch's retriever tried to embed the dict directly,
            crashing inside the tokenizer's string-cleaning step (`.replace`) before even reaching `format_docs`.
            Tied this back to why `chains_v1.py`'s `demo_passthrough_chain()` needed an extra unwrapping
            `RunnableLambda` — same root cause, dict-shaped invoke.
            **Design decision made**: this chain only ever takes one question, so the chosen invocation shape
            going forward is a **plain string** (`chain.invoke("some question")`, matching the working
            `result_a` case) — not a dict. `RAGPipeline.ask(question: str)` will call `self.chain.invoke(question)`
            accordingly. (Noted but not used: the `itemgetter("question")`-per-branch pattern is the standard
            fix if dict-shaped multi-input invocation were ever needed later — it isn't, for this project.)
      - [x] **`src/rag_demo/pipeline.py` (`RAGPipeline` class)**: implemented and verified end-to-end.
            `__init__` builds the prompt template, `self.context_chain = retriever | RunnableLambda(format_docs)`,
            and `self.chain = RunnableParallel(context=self.context_chain, question=RunnablePassthrough()) | prompt
            | llm | StrOutputParser()`. `ask(question)` calls `self.chain.invoke(question)`. Ran via
            `uv run python src/rag_demo/pipeline.py` (test script in the `if __name__ == "__main__"` block:
            `load_dotenv()`, build `KnowledgeBase`, `kb.build_index("data")`, `retriever = kb.as_retriever(k=3)`,
            `ChatOpenAI(model="gpt-4o-mini", temperature=0)`, `rag_pipeline.ask("Who was Ada Lovelace?")`) — real
            OpenAI call succeeded, returned a correct, context-grounded answer. Confirmed `type(ai_response)` is
            `langchain_core.messages.base.TextAccessor` (a `str` subclass used for `.text`/`.text()` backward-compat
            in this LangChain version) rather than plain `str` — behaves identically to `str` everywhere, not a bug.
            Also hit and explained a harmless `huggingface/tokenizers` fork-parallelism warning (fix: add
            `TOKENIZERS_PARALLELISM=false` to `.env`) — cosmetic, unrelated to chain correctness.
- [x] **Phase 7 — inspect every stage**: no new code — walked the real assembled `rag_pipeline.chain`
      (a `RunnableSequence`) via its `.steps` list (`[RunnableParallel, ChatPromptTemplate, ChatOpenAI,
      StrOutputParser]`), invoking each stage on a fresh question ("What is Crispr?", deliberately different
      from earlier Ada tests) and confirming predicted types at every hop: `str` → `dict{context,question}` →
      `ChatPromptValue` → `AIMessage` → `TextAccessor(str)`. User independently verified
      `stage3.content == stage4` (`True`) — confirms `StrOutputParser` is just extracting `.content`. Also
      inspected `AIMessage.response_metadata` (token usage, model name, finish_reason) — noted as relevant
      later for Phase 12 (cost/observability), not used yet. Mental model confirmed accurate end-to-end.
- [ ] **Phase 8 — REPL workflow**: effectively already in place (user already runs modules via
      `uv run python -m rag_demo.<module>` and has a working VS Code REPL habit) — mostly a documentation/
      write-up step, not new skills. Not formally written up yet.
- [x] **Phase 9 — main.py**: implemented and verified. Thin orchestration only: `load_dotenv(find_dotenv(usecwd=True))`
      (more robust than bare `load_dotenv()` — resolves `.env` from actual cwd, not an assumed relative path),
      builds `KnowledgeBase`/`build_index("data")`, `as_retriever(k=3)`, `ChatOpenAI(model="gpt-4o-mini",
      temperature=0)`, `RAGPipeline`, then a `while True` input loop with a real exit condition
      (`"bye"`/`"exit"`/`"quit"`) — an improvement over the old `rag.py`'s bare infinite loop. Verified live:
      asked "What is Jupiter?" via the real CLI, got a correct grounded answer, exited cleanly on "quit".
      Two minor cleanup items noted while reviewing (not yet addressed, low priority): `src/rag_demo/__init__.py`
      has a leftover scratch `Document(...)` expression (harmless but runs on every import — should be emptied),
      and `src/rag_demo/test_script.py` is a stale, superseded early draft of `RAGPipeline` (nothing imports it,
      just clutter).
- [x] **Phase 10 — verification exercises**: complete. Ada/Jupiter/CRISPR retrieval tests passed during
      Steps D/E and Phase 7. Out-of-scope test done live via `main.py`: asked "What's the capital of
      France?", got a correct "I don't know." (not a hallucinated answer). Inspected `retriever.invoke(...)`
      for that question in the REPL — confirmed the retriever has no relevance threshold, it always returns
      top-k "closest available" chunks even when none are truly relevant (one chunk was a false-positive
      match on the word "French" in `adalovelace.txt`, nothing to do with the country). Confirms the
      "don't hallucinate" behavior is entirely the LLM following the prompt's instructions, not the
      retriever filtering for relevance.
- [x] **Phase 11 — batch/async/stream awareness**: complete. `rag_pipeline.chain.batch([3 questions])`
      returned a `list` of 3 `TextAccessor` answers, each correctly grounded in its own source document
      (Ada/CRISPR/Jupiter) — same independent-parallel-routing behavior as the Step E retriever `.batch()`
      demo, now confirmed at the top of the fully assembled chain. `.ainvoke()`/`.abatch()`/`.astream()`
      covered conceptually only (async for concurrent requests without blocking; streaming for
      token-by-token output) — not implemented, per the plan.
- [x] **Phase 12 — production engineering context**: complete (discussion only, no code). Covered:
      in-memory vs. persistent vector DB, single-process vs. FastAPI/deployed service, fixed chunking vs.
      evaluated chunking, similarity-only vs. hybrid+reranked retrieval (tied back to the Phase 10
      false-positive "French" match as a concrete example of what reranking would catch), no evaluation
      vs. an automated eval suite (Phase 10's manual spot-check → automated at scale), print debugging vs.
      LangSmith/LangFuse tracing (tied back to `AIMessage.response_metadata` already inspected in Phase 7),
      `.env` vs. managed secret stores, and where Docker fits (reproducible env incl. local MiniLM weights).

## COURSE COMPLETE (2026-08-20)

All 12 phases done. The app is a fully working, real LCEL RAG pipeline — real retriever (replacing
`chains_v1.py`'s `fake_retriever`), real vector store, real OpenAI calls, thin `main.py` CLI, all four
target Runnable concepts (`RunnableSequence`/`RunnableParallel`/`RunnablePassthrough`/`RunnableLambda`)
understood and exercised end-to-end, plus verification tests and a production-context discussion.

**All optional cleanup items also closed out (2026-08-21):**
- Phase 8 write-up done — added a short "Development workflow" section to `README.md` (the `-m` module-run
  pattern + VS Code REPL habit).
- `src/rag_demo/__init__.py` emptied (was a leftover scratch `Document(...)` expression) — confirmed
  package still imports cleanly.
- `src/rag_demo/test_script.py` was already gone (user had cleared it independently).
- `build_index`'s `if not documents: return None` guard moved to right after `load_documents`, before
  `split_documents` — verified via `uv run python -m rag_demo.knowledge_base`, same output as before.
- The "unused `pprint` import" note turned out to be stale — `pprint` is actually used in
  `knowledge_base.py`'s `if __name__ == "__main__":` block. Corrected here as a reminder that this file
  is a summary, not ground truth — always verify against the real code.

**Nothing outstanding.** If a future session resumes this project, there's no required next step —
check in with the user about what they want to do next (extend the project further, or something new).

## COURSE 2 — CI/CD (started 2026-08-25, IN PROGRESS)

A second guided course, independent of the RAG course above (that one is finished — nothing
here supersedes it). Goal: evolve this project into a small production-style app to teach CI/CD
fundamentals (change → test → review → merge → auto-deploy) using GitHub Actions + Google Cloud
Run, with FastAPI/testing/Docker/linting as supporting concepts, not their own deep-dive.
**Same teach-by-doing constraint as the RAG course**: explain → small challenge → name the
file(s) → rough description → hints → user writes the code → inspect the real result → verify →
fix-it-yourself challenges if wrong. Terminal commands are given explicitly with a one-line
explanation. No Kubernetes.

**Full plan** (8 chapters, repo-inspection findings, rationale for every design choice):
`/Users/sinclairmacbook/.claude/plans/iridescent-hatching-squirrel.md`

User context for this course: GCP account exists but no project yet (Chapter 5 includes
project/billing/API setup); public GitHub repo is fine (simplifies Chapter 8 branch
protection); Chapter 6 CD auth deliberately uses Workload Identity Federation, not a
downloaded service-account key (user's explicit steer, values avoiding the long-lived-
credential habit over saving setup time).

Each chapter's teaching content is also written verbatim to its own file in `chapters/`
(e.g. `chapters/chapter-01-fastapi.md`) so Codex — which the user runs against this same
repo in parallel for the actual implementation work — can read the exact ask without
needing this conversation. Keep those files in sync if a chapter's guidance changes.

### Progress against the CI/CD plan

- [x] **Chapter 1 — FastAPI**: `src/rag_demo/api.py` implemented and verified. Reuses
      `KnowledgeBase`/`RAGPipeline` unchanged, built once at import time. All 5 endpoints
      live-tested with a running `uvicorn` server (not just read): `/health` → `{"status":"ok"}`;
      `POST /query` → real OpenAI call, correct grounded Ada Lovelace answer; `GET /documents`
      → real file listing; `POST /documents` upload/`DELETE /documents/{filename}` round-tripped
      successfully and correctly rebuild the index (`rebuild_rag_pipeline()`) each time; non-`.txt`
      upload rejected (400); delete of nonexistent file rejected (404); path-traversal delete
      attempts safely blocked (Starlette route matching + explicit `filename in (".", "..", "...")`
      guard). Design decision: `main.py`'s CLI loop left untouched, kept alongside the new API as
      a second way to exercise the pipeline. Two cosmetic comment typos noted, not fixed (user's
      call, non-blocking): "stame steps" (api.py:16), "POST /docuemnts" (api.py:73).
- [x] **Chapter 2 — Testing**: `tests/` created, `pytest` added as a dev dependency
      (`pyproject.toml` `[dependency-groups] dev`). Implemented and verified — assistant ran
      `uv run pytest -v`, all 4 tests pass (26.42s, dominated by the real-embedding integration
      test). `tests/test_formatting.py` — unit test, hand-built `Document`s, exact-string assert.
      `tests/test_documents.py` — unit test against the real `data/` folder (now 4 files after
      `lang_chain.txt` was added alongside the original 3; asserts `len(documents) == 4` and
      `"adalovelace.txt"` in sources). `tests/test_knowledge_base.py` — integration test, real
      `KnowledgeBase.build_index("data")` + real embedding model, asserts Ada Lovelace question
      retrieves from `adalovelace.txt`. `tests/test_pipeline.py` — item 4 ("your call") was
      answered by writing a stub-LLM test rather than skipping: `RunnableLambda` stubs stand in
      for both the retriever and the LLM (no real OpenAI call), captures the assembled prompt via
      `.to_string()` and asserts it contains both the injected context and the question, and
      asserts the final output equals the stub's canned response — exercises `RAGPipeline`'s own
      wiring in isolation. Confirms `RAGPipeline.__init__(retriever, llm)` already supported
      dependency injection with no changes needed. Two harmless comment typos noted, not fixed
      (user's call, same as the Chapter 1 precedent): `test_pipeline.py:19` "RAGPipleline",
      `test_documents.py:13` "ta know data file".
- [x] **Chapter 3 — Git/GitHub**: complete, verified via `gh`/`git` state (not just user report).
      Decision: `.DS_Store` (all 3 instances) and `ignore.md` both added to `.gitignore` and left
      on disk, not committed (user's call). Initial commit `df36fc8` ("Initial commit: RAG
      pipeline, FastAPI, tests"). Public repo created at
      `https://github.com/mr-j-sinclair/rag-demo` via `gh repo create --source=. --remote=origin`,
      pushed with `git push -u origin main`. Feature-branch practice run: branch
      `readme-change-fastapi` → README tweak → commit → push → `gh pr create --fill` (assistant ran
      this one directly, at the user's explicit instruction) → PR #1 → `gh pr merge --squash` →
      merged commit `1d0a33a` on `main`, confirmed via `gh pr view 1` (`state: MERGED`). Local repo
      back on `main`, up to date with `origin/main`, clean working tree. Minor non-blocking loose
      end: local `readme-change-fastapi` branch still exists locally post-merge (`git branch -d
      readme-change-fastapi` to clean up, whenever).
- [ ] **Chapter 4 — Basic CI**: `.github/workflows/ci.yml` — checkout/setup-python/uv
      sync/ruff/pytest. Not started.
- [ ] **Chapter 5 — Docker + Cloud Run**: GCP project setup, `Dockerfile`, switch embeddings to
      HF Hub id (drop local gitignored model-folder dependency), CPU-only torch, manual first
      deploy. Not started.
- [ ] **Chapter 6 — Basic CD**: workflow extension, Workload Identity Federation auth from
      GitHub Actions to GCP, auto-deploy on merge to `main`. Not started.
- [ ] **Chapter 7 — Real feature via the workflow**: hybrid retrieval (`EnsembleRetriever` +
      `BM25Retriever`), built entirely through branch → PR → CI → merge → CD. Not started.
- [ ] **Chapter 8 — Quality/review/docs**: real `ruff` config, branch protection + required
      reviewers (Barry/Vitali), optional Makefile, full README rewrite. Not started.

## Key design decisions already made (don't re-litigate without reason)

- `KnowledgeBase` (class) owns index-building state: splitter, embeddings, vector store.
- `RAGPipeline` (class, not yet built) will own the query-time chain — composition
  (`RAGPipeline` *has-a* retriever and *has-a* LLM), not inheritance.
- `load_documents` and (soon) `format_docs` are plain functions, not methods — stateless transforms.
- No custom `Retriever` class — LangChain's `vector_store.as_retriever()` already provides that abstraction.
- `main.py` stays thin orchestration only.

## Session log

- **2026-08-17**: Environment set up (`uv init`, dependencies, `.env`/`.env.example`/`.gitignore`,
  data + model copied in). Steps A, B, C implemented and verified. Took a break; this `CLAUDE.md` created.
- **2026-08-18**: Step D implemented, reviewed, and verified (incl. fixing a module-level
  import-side-effect issue). Step E explained and skeleton given; awaiting user implementation.
- **2026-08-19**: Step E implemented, reviewed, and verified — found/fixed a script-vs-package-import
  bug along the way (`from documents import ...` → `from rag_demo.documents import ...`). All of
  Steps A–E (the full "build a real retriever" arc) now complete. Moved into Phase 6: `format_docs`
  done, prompt template built and tested standalone. RunnableParallel/RunnablePassthrough exercise
  completed — user ran both invoke shapes, assistant reproduced the dict-input error to get the exact
  traceback (`AttributeError: 'dict' object has no attribute 'replace'`) and explained root cause;
  design decision locked in: chain takes a plain string question, not a dict. Handed off `pipeline.py`/
  `RAGPipeline` (skeleton given, not yet implemented).
- **2026-08-20**: `RAGPipeline` implemented by the user and verified — full end-to-end run against real
  OpenAI API succeeded (`ask("Who was Ada Lovelace?")` returned a correct, context-grounded answer).
  Explained a harmless `huggingface/tokenizers` fork-parallelism warning (fix: `TOKENIZERS_PARALLELISM=false`
  in `.env`) and why `type(ai_response)` is `TextAccessor` not `str` (a `str` subclass, behaves identically).
  Phase 6 (LCEL chain) is now fully complete. Later same day: Phase 7 done — walked
  `rag_pipeline.chain.steps` stage-by-stage on a fresh question, all predicted types confirmed, user
  self-verified `StrOutputParser` just extracts `.content`. Later same day: Phase 9 done —
  `main.py` implemented (thin orchestration + input loop with real exit condition), verified live via
  the actual CLI ("What is Jupiter?" → correct grounded answer → clean exit on "quit"). Later same day:
  Phase 10 done — out-of-scope question ("capital of France?") correctly got "I don't know.", and
  inspecting the retriever's actual top-3 chunks in the REPL confirmed retrievers have no relevance
  threshold (a false-positive "French"/"France" keyword match came back). Later same day: Phase 11 done —
  `.batch()` on the full assembled `rag_pipeline.chain` correctly routed 3 independent questions to 3
  correctly-grounded answers. Later same day: Phase 12 discussion delivered (production-context mapping,
  no code) — **all 12 phases now complete. Course finished.** Only optional items remain (see
  "COURSE COMPLETE" section above) — no required next step for a future session.
- **2026-08-25**: RAG course fully wrapped; started **COURSE 2 (CI/CD)**. Inspected the repo fresh
  (confirmed zero git commits, no remote, no tests/lint/Dockerfile/`.github/` yet, `torch` pinned
  without a CPU-only constraint, `models/all-MiniLM-L6-v2` gitignored and loaded by local path —
  flagged as a Chapter 5 concern). Asked the user about GCP readiness (account exists, no project
  yet) and GitHub repo visibility (public is fine); both folded into the plan. User steered Chapter 6
  away from a service-account-key GitHub secret toward Workload Identity Federation for GCP auth —
  plan updated accordingly before approval. Full 8-chapter plan approved and saved to
  `/Users/sinclairmacbook/.claude/plans/iridescent-hatching-squirrel.md`. Added two new standing
  instructions to this file at the user's request: (1) keep the CI/CD chapter checklist below
  updated immediately per chapter, same as the RAG course always did; (2) write each chapter's
  content verbatim into its own file under `chapters/` so Codex (which the user runs against
  this repo in parallel) can see the exact ask without this conversation. Chapter 1 (FastAPI)
  then taught and completed same day: `chapters/chapter-01-fastapi.md` written, user implemented
  `src/rag_demo/api.py` (likely with Codex), assistant independently ran a live `uvicorn` server
  and verified all 5 endpoints for real (see Chapter 1 checklist entry for detail) rather than
  just reading the code. Chapter 1 done.
- **2026-08-26**: Chapter 2 (testing) implemented (likely with Codex) and verified — assistant
  read all 4 test files and ran `uv run pytest -v` independently, all pass. See Chapter 2
  checklist entry for detail, incl. the stub-LLM design decision for `test_pipeline.py`. Chapter 2
  done.
- **2026-08-27**: Chapter 3 (Git/GitHub) taught and completed same day — repo went from zero
  commits to: initial commit, public GitHub repo (`mr-j-sinclair/rag-demo`), and a full
  feature-branch → PR → squash-merge cycle practiced for real (PR #1). `.DS_Store`/`ignore.md`
  gitignored per user's decision (left on disk, not committed). Verified via actual `git`/`gh`
  state, not user report. See Chapter 3 checklist entry for full detail. Chapter 3 done. Chapter 4
  (Basic CI — `.github/workflows/ci.yml`) not yet started.

## Resuming a session

**Two courses exist in this file — check which one is active first** (currently: COURSE 2/CI-CD,
since COURSE COMPLETE marks the RAG course finished).

1. Check the active course's checkbox list (RAG course: "Progress against the plan"; CI/CD course:
   "COURSE 2" section) to see the last completed step.
2. Re-read the actual files (RAG: `src/rag_demo/`; CI/CD: also check for `tests/`, `.github/`,
   `Dockerfile`, `pyproject.toml` lint config as relevant) to confirm what's really there — this
   file is a summary, not a substitute for reading the code.
3. Pick up teaching from the first unchecked `[ ]` item, in the same style: explain, skeleton,
   let the user implement, review, verify by running + inspecting output.
