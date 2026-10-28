"""Hook behavior for the optional Hermes shell shims.

The shims in this directory import this module. Nothing under skills/ does.
Hermes passes a JSON object on stdin. See the shell-hook wire format in
website/docs/user-guide/features/hooks.md.
"""

from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path


ROOT_RM = re.compile(
    r"^(?:/|/\*|~|~/|~/\*|\$HOME|\$\{HOME\}|%USERPROFILE%|[A-Za-z]:\\?|[A-Za-z]:/\*?|[A-Za-z]:\\\*?)$",
    re.IGNORECASE,
)
RM_FLAGS = re.compile(r"^-[a-zA-Z]*$")
FORK = re.compile(r":\(\)\s*\{")
POWER = re.compile(r"(?:^|[;&|`\n])\s*(?:sudo\s+)?(?:shutdown|reboot|poweroff|halt)\b")
MKFS = re.compile(r"(?:^|[;&|`\n])\s*(?:sudo\s+)?mkfs(?:\.[a-z0-9]+)?\b")
DD_DISK = re.compile(r"\bdd\b[\s\S]{0,200}\bof=(?:/dev/|\\\\)")


def hermes_home() -> Path:
    raw = os.environ.get("HERMES_HOME")
    if raw:
        return Path(raw)
    return Path.home() / ".hermes"


def _load(raw: str) -> dict:
    data = json.loads(raw)
    if not isinstance(data, dict):
        raise ValueError("payload is not an object")
    return data


def _command(payload: dict) -> str:
    tool_input = payload.get("tool_input")
    if isinstance(tool_input, dict):
        command = tool_input.get("command")
        if isinstance(command, str):
            return command
    extra = payload.get("extra")
    if isinstance(extra, dict):
        args = extra.get("args")
        if isinstance(args, dict) and isinstance(args.get("command"), str):
            return args["command"]
    return ""


def destructive(command: str) -> str | None:
    """Return a short reason when the command should not run."""
    text = command.strip()
    if not text:
        return None
    if FORK.search(text):
        return "fork bomb"
    if POWER.search(text):
        return "power command"
    if MKFS.search(text):
        return "mkfs"
    if DD_DISK.search(text):
        return "disk write"
    for segment in re.split(r"[;&|`\n]", text):
        tokens = segment.split()
        if not tokens:
            continue
        if tokens[0] == "sudo":
            tokens = tokens[1:]
        if not tokens or tokens[0] != "rm":
            continue
        flags = []
        operands = []
        for token in tokens[1:]:
            if token == "--":
                continue
            if token.startswith("-") and RM_FLAGS.match(token):
                flags.append(token[1:])
            else:
                operands.append(token)
        letters = "".join(flags)
        if "r" not in letters or "f" not in letters:
            continue
        for operand in operands:
            if ROOT_RM.match(operand):
                return "rm of a root"
    return None


def guard(raw: str) -> int:
    try:
        payload = _load(raw)
    except (json.JSONDecodeError, ValueError):
        print(json.dumps({"action": "block", "message": "hstack guard could not read the tool call"}))
        return 2
    tool = payload.get("tool_name")
    if tool not in (None, "terminal"):
        print("{}")
        return 0
    command = _command(payload)
    if tool == "terminal" and not command:
        print(json.dumps({"action": "block", "message": "hstack guard could not read the terminal command"}))
        return 2
    reason = destructive(command)
    if reason:
        print(json.dumps({"action": "block", "message": f"hstack guard blocked a {reason}"}))
        return 0
    print("{}")
    return 0


def _session_id(payload: dict) -> str:
    for key in ("session_id",):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()[:80]
    extra = payload.get("extra")
    if isinstance(extra, dict):
        value = extra.get("session_id")
        if isinstance(value, str) and value.strip():
            return value.strip()[:80]
    return "unknown"


def _platform(payload: dict) -> str:
    extra = payload.get("extra")
    if isinstance(extra, dict) and isinstance(extra.get("platform"), str):
        return extra["platform"].strip()[:40] or "unknown"
    if isinstance(payload.get("platform"), str):
        return payload["platform"].strip()[:40] or "unknown"
    return "unknown"


def save(raw: str) -> int:
    try:
        payload = _load(raw)
    except (json.JSONDecodeError, ValueError):
        print("{}")
        return 0
    home = hermes_home()
    try:
        directory = home / "hstack"
        directory.mkdir(parents=True, exist_ok=True)
        line = "\t".join(
            (
                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                _session_id(payload).replace("\t", " "),
                _platform(payload).replace("\t", " "),
            )
        )
        with (directory / "session-log.tsv").open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
    except OSError:
        print("{}")
        return 0
    print("{}")
    return 0


_SKILLS = (
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
    "hstack",
)


def _message_text(payload: dict) -> str:
    extra = payload.get("extra") if isinstance(payload.get("extra"), dict) else {}
    value = extra.get("user_message")
    if value is None:
        value = payload.get("user_message")
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and isinstance(item.get("text"), str):
                parts.append(item["text"])
        return "\n".join(parts)
    return ""


def _first_turn(payload: dict) -> bool:
    extra = payload.get("extra") if isinstance(payload.get("extra"), dict) else {}
    flag = extra.get("is_first_turn", payload.get("is_first_turn"))
    return flag is True


def _playbook(message: str) -> str | None:
    text = message.lower()
    if any(name in text for name in ("/hstack",) + tuple(f"/{name}" for name in _SKILLS)):
        return None
    if any(name in text.split() for name in _SKILLS):
        return None
    rules = (
        (("security", "injection", "secret", "auth"), "security.md"),
        (("deploy", "production"), "deploy.md"),
        (("diagram",), "diagram.md"),
        (("pull request", "merge"), "land.md"),
        (("refactor",), "refactor.md"),
        (("layout", "design"), "design.md"),
        (("broken", "crash", "bug"), "fix.md"),
        (("implement", "add a", "build"), "feature.md"),
    )
    for words, filename in rules:
        if any(word in text for word in words):
            return filename
    return None


def suggest(raw: str) -> int:
    try:
        payload = _load(raw)
    except (json.JSONDecodeError, ValueError):
        print("{}")
        return 0
    if not _first_turn(payload):
        print("{}")
        return 0
    filename = _playbook(_message_text(payload))
    if not filename:
        print("{}")
        return 0
    context = (
        f"HStack playbook {filename} matches this task. "
        "Load it through the hstack router. Do not load another stack unless the user asks."
    )
    print(json.dumps({"context": context}))
    return 0
