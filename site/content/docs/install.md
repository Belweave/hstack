---
title: Install
description: Install HStack from hstack.sh on macOS, Linux, or Windows. Dry-run, uninstall, and version pin use the same flags.
---

The installer downloads `install.sh` and the skill archive from hstack.sh, checks the sha256, and extracts into the Hermes skills directory. It does not clone the repository.

:::tabs
:::tab macOS / Linux
```sh install.sh
# archive is checked with sha256 before extract
curl -fsSL https://hstack.sh/install | sh
```
:::tab Windows
```powershell install.ps1
irm https://hstack.sh/install.ps1 -OutFile install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1
```
:::

:::note
`irm | iex` does not pass `--dry-run`, `--uninstall`, or `--with`. `install.ps1` reads those flags from `$args` when PowerShell runs the file with `-File`.
:::

From a checkout of the repo, `sh install.sh` installs the skills beside the script. A second run replaces the HStack skills and leaves every other skill alone.

## Dry-run

Dry-run prints the plan and writes nothing.

:::tabs
:::tab macOS / Linux
```sh install.sh
curl -fsSL https://hstack.sh/install | sh -s -- --dry-run
```
:::tab Windows
```powershell install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1 --dry-run
```
:::

## Uninstall

Uninstall removes `skills/hstack` only when this installer created it, and it removes add-ons and hooks this installer created. `--uninstall --with browser` removes only that add-on. `--uninstall --with hermes-hooks` removes the hooks and leaves the skills.

:::tabs
:::tab macOS / Linux
```sh install.sh
curl -fsSL https://hstack.sh/install | sh -s -- --uninstall
```
:::tab Windows
```powershell install.ps1
powershell -ExecutionPolicy Bypass -File .\install.ps1 --uninstall
```
:::

## Version and host

With no version set, the installer fetches `/dl/hstack.tar.gz`, the latest alias. That alias is 0.2.1. `HSTACK_VERSION=0.2.0` still fetches `/dl/hstack-v0.2.0.tar.gz`, and `HSTACK_VERSION=0.1.0` still fetches `/dl/hstack-v0.1.0.tar.gz`. Those versioned files stay byte for byte. `HSTACK_BASE_URL` points the download at another host, such as a `*.vercel.app` URL before DNS is in place.

```sh install.sh
curl -fsSL https://hstack.sh/install | HSTACK_VERSION=0.1.0 sh
```

The archive is one directory. Inside 0.2.1: the skills, `scripts/apply_addons.py`, `scripts/apply_hooks.py`, `hooks/`, and the `bin/` helpers. The published checksum files are `HEX  filename`, two spaces. A mismatch stops the install and does not write skills.

WSL can run `install.sh`. The Windows script takes the same flags and the same archive.
