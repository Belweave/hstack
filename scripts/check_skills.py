#!/usr/bin/env python3
"""Check HStack skills against the v0.1 plan.

Token totals use Hermes's estimator: ASCII text is ceil(utf-8 bytes / 4),
which is (len + 3) // 4. Descriptions must stay inside 60 characters so
Hermes's index clip does not change them. The clip below is the word-boundary
cut in Hermes Agent main (agent/skill_utils.py). The stable installer cut,
desc[:57] + "..." when the text is longer than 60, is checked as well.
"""

from __future__ import annotations

import hashlib
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
    "refactor.md": 500,
    "design.md": 500,
    "qa.md": 500,
    "perf.md": 500,
    "trace.md": 500,
    "retro.md": 500,
    "docs.md": 500,
    "security.md": 500,
    "explain.md": 500,
    "memory.md": 500,
    "author.md": 500,
    "prose.md": 500,
    "experiment.md": 500,
    "parallel.md": 500,
    "overnight.md": 500,
    "pickup.md": 500,
    "worktree.md": 500,
    "spec.md": 500,
    "eval.md": 500,
    "deploy.md": 500,
    "browse.md": 500,
    "safety.md": 500,
    "decisions.md": 500,
    "triage.md": 500,
    "types.md": 500,
    "verify.md": 500,
    "diagram.md": 500,
}

ROUTES_FILE = "routes.md"
ROUTES_CEILING = 500
STACKS_FILE = "stacks.md"
STACKS_CEILING = 1400
ROUTER_SCRIPT = "scripts/hstack_stack.py"

# Frozen at hermes-agent ee7e0f517232fb619c72e49d7e648436bddc598e.
BUNDLED = {
    "systematic-debugging": (3515, "skills/software-development/systematic-debugging/SKILL.md"),
    "test-driven-development": (2575, "skills/software-development/test-driven-development/SKILL.md"),
    "requesting-code-review": (2196, "skills/software-development/requesting-code-review/SKILL.md"),
    "dogfood": (2163, "skills/software-development/dogfood/SKILL.md"),
    "spike": (2181, "skills/software-development/spike/SKILL.md"),
    "simplify-code": (3674, "skills/software-development/simplify-code/SKILL.md"),
    "hermes-agent-skill-authoring": (3663, "skills/software-development/hermes-agent-skill-authoring/SKILL.md"),
    "github": (612, "skills/software-development/github/SKILL.md"),
    "humanizer": (8616, "skills/creative/humanizer/SKILL.md"),
    "architecture-diagram": (1458, "skills/creative/architecture-diagram/SKILL.md"),
    "design-md": (2120, "skills/creative/design-md/SKILL.md"),
    "pdf": (3123, "skills/productivity/pdf/SKILL.md"),
}

