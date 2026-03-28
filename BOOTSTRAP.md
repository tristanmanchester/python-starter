# BOOTSTRAP.md

Goal: prepare this repo for work on a fresh machine quickly and safely.

If you are an agent, read this file first, execute the setup steps, run the
validation commands, and report any blockers clearly.

## Setup

1. Ensure `git` is installed.
2. Ensure Python `3.11+` is available.
3. Ensure `uv` is installed. If it is missing, install it first.

Helpful checks:

```bash
git --version
python3 --version
uv --version
```

## Repo Init

From the repository root, run:

```bash
uv sync
```

## Validation

Run the full quality gate after setup and after any code changes:

```bash
uv run ruff check .
uv run ruff format . --check
uv run pytest -q
uv run check-deep-modules src
```

## Optional Extras

Install extras only if the task requires them:

```bash
uv sync --extra analysis
uv sync --extra notebook
uv sync --extra ml
uv sync --extra architecture
```

Available extras:

- `analysis`: `numpy`, `pandas`, `matplotlib`
- `notebook`: `marimo`
- `ml`: `torch`, `torchvision`, `tensorboard`
- `architecture`: `import-linter`, `radon`

## Expectations

- If a command fails, fix the smallest root cause and rerun the full validation
  set.
- Prefer small, readable changes over broad refactors.
- Do not add heavy dependencies unless the task actually needs them.
- Keep reusable code in `src/`.
- Keep notebooks exploratory; move stable logic into `src/`.

## Suggested Agent Prompt

Use this prompt with an agent on a fresh machine:

```text
Read BOOTSTRAP.md, prepare the environment, run the validation commands, and
tell me what is still blocking work.
```
