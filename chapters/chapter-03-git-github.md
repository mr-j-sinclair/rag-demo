# Chapter 3 — Git and GitHub workflow

**The concepts**, in the order you'll use them:

```
working directory → (git add) → staging area → (git commit) → local history
                                                                       │
                                                            (git push) │
                                                                       ▼
                                                              GitHub remote (origin)
```

- **Staging area**: `git add` doesn't commit — it marks *which* changes go into the *next* commit. Lets you build a commit out of only some of your changes.
- **Commit**: a permanent snapshot + message, stored locally. Cheap, instant, no network involved.
- **Remote**: a copy of the repo hosted elsewhere (GitHub). `origin` is just the conventional name for "the main remote."
- **Push**: uploads your local commits to the remote.
- **Branch**: a movable pointer to a commit. `main` is just a branch by convention, not special to Git itself.
- **Pull Request (PR)**: a GitHub-level concept (not Git itself) — "here's a branch, please review and merge it into another branch." This is the hook CI (Chapter 4) and branch protection (Chapter 8) attach to.

```
main:     A---B---C--------------F   (after merge)
                    \            /
feature:             D----E----'
                (git checkout -b)  (PR merged)
```

## Decision 1 — what happens to `.DS_Store` and `ignore.md`?

Both were untracked. Two options for each:

- **`.gitignore` it** — Git will never see it again, but it stays on your disk.
- **Delete it** — gone from disk too.

`.DS_Store` is macOS Finder metadata — it'll keep regenerating in any folder you open in Finder (there were already three: root, `models/`, `src/`). `ignore.md` looks like pasted debug output used as scratch notes while working through the LCEL chain earlier in the RAG course — not documentation anyone would want in the repo's history.

**Decision made**: both get added to `.gitignore` and left on disk, not committed. Both patterns (`.DS_Store`, `ignore.md`) have been added to the project's `.gitignore`.

## Step 1 — first commit

```bash
git status
```
Sanity check — confirms exactly what's about to be staged. You should see everything except `.venv`, `.env`, `models/all-MiniLM-L6-v2`, `.DS_Store`, and `ignore.md` (all now gitignored).

```bash
git add .
```
Stages everything currently untracked/modified — safe here since you just confirmed with `git status` what that includes.

```bash
git commit -m "Initial commit: RAG pipeline, FastAPI, tests"
```
Creates the first snapshot in local history. No network involved yet.

## Step 2 — create the GitHub repo and push

Already authenticated as `mr-j-sinclair` via `gh`, so:

```bash
gh repo create rag-demo --public --source=. --remote=origin
```
Creates a public GitHub repo named `rag-demo`, wires your local repo to it as `origin`, in one step (`--source=.` means "use the current directory," `--remote=origin` names the remote).

```bash
git push -u origin main
```
Uploads your commit(s) to GitHub. `-u` sets `main` to track `origin/main`, so future `git push`/`git pull` on this branch don't need the remote/branch named again.

## Step 3 — feature branch → PR → merge (practice run)

Pick something trivial to change — e.g. add a one-line note to `README.md`. Then:

```bash
git checkout -b readme-tweak
```
Creates and switches to a new branch pointing at the same commit as `main` — nothing's shared yet, changes here won't touch `main` until merged.

*(Edit the file yourself, then:)*

```bash
git add README.md
git commit -m "Tweak README"
git push -u origin readme-tweak
```
Same add/commit as before, then pushes the new branch to GitHub (not `main`).

```bash
gh pr create --fill
```
Opens a Pull Request from `readme-tweak` into `main`, using the commit message as the PR title/body (`--fill`).

```bash
gh pr merge --squash
```
Merges it into `main` on GitHub (squash = one clean commit on `main`, regardless of how many commits were on the branch).

```bash
git checkout main
git pull
```
Switches back to `main` locally and pulls down the merge that just happened on GitHub.

Take it step by step and ping after each stage (or if anything errors) — verify the actual result before moving on rather than assuming it worked.