DISPOSITIONS = ("skill", "routed-reference", "plugin-or-tool", "helper-script", "skip")
FEATURE_COUNT = 520
FEATURE_IDS_SHA256 = "03dd1077b3e50978c6c7142e24a3bf52bcc92172ebcff32b89e3cfe4f83ce4a0"
DISPOSITION_COUNTS = {
    "helper-script": 15,
    "plugin-or-tool": 3,
    "routed-reference": 260,
    "skill": 67,
    "skip": 175,
}
SUMMARY_LINE = "520 rows. helper-script 15, plugin-or-tool 3, routed-reference 260, skill 67, skip 175."
FEATURE_HEADER = ["id", "source", "item", "kind", "disposition", "target", "on_demand", "reason"]
ROUTE_HEADER = [
    "route",
    "when it fires",
    "budget playbook tokens",
    "measured playbook tokens",
    "measured route upper bound",
]
SKILL_HEADER = ["skill", "measured body tokens"]
BUNDLED_HEADER = ["bundled skill", "path", "tokens"]

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
        if meta.get("version") != "0.2.1":
            fail(f"{name}: version must be 0.2.1")
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
    expected = sorted([*PLAYBOOKS, ROUTES_FILE, STACKS_FILE])
    found = sorted(p.name for p in ref.glob("*.md")) if ref.is_dir() else []
    if found != expected:
        fail(f"playbooks are {found}, expected {expected}")
    other = [p.name for p in ref.iterdir() if p.is_file() and p.suffix != ".md"] if ref.is_dir() else []
    if other:
        fail(f"unexpected files in references: {other}")
    sizes: dict[str, int] = {}
    ceilings = {**PLAYBOOKS, ROUTES_FILE: ROUTES_CEILING, STACKS_FILE: STACKS_CEILING}
    for name, ceiling in ceilings.items():
        text = (ref / name).read_text(encoding="utf-8")
        sizes[name] = estimate_tokens(text)
        if sizes[name] > ceiling:
            fail(f"{name}: playbook is {sizes[name]} tokens, ceiling is {ceiling}")
        if name not in (ROUTES_FILE, STACKS_FILE) and sizes[name] > 500:
            fail(f"{name}: playbook exceeds the 500 token cap")
        blob = text.lower()
        if name != STACKS_FILE:
            for banned in BANNED:
                if banned in blob:
                    fail(f"{name}: playbook contains {banned}")
        prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
        for util in SHELL_UTILS:
            if f"`{util}`" in prose:
                fail(f"{name}: prose names `{util}` in backticks")
    stray = [
        p.relative_to(SKILL_ROOT / "hstack").as_posix()
        for p in (SKILL_ROOT / "hstack").rglob("*")
        if p.is_file()
        and p.suffix != ".pyc"
        and "__pycache__" not in p.parts
        and p.name != "SKILL.md"
        and p.parent.name != "references"
        and p.relative_to(SKILL_ROOT / "hstack").as_posix() != ROUTER_SCRIPT
    ]
    if stray:
        fail(f"unexpected files beside the router: {stray}")
    return sizes


def split_row(line: str) -> list[str] | None:
    if not line.startswith("|"):
        return None
    parts = line.split("|")
    if parts[0].strip() or parts[-1].strip():
        return None
    return [part.strip() for part in parts[1:-1]]


def is_separator(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell) for cell in cells)


def table_after(text: str, header: list[str]) -> list[list[str]] | None:
    lines = text.splitlines()
    for index, line in enumerate(lines):
        cells = split_row(line)
        if cells != header:
            continue
        rows: list[list[str]] = []
        for follow in lines[index + 1 :]:
            parsed = split_row(follow)
            if parsed is None:
                break
            if is_separator(parsed):
                continue
            rows.append(parsed)
        return rows
    return None


def feature_row_problems(rows: list[list[str]]) -> list[str]:
    problems: list[str] = []
    for index, row in enumerate(rows, start=1):
        if len(row) != len(FEATURE_HEADER) or any(cell == "" for cell in row):
            problems.append(f"feature row {index} is empty or short")
    return problems


def check_empty_row_fixture() -> None:
    blank = ["", "", "", "", "", "", "", ""]
    partial = ["id", "gstack", "", "skill", "skill", "target", "skill:hstack", "because"]
    filled = ["id", "gstack", "item", "skill", "skill", "target", "skill:hstack", "because"]
    caught = feature_row_problems([blank, partial])
    if len(caught) != 2 or any("empty" not in problem for problem in caught):
        fail("empty-row fixture did not fail")
    if feature_row_problems([filled]):
        fail("a filled feature row was rejected")


def named_views(text: str) -> list[str]:
    return re.findall(r"skill_view\(\s*\"([^\"]+)\"", text)


