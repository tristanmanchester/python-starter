# AGENTS.md

Repository instructions for coding agents.

## Goal

Build small, readable Python changes quickly.
Optimise for correctness, fast feedback, and code that is easy for both humans and agents to navigate later.


## Interview / assessment mode

- This template may be used on unfamiliar hardware in a timed technical session.
- Prefer low-ceremony solutions and fast setup.
- Favour the standard library and existing dependencies before adding new ones.
- Keep changes easy to explain aloud and easy to review under time pressure.

## Repo map

- `src/`: reusable package code
- `tests/`: pytest tests
- `notebooks/`: marimo scratch work only
- `scripts/`: tiny wrappers and checks
- `.agents/skills/`: local skills that may be invoked explicitly or implicitly
- `docs/`: short design notes

## Default workflow

1. If the task is not trivial, write a short plan first (3-7 bullets).
2. Prefer the smallest change that solves the problem.
3. Put reusable logic in `src/`.
4. Add or update tests whenever behaviour changes.
5. Before finishing, run the quality gate:
   - `uv run ruff check .`
   - `uv run ruff format .`
   - `uv run pytest -q`
   - `uv run check-deep-modules src`

## Engineering conventions

- Use Python 3.11+ features and modern type hints.
- Prefer absolute imports over relative imports.
- Prefer pure functions and small data-carrying classes where possible.
- Keep public interfaces intentionally small.
- Hide helpers with a leading underscore.
- In public-facing modules, define `__all__` when it clarifies the intended interface.
- Avoid giant “do everything” files. Split code by responsibility.
- Avoid notebook-only logic. If it matters, move it into `src/`.

## Deep-modules guidance

This repo prefers **deep modules**:
- simple interface
- richer internal implementation
- fewer public entry points
- low cognitive overhead for callers

Practical defaults:
- target < 350 lines per module
- target <= 7 public names per module
- keep branching and argument counts modest
- push incidental complexity downward into helpers, not outward into callers

If a module legitimately breaks these rules, add a brief comment explaining why.
The deep-modules checker also supports:

```python
# deep-modules: disable
```

## Experiments and notebooks

- Use `marimo` notebooks for exploration only.
- Stable code belongs in `src/`.
- Record seeds, config, and outputs for ML / data experiments.
- Prefer simple local tracking first: JSON/CSV/TensorBoard under `runs/`.

## Dependency management

- Use `uv` for syncing, adding, and running dependencies.
- Do not hand-edit `uv.lock` if one exists; let `uv` manage it.
- Avoid adding heavy dependencies unless the task really needs them.

## Done means

A task is done when:
- the requested behaviour exists
- the relevant tests pass
- lint/format checks pass
- the code is easy to review
- any new constraints or workflow gotchas are reflected here or in docs

## Do not

- do not dump everything into one giant file
- do not leave behind unexplained TODOs
- do not invent architecture without a real need
- do not keep important logic trapped in notebooks
- do not finish without running the quality gate
