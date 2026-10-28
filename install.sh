#!/bin/sh
# Install HStack into Hermes Agent.
#   curl -fsSL https://hstack.sh/install | sh
#   curl -fsSL https://hstack.sh/install | sh -s -- --uninstall
#   sh install.sh [--dry-run] [--uninstall] [--with name,name]
# Skills go to ${HERMES_HOME:-$HOME/.hermes}/skills/hstack.
# A second run replaces an install this script created. It will not touch
# any other skill, and it will not delete a directory it did not mark.
# The curl form downloads the archive from hstack.sh. The repository is private,
# so this script does not fetch from a git host. The archive also carries the
# addon helpers under bin/ and scripts/apply_addons.py.

set -eu

DRY=0
UNINSTALL=0
WITH=
WORK=
STAGE=
ADDON_ROOT=

usage() {
  printf '%s\n' \
    'Usage: sh install.sh [--dry-run] [--uninstall] [--with name,name]' \
    '       curl -fsSL https://hstack.sh/install | sh' \
    '       curl -fsSL https://hstack.sh/install | sh -s -- --uninstall' \
    '' \
    'Installs into the Hermes home, at skills/hstack. The usual home is .hermes in your home directory.' \
    'The default install is skills only. --with adds an optional addon:' \
    'browser, github, docs, search, perf, test, security, trail.' \
    'The curl form downloads the archive from hstack.sh.' \
    'HSTACK_BASE_URL overrides that host. HSTACK_VERSION pins a release.' \
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

addon_ok() {
  case "$1" in
    browser|github|docs|search|perf|test|security|trail) return 0 ;;
    *) return 1 ;;
  esac
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dry-run) DRY=1; shift ;;
    --uninstall) UNINSTALL=1; shift ;;
    --help|-h) usage; exit 0 ;;
    --with=*)
      _with_val=${1#--with=}
      if [ -z "$_with_val" ]; then
        die "--with needs a comma-separated list"
      fi
      WITH="${WITH:+$WITH,}${_with_val}"
      shift
      ;;
    --with)
      shift
      if [ $# -eq 0 ]; then
        die "--with needs a comma-separated list"
      fi
      WITH="${WITH:+$WITH,}$1"
      shift
      ;;
    *) die "unknown argument: $1" ;;
  esac
done

if [ -n "$WITH" ]; then
  _rest=$WITH
  while [ -n "$_rest" ]; do
    _addon=${_rest%%,*}
    case "$_rest" in
      *,*) _rest=${_rest#*,} ;;
      *) _rest= ;;
    esac
    if [ -z "$_addon" ] || ! addon_ok "$_addon"; then
      die "unknown addon: ${_addon:-empty}"
    fi
  done
fi

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

script=$0
SCRIPT_DIR=
if [ -f "$script" ]; then
  SCRIPT_DIR=$(CDPATH='' cd "$(dirname "$script")" && pwd -P)
fi

run_addons() {
  _mode=$1
  if [ "$_mode" != uninstall ] && [ -z "$WITH" ]; then
    return 0
  fi
  if [ "$_mode" = uninstall ] && [ -z "$WITH" ] && [ ! -e "$HERMES_HOME/hstack" ]; then
    return 0
  fi
  command -v python3 >/dev/null 2>&1 || die "python3 is required for addons"
  _py=
  if [ -n "$ADDON_ROOT" ] && [ -f "$ADDON_ROOT/scripts/apply_addons.py" ]; then
    _py=$ADDON_ROOT/scripts/apply_addons.py
  elif [ -f "$HERMES_HOME/hstack/apply_addons.py" ]; then
    _py=$HERMES_HOME/hstack/apply_addons.py
  elif [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/scripts/apply_addons.py" ]; then
    _py=$SCRIPT_DIR/scripts/apply_addons.py
  fi
  if [ -z "$_py" ]; then
    if [ "$_mode" = uninstall ] && [ ! -d "$HERMES_HOME/hstack" ]; then
      return 0
    fi
    if [ "$DRY" -eq 1 ]; then
      say "dry-run: would configure addons: ${WITH:-all}"
      return 0
    fi
    die "missing scripts/apply_addons.py"
  fi
  _source=$ADDON_ROOT
  if [ -z "$_source" ] && [ -n "$SCRIPT_DIR" ]; then
    _source=$SCRIPT_DIR
  fi
  set -- python3 "$_py" --hermes-home "$HERMES_HOME"
  if [ -n "$_source" ]; then
    set -- "$@" --source "$_source"
  fi
  if [ "$DRY" -eq 1 ]; then
    set -- "$@" --dry-run
  fi
  if [ "$_mode" = uninstall ]; then
    set -- "$@" --uninstall
  fi
  if [ -n "$WITH" ]; then
    set -- "$@" --with "$WITH"
  fi
  "$@"
}

if [ "$UNINSTALL" -eq 1 ] && [ -n "$WITH" ]; then
  run_addons uninstall
  exit 0
fi

if [ "$UNINSTALL" -eq 1 ]; then
  if [ ! -d "$DEST" ]; then
    say "nothing to remove at $DEST"
  else
    if [ ! -f "$MARKER" ] || [ -L "$MARKER" ]; then
      die "refusing to remove $DEST (missing .hstack-managed)"
    fi
    if [ "$DRY" -eq 1 ]; then
      say "dry-run: would remove $DEST"
    else
      rm -rf "$DEST"
      say "removed $DEST"
    fi
  fi
  run_addons uninstall
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
SUM=
if [ -n "$SCRIPT_DIR" ] && [ -f "$SCRIPT_DIR/skills/hstack/hstack/SKILL.md" ]; then
  MODE=local
  SRC="$SCRIPT_DIR/skills/hstack"
  ADDON_ROOT=$SCRIPT_DIR
fi

if [ -z "$MODE" ]; then
  MODE=remote
  BASE=${HSTACK_BASE_URL:-https://hstack.sh}
  case "$BASE" in
    */) BASE=${BASE%/} ;;
  esac
  case "$BASE" in
    http://*|https://*) ;;
    *) die "refusing HSTACK_BASE_URL" ;;
  esac
  case "$BASE" in
    *[[:space:]]*|*'<'*|*'..'*) die "refusing HSTACK_BASE_URL" ;;
  esac
  NAME=hstack.tar.gz
  if [ -n "${HSTACK_VERSION:-}" ]; then
    case "$HSTACK_VERSION" in
      ''|*[!0-9.]*|*..*) die "refusing HSTACK_VERSION" ;;
    esac
    NAME="hstack-v${HSTACK_VERSION}.tar.gz"
  fi
  URL="$BASE/dl/$NAME"
  SUM="$BASE/dl/${NAME}.sha256"
