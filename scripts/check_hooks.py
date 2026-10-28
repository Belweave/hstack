#!/usr/bin/env python3
"""Hooks install, uninstall, and idempotency on linux, macOS, and Windows paths."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "hooks"))
import apply_hooks  # noqa: E402
import hstack_hook  # noqa: E402


def fail(message: str) -> None:
    print(f"check_hooks: {message}", file=sys.stderr)
    raise SystemExit(1)


def config_text(home: str) -> str:
    foreign = """model: local
hooks:
  pre_tool_call:
    - matcher: "write_file"
      command: "/usr/bin/other"
  post_tool_call:
    - command: "/usr/bin/log"
mcp_servers:
  other:
    url: "https://example.com/mcp"
"""
    once = apply_hooks.render(foreign, home, ["guard", "save", "suggest"], remove=False)
    twice = apply_hooks.render(once, home, ["guard", "save", "suggest"], remove=False)
    if once != twice:
        fail(f"second render changed {home}")
    if once.count("# hstack:guard") != 1:
        fail(f"guard was duplicated for {home}")
    command = apply_hooks.hook_command(home, "guard")
    if command not in once:
        fail(f"guard command missing for {home}: {command}")
    if "/usr/bin/other" not in once or "/usr/bin/log" not in once:
        fail(f"foreign hook was dropped for {home}")
    if "example.com" not in once:
        fail(f"foreign server was dropped for {home}")
    removed = apply_hooks.render(once, home, ["guard"], remove=True)
    if "# hstack:guard" in removed or command in removed:
        fail(f"guard survived uninstall for {home}")
    if "# hstack:save" not in removed:
        fail(f"uninstall guard removed save for {home}")
    cleared = apply_hooks.render(removed, home, ["save", "suggest"], remove=True)
    if "# hstack:" in cleared:
        fail(f"hook marker survived full removal for {home}")
    if "/usr/bin/other" not in cleared or "/usr/bin/log" not in cleared or "example.com" not in cleared:
        fail(f"foreign config was damaged for {home}")
    only = apply_hooks.render("", home, ["guard", "save", "suggest"], remove=False)
    gone = apply_hooks.render(only, home, ["guard", "save", "suggest"], remove=True)
    if "hooks:" in gone or gone.strip():
        fail(f"empty hooks block survived for {home}")
    return once


def live(root: Path, command_home: str, hooks: list[str]) -> None:
    source = ROOT
    apply_hooks.apply(root, source, hooks, remove=False, dry_run=True, command_home=command_home)
    if (root / "config.yaml").exists():
        fail(f"dry-run wrote config for {command_home}")
    apply_hooks.apply(root, source, hooks, remove=False, dry_run=False, command_home=command_home)
    config = (root / "config.yaml").read_text(encoding="utf-8")
    backups = list((root / "hstack" / "backups").glob("config.yaml.*")) if (root / "hstack" / "backups").exists() else []
    # First write creates the file, so there is no previous config to back up.
    apply_hooks.apply(root, source, hooks, remove=False, dry_run=False, command_home=command_home)
    backups_after = list((root / "hstack" / "backups").glob("config.yaml.*")) if (root / "hstack" / "backups").exists() else []
    if len(backups_after) != len(backups):
        fail(f"idempotent install took another backup for {command_home}")
    again = (root / "config.yaml").read_text(encoding="utf-8")
    if again != config:
        fail(f"idempotent install changed config for {command_home}")
    for hook in hooks:
        if again.count(f"# hstack:{hook}") != 1:
            fail(f"{hook} was not singular for {command_home}")
        if apply_hooks.hook_command(command_home, hook) not in again:
            fail(f"{hook} command path mismatch for {command_home}")
        if not (root / "hstack" / "hooks" / apply_hooks.SCRIPTS[hook]).is_file():
            fail(f"missing shim {hook} for {command_home}")
    apply_hooks.apply(root, source, hooks, remove=True, dry_run=False, command_home=command_home)
    if (root / "config.yaml").exists() and (root / "config.yaml").read_text(encoding="utf-8").strip():
        fail(f"uninstall left config for {command_home}")
    if (root / "hstack" / "hooks").exists():
        fail(f"uninstall left hook scripts for {command_home}")


def foreign_backup(root: Path) -> None:
    root.mkdir(parents=True, exist_ok=True)
    original = 'model: local\nhooks:\n  post_tool_call:\n    - command: "/usr/bin/log"\n'
    (root / "config.yaml").write_text(original, encoding="utf-8")
    apply_hooks.apply(root, ROOT, ["guard"], remove=False, dry_run=False, command_home=root.as_posix())
    backups = list((root / "hstack" / "backups").glob("config.yaml.*"))
    if len(backups) != 1:
        fail(f"expected one backup, found {len(backups)}")
    if backups[0].read_text(encoding="utf-8") != original:
        fail("backup is not the original config")
    apply_hooks.apply(root, ROOT, ["guard"], remove=False, dry_run=False, command_home=root.as_posix())
    if len(list((root / "hstack" / "backups").glob("config.yaml.*"))) != 1:
        fail("second install added a backup")
    text = (root / "config.yaml").read_text(encoding="utf-8")
    if "/usr/bin/log" not in text or "# hstack:guard" not in text:
        fail("guard install damaged a foreign hook")
    apply_hooks.apply(root, ROOT, ["guard"], remove=True, dry_run=False, command_home=root.as_posix())
    left = (root / "config.yaml").read_text(encoding="utf-8")
    if "# hstack:" in left or "hstack/hooks" in left:
        fail("guard uninstall left its entry")
    if "/usr/bin/log" not in left:
        fail("guard uninstall removed the foreign hook")


def installer() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        home = Path(tmp) / "linux"
        env = {**os.environ, "HERMES_HOME": str(home)}
        subprocess.run(["sh", str(ROOT / "install.sh")], cwd=ROOT, env=env, check=True)
        if (home / "config.yaml").exists():
            fail("default install wrote config.yaml")
        if (home / "hstack" / "hooks").exists():
            fail("default install wrote hooks")
        subprocess.run(["sh", str(ROOT / "install.sh"), "--with", "hermes-hooks"], cwd=ROOT, env=env, check=True)
        text = (home / "config.yaml").read_text(encoding="utf-8")
        for hook in ("guard", "save", "suggest"):
            if text.count(f"# hstack:{hook}") != 1:
                fail(f"installer missing {hook}")
        before = text
        subprocess.run(["sh", str(ROOT / "install.sh"), "--with", "hermes-hooks"], cwd=ROOT, env=env, check=True)
        if (home / "config.yaml").read_text(encoding="utf-8") != before:
            fail("installer was not idempotent")
        subprocess.run(["sh", str(ROOT / "install.sh"), "--uninstall", "--with", "hermes-hooks-guard"], cwd=ROOT, env=env, check=True)
        left = (home / "config.yaml").read_text(encoding="utf-8")
        if "# hstack:guard" in left or "hooks/guard.py" in left:
            fail("subset uninstall left the guard")
        if "# hstack:save" not in left or "# hstack:suggest" not in left:
            fail("subset uninstall removed another hook")
        if not (home / "skills" / "hstack" / "hstack" / "SKILL.md").is_file():
            fail("hook uninstall removed skills")
        subprocess.run(["sh", str(ROOT / "install.sh"), "--with", "browser,hermes-hooks-guard"], cwd=ROOT, env=env, check=True)
        both = (home / "config.yaml").read_text(encoding="utf-8")
        if "hstack_playwright" not in both or "# hstack:guard" not in both:
            fail("combined addon and hook install missed one")
        subprocess.run(["sh", str(ROOT / "install.sh"), "--uninstall"], cwd=ROOT, env=env, check=True)
        if (home / "skills" / "hstack").exists():
            fail("full uninstall left skills")
        if (home / "config.yaml").exists():
            fail("full uninstall left a config this installer created")
        state = home / "hstack" / "hooks.json"
        if state.exists():
            fail(f"hook state remained: {state.read_text()}")


def behavior() -> None:
    blocked = hstack_hook.guard(json.dumps({"tool_name": "terminal", "tool_input": {"command": "rm -rf /"}}))
    if blocked != 0:
        fail("guard should block with JSON, not a crash")
    allowed = hstack_hook.guard(json.dumps({"tool_name": "terminal", "tool_input": {"command": "rm -rf ./build"}}))
    if allowed != 0:
        fail("guard blocked a local rm")
    home = Path(tempfile.mkdtemp())
    os.environ["HERMES_HOME"] = str(home)
    hstack_hook.save(json.dumps({"session_id": "abc", "extra": {"platform": "cli", "user_message": "secret-token"}}))
    log = (home / "hstack" / "session-log.tsv").read_text(encoding="utf-8")
    if "abc" not in log or "secret-token" in log:
        fail("session log saved the wrong fields")
    injected = hstack_hook.suggest(
        json.dumps({"extra": {"is_first_turn": True, "user_message": "the export is broken"}})
    )
    if injected != 0:
        fail("suggest failed")
    later = hstack_hook.suggest(
        json.dumps({"extra": {"is_first_turn": False, "user_message": "the export is broken"}})
    )
    if later != 0:
        fail("suggest failed on a later turn")


def main() -> int:
    for home in ("/home/dev/.hermes", "/Users/dev/.hermes", "C:/Users/dev/.hermes"):
        config_text(home)
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        live(base / "linux", "/home/dev/.hermes", ["guard", "save", "suggest"])
        live(base / "macos", "/Users/dev/.hermes", ["guard", "save", "suggest"])
        live(base / "windows", "C:/Users/dev/.hermes", ["guard", "save", "suggest"])
        foreign_backup(base / "foreign")
    installer()
    behavior()
    print("check_hooks: linux, macos-sim, and windows paths ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
