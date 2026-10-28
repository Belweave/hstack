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

printf '%s\n' 'check_install: ok'
