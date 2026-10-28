#!/usr/bin/env python3
"""Install or remove optional Hermes shell hooks.

Default installs do not call this. install.sh does, and only with
--with hermes-hooks or a named subset. The shims live under
<home>/hstack/hooks and are registered in config.yaml under hooks:.
A backup is taken before a config change. A second run that would
write the same text does not write again.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path


HOOKS = ("guard", "save", "suggest")
ALIASES = {
    "hermes-hooks": HOOKS,
    "hermes-hooks-guard": ("guard",),
    "hermes-hooks-save": ("save",),
    "hermes-hooks-suggest": ("suggest",),
}
EVENTS = {
    "guard": "pre_tool_call",
    "save": "on_session_finalize",
    "suggest": "pre_llm_call",
}
SCRIPTS = {
    "guard": "guard.py",
    "save": "save.py",
    "suggest": "suggest.py",
}
MARKER = ".hstack-hooks"
STATE_NAME = "hooks.json"


def say(message: str) -> None:
    print(f"hstack: {message}")


def die(message: str) -> None:
    print(f"hstack: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_with(raw: str) -> list[str]:
    names = [part.strip() for part in raw.split(",")] if raw else []
    if any(not name for name in names):
        die("empty hook name")
    chosen: list[str] = []
    for name in names:
        if name not in ALIASES:
            die(f"unknown hook: {name}")
        for hook in ALIASES[name]:
            if hook not in chosen:
                chosen.append(hook)
    return chosen


def command_home(home: str) -> str:
    return home.replace("\\", "/").rstrip("/")


def hook_command(home: str, hook: str) -> str:
    return f"{command_home(home)}/hstack/hooks/{SCRIPTS[hook]}"


def yaml_quote(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def entry_lines(home: str, hook: str) -> list[str]:
    command = yaml_quote(hook_command(home, hook))
    lines = [f"    # hstack:{hook}"]
    if hook == "guard":
        lines.append('    - matcher: "terminal"')
        lines.append(f"      command: {command}")
        lines.append("      timeout: 5")
        lines.append("      fail_closed: true")
    else:
        lines.append(f"    - command: {command}")
        lines.append("      timeout: 5")
    return lines


def top_level_name(line: str) -> str | None:
    if not line or line[0] in " \t#":
        return None
    head = line.split("#", 1)[0].rstrip()
    if ":" not in head:
        return None
    name, _rest = head.split(":", 1)
    if not name or " " in name or "\t" in name:
        return None
    return name


def find_block(lines: list[str], key: str) -> tuple[int, int] | None:
    start = None
    for index, line in enumerate(lines):
        if top_level_name(line) == key:
            if start is not None:
                die(f"config.yaml has more than one {key} key")
            start = index
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if top_level_name(lines[index]):
            end = index
            break
    return start, end


def normalize(text: str) -> str:
    if "\t" in text:
        die("refusing config.yaml that contains a tab")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def event_key(line: str) -> str | None:
    if not line.startswith("  ") or line.startswith("   ") or line.startswith("  #"):
        return None
    head = line.split("#", 1)[0].rstrip()
    if not head.endswith(":") or " " in head.strip():
        return None
    name = head.strip()[:-1]
    if not name:
        return None
    return name


def marker_at(line: str, hook: str) -> bool:
    return line.strip() == f"# hstack:{hook}"


def entry_span(lines: list[str], start: int) -> int:
    """Return the line after the hook entry that begins at start."""
    index = start + 1
    seen_item = False
    while index < len(lines):
        line = lines[index]
        if line.strip() == "":
            index += 1
            continue
        if marker_at(line, "guard") or marker_at(line, "save") or marker_at(line, "suggest"):
            break
        if line.startswith("    - "):
            if seen_item:
                break
            seen_item = True
            index += 1
            continue
        if line.startswith("      "):
            index += 1
            continue
        break
    while index > start + 1 and lines[index - 1].strip() == "":
        index -= 1
    return index


def find_marker(lines: list[str], start: int, end: int, hook: str) -> int | None:
    for index in range(start, end):
        if marker_at(lines[index], hook):
            return index
    return None


def ensure_nested(lines: list[str], start: int) -> None:
    rest = lines[start].split(":", 1)[1].split("#", 1)[0].strip()
    if rest:
        die("refusing hooks because the header is not a nested mapping")


def event_bounds(lines: list[str], start: int, end: int, event: str) -> tuple[int, int] | None:
    for index in range(start + 1, end):
        if event_key(lines[index]) != event:
            continue
        nxt = index + 1
        while nxt < end and event_key(lines[nxt]) is None:
            nxt += 1
        return index, nxt
    return None


def drop_empty_events(lines: list[str]) -> None:
    located = find_block(lines, "hooks")
    if located is None:
        return
    start, end = located
    empty = []
    index = start + 1
    while index < end:
        if event_key(lines[index]) is None:
            index += 1
            continue
        nxt = index + 1
        while nxt < end and event_key(lines[nxt]) is None:
            nxt += 1
        if not any(line.strip() for line in lines[index + 1 : nxt]):
            empty.append((index, nxt))
        index = nxt
    for begin, stop in reversed(empty):
        del lines[begin:stop]
        end -= stop - begin
    located = find_block(lines, "hooks")
    if located is None:
        return
    start, end = located
    if not any(line.strip() for line in lines[start + 1 : end]):
        del lines[start:end]


def render(text: str, home: str, hooks: list[str], remove: bool) -> str:
    text = normalize(text)
    if text and not text.endswith("\n"):
        text += "\n"
    lines = text.splitlines()
    located = find_block(lines, "hooks")
    if located is None:
        if remove or not hooks:
            return text
        block = ["hooks:"]
        for hook in hooks:
            block.append(f"  {EVENTS[hook]}:")
            block.extend(entry_lines(home, hook))
        return text + "\n".join(block) + "\n"
    start, end = located
    ensure_nested(lines, start)
    for hook in hooks:
        located = find_block(lines, "hooks")
        if located is None:
            if remove:
                break
            lines.extend(["hooks:"])
            located = find_block(lines, "hooks")
            if located is None:
                break
        start, end = located
        marker = find_marker(lines, start, end, hook)
        if remove:
            if marker is None:
                continue
            stop = entry_span(lines, marker)
            del lines[marker:stop]
            continue
        fresh = entry_lines(home, hook)
        if marker is not None:
            stop = entry_span(lines, marker)
            if lines[marker:stop] == fresh:
                continue
            lines[marker:stop] = fresh
            continue
        event = EVENTS[hook]
        located = find_block(lines, "hooks")
        if located is None:
            break
        start, end = located
        bounds = event_bounds(lines, start, end, event)
        if bounds is None:
            lines[end:end] = [f"  {event}:", *fresh]
            continue
        _event_at, insert_at = bounds
        lines[insert_at:insert_at] = fresh
    if remove:
        drop_empty_events(lines)
    joined = "\n".join(lines).strip("\n")
    if joined:
        joined += "\n"
    return joined


def read_state(path: Path) -> dict:
    if not path.is_file():
        return {"hooks": [], "created_config": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"cannot read hook state: {exc}")
    hooks = data.get("hooks")
    if not isinstance(hooks, list) or any(item not in HOOKS for item in hooks):
        die("hook state is invalid")
    return {"hooks": list(hooks), "created_config": bool(data.get("created_config"))}


def write_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def source_hooks(source: Path) -> Path:
    direct = source / "hooks"
    if (direct / "guard.py").is_file():
        return direct
    nested = source / "hooks"
    die(f"missing hooks in {source}")
    return nested


def copy_hooks(source: Path, dest: Path, hooks: list[str], dry_run: bool) -> None:
    origin = source_hooks(source)
    names = ["hstack_hook.py", *[SCRIPTS[hook] for hook in hooks]]
    if dry_run:
        for name in names:
            say(f"dry-run: would copy hooks/{name} to {dest / name}")
        return
    if dest.is_symlink():
        die(f"refusing to follow symlink {dest}")
    dest.mkdir(parents=True, exist_ok=True)
    for name in names:
        src = origin / name
        if not src.is_file():
            die(f"missing hook file {src}")
        target = dest / name
        shutil.copyfile(src, target)
        target.chmod(0o755)


def copy_self(dest_root: Path, dry_run: bool) -> None:
    target = dest_root / "apply_hooks.py"
    if dry_run:
        say(f"dry-run: would copy apply_hooks.py to {target}")
        return
    shutil.copyfile(Path(__file__).resolve(), target)
    target.chmod(0o644)


def backup_config(config: Path, root: Path) -> None:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    dest = root / "hstack" / "backups" / f"config.yaml.{stamp}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(config, dest)
    say(f"backed up config.yaml to {dest}")


def remove_scripts(dest: Path, hooks: list[str], dry_run: bool) -> None:
    names = [SCRIPTS[hook] for hook in hooks]
    if not dest.exists():
        return
    for name in names:
        target = dest / name
        if dry_run:
            say(f"dry-run: would remove {target}")
            continue
        if target.is_file() and not target.is_symlink():
            target.unlink()
    if dry_run:
        return
    remaining = [hook for hook in HOOKS if (dest / SCRIPTS[hook]).exists()]
    if not remaining:
        shared = dest / "hstack_hook.py"
        if shared.is_file() and not shared.is_symlink():
            shared.unlink()
    if dest.is_dir() and not any(dest.iterdir()):
        dest.rmdir()


def prune_root(root: Path) -> None:
    if not root.is_dir():
        return
    backups = root / "backups"
    if backups.is_dir() and not any(backups.iterdir()):
        backups.rmdir()
    if root.is_dir() and not any(root.iterdir()):
        root.rmdir()


def apply(root: Path, source: Path | None, hooks: list[str], remove: bool, dry_run: bool, command_home: str | None = None) -> None:
    if root.is_symlink():
        die(f"refusing to follow symlink {root}")
    home = command_home or root.as_posix()
    dest_root = root / "hstack"
    dest_hooks = dest_root / "hooks"
    state_path = dest_root / STATE_NAME
    marker = dest_root / MARKER
    config = root / "config.yaml"
    state = read_state(state_path) if state_path.is_file() else {"hooks": [], "created_config": False}
    targets = hooks
    if remove and not targets:
        targets = list(state["hooks"]) or list(HOOKS)
    if not targets and not remove:
        return
    if remove and dest_root.exists() and not marker.is_file() and not state_path.is_file() and not config.is_file():
        say("no hooks to remove")
        return
    if not remove:
        if source is None:
            die("missing --source")
        copy_hooks(source, dest_hooks, targets, dry_run)
        copy_self(dest_root, dry_run)
    text = config.read_text(encoding="utf-8") if config.is_file() else ""
    updated = render(text, home, targets, remove)
    if dry_run:
        if updated != (text if text.endswith("\n") or text == "" else text + "\n") and not (updated == text):
            verb = "remove" if remove else "write"
            say(f"dry-run: would {verb} hooks {', '.join(targets)}")
        elif updated == text or (text == "" and updated.strip() == ""):
            say(f"dry-run: hooks unchanged ({', '.join(targets)})")
        else:
            say(f"dry-run: would {'remove' if remove else 'write'} hooks {', '.join(targets)}")
        return
    changed = updated != text and not (text == "" and updated == "")
    if text and not text.endswith("\n") and updated == text + "\n":
        changed = updated != text
    if config.is_file() and updated != text:
        backup_config(config, root)
        config.write_text(updated, encoding="utf-8")
        say(("removed" if remove else "wrote") + " hooks " + ", ".join(targets))
    elif not config.is_file() and updated.strip():
        config.parent.mkdir(parents=True, exist_ok=True)
        config.write_text(updated, encoding="utf-8")
        state["created_config"] = True
        say("wrote hooks " + ", ".join(targets))
    else:
        say("hooks unchanged (" + ", ".join(targets) + ")")
    if remove:
        remove_scripts(dest_hooks, targets, dry_run=False)
        state["hooks"] = [hook for hook in state["hooks"] if hook not in targets]
        if state["created_config"] and config.is_file() and not config.read_text(encoding="utf-8").strip():
            config.unlink()
            state["created_config"] = False
            say(f"removed empty {config}")
        if state["hooks"]:
            write_state(state_path, state)
        else:
            if state_path.is_file():
                state_path.unlink()
            if marker.is_file() and not marker.is_symlink():
                marker.unlink()
            self_copy = dest_root / "apply_hooks.py"
            if self_copy.is_file() and not self_copy.is_symlink():
                self_copy.unlink()
            backups = dest_root / "backups"
            if backups.is_dir():
                for child in backups.iterdir():
                    if child.is_file() and child.name.startswith("config.yaml."):
                        child.unlink()
            prune_root(dest_root)
        return
    if not marker.exists():
        dest_root.mkdir(parents=True, exist_ok=True)
        marker.write_text("managed-by: hstack install.sh\n", encoding="utf-8")
    state["hooks"] = list(dict.fromkeys([*state["hooks"], *targets]))
    write_state(state_path, state)


def main() -> int:
    parser = argparse.ArgumentParser(prog="apply_hooks")
    parser.add_argument("--hermes-home")
    parser.add_argument("--source")
    parser.add_argument("--with", dest="with_names", default="")
    parser.add_argument("--command-home", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    if args.validate:
        parse_with(args.with_names or "hermes-hooks")
        return 0
    if not args.hermes_home:
        die("missing --hermes-home")
    requested = parse_with(args.with_names) if args.with_names else []
    if args.uninstall and not requested:
        requested = []
    apply(
        Path(args.hermes_home),
        Path(args.source) if args.source else None,
        requested,
        remove=args.uninstall,
        dry_run=args.dry_run,
        command_home=args.command_home or None,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
