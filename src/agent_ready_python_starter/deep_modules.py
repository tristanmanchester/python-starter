from __future__ import annotations

import argparse
import ast
from collections.abc import Iterable, Iterator, Sequence
from dataclasses import dataclass
from pathlib import Path

_DEFAULT_MAX_PUBLIC_API = 7
_DEFAULT_MAX_MODULE_LINES = 350
_DEFAULT_MIN_DEPTH_RATIO = 8.0
_DEFAULT_MIN_LINES_FOR_RATIO = 24
_DISABLE_MARKER = "deep-modules: disable"

__all__ = ["Issue", "ModuleStats", "analyse_source", "find_issues", "main", "run"]


@dataclass(frozen=True)
class ModuleStats:
    path: Path
    sloc: int
    public_names: tuple[str, ...]
    has_explicit_all: bool

    @property
    def depth_ratio(self) -> float:
        if not self.public_names:
            return float("inf")
        return self.sloc / len(self.public_names)


@dataclass(frozen=True)
class Issue:
    path: Path
    kind: str
    message: str


def parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Check simple 'deep module' heuristics: file length, public API size, "
            "and interface depth ratio."
        )
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["src"],
        help="Files or directories to scan (default: src).",
    )
    parser.add_argument(
        "--max-public-api",
        type=int,
        default=_DEFAULT_MAX_PUBLIC_API,
        help=f"Maximum public names allowed in a module (default: {_DEFAULT_MAX_PUBLIC_API}).",
    )
    parser.add_argument(
        "--max-module-lines",
        type=int,
        default=_DEFAULT_MAX_MODULE_LINES,
        help=(
            "Maximum non-blank, non-comment lines per module "
            f"(default: {_DEFAULT_MAX_MODULE_LINES})."
        ),
    )
    parser.add_argument(
        "--min-depth-ratio",
        type=float,
        default=_DEFAULT_MIN_DEPTH_RATIO,
        help=(
            "Minimum SLOC/public-API ratio for modules with public names "
            f"(default: {_DEFAULT_MIN_DEPTH_RATIO})."
        ),
    )
    parser.add_argument(
        "--min-lines-for-ratio",
        type=int,
        default=_DEFAULT_MIN_LINES_FOR_RATIO,
        help=(
            "Only apply the depth-ratio check to modules with at least this many "
            f"non-blank, non-comment lines (default: {_DEFAULT_MIN_LINES_FOR_RATIO})."
        ),
    )
    return parser.parse_args(list(argv) if argv is not None else None)


def count_sloc(source: str) -> int:
    return sum(
        1
        for line in source.splitlines()
        if (stripped := line.strip()) and not stripped.startswith("#")
    )


def has_disable_marker(source: str) -> bool:
    head = "\n".join(source.splitlines()[:8]).lower()
    return _DISABLE_MARKER in head


def _normalize_all_value(value: object) -> tuple[str, ...] | None:
    if not isinstance(value, (list, tuple, set)):
        return None
    if not all(isinstance(item, str) for item in value):
        return None
    return tuple(sorted(set(value)))


def _extract_assigned_all_value(node: ast.Assign | ast.AnnAssign) -> object | None:
    try:
        return ast.literal_eval(node.value)
    except (ValueError, TypeError):
        return None


def extract_explicit_all(module: ast.Module) -> tuple[str, ...] | None:
    for node in module.body:
        if isinstance(node, ast.Assign):
            targets = [
                target
                for target in node.targets
                if isinstance(target, ast.Name) and target.id == "__all__"
            ]
            if targets:
                value = _extract_assigned_all_value(node)
                return _normalize_all_value(value)
        if (
            isinstance(node, ast.AnnAssign)
            and isinstance(node.target, ast.Name)
            and node.target.id == "__all__"
        ):
            value = _extract_assigned_all_value(node)
            return _normalize_all_value(value)
    return None


def collect_public_names(
    module: ast.Module, explicit_all: tuple[str, ...] | None
) -> tuple[str, ...]:
    if explicit_all is not None:
        return explicit_all

    public_names: set[str] = set()

    for node in module.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if not node.name.startswith("_"):
                public_names.add(node.name)
            continue

        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and not target.id.startswith("_"):
                    public_names.add(target.id)
            continue

        if isinstance(node, ast.AnnAssign):
            target = node.target
            if isinstance(target, ast.Name) and not target.id.startswith("_"):
                public_names.add(target.id)

    return tuple(sorted(public_names))


