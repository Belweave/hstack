#!/usr/bin/env python3
"""Fail if HStack loads or installs an external stack without a confirm step."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills" / "hstack"
STACKS = SKILLS / "hstack" / "references" / "stacks.md"
OWNED = {
    "hstack",
    "reframe",
    "shape",
    "prove",
    "council",
    "ship",
    "takeover",
    "modernize",
    "blast",
    "swarm",
    "arena",
    "principles",
    "systematic-debugging",
    "test-driven-development",
    "requesting-code-review",
    "dogfood",
    "spike",
    "simplify-code",
    "hermes-agent-skill-authoring",
    "github",
    "humanizer",
    "architecture-diagram",
    "design-md",
    "pdf",
}
URLS = (
    "codeload.github.com",
    "github.com/garrytan/gstack",
    "github.com/garrytan/gbrain",
    "github.com/t3dotgg/tstack",
    "github.com/cursor/plugins",
)
INSTALL = "hstack_stack.py install"

ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def skill_views(text: str) -> list[str]:
    names = []
    needle = 'skill_view("'
    start = 0
    while True:
        index = text.find(needle, start)
        if index < 0:
            break
        end = text.find('"', index + len(needle))
        if end < 0:
            break
        names.append(text[index + len(needle) : end])
        start = end + 1
    return names


def check_tree() -> None:
    if not STACKS.is_file():
        fail("missing stacks registry")
        return
    registry = STACKS.read_text(encoding="utf-8")
    yes_at = registry.find("until the user says yes")
    install_at = registry.find(INSTALL)
    if yes_at < 0 or install_at < 0 or yes_at > install_at:
        fail("stacks.md must require a yes before hstack_stack.py install")
    for phrase in ("at most one", "decline", "--yes", "detect"):
        if phrase not in registry:
            fail(f"stacks.md is missing {phrase}")
    for name in skill_views(registry):
        if name not in OWNED:
            fail(f"stacks.md loads {name}")

    for path in SKILLS.rglob("*.md"):
        if path.resolve() == STACKS.resolve():
            continue
        text = path.read_text(encoding="utf-8")
        for url in URLS:
            if url in text:
                fail(f"{path.relative_to(ROOT)} contains {url}")
        if INSTALL in text:
            fail(f"{path.relative_to(ROOT)} installs a stack")
        for name in skill_views(text):
            if name not in OWNED:
                fail(f"{path.relative_to(ROOT)} loads {name}")

    for path in (ROOT / "hooks").glob("*.py"):
        text = path.read_text(encoding="utf-8")
        for url in URLS:
            if url in text:
                fail(f"{path.relative_to(ROOT)} contains {url}")
        if INSTALL in text:
            fail(f"{path.relative_to(ROOT)} installs a stack")


def check_fixtures() -> None:
    sneaky = 'Load it with skill_view("gstack-ship").'
    if any(name not in OWNED for name in skill_views(sneaky)):
        pass
    else:
        fail("fixture did not catch an outside skill_view")
    bare = "Run hstack_stack.py install gstack --yes now."
    if "until the user says yes" in bare:
        fail("fixture install unexpectedly contains a yes")
    confirmed = "Do not download until the user says yes.\nThen hstack_stack.py install --yes.\n"
    if confirmed.find("until the user says yes") > confirmed.find(INSTALL):
        fail("ordered confirm fixture was rejected")


def main() -> int:
    check_fixtures()
    check_tree()
    if ERRORS:
        for message in ERRORS:
            print(f"error: {message}", file=sys.stderr)
        return 1
    print("check_consent: ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
