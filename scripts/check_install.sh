#!/bin/sh
# Exercise install.sh against a temporary HERMES_HOME. No network.
set -eu

ROOT=$(CDPATH='' cd "$(dirname "$0")/.." && pwd -P)
INSTALL=$ROOT/install.sh
TMP=$(mktemp -d)
trap 'rm -rf "$TMP"' EXIT

fail() {
  printf 'check_install: %s\n' "$1" >&2
  exit 1
}

if grep -q 'github.com' "$INSTALL"; then
  fail "installer must not fetch from GitHub"
fi
if grep -q 'github.com' "$ROOT/install.ps1"; then
  fail "install.ps1 must not fetch from GitHub"
fi
if grep -q 'HSTACK_REF' "$INSTALL" "$ROOT/install.ps1"; then
  fail "installers still select a git ref"
fi

count_skills() {
  _n=0
  for _dir in "$1"/skills/hstack/*; do
    if [ -f "$_dir/SKILL.md" ]; then
      _n=$((_n + 1))
    fi
  done
  printf '%s\n' "$_n"
}

HERMES_HOME=$TMP/fresh sh "$INSTALL" --dry-run >"$TMP/dry.out"
if [ -e "$TMP/fresh" ]; then
  fail "dry-run created HERMES_HOME"
fi
grep -q 'dry-run' "$TMP/dry.out" || fail "dry-run produced no plan"

HERMES_HOME=$TMP/home sh "$INSTALL"
test -f "$TMP/home/skills/hstack/.hstack-managed" || fail "missing marker"
test -f "$TMP/home/skills/hstack/hstack/SKILL.md" || fail "missing router"
test -f "$TMP/home/skills/hstack/hstack/references/frame.md" || fail "missing playbook"
test "$(count_skills "$TMP/home")" -eq 12 || fail "expected 12 skills"

before=$(cksum "$TMP/home/skills/hstack/hstack/SKILL.md" "$TMP/home/skills/hstack/.hstack-managed")
HERMES_HOME=$TMP/home sh "$INSTALL" --dry-run >/dev/null
after=$(cksum "$TMP/home/skills/hstack/hstack/SKILL.md" "$TMP/home/skills/hstack/.hstack-managed")
test "$before" = "$after" || fail "dry-run changed an installed tree"

printf '%s\n' 'extra' > "$TMP/home/skills/hstack/extra.txt"
HERMES_HOME=$TMP/home sh "$INSTALL"
test ! -e "$TMP/home/skills/hstack/extra.txt" || fail "reinstall kept a file it does not own"
test -f "$TMP/home/skills/hstack/.hstack-managed" || fail "reinstall dropped the marker"
test "$(count_skills "$TMP/home")" -eq 12 || fail "reinstall dropped a skill"

mkdir -p "$TMP/home/skills/other"
printf '%s\n' 'keep' > "$TMP/home/skills/other/note.txt"
HERMES_HOME=$TMP/home sh "$INSTALL" --uninstall
test ! -d "$TMP/home/skills/hstack" || fail "uninstall left the skill tree"
test -f "$TMP/home/skills/other/note.txt" || fail "uninstall removed a foreign skill"
HERMES_HOME=$TMP/home sh "$INSTALL" --uninstall

mkdir -p "$TMP/home/skills/hstack"
printf '%s\n' 'mine' > "$TMP/home/skills/hstack/mine.txt"
if HERMES_HOME=$TMP/home sh "$INSTALL" >"$TMP/clobber.out" 2>"$TMP/clobber.err"; then
  fail "overwrite of an unmarked directory should fail"
fi
test -f "$TMP/home/skills/hstack/mine.txt" || fail "failed overwrite removed foreign files"
grep -q 'refusing' "$TMP/clobber.err" || fail "overwrite error was not a refusal"

rm -rf "$TMP/home/skills/hstack"
mkdir -p "$TMP/home/skills/hstack"
HERMES_HOME=$TMP/home sh "$INSTALL"
test -f "$TMP/home/skills/hstack/hstack/SKILL.md" || fail "empty directory was not installed"

rm -rf "$TMP/home/skills/hstack"
mkdir -p "$TMP/elsewhere"
ln -s "$TMP/elsewhere" "$TMP/home/skills/hstack"
if HERMES_HOME=$TMP/home sh "$INSTALL" >"$TMP/link.out" 2>"$TMP/link.err"; then
  fail "symlink destination should fail"
fi
test -L "$TMP/home/skills/hstack" || fail "symlink was replaced"
test ! -e "$TMP/elsewhere/.hstack-managed" || fail "installer followed a symlink"
rm "$TMP/home/skills/hstack"

for bad in / /usr /bin /etc /var /root; do
  if HERMES_HOME=$bad sh "$INSTALL" --dry-run >"$TMP/bad.out" 2>"$TMP/bad.err"; then
    fail "should refuse HERMES_HOME=$bad"
  fi
  grep -q 'refusing' "$TMP/bad.err" || fail "HERMES_HOME=$bad failed without a refusal"
done

HERMES_HOME=$TMP/home sh "$INSTALL"
HERMES_HOME=$TMP/home sh "$INSTALL" --dry-run --uninstall >"$TMP/udry.out"
test -f "$TMP/home/skills/hstack/.hstack-managed" || fail "uninstall dry-run removed the install"
grep -q 'dry-run' "$TMP/udry.out" || fail "uninstall dry-run was silent"

sh "$INSTALL" --help >/dev/null
if sh "$INSTALL" --nope >"$TMP/nope.out" 2>"$TMP/nope.err"; then
  fail "unknown argument should fail"
fi

if HERMES_HOME=$TMP/noaddon sh "$INSTALL" --with nope >"$TMP/noaddon.out" 2>"$TMP/noaddon.err"; then
  fail "unknown addon should fail"
fi
test ! -e "$TMP/noaddon" || fail "unknown addon created HERMES_HOME"
grep -q 'unknown addon' "$TMP/noaddon.err" || fail "unknown addon was not reported"
if sh "$INSTALL" --with= >"$TMP/emptywith.out" 2>"$TMP/emptywith.err"; then
  fail "empty --with should fail"
fi
if HERMES_HOME=$TMP/gap sh "$INSTALL" --with browser,,docs >"$TMP/gap.out" 2>"$TMP/gap.err"; then
  fail "empty addon name should fail"
fi
test ! -e "$TMP/gap" || fail "empty addon name created HERMES_HOME"

python3 "$ROOT/scripts/apply_addons.py" --validate

HERMES_HOME=$TMP/dryadd sh "$INSTALL" --dry-run --with browser,docs >"$TMP/dryadd.out"
test ! -e "$TMP/dryadd" || fail "addon dry-run created HERMES_HOME"
grep -q 'hstack_playwright' "$TMP/dryadd.out" || fail "addon dry-run did not name the browser server"
grep -q 'hstack_context7' "$TMP/dryadd.out" || fail "addon dry-run did not name the docs server"

mkdir -p "$TMP/keep"
printf '%s\n' 'model: local' 'mcp_servers:' '  other:' '    url: "https://example.com/mcp"' > "$TMP/keep/config.yaml"
HERMES_HOME=$TMP/keep sh "$INSTALL" --with docs,search
grep -q 'url: "https://example.com/mcp"' "$TMP/keep/config.yaml" || fail "addon install dropped a foreign server"
grep -q 'hstack_context7:' "$TMP/keep/config.yaml" || fail "docs addon did not write context7"
grep -q 'https://mcp.context7.com/mcp' "$TMP/keep/config.yaml" || fail "docs addon did not write the context7 URL"
grep -q 'hstack_deepwiki:' "$TMP/keep/config.yaml" || fail "search addon did not write deepwiki"
test -f "$TMP/keep/hstack/.hstack-addons" || fail "missing addon marker"
test -f "$TMP/keep/hstack/apply_addons.py" || fail "installer did not keep a copy of apply_addons.py"
test -f "$TMP/keep/skills/hstack/.hstack-managed" || fail "addon install dropped the skill marker"
before_cfg=$(cksum "$TMP/keep/config.yaml")
HERMES_HOME=$TMP/keep sh "$INSTALL" --with docs >/dev/null
after_cfg=$(cksum "$TMP/keep/config.yaml")
test "$before_cfg" = "$after_cfg" || fail "re-adding docs changed config.yaml"
count=$(grep -c 'hstack_context7:' "$TMP/keep/config.yaml" || true)
test "$count" = 1 || fail "context7 was duplicated"
HERMES_HOME=$TMP/keep sh "$INSTALL" --dry-run --uninstall --with docs >"$TMP/keepdry.out"
grep -q 'would remove mcp server hstack_context7' "$TMP/keepdry.out" || fail "addon uninstall dry-run was silent"
grep -q 'hstack_context7:' "$TMP/keep/config.yaml" || fail "addon uninstall dry-run edited config.yaml"
HERMES_HOME=$TMP/keep sh "$INSTALL" --uninstall --with docs
if grep -q 'hstack_context7:' "$TMP/keep/config.yaml"; then
  fail "uninstall --with docs left context7"
fi
grep -q 'hstack_deepwiki:' "$TMP/keep/config.yaml" || fail "uninstall --with docs removed search"
grep -q 'url: "https://example.com/mcp"' "$TMP/keep/config.yaml" || fail "uninstall --with docs removed a foreign server"
test -f "$TMP/keep/skills/hstack/hstack/SKILL.md" || fail "uninstall --with docs removed skills"

mkdir -p "$TMP/marked/hstack"
printf '%s\n' 'mine' > "$TMP/marked/hstack/mine.txt"
if HERMES_HOME=$TMP/marked sh "$INSTALL" --with github >"$TMP/marked.out" 2>"$TMP/marked.err"; then
  fail "unmarked addon directory should fail"
fi
test -f "$TMP/marked/hstack/mine.txt" || fail "refused addon install removed foreign files"
grep -q 'refusing' "$TMP/marked.err" || fail "unmarked addon directory was not a refusal"

printf '%s\n' 'mcp_servers:' '	bad: true' > "$TMP/tabs.yaml"
mkdir -p "$TMP/tabs"
cp "$TMP/tabs.yaml" "$TMP/tabs/config.yaml"
if HERMES_HOME=$TMP/tabs sh "$INSTALL" --with docs >"$TMP/tabs.out" 2>"$TMP/tabs.err"; then
  fail "a tab in config.yaml should fail"
fi
tab_before=$(cksum < "$TMP/tabs.yaml")
tab_after=$(cksum < "$TMP/tabs/config.yaml")
test "$tab_before" = "$tab_after" || fail "tab refusal rewrote config.yaml"

HERMES_HOME=$TMP/all sh "$INSTALL" --with browser,github,docs,search,perf,test,security,trail
for helper in hstack-visdiff hstack-pr hstack-bench hstack-test hstack-scan hstack-decisions; do
  test -x "$TMP/all/hstack/bin/$helper" || fail "missing executable $helper"
done
grep -q 'hstack_playwright:' "$TMP/all/config.yaml" || fail "browser addon did not write playwright"
grep -q '@playwright/mcp@0.0.83' "$TMP/all/config.yaml" || fail "browser addon did not pin Playwright"
grep -q 'https://mcp.deepwiki.com/mcp' "$TMP/all/config.yaml" || fail "search addon URL missing on the full install"
"$TMP/all/hstack/bin/hstack-bench" --repeat 3 -- true >"$TMP/bench.out"
grep -q 'min_s' "$TMP/bench.out" || fail "bench did not report min"
grep -q 'median_s' "$TMP/bench.out" || fail "bench did not report median"
grep -q 'max_s' "$TMP/bench.out" || fail "bench did not report max"
if "$TMP/all/hstack/bin/hstack-bench" --repeat 2 -- true >"$TMP/bench2.out" 2>"$TMP/bench2.err"; then
  fail "bench should reject fewer than 3 repeats"
fi
"$TMP/all/hstack/bin/hstack-pr" --dry-run status >"$TMP/pr.out"
grep -q 'gh pr view' "$TMP/pr.out" || fail "pr dry-run did not name gh"
"$TMP/all/hstack/bin/hstack-scan" --root "$TMP/all" >"$TMP/scan.out"
"$TMP/all/hstack/bin/hstack-visdiff" --dry-run "$TMP/a.png" "$TMP/b.png" >"$TMP/vis.out"
grep -q 'would compare' "$TMP/vis.out" || fail "visdiff dry-run was silent"
mkdir -p "$TMP/pytest"
printf '%s\n' '[pytest]' > "$TMP/pytest/pytest.ini"
"$TMP/all/hstack/bin/hstack-test" --dry-run --root "$TMP/pytest" >"$TMP/testdetect.out"
grep -q 'pytest' "$TMP/testdetect.out" || fail "test helper did not detect pytest"
"$TMP/all/hstack/bin/hstack-decisions" --choice keep --rejected drop --reason 'one row' --file "$TMP/decisions.tsv" >"$TMP/decisions.out"
grep -q 'keep' "$TMP/decisions.tsv" || fail "decisions helper did not append"
HERMES_HOME=$TMP/all sh "$INSTALL" --uninstall --with browser
test ! -e "$TMP/all/hstack/bin/hstack-visdiff" || fail "uninstall --with browser left visdiff"
test -x "$TMP/all/hstack/bin/hstack-pr" || fail "uninstall --with browser removed github"
if grep -q 'hstack_playwright:' "$TMP/all/config.yaml"; then
  fail "uninstall --with browser left playwright"
fi
grep -q 'hstack_context7:' "$TMP/all/config.yaml" || fail "uninstall --with browser removed docs"
test -f "$TMP/all/skills/hstack/hstack/SKILL.md" || fail "partial addon uninstall removed skills"
HERMES_HOME=$TMP/all sh "$INSTALL" --uninstall
test ! -d "$TMP/all/skills/hstack" || fail "full uninstall left skills"
test ! -d "$TMP/all/hstack" || fail "full uninstall left addons"
test ! -e "$TMP/all/config.yaml" || fail "full uninstall left a config this installer created"

printf '%s\n' 'check_install: ok'