def route_upper_bound(route: str, bodies: dict[str, int], routes_tokens: int) -> int:
    router = (SKILL_ROOT / "hstack" / "SKILL.md").read_text(encoding="utf-8")
    if "references/stacks.md" not in router:
        fail("router must load references/stacks.md after the playbook")
    stacks = (SKILL_ROOT / "hstack" / "references" / STACKS_FILE).read_text(encoding="utf-8")
    playbook = (SKILL_ROOT / "hstack" / "references" / f"{route}.md").read_text(encoding="utf-8")
    total = bodies["hstack"] + routes_tokens + estimate_tokens(playbook) + estimate_tokens(stacks)
    seen = {"hstack"}
    for name in named_views(playbook):
        if name in seen:
            continue
        seen.add(name)
        if name in DESCRIPTIONS:
            total += bodies[name]
            skill_text = (SKILL_ROOT / name / "SKILL.md").read_text(encoding="utf-8")
            for hop in named_views(skill_text):
                if hop in seen:
                    continue
                seen.add(hop)
                if hop in BUNDLED:
                    total += BUNDLED[hop][0]
                elif hop in DESCRIPTIONS:
                    total += bodies[hop]
                else:
                    fail(f"{route}: unknown skill_view target {hop}")
        elif name in BUNDLED:
            total += BUNDLED[name][0]
        else:
            fail(f"{route}: unknown skill_view target {name}")
    return total


def require_int(label: str, cell: str) -> int | None:
    if cell == "" or cell == "unmeasured":
        fail(f"{label} is empty or unmeasured")
        return None
    if not re.fullmatch(r"\d+", cell):
        fail(f"{label} is not an integer: {cell}")
        return None
    return int(cell)


