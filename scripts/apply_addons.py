#!/usr/bin/env python3
"""Enable or remove optional HStack addons inside a Hermes home.

The default skill install does not call this. install.sh does, and only
when the user passed --with. MCP entries are added under mcp_servers with
an hstack_ prefix. Helper scripts are copied into <home>/hstack/bin.
Nothing here downloads a package or writes a token.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ADDONS = ("browser", "github", "docs", "search", "perf", "test", "security", "trail")

MCP = {
    "browser": (
        "hstack_playwright",
        '  hstack_playwright:\n'
        '    command: "npx"\n'
        '    args: ["-y", "@playwright/mcp@0.0.83"]\n',
    ),
    "docs": (
        "hstack_context7",
        '  hstack_context7:\n'
        '    url: "https://mcp.context7.com/mcp"\n',
    ),
    "search": (
        "hstack_deepwiki",
        '  hstack_deepwiki:\n'
        '    url: "https://mcp.deepwiki.com/mcp"\n',
    ),
}

FILES = {
    "browser": ("hstack-visdiff",),
    "github": ("hstack-pr",),
    "perf": ("hstack-bench",),
    "test": ("hstack-test",),
    "security": ("hstack-scan",),
    "trail": ("hstack-decisions",),
}

MARKER_NAME = ".hstack-addons"


def say(message: str) -> None:
    print(f"hstack: {message}")


def die(message: str) -> None:
    print(f"hstack: {message}", file=sys.stderr)
    raise SystemExit(1)


def parse_with(raw: str) -> list[str]:
    names = [part.strip() for part in raw.split(",")] if raw else []
    if any(not name for name in names):
        die("empty addon name")
    unknown = [name for name in names if name not in ADDONS]
    if unknown:
        die("unknown addon: " + ", ".join(unknown))
    seen: list[str] = []
    for name in names:
        if name not in seen:
            seen.append(name)
    return seen


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


def server_key_line(line: str, key: str) -> bool:
    return line.startswith("  ") and not line.startswith("   ") and line.split(":", 1)[0].strip() == key and line.rstrip().endswith(":")


def normalize_config(text: str) -> str:
    if "\t" in text:
        die("refusing config.yaml that contains a tab")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def upsert_server(text: str, key: str, block: str) -> str:
    text = normalize_config(text)
    lines = text.splitlines()
    located = find_block(lines, "mcp_servers")
    block_lines = block.splitlines()
    if located is None:
        if text and not text.endswith("\n"):
            text += "\n"
        if text and not text.endswith("\n"):
            text += "\n"
        addition = "mcp_servers:\n" + block
        if text and not text.endswith("\n"):
            text += "\n"
        return text + addition
    start, end = located
    header_rest = lines[start].split(":", 1)[1].split("#", 1)[0].strip()
    if header_rest:
        die("refusing mcp_servers because the header is not a nested mapping")
    for index in range(start + 1, end):
        if server_key_line(lines[index], key):
            return text if text.endswith("\n") or text == "" else text + "\n"
    insert_at = start + 1
    new_lines = lines[:insert_at] + block_lines + lines[insert_at:]
    joined = "\n".join(new_lines)
    if text.endswith("\n") or joined:
        joined += "\n"
    return joined


def remove_server(text: str, key: str) -> str:
    text = normalize_config(text)
    lines = text.splitlines()
    located = find_block(lines, "mcp_servers")
    if located is None:
        return text if text.endswith("\n") or text == "" else text + ("\n" if text else "")
    start, end = located
    remove_from = None
    for index in range(start + 1, end):
        if server_key_line(lines[index], key):
            remove_from = index
            break
    if remove_from is None:
        return text if text.endswith("\n") or not text else text + "\n"
    remove_to = end
    for index in range(remove_from + 1, end):
        if server_key_line(lines[index], lines[index].split(":", 1)[0].strip()):
            remove_to = index
            break
    kept = lines[:remove_from] + lines[remove_to:]
    # Drop an mcp_servers header that no longer has a child key.
    located = find_block(kept, "mcp_servers")
    if located is not None:
        block_start, block_end = located
        has_child = any(
            line.startswith("  ") and line.strip() and not line.strip().startswith("#")
            for line in kept[block_start + 1 : block_end]
        )
        if not has_child:
            kept = kept[:block_start] + kept[block_end:]
    joined = "\n".join(kept).strip("\n")
    if joined:
        joined += "\n"
    return joined


def read_state(path: Path) -> dict:
    if not path.is_file():
        return {"addons": [], "created_config": False}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        die(f"cannot read addon state: {exc}")
    addons = data.get("addons")
    if not isinstance(addons, list) or any(not isinstance(item, str) for item in addons):
        die("addon state is invalid")
    return {"addons": list(addons), "created_config": bool(data.get("created_config"))}


def write_state(path: Path, state: dict) -> None:
    path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def hooks_owned(dest_root: Path) -> bool:
    return (dest_root / ".hstack-hooks").is_file() or (dest_root / "hooks.json").is_file()


def ensure_home_dir(dest_root: Path, dry_run: bool) -> None:
    if dest_root.is_symlink():
        die(f"refusing to follow symlink {dest_root}")
    marker = dest_root / MARKER_NAME
    if dest_root.exists() and not dest_root.is_dir():
        die(f"refusing {dest_root} (not a directory)")
    if (
        dest_root.is_dir()
        and any(dest_root.iterdir())
        and not marker.is_file()
        and not hooks_owned(dest_root)
    ):
        die(f"refusing to overwrite non-empty {dest_root} (not an HStack addon install)")
    if dry_run:
        return
    dest_root.mkdir(parents=True, exist_ok=True)
    marker.write_text("managed-by: hstack install.sh\n", encoding="utf-8")


def copy_files(source: Path, dest_bin: Path, names: tuple[str, ...], dry_run: bool) -> None:
    for name in names:
        src = source / "bin" / name
        target = dest_bin / name
        if dry_run:
            say(f"dry-run: would copy bin/{name} to {target}")
            continue
        if not src.is_file():
            die(f"missing helper {src}")
        dest_bin.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        target.chmod(0o755)


def copy_self(dest_root: Path, dry_run: bool) -> None:
    target = dest_root / "apply_addons.py"
    if dry_run:
        say(f"dry-run: would copy apply_addons.py to {target}")
        return
    shutil.copyfile(Path(__file__).resolve(), target)
    target.chmod(0o644)


def remove_files(dest_bin: Path, names: tuple[str, ...], dry_run: bool) -> None:
    for name in names:
        target = dest_bin / name
        if dry_run:
            say(f"dry-run: would remove {target}")
            continue
        if target.is_file() and not target.is_symlink():
            target.unlink()


def say_mcp(dry_run: bool, remove: bool, key: str) -> None:
    if dry_run and remove:
        say(f"dry-run: would remove mcp server {key}")
    elif dry_run:
        say(f"dry-run: would write mcp server {key}")
    elif remove:
        say(f"removed mcp server {key}")
    else:
        say(f"wrote mcp server {key}")


def apply_config(config: Path, names: list[str], remove: bool, state: dict, dry_run: bool) -> None:
    keys = [(addon, MCP[addon][0], MCP[addon][1]) for addon in names if addon in MCP]
    if not keys:
        return
    existed = config.is_file()
    text = config.read_text(encoding="utf-8") if existed else ""
    updated = text
    for _addon, key, block in keys:
        updated = remove_server(updated, key) if remove else upsert_server(updated, key, block)
        say_mcp(dry_run, remove, key)
    if dry_run:
        return
    if not updated.strip():
        if existed and state.get("created_config"):
            config.unlink()
            state["created_config"] = False
        elif existed and updated != text:
            config.write_text("", encoding="utf-8")
        return
    if not existed:
        state["created_config"] = True
        config.parent.mkdir(parents=True, exist_ok=True)
    if updated != text or not existed:
        config.write_text(updated if updated.endswith("\n") else updated + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(prog="apply_addons")
    parser.add_argument("--hermes-home")
    parser.add_argument("--source")
    parser.add_argument("--with", dest="with_names", default="")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--validate", action="store_true")
    args = parser.parse_args()
    requested = parse_with(args.with_names)
    if args.validate:
        return 0
    if not args.hermes_home:
        die("missing --hermes-home")
    home = Path(args.hermes_home)
    if home.is_symlink():
        die(f"refusing to follow symlink {home}")
    dest_root = home / "hstack"
    dest_bin = dest_root / "bin"
    state_path = dest_root / "addons.json"
    config = home / "config.yaml"
    uninstall_all = args.uninstall and not requested
    if args.uninstall and not (dest_root / MARKER_NAME).is_file():
        say("no addons to remove")
        return 0
    if (
        dest_root.exists()
        and not (dest_root / MARKER_NAME).is_file()
        and any(dest_root.iterdir())
        and not hooks_owned(dest_root)
    ):
        die(f"refusing to overwrite non-empty {dest_root} (not an HStack addon install)")
    state = read_state(state_path) if state_path.is_file() else {"addons": [], "created_config": False}
    if uninstall_all:
        targets = list(dict.fromkeys([*state["addons"], *ADDONS]))
    else:
        targets = requested
    if not targets and not args.uninstall:
        return 0
    if not args.uninstall:
        if not args.source:
            die("missing --source")
        source = Path(args.source)
        ensure_home_dir(dest_root, args.dry_run)
        for name in targets:
            say(f"{'dry-run: would enable' if args.dry_run else 'enabling'} addon {name}")
            copy_files(source, dest_bin, FILES.get(name, ()), args.dry_run)
        copy_self(dest_root, args.dry_run)
        apply_config(config, targets, remove=False, state=state, dry_run=args.dry_run)
        if not args.dry_run:
            merged = list(dict.fromkeys([*state["addons"], *targets]))
            state["addons"] = merged
            write_state(state_path, state)
        return 0
    # uninstall
    if not (dest_root / MARKER_NAME).is_file() and dest_root.exists():
        die(f"refusing to remove {dest_root} (missing {MARKER_NAME})")
    real_targets = targets if not uninstall_all else list(state["addons"])
    if uninstall_all and not real_targets and not dest_root.exists():
        say("no addons to remove")
        return 0
    for name in real_targets:
        say(f"{'dry-run: would remove' if args.dry_run else 'removing'} addon {name}")
        remove_files(dest_bin, FILES.get(name, ()), args.dry_run)
    apply_config(config, real_targets if real_targets else [], remove=True, state=state, dry_run=args.dry_run)
    remaining = [name for name in state["addons"] if name not in real_targets]
    script_copy = dest_root / "apply_addons.py"
    if args.dry_run:
        if not remaining:
            say(f"dry-run: would remove {script_copy}")
        return 0
    state["addons"] = remaining
    if remaining:
        write_state(state_path, state)
        return 0
    if script_copy.is_file() and not script_copy.is_symlink():
        script_copy.unlink()
    if state_path.is_file():
        state_path.unlink()
    if dest_bin.is_dir() and not any(dest_bin.iterdir()):
        dest_bin.rmdir()
    marker = dest_root / MARKER_NAME
    if marker.is_file():
        marker.unlink()
    if dest_root.is_dir() and not any(dest_root.iterdir()):
        dest_root.rmdir()
    say(f"removed addons from {home}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
