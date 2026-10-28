#!/bin/sh
# Piped install against the local site build, with GNU tar and with BSD tar plus shasum.
set -eu

ROOT=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
SITE=$ROOT/site
TMP=$(mktemp -d)
PORT=${PORT:-4179}
PID=

fail() {
  printf 'check_piped: %s\n' "$1" >&2
  exit 1
}

cleanup() {
  if [ -n "$PID" ]; then
    kill "$PID" >/dev/null 2>&1 || true
  fi
  rm -rf "$TMP"
}
trap cleanup EXIT

if [ ! -f "$SITE/dist/install.sh" ] || [ ! -f "$SITE/dist/dl/hstack.tar.gz" ]; then
  fail "site/dist is missing; run npm run build in site/"
fi

PORT=$PORT node "$SITE/scripts/preview.mjs" >"$TMP/preview.log" 2>&1 &
PID=$!
i=0
while ! curl -fsS "http://127.0.0.1:$PORT/install" >/dev/null 2>&1; do
  i=$((i + 1))
  if [ "$i" -gt 50 ]; then
    fail "preview did not start"
  fi
  sleep 0.1
done

count_skills() {
  _n=0
  for _dir in "$1"/skills/hstack/*; do
    if [ -f "$_dir/SKILL.md" ]; then
      _n=$((_n + 1))
    fi
  done
  printf '%s\n' "$_n"
}

install_with() {
  label=$1
  path_value=$2
  home=$TMP/$label
  mkdir -p "$home"
  if [ -n "$path_value" ]; then
    PATH="$path_value" HOME="$home" HERMES_HOME="$home/hermes" HSTACK_BASE_URL="http://127.0.0.1:$PORT" \
      /bin/sh -c 'curl -fsSL "$HSTACK_BASE_URL/install" | sh'
  else
    HOME="$home" HERMES_HOME="$home/hermes" HSTACK_BASE_URL="http://127.0.0.1:$PORT" \
      /bin/sh -c 'curl -fsSL "$HSTACK_BASE_URL/install" | sh'
  fi
  test -f "$home/hermes/skills/hstack/.hstack-managed" || fail "$label missing marker"
  test -f "$home/hermes/skills/hstack/hstack/SKILL.md" || fail "$label missing router"
  test -f "$home/hermes/skills/hstack/hstack/references/frame.md" || fail "$label missing playbook"
  test "$(count_skills "$home/hermes")" -eq 12 || fail "$label expected 12 skills"
  test ! -e "$home/hermes/skills/hstack/VERSION" || fail "$label left VERSION in the skill tree"
  grep -q 'version: 0.1.0' "$home/hermes/skills/hstack/.hstack-managed" || fail "$label marker version"
  diff -q "$ROOT/skills/hstack/reframe/SKILL.md" "$home/hermes/skills/hstack/reframe/SKILL.md" >/dev/null \
    || fail "$label skill bytes differ"
  if [ -n "$path_value" ]; then
    PATH="$path_value" HOME="$home" HERMES_HOME="$home/hermes" HSTACK_BASE_URL="http://127.0.0.1:$PORT" \
      /bin/sh -c 'curl -fsSL "$HSTACK_BASE_URL/install" | sh -s -- --dry-run' >"$TMP/$label.dry"
    PATH="$path_value" HOME="$home" HERMES_HOME="$home/hermes" HSTACK_BASE_URL="http://127.0.0.1:$PORT" \
      /bin/sh -c 'curl -fsSL "$HSTACK_BASE_URL/install" | sh -s -- --uninstall'
  else
    HOME="$home" HERMES_HOME="$home/hermes" HSTACK_BASE_URL="http://127.0.0.1:$PORT" \
      /bin/sh -c 'curl -fsSL "$HSTACK_BASE_URL/install" | sh -s -- --dry-run' >"$TMP/$label.dry"
    HOME="$home" HERMES_HOME="$home/hermes" HSTACK_BASE_URL="http://127.0.0.1:$PORT" \
      /bin/sh -c 'curl -fsSL "$HSTACK_BASE_URL/install" | sh -s -- --uninstall'
  fi
  grep -q "http://127.0.0.1:$PORT/dl/hstack.tar.gz" "$TMP/$label.dry" || fail "$label dry-run omitted the archive URL"
  test ! -d "$home/hermes/skills/hstack" || fail "$label uninstall left the tree"
}

install_with linux ""

WITH=$TMP/with
mkdir -p "$WITH"
HOME="$WITH" HERMES_HOME="$WITH/hermes" HSTACK_BASE_URL="http://127.0.0.1:$PORT" \
  /bin/sh -c 'curl -fsSL "$HSTACK_BASE_URL/install" | sh -s -- --with browser'
test -x "$WITH/hermes/hstack/bin/hstack-visdiff" || fail "piped --with browser missing visdiff"
test -f "$WITH/hermes/hstack/apply_addons.py" || fail "piped --with browser missing apply_addons.py"
grep -q 'hstack_playwright' "$WITH/hermes/config.yaml" || fail "piped --with browser missing playwright"
test -f "$WITH/hermes/skills/hstack/hstack/SKILL.md" || fail "piped --with browser missing skills"
test ! -e "$WITH/hermes/skills/hstack/bin" || fail "helpers landed in the skill tree"
test ! -e "$WITH/hermes/skills/hstack/VERSION" || fail "piped --with browser left VERSION in the skill tree"

MAC=$TMP/macbin
mkdir -p "$MAC"
link() {
  command -v "$1" >/dev/null 2>&1 || fail "missing $1"
  ln -sf "$(command -v "$1")" "$MAC/$2"
}
link curl curl
link shasum shasum
link awk awk
link mktemp mktemp
link find find
link grep grep
link od od
link tr tr
link wc wc
link cp cp
link mv mv
link rm rm
link mkdir mkdir
link dirname dirname
link basename basename
link pwd pwd
ln -sf "$(command -v bsdtar)" "$MAC/tar"
ln -sf /bin/sh "$MAC/sh"
if [ -x "$MAC/sha256sum" ]; then
  fail "macOS-like PATH still has sha256sum"
fi
install_with macos "$MAC:/bin"

HOME=$TMP/pin HERMES_HOME=$TMP/pin/hermes HSTACK_BASE_URL="http://127.0.0.1:$PORT" HSTACK_VERSION=0.1.0 \
  /bin/sh -c 'curl -fsSL "$HSTACK_BASE_URL/install" | sh'
test -f "$TMP/pin/hermes/skills/hstack/shape/SKILL.md" || fail "version pin did not install"

mkdir -p "$TMP/bad/dl"
cp "$SITE/dist/dl/hstack.tar.gz" "$TMP/bad/dl/hstack.tar.gz"
printf '%s\n' '0000000000000000000000000000000000000000000000000000000000000000  hstack.tar.gz' > "$TMP/bad/dl/hstack.tar.gz.sha256"
cp "$SITE/dist/install.sh" "$TMP/bad/install.sh"
BADPORT=$((PORT + 1))
python3 - "$TMP/bad" "$BADPORT" << 'PY' &
import http.server, socketserver, sys
root, port = sys.argv[1], int(sys.argv[2])
class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=root, **kwargs)
    def log_message(self, fmt, *args):
        return
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path in ("/install", "/install/"):
            self.path = "/install.sh"
        return super().do_GET()
with socketserver.TCPServer(("127.0.0.1", port), Handler) as httpd:
    httpd.serve_forever()
PY
BPID=$!
trap 'kill "$PID" "$BPID" >/dev/null 2>&1 || true; rm -rf "$TMP"' EXIT
j=0
while ! curl -fsS "http://127.0.0.1:$BADPORT/install" >/dev/null 2>&1; do
  j=$((j + 1))
  if [ "$j" -gt 50 ]; then
    fail "bad checksum server did not start"
  fi
  sleep 0.1
done
if HOME=$TMP/badhome HERMES_HOME=$TMP/badhome/hermes HSTACK_BASE_URL="http://127.0.0.1:$BADPORT" \
  /bin/sh -c 'curl -fsSL "$HSTACK_BASE_URL/install" | sh' >"$TMP/bad.out" 2>"$TMP/bad.err"; then
  fail "bad checksum should fail"
fi
grep -q 'checksum mismatch' "$TMP/bad.err" || fail "bad checksum was not reported"
test ! -d "$TMP/badhome/hermes/skills/hstack" || fail "bad checksum wrote a skill tree"

printf '%s\n' 'check_piped: linux, addons, macos-like, version pin, and checksum mismatch ok'
