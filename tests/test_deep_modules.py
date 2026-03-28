from pathlib import Path

from agent_ready_python_starter.deep_modules import analyse_source, find_issues


def test_explicit_all_defines_public_interface() -> None:
    source = """
__all__ = ["train", "evaluate"]

def train():
    return 1

def evaluate():
    return 2

def helper():
    return 3

public_alias = helper
"""
    stats = analyse_source(source, Path("example.py"))
    assert stats is not None
    assert stats.public_names == ("evaluate", "train")


def test_deep_modules_flags_wide_module() -> None:
    source = """
def a():
    return 1

def b():
    return 2

def c():
    return 3

def d():
    return 4

def e():
    return 5

def f():
    return 6

def g():
    return 7

def h():
    return 8
"""
    stats = analyse_source(source, Path("wide.py"))
    assert stats is not None
    issues = find_issues(
        stats,
        max_public_api=7,
        max_module_lines=350,
        min_depth_ratio=0.1,
        min_lines_for_ratio=999,
    )
    assert any(issue.kind == "too-many-public-names" for issue in issues)


def test_disable_marker_skips_module() -> None:
    source = """
# deep-modules: disable

def a():
    return 1

def b():
    return 2

def c():
    return 3

def d():
    return 4

def e():
    return 5

def f():
    return 6

def g():
    return 7

def h():
    return 8
"""
    assert analyse_source(source, Path("ignored.py")) is None
