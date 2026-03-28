# Deep modules in this template

The idea is simple:

> Prefer modules whose interfaces are simpler than their implementations.

That usually means:
- fewer public names
- more hidden helpers
- clear boundaries
- lower cognitive load at call sites

This template does **not** claim to measure that perfectly.
It uses a few lightweight proxies that are cheap enough to run constantly:

1. **module length cap**: giant files are hard to navigate
2. **public API cap**: too many public names usually means a shallow interface
3. **depth ratio**: `SLOC / public API size`

These checks are deliberately rough.
They are there to start the right conversation, not to replace judgement.

## Practical tips

- Put convenience re-exports in `__init__.py` or a dedicated `api.py`.
- Keep internal helpers private with `_` prefixes.
- Use `__all__` in public-facing modules to make the intended surface explicit.
- Split files by responsibility, not by arbitrary line counts.
- Prefer one cohesive module over many tiny, anemic wrappers.

## When to disable the check

Some modules are intentionally small-and-wide:
- schema / constants modules
- compatibility shims
- hand-built public API barrels

In those cases, add this near the top of the file:

```python
# deep-modules: disable
```

Use it sparingly and leave a short reason if the exception is non-obvious.