def analyse_source(source: str, path: Path) -> ModuleStats | None:
    if has_disable_marker(source):
        return None

    module = ast.parse(source, filename=str(path))
    explicit_all = extract_explicit_all(module)
    public_names = collect_public_names(module, explicit_all)
    return ModuleStats(
        path=path,
        sloc=count_sloc(source),
        public_names=public_names,
        has_explicit_all=explicit_all is not None,
    )


def analyse_path(path: Path) -> ModuleStats | None:
    return analyse_source(path.read_text(encoding="utf-8"), path)


def find_issues(
    stats: ModuleStats,
    *,
    max_public_api: int,
    max_module_lines: int,
    min_depth_ratio: float,
    min_lines_for_ratio: int,
) -> list[Issue]:
    issues: list[Issue] = []

    if stats.sloc > max_module_lines:
        issues.append(
            Issue(
                path=stats.path,
                kind="module-too-long",
                message=(
                    f"{stats.sloc} SLOC exceeds limit of {max_module_lines}. "
                    "Split by responsibility or hide incidental detail."
                ),
            )
        )

    public_api_size = len(stats.public_names)
    if public_api_size > max_public_api:
        preview = ", ".join(stats.public_names[:8])
        issues.append(
            Issue(
                path=stats.path,
                kind="too-many-public-names",
                message=(
                    f"{public_api_size} public names exceeds limit of {max_public_api}: {preview}"
                ),
            )
        )

    if (
        public_api_size > 0
        and stats.sloc >= min_lines_for_ratio
        and stats.depth_ratio < min_depth_ratio
    ):
        issues.append(
            Issue(
                path=stats.path,
                kind="shallow-module",
                message=(
                    f"depth ratio {stats.depth_ratio:.1f} < {min_depth_ratio:.1f} "
                    f"({stats.sloc} SLOC / {public_api_size} public names)."
                ),
            )
        )

    return issues


def iter_python_files(paths: Iterable[Path]) -> Iterator[Path]:
    skip_dirs = {".git", ".venv", "__pycache__", "build", "dist"}
    skip_names = {"__init__.py", "conftest.py"}

    for path in paths:
        if not path.exists():
            continue

        if path.is_file() and path.suffix == ".py":
            if path.name not in skip_names and not any(part in skip_dirs for part in path.parts):
                yield path
            continue

        if not path.is_dir():
            continue

        for child in path.rglob("*.py"):
            if child.name in skip_names:
                continue
            if "tests" in child.parts or "notebooks" in child.parts:
                continue
            if any(part in skip_dirs for part in child.parts):
                continue
            yield child


def run(
    paths: Sequence[str | Path],
    *,
    max_public_api: int = _DEFAULT_MAX_PUBLIC_API,
    max_module_lines: int = _DEFAULT_MAX_MODULE_LINES,
    min_depth_ratio: float = _DEFAULT_MIN_DEPTH_RATIO,
    min_lines_for_ratio: int = _DEFAULT_MIN_LINES_FOR_RATIO,
) -> int:
    issues: list[Issue] = []
    scanned = 0

    for path in iter_python_files(Path(p) for p in paths):
        try:
            stats = analyse_path(path)
        except SyntaxError as exc:
            issues.append(
                Issue(
                    path=path,
                    kind="syntax-error",
                    message=f"failed to parse module: {exc.msg} (line {exc.lineno})",
                )
            )
            continue

        if stats is None:
            continue

        scanned += 1
        issues.extend(
            find_issues(
                stats,
                max_public_api=max_public_api,
                max_module_lines=max_module_lines,
                min_depth_ratio=min_depth_ratio,
                min_lines_for_ratio=min_lines_for_ratio,
            )
        )

    if issues:
        grouped: dict[Path, list[Issue]] = {}
        for issue in issues:
            grouped.setdefault(issue.path, []).append(issue)

        for path, path_issues in sorted(grouped.items()):
            print(path)
            for issue in path_issues:
                print(f"  - [{issue.kind}] {issue.message}")
        print()
        print(f"Deep-modules check failed: {len(issues)} issue(s) across {len(grouped)} file(s).")
        return 1

    print(f"Deep-modules check passed: scanned {scanned} module(s).")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    args = parse_args(argv)
    return run(
        args.paths,
        max_public_api=args.max_public_api,
        max_module_lines=args.max_module_lines,
        min_depth_ratio=args.min_depth_ratio,
        min_lines_for_ratio=args.min_lines_for_ratio,
    )


if __name__ == "__main__":
    raise SystemExit(main())
