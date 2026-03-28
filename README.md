# agent-ready-python-starter

A tiny Python starter repo for fast, agent-assisted work.

It is intentionally boring:
- `uv` for project + environment management
- `ruff` for linting + formatting
- `pytest` for tests
- `src/` layout for clean imports
- `AGENTS.md` and local agent skills for repeatable AI workflows
- a custom **deep-modules** check to keep files navigable for humans and agents

## Quick start

```bash
# base dev environment
uv sync

# common extras
uv sync --extra analysis
uv sync --extra notebook
uv sync --extra ml
```

## Quality commands

```bash
uv run ruff check .
uv run ruff format .
uv run pytest -q
uv run check-deep-modules src
```

Run all four before you call a task done.

## Optional extras

- `analysis`: `numpy`, `pandas`, `matplotlib`
- `notebook`: `marimo`
- `ml`: `torch`, `torchvision`, `tensorboard`
- `architecture`: `import-linter`, `radon`

Examples:

```bash
uv sync --extra analysis --extra notebook
uv sync --extra analysis --extra ml
uv sync --extra architecture
```

## Marimo

This repo includes `notebooks/scratch.py` as a tiny marimo notebook starter.

```bash
uv sync --extra notebook
uv run marimo edit notebooks/scratch.py
```

Use notebooks for exploration; promote stable logic into `src/`.

## Why this template is agent-friendly

- `AGENTS.md` gives repo-specific instructions to coding agents.
- `.agents/skills/*` contains small, task-focused local skills.
- `ruff` catches common mistakes quickly.
- `pytest` makes “done” concrete.
- `check-deep-modules` keeps interfaces smaller than implementations.
- `src/` layout and explicit package boundaries help both people and tools navigate the codebase.

## Deep modules

The goal is not academic purity. The goal is to avoid shallow, sprawling files with huge public surfaces.

This template uses a lightweight heuristic:

- soft cap on public names per module
- soft cap on module length
- a simple “depth ratio”: `SLOC / public API size`

The checker is conservative and intentionally easy to bypass for justified cases:

```python
# deep-modules: disable
```

Put that comment near the top of a file if a module is intentionally small-and-wide.

## Layout

```text
.
├── .agents/skills/          # local skills for Codex / compatible agents
├── AGENTS.md                # repo-wide agent instructions
├── docs/                    # small design notes
├── notebooks/               # marimo scratch work
├── scripts/                 # tiny wrappers and utilities
├── src/                     # application/package code
└── tests/                   # pytest tests
```

## Notes

- Keep reusable code in `src/`, not notebooks.
- Keep modules small enough to read in one pass.
- Prefer explicit `__all__` in public-facing modules.
- If the repo grows, `docs/importlinter.example.ini` is a starting point for stricter architectural rules.