fi

if [ "$DRY" -eq 1 ]; then
  say "dry-run: would install into $DEST"
  if [ "$MODE" = local ]; then
    say "dry-run: source tree $SRC"
  else
    say "dry-run: would download $URL"
    say "dry-run: would verify $SUM"
  fi
  run_addons install
  exit 0
fi

hash_file() {
  if command -v sha256sum >/dev/null 2>&1; then
    sha256sum "$1" | awk 'NR==1 { print $1 }'
  elif command -v shasum >/dev/null 2>&1; then
    shasum -a 256 "$1" | awk 'NR==1 { print $1 }'
  else
    die "sha256sum or shasum is required"
  fi
}

if [ "$MODE" = remote ]; then
  command -v curl >/dev/null 2>&1 || die "curl is required to download HStack"
  command -v tar >/dev/null 2>&1 || die "tar is required to download HStack"
  WORK=$(mktemp -d)
  archive="$WORK/hstack.tar.gz"
  sumfile="$WORK/hstack.tar.gz.sha256"
  curl -fsSL -o "$archive" "$URL" || die "download failed"
  curl -fsSL -o "$sumfile" "$SUM" || die "checksum download failed"
  if [ ! -s "$archive" ] || [ ! -s "$sumfile" ]; then
    die "download was empty"
  fi
  magic=$(od -An -t x1 -N 2 "$archive" | tr -d ' \n')
  case "$magic" in
    1f8b) ;;
    *) die "download was not a gzip archive" ;;
  esac
  expected=$(awk 'NR==1 { print $1 }' "$sumfile")
  case "$expected" in
    *[!0-9A-Fa-f]*|'') die "checksum was not a sha256 digest" ;;
  esac
  elen=$(printf '%s' "$expected" | wc -c | tr -d ' ')
  if [ "$elen" -ne 64 ]; then
    die "checksum was not a sha256 digest"
  fi
  actual=$(hash_file "$archive")
  if [ "$actual" != "$expected" ]; then
    die "checksum mismatch"
  fi
  tar -tzf "$archive" > "$WORK/members" || die "could not read archive"
  while IFS= read -r member || [ -n "$member" ]; do
    norm=$member
    case "$norm" in
      ./*) norm=${norm#./} ;;
    esac
    case "$norm" in
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
  ADDON_ROOT=$top
  if [ ! -f "$SRC/hstack/SKILL.md" ]; then
    die "archive is missing hstack/SKILL.md"
  fi
fi

if [ ! -f "$SRC/hstack/SKILL.md" ]; then
  die "missing hstack/SKILL.md"
fi

if find "$SRC" \( -type l -o -type b -o -type c -o -type p -o -type s \) -print | grep -q .; then
  die "refusing to copy a link or special file from the skill tree"
fi

ver=0.1.0
if [ -n "$ADDON_ROOT" ] && [ -f "$ADDON_ROOT/VERSION" ]; then
  got=$(tr -cd '0-9.' < "$ADDON_ROOT/VERSION")
  if [ -n "$got" ]; then
    ver=$got
  fi
fi
parent=$(dirname "$DEST")
mkdir -p "$parent"
STAGE=$(mktemp -d "${parent}/.hstack-stage.XXXXXX")
cp -R "$SRC/." "$STAGE/"
if [ -f "$STAGE/VERSION" ]; then
  got=$(tr -cd '0-9.' < "$STAGE/VERSION")
  if [ -n "$got" ]; then
    ver=$got
  fi
  rm -f "$STAGE/VERSION"
fi
if [ ! -f "$STAGE/hstack/SKILL.md" ]; then
  die "install tree is missing hstack/SKILL.md"
fi
printf '%s\n' 'managed-by: hstack install.sh' "version: $ver" > "$STAGE/.hstack-managed"

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
run_addons install
