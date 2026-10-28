#!/bin/sh
# Install HStack into Hermes Agent.
#   curl -fsSL https://hstack.sh/install | sh
#   curl -fsSL https://hstack.sh/install | sh -s -- --uninstall
#   sh install.sh [--dry-run] [--uninstall]
# Skills go to ${HERMES_HOME:-$HOME/.hermes}/skills/hstack.
# A second run replaces an install this script created. It will not touch
# any other skill, and it will not delete a directory it did not mark.

set -eu

DRY=0
UNINSTALL=0
WORK=
STAGE=

usage() {
  printf '%s\n' \
    'Usage: sh install.sh [--dry-run] [--uninstall]' \
    '       curl -fsSL https://hstack.sh/install | sh' \
    '       curl -fsSL https://hstack.sh/install | sh -s -- --uninstall' \
    '' \
    'Installs into the Hermes home, at skills/hstack. The usual home is .hermes in your home directory.' \
    'HSTACK_REF selects the git branch when the script downloads (default: main).' \
    'Running this file from a git checkout installs that checkout.'
}

die() {
  printf 'hstack: %s\n' "$1" >&2
  exit 1
}

say() {
  printf 'hstack: %s\n' "$1"
}

cleanup() {
  status=$?
  if [ -n "$STAGE" ] && [ -d "$STAGE" ]; then
    rm -rf "$STAGE" || true
  fi
  if [ -n "$WORK" ] && [ -d "$WORK" ]; then
    rm -rf "$WORK" || true
  fi
  exit "$status"
}

trap cleanup EXIT

for arg in "$@"; do
  case "$arg" in
    --dry-run) DRY=1 ;;
    --uninstall) UNINSTALL=1 ;;
    --help|-h) usage; exit 0 ;;
    *) die "unknown argument: $arg" ;;
  esac
done

if [ -z "${HOME:-}" ]; then
  die "HOME is not set"
fi

RAW_HOME=${HERMES_HOME:-$HOME/.hermes}
case "$RAW_HOME" in
  ''|..|../*|*/..|*/../*) die "refusing HERMES_HOME" ;;
esac
if printf '%s' "$RAW_HOME" | grep -q '[[:cntrl:]]'; then
  die "refusing HERMES_HOME"
fi
case "$RAW_HOME" in
  /|/usr|/bin|/etc|/var|/root) die "refusing HERMES_HOME=$RAW_HOME" ;;
esac

while :; do
  case "$RAW_HOME" in
    /) break ;;
    */) RAW_HOME=${RAW_HOME%/} ;;
    *) break ;;
  esac
done

resolve_path() {
  _target=$1
  if [ -d "$_target" ]; then
    (CDPATH='' cd "$_target" && pwd -P)
    return
  fi
  _parent=$(dirname "$_target")
  _base=$(basename "$_target")
  if [ -d "$_parent" ]; then
    printf '%s/%s\n' "$(CDPATH='' cd "$_parent" && pwd -P)" "$_base"
    return
  fi
  printf '%s\n' "$_target"
}

HERMES_HOME=$(resolve_path "$RAW_HOME")
case "$HERMES_HOME" in
  /|/usr|/bin|/etc|/var|/root) die "refusing HERMES_HOME=$HERMES_HOME" ;;
  *..*) die "refusing HERMES_HOME=$HERMES_HOME" ;;
esac

if [ -e "$HERMES_HOME" ] && [ ! -d "$HERMES_HOME" ]; then
  die "HERMES_HOME is not a directory: $HERMES_HOME"
fi

DEST="$HERMES_HOME/skills/hstack"
MARKER="$DEST/.hstack-managed"

if [ -L "$DEST" ]; then
  die "refusing to follow symlink $DEST"
fi
if [ -e "$DEST" ] && [ ! -d "$DEST" ]; then
  die "refusing $DEST (not a directory)"
fi

