#!/usr/bin/env python3
"""External stack detection, decline, and the sha256 gate. No real download."""

from __future__ import annotations

import hashlib
import http.server
import json
import socketserver
import subprocess
import tarfile
import tempfile
import threading
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "hstack" / "hstack" / "scripts" / "hstack_stack.py"


def fail(message: str) -> None:
    print(f"check_stacks: {message}", file=sys.stderr)
    raise SystemExit(1)


import sys  # noqa: E402


def run(args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(SCRIPT), *args], text=True, capture_output=True)


def registry(url: str, digest: str, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "stacks.md"
    payload = {
        "stacks": [
            {
                "id": "gstack",
                "good_at": "test",
                "license": "MIT",
                "commit": "9e3308f65adf547b7e4776e5ed22467a2649d2ee",
                "sha256": digest,
                "archive": url,
            },
            {
                "id": "pstack",
                "good_at": "test",
                "license": "MIT",
                "commit": "c742dd61706fbacc1b95f1a20b7b988cf096ce6c",
                "sha256": "0" * 64,
                "archive": url,
            },
            {
                "id": "tstack",
                "good_at": "test",
                "license": "MIT",
                "commit": "1085050f3baed1ac724caa4a8166145fb2ac88af",
                "sha256": "0" * 64,
                "archive": url,
            },
            {
                "id": "gbrain",
                "good_at": "test",
                "license": "MIT",
                "commit": "82b7ef601fdfc449b0d242f7e61a4604aa2c8a8e",
                "sha256": "0" * 64,
                "archive": url,
            },
        ]
    }
    path.write_text("```json\n" + json.dumps(payload) + "\n```\n", encoding="utf-8")
    return path


def make_archive(directory: Path) -> tuple[Path, str]:
    top = directory / "payload"
    (top / "readme").parent.mkdir(parents=True)
    (top / "readme").write_text("not a skill\n", encoding="utf-8")
    archive = directory / "stack.tar.gz"
    with tarfile.open(archive, "w:gz") as handle:
        handle.add(top, arcname="upstream")
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    return archive, digest


def detect_cases(tmp: Path) -> None:
    home = tmp / "home"
    hermes = tmp / "hermes"
    marker = home / ".claude" / "skills" / "gstack" / "bin" / "gstack-state-root.sh"
    marker.parent.mkdir(parents=True)
    marker.write_text("#!/bin/sh\ntouch \"$0.ran\"\n", encoding="utf-8")
    marker.chmod(0o755)
    reg = registry("https://example.invalid/nope.tar.gz", "ab" * 32, tmp)
    result = run(["detect", "--session", "chat-1", "--home", str(home), "--hermes-home", str(hermes), "--registry", str(reg)])
    if result.returncode != 0:
        fail(result.stderr)
    if "id=gstack installed=yes" not in result.stdout:
        fail("gstack marker was not detected")
    if marker.with_name("gstack-state-root.sh.ran").exists():
        fail("detection executed gstack")
    if "id=pstack installed=no" not in result.stdout:
        fail("pstack should be absent")
    poteto = home / ".cursor" / "plugins" / "cache" / "pstack" / "skills" / "poteto-mode" / "SKILL.md"
    poteto.parent.mkdir(parents=True)
    poteto.write_text("---\nname: poteto-mode\n---\n", encoding="utf-8")
    result = run(["detect", "--session", "chat-1", "--home", str(home), "--hermes-home", str(hermes), "--registry", str(reg)])
    if "id=pstack installed=yes" not in result.stdout:
        fail("pstack skill file was not detected")
    skills = home / ".claude" / "skills"
    (skills / "leaving-pr-comments").mkdir()
    (skills / "leaving-pr-comments" / "SKILL.md").write_text("x\n", encoding="utf-8")
    (skills / "sol-loop").mkdir()
    (skills / "sol-loop" / "SKILL.md").write_text("x\n", encoding="utf-8")
    result = run(["detect", "--home", str(home), "--hermes-home", str(hermes), "--registry", str(reg)])
    if "id=tstack installed=yes" not in result.stdout:
        fail("tstack pair was not detected")
    (home / ".gbrain").mkdir()
    (home / ".gbrain" / "config.json").write_text("{}\n", encoding="utf-8")
    result = run(["detect", "--home", str(home), "--hermes-home", str(hermes), "--registry", str(reg)])
    if "id=gbrain installed=yes" not in result.stdout:
        fail("gbrain config was not detected")
    state_only = tmp / "state-only"
    (state_only / ".gstack").mkdir(parents=True)
    (state_only / ".gstack" / "config.yaml").write_text("telemetry: off\n", encoding="utf-8")
    result = run(["detect", "--home", str(state_only), "--hermes-home", str(tmp / "empty-hermes"), "--registry", str(reg)])
    if "id=gstack installed=yes" in result.stdout:
        fail("gstack state directory counted as an install")


def install_cases(tmp: Path) -> None:
    archive, digest = make_archive(tmp)
    hits = {"n": 0}

    class Handler(http.server.BaseHTTPRequestHandler):
        def do_GET(self):  # noqa: N802
            hits["n"] += 1
            body = archive.read_bytes()
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def log_message(self, fmt: str, *args) -> None:
            return

    server = socketserver.TCPServer(("127.0.0.1", 0), Handler)
    port = server.server_address[1]
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        url = f"http://127.0.0.1:{port}/stack.tar.gz"
        hermes = tmp / "install-home"
        reg = registry(url, digest, tmp)
        refused = run(["install", "gstack", "--session", "chat-1", "--hermes-home", str(hermes), "--registry", str(reg)])
        if refused.returncode == 0 or "without --yes" not in refused.stderr:
            fail(f"install without yes did not refuse: {refused.stderr}")
        if hits["n"] != 0:
            fail("install without yes downloaded")
        bad = registry(url, "a" * 64, tmp / "bad")
        mismatched = run(
            ["install", "gstack", "--yes", "--session", "chat-1", "--hermes-home", str(hermes), "--registry", str(bad)]
        )
        if mismatched.returncode == 0 or "checksum mismatch" not in mismatched.stderr:
            fail(f"bad checksum was not rejected: {mismatched.stderr}")
        if (hermes / "hstack" / "external").exists():
            fail("bad checksum extracted")
        good = run(
            ["install", "gstack", "--yes", "--session", "chat-1", "--hermes-home", str(hermes), "--registry", str(reg)]
        )
        if good.returncode != 0:
            fail(good.stderr)
        receipt = hermes / "hstack" / "external" / "gstack" / "9e3308f65adf547b7e4776e5ed22467a2649d2ee"
        if not (receipt / ".hstack-external").is_file() or not (receipt / "readme").is_file():
            fail("extract did not land outside the skill tree")
        if (hermes / "skills").exists():
            fail("install wrote a skill tree")
        before = hits["n"]
        again = run(
            ["install", "gstack", "--yes", "--session", "chat-1", "--hermes-home", str(hermes), "--registry", str(reg)]
        )
        if again.returncode != 0 or "already installed" not in again.stdout:
            fail("second install was not idempotent")
        if hits["n"] != before:
            fail("idempotent install downloaded again")
        declined = run(["decline", "pstack", "--session", "chat-1", "--hermes-home", str(hermes), "--registry", str(reg)])
        if declined.returncode != 0:
            fail(declined.stderr)
        blocked = run(
            ["install", "pstack", "--yes", "--session", "chat-1", "--hermes-home", str(hermes), "--registry", str(reg)]
        )
        if blocked.returncode == 0 or "declined" not in blocked.stderr:
            fail("declined install was not refused")
    finally:
        server.shutdown()


def main() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        detect_cases(root / "detect")
        install_cases(root / "install")
    print("check_stacks: detect, decline, checksum, and idempotent install ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
