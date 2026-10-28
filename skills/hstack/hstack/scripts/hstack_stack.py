#!/usr/bin/env python3
"""Detect, decline, or install an external stack.

Detection only reads files. Install downloads only when --yes is present,
checks the registry sha256 before extract, and writes outside the HStack
skill tree. It does not run the other project.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tarfile
import tempfile
import urllib.request
from pathlib import Path


SESSION_RE = re.compile(r"^[A-Za-z0-9._-]{1,64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
MAX_BYTES = 100 * 1024 * 1024


def say(message: str) -> None:
    print(message)


def die(message: str, code: int = 1) -> None:
    print(f"hstack-stack: {message}", file=sys.stderr)
    raise SystemExit(code)


def hermes_home(raw: str | None) -> Path:
    if raw:
        return Path(raw)
    env = os.environ.get("HERMES_HOME")
    if env:
        return Path(env)
    return Path.home() / ".hermes"


def user_home(raw: str | None) -> Path:
    if raw:
        return Path(raw)
    return Path.home()


def default_registry() -> Path:
    return Path(__file__).resolve().parents[1] / "references" / "stacks.md"


def load_registry(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```json\n(.*?)\n```", text, re.DOTALL)
    if not match:
        die(f"registry has no json block: {path}")
    try:
        data = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        die(f"registry json is invalid: {exc}")
    stacks = data.get("stacks")
    if not isinstance(stacks, list) or not stacks:
        die("registry has no stacks")
    return stacks


def stack_by_id(stacks: list[dict], stack_id: str) -> dict:
    for item in stacks:
        if item.get("id") == stack_id:
            return item
    die(f"unknown stack: {stack_id}")
    raise AssertionError


def check_session(session: str) -> str:
    if not SESSION_RE.match(session or ""):
        die("session id must be 1-64 letters, numbers, dots, underscores, or dashes")
    return session


def decline_path(home: Path, session: str) -> Path:
    return home / "hstack" / "declines" / session


def read_declines(home: Path, session: str | None) -> set[str]:
    if not session:
        return set()
    path = decline_path(home, session)
    if not path.is_file():
        return set()
    return {line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()}


def is_symlink(path: Path) -> bool:
    return path.is_symlink()


def skill_file(path: Path) -> bool:
    return path.is_file() and not path.is_symlink()


def walk_suffix(root: Path, suffix: str, max_depth: int = 8) -> bool:
    if not root.is_dir() or root.is_symlink():
        return False
    needle = tuple(suffix.strip("/").split("/"))
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        current = Path(dirpath)
        rel_parts = current.relative_to(root).parts
        if len(rel_parts) > max_depth:
            dirnames[:] = []
            continue
        dirnames[:] = [
            name
            for name in dirnames
            if name not in {".git", "node_modules"} and not (current / name).is_symlink()
        ]
        if "SKILL.md" not in filenames:
            continue
        parts = current.parts
        if len(parts) >= len(needle) - 1 and parts[-(len(needle) - 1) :] == needle[:-1]:
            candidate = current / needle[-1]
            if skill_file(candidate):
                return True
    return False


def pair_present(root: Path) -> bool:
    if not root.is_dir() or root.is_symlink():
        return False
    levels = [root]
    try:
        children = [child for child in root.iterdir() if child.is_dir() and not child.is_symlink()]
    except OSError:
        return False
    levels.extend(children[:80])
    for child in children[:40]:
        try:
            levels.extend(grand for grand in child.iterdir() if grand.is_dir() and not grand.is_symlink())
        except OSError:
            continue
    for directory in levels:
        left = directory / "leaving-pr-comments" / "SKILL.md"
        right = directory / "sol-loop" / "SKILL.md"
        if skill_file(left) and skill_file(right):
            return True
    return False


def gbrain_config(home: Path) -> Path:
    parent = os.environ.get("GBRAIN_HOME")
    if parent:
        return Path(parent) / ".gbrain" / "config.json"
    return home / ".gbrain" / "config.json"


def mcp_gbrain(config: Path) -> bool:
    if not config.is_file() or config.is_symlink():
        return False
    lines = config.read_text(encoding="utf-8").splitlines()
    inside = False
    for line in lines:
        if line.startswith("mcp_servers:"):
            inside = True
            continue
        if inside and line and not line.startswith(" ") and not line.startswith("#"):
            inside = False
        if inside and line.startswith("  gbrain:"):
            return True
    return False


def gbrain_skills(roots: list[Path]) -> bool:
    for root in roots:
        if not root.is_dir() or root.is_symlink():
            continue
        for dirpath, dirnames, _filenames in os.walk(root, followlinks=False):
            current = Path(dirpath)
            depth = len(current.relative_to(root).parts)
            if depth > 4:
                dirnames[:] = []
                continue
            dirnames[:] = [name for name in dirnames if not (current / name).is_symlink()]
            if skill_file(current / "gbrain-upgrade" / "SKILL.md") and skill_file(current / "brain-ops" / "SKILL.md"):
                return True
    return False


def receipt_installed(hermes: Path, stack_id: str, commit: str) -> bool:
    receipt = hermes / "hstack" / "external" / stack_id / commit / ".hstack-external"
    return receipt.is_file() and not receipt.is_symlink()


def gstack_installed(hermes: Path, home: Path) -> bool:
    category = hermes / "skills" / "gstack"
    if category.is_dir() and not category.is_symlink():
        for child in category.iterdir():
            if child.is_dir() and skill_file(child / "SKILL.md"):
                return True
    for base in (home / ".claude" / "skills" / "gstack", home / ".codex" / "skills" / "gstack"):
        marker = base / "bin" / "gstack-state-root.sh"
        if marker.is_file():
            return True
    return False


def pstack_installed(home: Path) -> bool:
    for root in (home / ".cursor" / "plugins", home / ".claude" / "plugins"):
        if walk_suffix(root, "skills/poteto-mode/SKILL.md"):
            return True
    return False


def tstack_installed(hermes: Path, home: Path) -> bool:
    roots = [
        home / ".claude" / "skills",
        home / ".codex" / "skills",
        home / ".agents" / "skills",
        hermes / "skills",
    ]
    return any(pair_present(root) for root in roots)


def gbrain_installed(hermes: Path, home: Path) -> bool:
    config = gbrain_config(home)
    if config.is_file() and not config.is_symlink():
        return True
    if mcp_gbrain(hermes / "config.yaml"):
        return True
    return gbrain_skills([hermes / "skills", home / ".claude" / "skills", home / ".codex" / "skills"])


def installed(stack_id: str, hermes: Path, home: Path, commit: str) -> bool:
    if receipt_installed(hermes, stack_id, commit):
        return True
    if stack_id == "gstack":
        return gstack_installed(hermes, home)
    if stack_id == "pstack":
        return pstack_installed(home)
    if stack_id == "tstack":
        return tstack_installed(hermes, home)
    if stack_id == "gbrain":
        return gbrain_installed(hermes, home)
    return False


def script_path() -> str:
    return str(Path(__file__).resolve())


def detect(stacks: list[dict], hermes: Path, home: Path, session: str | None) -> int:
    declined = read_declines(hermes, session)
    for item in stacks:
        stack_id = str(item["id"])
        commit = str(item["commit"])
        present = installed(stack_id, hermes, home, commit)
        refused = stack_id in declined
        fields = [
            f"id={stack_id}",
            f"installed={'yes' if present else 'no'}",
            f"declined={'yes' if refused else 'no'}",
            f"license={item.get('license', '')}",
            f"commit={commit}",
            f"good_at={item.get('good_at', '')}",
        ]
        say(" ".join(fields))
        if not present and not refused and session:
            say(
                "install_command="
                + script_path()
                + f" install {stack_id} --yes --session {session}"
            )
    return 0


def decline(stack_id: str, hermes: Path, session: str) -> int:
    path = decline_path(hermes, session)
    path.parent.mkdir(parents=True, exist_ok=True)
    current = read_declines(hermes, session)
    current.add(stack_id)
    path.write_text("".join(f"{item}\n" for item in sorted(current)), encoding="utf-8")
    say(f"declined id={stack_id} session={session}")
    return 0


def safe_members(archive: tarfile.TarFile) -> list[tarfile.TarInfo]:
    members = []
    for member in archive.getmembers():
        name = member.name
        if not name or name.startswith("/") or name.startswith("\\"):
            die(f"archive member is absolute: {name}")
        parts = Path(name).parts
        if ".." in parts:
            die(f"archive member contains ..: {name}")
        if member.issym() or member.islnk() or member.isdev() or member.isfifo():
            die(f"archive member is a link or special file: {name}")
        members.append(member)
    return members


def download(url: str, dest: Path) -> None:
    parsed = urllib.request.urlparse(url)
    if parsed.scheme == "http" and parsed.hostname not in {"127.0.0.1", "localhost"}:
        die("refusing a non-local http archive")
    if parsed.scheme not in {"https", "http"}:
        die("refusing archive URL")
    request = urllib.request.Request(url, headers={"User-Agent": "hstack-stack"})
    with urllib.request.urlopen(request, timeout=120) as response, dest.open("wb") as handle:
        total = 0
        while True:
            chunk = response.read(1024 * 256)
            if not chunk:
                break
            total += len(chunk)
            if total > MAX_BYTES:
                die("archive is larger than the limit")
            handle.write(chunk)


def install(item: dict, hermes: Path, session: str, yes: bool) -> int:
    stack_id = str(item["id"])
    if not yes:
        die("refusing to download without --yes", 2)
    if stack_id in read_declines(hermes, session):
        die(f"refusing to install {stack_id}; this session declined it", 2)
    commit = str(item["commit"])
    digest = str(item["sha256"]).lower()
    url = str(item["archive"])
    if not COMMIT_RE.match(commit) or not re.fullmatch(r"[0-9a-f]{64}", digest):
        die("registry pin is not a commit and sha256")
    dest = hermes / "hstack" / "external" / stack_id / commit
    receipt = dest / ".hstack-external"
    if receipt.is_file():
        text = receipt.read_text(encoding="utf-8")
        if f"sha256={digest}" in text and f"commit={commit}" in text:
            say(f"already installed id={stack_id} path={dest}")
            say("handoff: files are outside HStack skills. Do not read them until the user says yes.")
            return 0
    work = Path(tempfile.mkdtemp(prefix="hstack-stack-"))
    try:
        archive_path = work / "stack.tar.gz"
        download(url, archive_path)
        actual = hashlib.sha256(archive_path.read_bytes()).hexdigest()
        if actual != digest:
            die("checksum mismatch")
        magic = archive_path.read_bytes()[:2]
        if magic != b"\x1f\x8b":
            die("download was not a gzip archive")
        with tarfile.open(archive_path, "r:gz") as archive:
            members = safe_members(archive)
            archive.extractall(work / "tree", members=members)
        extracted = work / "tree"
        tops = [child for child in extracted.iterdir() if child.is_dir()]
        if len(tops) != 1:
            die("expected one top-level directory in the archive")
        if dest.exists():
            shutil.rmtree(dest)
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tops[0]), str(dest))
        receipt.write_text(
            f"id={stack_id}\ncommit={commit}\nsha256={digest}\n",
            encoding="utf-8",
        )
    finally:
        shutil.rmtree(work, ignore_errors=True)
    say(f"installed id={stack_id} commit={commit} path={dest}")
    say("handoff: files are outside HStack skills. Do not read them until the user says yes.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(prog="hstack_stack")
    parser.add_argument("action", choices=("detect", "decline", "install"))
    parser.add_argument("stack_id", nargs="?")
    parser.add_argument("--session", default="")
    parser.add_argument("--yes", action="store_true")
    parser.add_argument("--hermes-home", default="")
    parser.add_argument("--home", default="")
    parser.add_argument("--registry", default="")
    args = parser.parse_args()
    hermes = hermes_home(args.hermes_home or None)
    home = user_home(args.home or None)
    registry = Path(args.registry) if args.registry else default_registry()
    if not registry.is_file():
        die(f"missing registry {registry}")
    stacks = load_registry(registry)
    if args.action == "detect":
        session = args.session or None
        if session:
            check_session(session)
        return detect(stacks, hermes, home, session)
    if not args.stack_id:
        die("missing stack id")
    item = stack_by_id(stacks, args.stack_id)
    session = check_session(args.session)
    if args.action == "decline":
        return decline(args.stack_id, hermes, session)
    return install(item, hermes, session, args.yes)


if __name__ == "__main__":
    sys.exit(main())