dir_nonempty() {
  _found=1
  for _entry in "$1"/* "$1"/.[!.]* "$1"/..?*; do
    if [ -e "$_entry" ] || [ -L "$_entry" ]; then
      _found=0
      break
    fi
  done
  return "$_found"
}

if [ "$UNINSTALL" -eq 1 ]; then
  if [ ! -d "$DEST" ]; then
    say "nothing to remove at $DEST"
    exit 0
  fi
  if [ ! -f "$MARKER" ] || [ -L "$MARKER" ]; then
    die "refusing to remove $DEST (missing .hstack-managed)"
  fi
  if [ "$DRY" -eq 1 ]; then
    say "dry-run: would remove $DEST"
    exit 0
  fi
  rm -rf "$DEST"
  say "removed $DEST"
  exit 0
fi

if [ -d "$DEST" ] && [ ! -f "$MARKER" ]; then
  if dir_nonempty "$DEST"; then
    die "refusing to overwrite non-empty $DEST (not an HStack install)"
  fi
fi

MODE=
SRC=
URL=
script=$0
if [ -f "$script" ]; then
  script_dir=$(CDPATH='' cd "$(dirname "$script")" && pwd -P)
  if [ -f "$script_dir/skills/hstack/hstack/SKILL.md" ]; then
    MODE=local
    SRC="$script_dir/skills/hstack"
  fi
fi

if [ -z "$MODE" ]; then
  MODE=remote
  REF=${HSTACK_REF:-main}
  case "$REF" in
    ''|-*|*..*|*[[:space:]]*|*'/'*) die "refusing HSTACK_REF" ;;
  esac
  case "$REF" in
    *[!A-Za-z0-9._-]*) die "refusing HSTACK_REF" ;;
  esac
  URL="https://github.com/Belweave/hstack/archive/refs/heads/${REF}.tar.gz"
fi

if [ "$DRY" -eq 1 ]; then
  say "dry-run: would install into $DEST"
  if [ "$MODE" = local ]; then
    say "dry-run: source tree $SRC"
  else
    say "dry-run: would download $URL"
  fi
  exit 0
fi

if [ "$MODE" = remote ]; then
  command -v curl >/dev/null 2>&1 || die "curl is required to download HStack"
  command -v tar >/dev/null 2>&1 || die "tar is required to download HStack"
  WORK=$(mktemp -d)
  archive="$WORK/hstack.tar.gz"
  curl -fsSL -o "$archive" "$URL" || die "download failed"
  if [ ! -s "$archive" ]; then
    die "download was empty"
  fi
  tar -tzf "$archive" > "$WORK/members" || die "could not read archive"
  while IFS= read -r member || [ -n "$member" ]; do
    case "$member" in
      ''|/*|*..*) die "archive member is absolute or contains .." ;;
    esac
  done < "$WORK/members"
  tar -tvzf "$archive" > "$WORK/listing" || die "could not list archive"
  while IFS= read -r line || [ -n "$line" ]; do
    case "$line" in
      l*|h*) die "archive contains a link; refusing to extract it" ;;
    esac
  done < "$WORK/listing"
  tar -xzf "$archive" -C "$WORK" || die "could not extract archive"
  tops=0
  top=
  for dir in "$WORK"/*; do
    if [ -d "$dir" ]; then
      tops=$((tops + 1))
      top=$dir
    fi
  done
  if [ "$tops" -ne 1 ] || [ -z "$top" ]; then
    die "expected one top-level directory in the archive"
  fi
  SRC="$top/skills/hstack"
  if [ ! -f "$SRC/hstack/SKILL.md" ]; then
    die "archive is missing skills/hstack/hstack/SKILL.md"
  fi
fi

if [ ! -f "$SRC/hstack/SKILL.md" ]; then
  die "missing skills/hstack/hstack/SKILL.md"
fi

if find "$SRC" \( -type l -o -type b -o -type c -o -type p -o -type s \) -print | grep -q .; then
  die "refusing to copy a link or special file from the skill tree"
fi

parent=$(dirname "$DEST")
mkdir -p "$parent"
STAGE=$(mktemp -d "${parent}/.hstack-stage.XXXXXX")
cp -R "$SRC/." "$STAGE/"
if [ ! -f "$STAGE/hstack/SKILL.md" ]; then
  die "install tree is missing hstack/SKILL.md"
fi
printf '%s\n' 'managed-by: hstack install.sh' 'version: 0.1.0' > "$STAGE/.hstack-managed"

if [ -d "$DEST" ]; then
  PREV="${parent}/.hstack-prev.$$"
  if [ -e "$PREV" ]; then
    die "temporary path already exists: $PREV"
  fi
  mv "$DEST" "$PREV"
  if mv "$STAGE" "$DEST"; then
    STAGE=
    rm -rf "$PREV"
  else
    mv "$PREV" "$DEST" || die "restore failed; previous tree left at $PREV"
    die "could not move the new tree into $DEST"
  fi
else
  mv "$STAGE" "$DEST"
  STAGE=
fi

say "installed into $DEST"