def check_parity(bodies: dict[str, int], playbooks: dict[str, int]) -> dict[str, int]:
    path = ROOT / "PARITY.md"
    if not path.is_file():
        fail("PARITY.md is missing")
        return {}
    text = path.read_text(encoding="utf-8")
    routes_tokens = playbooks.get(ROUTES_FILE, 0)
    catalog = f"The catalog measures {routes_tokens} tokens."
    if catalog not in text:
        fail(f"PARITY.md must contain {catalog!r}")
    if SUMMARY_LINE not in text:
        fail("PARITY.md summary line does not match the feature counts")

    feature_rows = table_after(text, FEATURE_HEADER)
    if feature_rows is None:
        fail("PARITY.md is missing the feature table")
        feature_rows = []
    for problem in feature_row_problems(feature_rows):
        fail(f"PARITY.md {problem}")
    if len(feature_rows) != FEATURE_COUNT:
        fail(f"PARITY.md has {len(feature_rows)} feature rows, expected {FEATURE_COUNT}")
    ids = [row[0] for row in feature_rows if len(row) == len(FEATURE_HEADER)]
    duplicates = sorted({item for item in ids if ids.count(item) > 1})
    if duplicates:
        fail(f"duplicate feature ids: {duplicates}")
    if ids and all(item.isascii() for item in ids):
        digest = hashlib.sha256("\n".join(sorted(ids)).encode("ascii")).hexdigest()
        if digest != FEATURE_IDS_SHA256:
            fail(f"feature id set changed: {digest}")
    counts = {name: 0 for name in DISPOSITIONS}
    route_names = {name[:-3] for name in PLAYBOOKS}
    for row in feature_rows:
        if len(row) != len(FEATURE_HEADER) or any(cell == "" for cell in row):
            continue
        source, _item, _kind, disposition, _target, demand, _reason = row[1:]
        if source not in ("gstack", "tstack", "pstack"):
            fail(f"{row[0]}: unknown source {source}")
        if disposition not in DISPOSITIONS:
            fail(f"{row[0]}: disposition {disposition!r} is not one of {DISPOSITIONS}")
            continue
        counts[disposition] += 1
        if disposition == "skip":
            if demand != "0":
                fail(f"{row[0]}: a skip loads nothing, got {demand}")
            continue
        if disposition == "skill":
            if not demand.startswith("skill:") or demand[6:] not in DESCRIPTIONS:
                fail(f"{row[0]}: skill rows use skill:<name>, got {demand}")
            continue
        if demand not in route_names:
            fail(f"{row[0]}: on_demand {demand!r} is not a route")
    if counts != DISPOSITION_COUNTS:
        fail(f"disposition counts are {counts}, expected {DISPOSITION_COUNTS}")

    route_rows = table_after(text, ROUTE_HEADER)
    if route_rows is None:
        fail("PARITY.md is missing the route budget table")
        route_rows = []
    seen_routes: list[str] = []
    uppers: dict[str, int] = {}
    for row in route_rows:
        if len(row) != len(ROUTE_HEADER) or any(cell == "" for cell in row):
            fail("route budget table has an empty row")
            continue
        route, _when, budget, measured, upper = row
        seen_routes.append(route)
        filename = f"{route}.md"
        if filename not in PLAYBOOKS:
            fail(f"unknown route {route}")
            continue
        budget_n = require_int(f"{route} budget", budget)
        measured_n = require_int(f"{route} measured playbook", measured)
        upper_n = require_int(f"{route} upper bound", upper)
        if budget_n is not None and budget_n != PLAYBOOKS[filename]:
            fail(f"{route}: budget is {budget_n}, ceiling is {PLAYBOOKS[filename]}")
        if measured_n is not None and measured_n != playbooks.get(filename):
            fail(f"{route}: measured playbook is {measured_n}, files are {playbooks.get(filename)}")
        computed = route_upper_bound(route, bodies, routes_tokens)
        uppers[route] = computed
        if upper_n is not None and upper_n != computed:
            fail(f"{route}: upper bound is {upper_n}, files load {computed}")
    missing = sorted(route_names - set(seen_routes))
    if missing:
        fail(f"route budget table is missing {missing}")
    if len(seen_routes) != len(set(seen_routes)):
        fail("route budget table has a duplicate route")

    skill_rows = table_after(text, SKILL_HEADER)
    if skill_rows is None:
        fail("PARITY.md is missing the direct skill token table")
        skill_rows = []
    seen_skills: list[str] = []
    for row in skill_rows:
        if len(row) != 2 or any(cell == "" for cell in row):
            fail("direct skill table has an empty row")
            continue
        name, measured = row
        seen_skills.append(name)
        measured_n = require_int(f"{name} body", measured)
        if name not in bodies:
            fail(f"direct skill table has unknown skill {name}")
            continue
        if measured_n is not None and measured_n != bodies[name]:
            fail(f"{name}: PARITY body is {measured_n}, file is {bodies[name]}")
    if sorted(seen_skills) != sorted(DESCRIPTIONS):
        fail(f"direct skill table is {sorted(seen_skills)}")

    bundled_rows = table_after(text, BUNDLED_HEADER)
    if bundled_rows is None:
        fail("PARITY.md is missing the bundled skill token table")
        bundled_rows = []
    seen_bundled: list[str] = []
    for row in bundled_rows:
        if len(row) != 3 or any(cell == "" for cell in row):
            fail("bundled skill table has an empty row")
            continue
        name, bundled_path, measured = row
        seen_bundled.append(name)
        if name not in BUNDLED:
            fail(f"unknown bundled skill {name}")
            continue
        tokens, expected_path = BUNDLED[name]
        if bundled_path.strip("`") != expected_path:
            fail(f"{name}: path is {bundled_path}")
        measured_n = require_int(f"{name} bundled", measured)
        if measured_n is not None and measured_n != tokens:
            fail(f"{name}: bundled tokens are {measured_n}, frozen count is {tokens}")
    if sorted(seen_bundled) != sorted(BUNDLED):
        fail("bundled skill table does not match the frozen set")
    return uppers


def main() -> int:
    check_clip_fixtures()
    check_empty_row_fixture()
    if (ROOT / "NOTICE").exists() or (ROOT / "NOTICE.md").exists():
        fail("NOTICE is not required; nothing was copied")
    bodies = check_skills()
    playbooks = check_playbooks()
    uppers = check_parity(bodies, playbooks)
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
    print(f"  {ROUTES_FILE:12} {playbooks[ROUTES_FILE]:4} / {ROUTES_CEILING}")
    print("on-demand route upper bounds:")
    for route, upper in uppers.items():
        print(f"  {route:12} {upper:5}")
    planning = bodies["hstack"] + bodies["reframe"] + bodies["shape"]
    print(f"planning path (router + reframe + shape): {planning}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
