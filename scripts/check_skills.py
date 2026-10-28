#!/usr/bin/env python3
"""Check HStack skills against the v0.1 plan.

Token totals use Hermes's estimator: ASCII text is ceil(utf-8 bytes / 4),
which is (len + 3) // 4. Descriptions must stay inside 60 characters so
Hermes's index clip does not change them. The clip below is the word-boundary
cut in Hermes Agent main (agent/skill_utils.py). The stable installer cut,
desc[:57] + "..." when the text is longer than 60, is checked as well.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / "skills" / "hstack"
LIMIT = 60

# Word-boundary clip. Same cuts as Hermes Agent main, October 2026.
_LAST_WHITESPACE = re.compile(r"\s\S*$")
_CLIP_TRAIL = re.compile(r"[\s.,;:\-\u2013\u2014(/]+$")

DESCRIPTIONS = {
    "hstack": "Pick the playbook for this task and load it.",
    "reframe": "Name the real job before any plan or code.",
    "shape": "Settle data shape and module boundaries first.",
    "prove": "Show a failing check, then a passing one, on real behavior.",
    "council": "Have other models challenge the diff, then fix blockers.",
    "ship": "Open a short PR, watch CI, and merge only if told.",
    "takeover": "Finish someone else's branch and keep their git credit.",
    "modernize": "Rebase an old PR and decide if it still belongs.",
    "blast": "Find what a small diff can break, and prove the safe fact.",
    "swarm": "Fan out parallel subagents and return one report.",
    "arena": "Try competing approaches, then keep the best parts.",
    "principles": "Apply the design rule that should change this decision.",
}

BODY_CEILING = {
    "hstack": 700,
    "reframe": 950,
    "shape": 850,
    "prove": 750,
    "council": 900,
    "ship": 1100,
    "takeover": 500,
    "modernize": 550,
    "blast": 450,
    "swarm": 500,
    "arena": 500,
    "principles": 800,
}

INDEX_TOKENS = {
    "hstack": 15,
    "reframe": 15,
    "shape": 15,
    "prove": 18,
    "council": 18,
    "ship": 16,
    "takeover": 18,
    "modernize": 17,
    "blast": 18,
    "swarm": 16,
    "arena": 16,
    "principles": 19,
}

PLAYBOOKS = {
    "frame.md": 400,
    "feature.md": 450,
    "fix.md": 350,
    "check.md": 400,
    "land.md": 300,
}

BANNED = ("gstack", "pstack", "tstack", "codex", "claude")
SHELL_UTILS = ("grep", "rg", "cat", "head", "tail", "sed", "awk", "find", "ls")
MARKETING = (
    "powerful",
    "comprehensive",
    "seamless",
    "advanced",
    "cutting-edge",
    "state-of-the-art",
    "revolutionary",
    "robust",
)

ERRORS: list[str] = []


def fail(message: str) -> None:
    ERRORS.append(message)


def estimate_tokens(text: str) -> int:
    """Hermes estimate_tokens_rough for text we actually ship (ASCII)."""
    if not text:
        return 0
    if not text.isascii():
        fail("non-ascii skill text is outside the estimator this check locks")
        return (len(text.encode("utf-8")) + 3) // 4
    return (len(text) + 3) // 4


def clip_description(desc: str) -> str:
    """Hermes main: fit to 60 characters, cut at a word boundary, add ..."""
    if len(desc) <= LIMIT:
        return desc
    head = desc[: LIMIT - 2]
    boundary = _LAST_WHITESPACE.search(head)
    if not boundary or boundary.start() == 0:
        return desc[: LIMIT - 3] + "..."
    return _CLIP_TRAIL.sub("", head[: boundary.start()]) + "..."


def clip_description_stable(desc: str) -> str:
    """Hermes stable installer, October 2026: hard cut, then ..."""
    if len(desc) <= LIMIT:
        return desc
    return desc[: LIMIT - 3] + "..."


def parse_list(value: str) -> list[str]:
    if not (value.startswith("[") and value.endswith("]")):
        raise ValueError(f"expected a flow list, got {value!r}")
    inner = value[1:-1].strip()
    if not inner:
        return []
    return [part.strip().strip("'\"") for part in inner.split(",")]


def parse_frontmatter(text: str) -> dict:
    if not text.startswith("---\n"):
        raise ValueError("frontmatter must start at the first byte")
    end = text.find("\n---\n", 3)
    if end < 0:
        raise ValueError("frontmatter is not closed")
    raw = text[4:end]
    data: dict = {}
    section = None
    for line in raw.split("\n"):
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        stripped = line.strip()
        key, sep, val = stripped.partition(":")
        if not sep:
            raise ValueError(f"bad frontmatter line: {line}")
        key = key.strip()
        val = val.strip()
        if indent == 0:
            section = None
            if key == "metadata" and val == "":
                data["metadata"] = {}
                section = "metadata"
            elif val.startswith("["):
                data[key] = parse_list(val)
            else:
                data[key] = val
        elif section == "metadata" and indent == 2 and key == "hermes" and val == "":
            data["metadata"]["hermes"] = {}
            section = "hermes"
        elif section == "hermes" and indent == 4:
            data["metadata"]["hermes"][key] = parse_list(val) if val.startswith("[") else val
        else:
            raise ValueError(f"unexpected frontmatter line: {line}")
    return data


def check_clip_fixtures() -> None:
    long = "Use when cutting, publishing, or abandoning a hermes-agent release and its notes."
    shown = clip_description(long)
    if shown != "Use when cutting, publishing, or abandoning a...":
        fail(f"word-boundary clip drifted: {shown!r}")
    if not shown.endswith("...") or len(shown) > LIMIT:
        fail("word-boundary clip exceeded 60 characters")
    hard = clip_description_stable(long)
    if hard != long[:57] + "...":
        fail("stable clip drifted")
    one_word = "x" * 80
    if clip_description(one_word) != ("x" * 57) + "...":
        fail("single-word clip drifted")
    if clip_description("Already short.") != "Already short.":
        fail("short descriptions must pass through the clip")


def check_skills() -> dict[str, int]:
    bodies: dict[str, int] = {}
    found = sorted(p.parent.name for p in SKILL_ROOT.glob("*/SKILL.md"))
    if found != sorted(DESCRIPTIONS):
        fail(f"skill set is {found}, expected {sorted(DESCRIPTIONS)}")
    extra = [p.name for p in SKILL_ROOT.iterdir() if p.name not in DESCRIPTIONS]
    if extra:
        fail(f"unexpected path under skills/hstack: {extra}")

    idle = estimate_tokens("  hstack:")
    if idle != 3:
        fail(f"category header is {idle} tokens, expected 3")

    for name, description in DESCRIPTIONS.items():
        path = SKILL_ROOT / name / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        if "\ufeff" in text:
            fail(f"{name}: BOM is not allowed")
        try:
            meta = parse_frontmatter(text)
        except ValueError as exc:
            fail(f"{name}: {exc}")
            continue
        if meta.get("name") != name:
            fail(f"{name}: frontmatter name is {meta.get('name')!r}")
        if meta.get("description") != description:
            fail(f"{name}: description is {meta.get('description')!r}")
        desc = str(meta.get("description", ""))
        if len(desc) > LIMIT or not desc.endswith("."):
            fail(f"{name}: description must be one sentence of at most 60 characters")
        if clip_description(desc) != desc or clip_description_stable(desc) != desc:
            fail(f"{name}: Hermes would clip the description")
        if meta.get("version") != "0.1.0":
            fail(f"{name}: version must be 0.1.0")
        if meta.get("license") != "MIT":
            fail(f"{name}: license must be MIT")
        if meta.get("author") != "Preetham Kyanam":
            fail(f"{name}: author must be Preetham Kyanam")
        if meta.get("platforms") != ["linux", "macos", "windows"]:
            fail(f"{name}: platforms must be linux, macos, windows")
        hermes = meta.get("metadata", {}).get("hermes", {})
        tags = hermes.get("tags")
        related = hermes.get("related_skills")
        if not isinstance(tags, list) or not tags:
            fail(f"{name}: metadata.hermes.tags is missing")
        if not isinstance(related, list) or not related:
            fail(f"{name}: metadata.hermes.related_skills is missing")
        if not re.search(r"^## When to Use\s*$", text, re.MULTILINE):
            fail(f"{name}: missing ## When to Use")
        lowered = desc.lower()
        hits = [word for word in MARKETING if re.search(rf"\b{word}\b", lowered)]
        if hits:
            fail(f"{name}: marketing words in the description: {hits}")
        prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for util in SHELL_UTILS:
            if f"`{util}`" in prose:
                fail(f"{name}: prose names `{util}` in backticks")
        row = f"    - {name}: {description}"
        row_tokens = estimate_tokens(row)
        if row_tokens != INDEX_TOKENS[name]:
            fail(f"{name}: index row is {row_tokens} tokens, expected {INDEX_TOKENS[name]}")
        idle += row_tokens
        bodies[name] = estimate_tokens(text)
        if bodies[name] > BODY_CEILING[name]:
            fail(f"{name}: body is {bodies[name]} tokens, ceiling is {BODY_CEILING[name]}")
        blob = text.lower()
        for banned in BANNED:
            if banned in blob:
                fail(f"{name}: skill text contains {banned}")

    if idle != 204:
        fail(f"idle index is {idle} tokens, expected 204")
    return bodies


def check_playbooks() -> dict[str, int]:
    ref = SKILL_ROOT / "hstack" / "references"
    found = sorted(p.name for p in ref.glob("*.md")) if ref.is_dir() else []
    if found != sorted(PLAYBOOKS):
        fail(f"playbooks are {found}, expected {sorted(PLAYBOOKS)}")
    sizes: dict[str, int] = {}
    for name, ceiling in PLAYBOOKS.items():
        text = (ref / name).read_text(encoding="utf-8")
        sizes[name] = estimate_tokens(text)
        if sizes[name] > ceiling:
            fail(f"{name}: playbook is {sizes[name]} tokens, ceiling is {ceiling}")
        if sizes[name] > 500:
            fail(f"{name}: playbook exceeds the 500 token cap")
        blob = text.lower()
        for banned in BANNED:
            if banned in blob:
                fail(f"{name}: playbook contains {banned}")
    stray = [p.relative_to(SKILL_ROOT / "hstack").as_posix() for p in (SKILL_ROOT / "hstack").rglob("*") if p.is_file() and p.name != "SKILL.md" and p.parent.name != "references"]
    if stray:
        fail(f"unexpected files beside the router: {stray}")
    return sizes


def main() -> int:
    check_clip_fixtures()
    if (ROOT / "NOTICE").exists() or (ROOT / "NOTICE.md").exists():
        fail("NOTICE is not required; nothing was copied")
    bodies = check_skills()
    playbooks = check_playbooks()
    if ERRORS:
        for message in ERRORS:
            print(f"error: {message}", file=sys.stderr)
        return 1
    print("idle index: 204")
    total = 0
    for name in DESCRIPTIONS:
        total += bodies[name]
        print(f"  {name:12} {bodies[name]:4} / {BODY_CEILING[name]}")
    print(f"  {'bodies':12} {total:4} / 8550")
    for name in PLAYBOOKS:
        print(f"  {name:12} {playbooks[name]:4} / {PLAYBOOKS[name]}")
    planning = bodies["hstack"] + bodies["reframe"] + bodies["shape"]
    print(f"planning path (router + reframe + shape): {planning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
