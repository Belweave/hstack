# Install HStack into Hermes Agent on Windows.
#   powershell -File install.ps1 [--dry-run] [--uninstall] [--with name,name]
# Skills go to $env:HERMES_HOME\skills\hstack, or $env:USERPROFILE\.hermes\skills\hstack.
# A second run replaces an install this script created. It will not touch
# any other skill, and it will not delete a directory it did not mark.

$ErrorActionPreference = 'Stop'

$Dry = $false
$Uninstall = $false
$With = New-Object System.Collections.Generic.List[string]
$AddonNames = @('browser', 'github', 'docs', 'search', 'perf', 'test', 'security', 'trail')

function Die([string]$Message) {
    [Console]::Error.WriteLine("hstack: $Message")
    exit 1
}

function Say([string]$Message) {
    Write-Host "hstack: $Message"
}

function Show-Usage {
    Write-Host @'
Usage: powershell -File install.ps1 [--dry-run] [--uninstall] [--with name,name]

Installs into the Hermes home, at skills\hstack. The usual home is .hermes in your profile directory.
The default install is skills only. --with adds an optional addon:
browser, github, docs, search, perf, test, security, trail.
HSTACK_REF selects the git branch when the script downloads (default: main).
Running this file from a git checkout installs that checkout.
'@
}

function Add-AddonNames([string]$Raw) {
    if ([string]::IsNullOrWhiteSpace($Raw)) {
        Die '--with needs a comma-separated list'
    }
    foreach ($name in $Raw.Split(',')) {
        $trimmed = $name.Trim()
        if (-not $trimmed -or $AddonNames -notcontains $trimmed) {
            Die "unknown addon: $trimmed"
        }
        if (-not $With.Contains($trimmed)) {
            [void]$With.Add($trimmed)
        }
    }
}

$index = 0
while ($index -lt $args.Count) {
    $arg = [string]$args[$index]
    if ($arg -eq '--dry-run') {
        $Dry = $true
    } elseif ($arg -eq '--uninstall') {
        $Uninstall = $true
    } elseif ($arg -eq '--help' -or $arg -eq '-h') {
        Show-Usage
        exit 0
    } elseif ($arg.StartsWith('--with=')) {
        Add-AddonNames $arg.Substring(7)
    } elseif ($arg -eq '--with') {
        $index++
        if ($index -ge $args.Count) {
            Die '--with needs a comma-separated list'
        }
        Add-AddonNames ([string]$args[$index])
    } else {
        Die "unknown argument: $arg"
    }
    $index++
}

if ([string]::IsNullOrWhiteSpace($env:USERPROFILE) -and [string]::IsNullOrWhiteSpace($env:HERMES_HOME)) {
    Die 'USERPROFILE is not set'
}

$RawHome = if ($env:HERMES_HOME) { $env:HERMES_HOME } else { Join-Path $env:USERPROFILE '.hermes' }
if ($RawHome -match '\.\.' -or $RawHome -match '[\u0000-\u001F]') {
    Die 'refusing HERMES_HOME'
}
$FullHome = [System.IO.Path]::GetFullPath($RawHome)
$RootPath = [System.IO.Path]::GetPathRoot($FullHome)
if ($FullHome.TrimEnd('\', '/') -eq $RootPath.TrimEnd('\', '/')) {
    Die "refusing HERMES_HOME=$FullHome"
}
foreach ($bad in @($env:SystemRoot, $(if ($env:SystemRoot) { Join-Path $env:SystemRoot 'System32' }))) {
    if ($bad -and $FullHome -eq [System.IO.Path]::GetFullPath($bad)) {
        Die "refusing HERMES_HOME=$FullHome"
    }
}
if (Test-Path -LiteralPath $FullHome) {
    $homeItem = Get-Item -LiteralPath $FullHome -Force
    if ($homeItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        Die "refusing to follow symlink $FullHome"
    }
    if (-not $homeItem.PSIsContainer) {
        Die "HERMES_HOME is not a directory: $FullHome"
    }
}

$Dest = Join-Path $FullHome 'skills\hstack'
$Marker = Join-Path $Dest '.hstack-managed'
if (Test-Path -LiteralPath $Dest) {
    $destItem = Get-Item -LiteralPath $Dest -Force
    if ($destItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
        Die "refusing to follow symlink $Dest"
    }
    if (-not $destItem.PSIsContainer) {
        Die "refusing $Dest (not a directory)"
    }
}

$ScriptDir = $PSScriptRoot
$Mode = ''
$Src = ''
$AddonRoot = ''
if ($ScriptDir -and (Test-Path -LiteralPath (Join-Path $ScriptDir 'skills\hstack\hstack\SKILL.md'))) {
    $Mode = 'local'
    $Src = Join-Path $ScriptDir 'skills\hstack'
    $AddonRoot = $ScriptDir
}

function Invoke-Addons([string]$ModeName) {
    if ($ModeName -ne 'uninstall' -and $With.Count -eq 0) {
        return
    }
    $addonDir = Join-Path $FullHome 'hstack'
    if ($ModeName -eq 'uninstall' -and $With.Count -eq 0 -and -not (Test-Path -LiteralPath $addonDir)) {
        return
    }
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        Die 'python is required for addons'
    }
    $py = $null
    $repoPy = if ($AddonRoot) { Join-Path $AddonRoot 'scripts\apply_addons.py' } else { $null }
    $homePy = Join-Path $addonDir 'apply_addons.py'
    $scriptPy = if ($ScriptDir) { Join-Path $ScriptDir 'scripts\apply_addons.py' } else { $null }
    foreach ($candidate in @($repoPy, $homePy, $scriptPy)) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            $py = $candidate
            break
        }
    }
    if (-not $py) {
        if ($Dry) {
            Say "dry-run: would configure addons: $($With -join ',')"
            return
        }
        Die 'missing scripts/apply_addons.py'
    }
    $pyArgs = @($py, '--hermes-home', $FullHome)
    if ($AddonRoot) {
        $pyArgs += @('--source', $AddonRoot)
    }
    if ($Dry) { $pyArgs += '--dry-run' }
    if ($ModeName -eq 'uninstall') { $pyArgs += '--uninstall' }
    if ($With.Count -gt 0) { $pyArgs += @('--with', ($With -join ',')) }
    & $python.Source @pyArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

if ($Uninstall -and $With.Count -gt 0) {
    Invoke-Addons 'uninstall'
    exit 0
}

if ($Uninstall) {
    if (-not (Test-Path -LiteralPath $Dest)) {
        Say "nothing to remove at $Dest"
    } else {
        if (-not (Test-Path -LiteralPath $Marker)) {
            Die "refusing to remove $Dest (missing .hstack-managed)"
        }
        $markerItem = Get-Item -LiteralPath $Marker -Force
        if ($markerItem.Attributes -band [System.IO.FileAttributes]::ReparsePoint) {
            Die "refusing to remove $Dest (missing .hstack-managed)"
        }
        if ($Dry) {
            Say "dry-run: would remove $Dest"
        } else {
            Remove-Item -LiteralPath $Dest -Recurse -Force
            Say "removed $Dest"
        }
    }
    Invoke-Addons 'uninstall'
    exit 0
}

if ((Test-Path -LiteralPath $Dest) -and -not (Test-Path -LiteralPath $Marker)) {
    $entries = @(Get-ChildItem -LiteralPath $Dest -Force)
    if ($entries.Count -gt 0) {
        Die "refusing to overwrite non-empty $Dest (not an HStack install)"
    }
}

if (-not $Mode) {
    $Mode = 'remote'
    $Ref = if ($env:HSTACK_REF) { $env:HSTACK_REF } else { 'main' }
    if ($Ref -notmatch '^[A-Za-z0-9._-]+$' -or $Ref.StartsWith('-') -or $Ref.Contains('..')) {
        Die 'refusing HSTACK_REF'
    }
    $Url = "https://github.com/Belweave/hstack/archive/refs/heads/$Ref.tar.gz"
}

if ($Dry) {
    Say "dry-run: would install into $Dest"
    if ($Mode -eq 'local') {
        Say "dry-run: source tree $Src"
    } else {
        Say "dry-run: would download $Url"
    }
    Invoke-Addons 'install'
    exit 0
}

if ($Mode -eq 'remote') {
    $Work = Join-Path ([System.IO.Path]::GetTempPath()) ("hstack-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $Work | Out-Null
    try {
        $archive = Join-Path $Work 'hstack.tar.gz'
        Invoke-WebRequest -Uri $Url -OutFile $archive
        $members = & tar -tzf $archive
        if ($LASTEXITCODE -ne 0) { Die 'could not read archive' }
        foreach ($member in $members) {
            if (-not $member -or $member.StartsWith('/') -or $member.StartsWith('\') -or $member.Contains('..')) {
                Die 'archive member is absolute or contains ..'
            }
        }
        & tar -xzf $archive -C $Work
        if ($LASTEXITCODE -ne 0) { Die 'could not extract archive' }
        $tops = @(Get-ChildItem -LiteralPath $Work -Directory)
        if ($tops.Count -ne 1) { Die 'expected one top-level directory in the archive' }
        $Src = Join-Path $tops[0].FullName 'skills\hstack'
        $AddonRoot = $tops[0].FullName
        if (-not (Test-Path -LiteralPath (Join-Path $Src 'hstack\SKILL.md'))) {
            Die 'archive is missing skills/hstack/hstack/SKILL.md'
        }
    } finally {
        if ($Mode -eq 'remote' -and (Test-Path -LiteralPath $Work) -and -not $Src) {
            Remove-Item -LiteralPath $Work -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}

if (-not (Test-Path -LiteralPath (Join-Path $Src 'hstack\SKILL.md'))) {
    Die 'missing skills/hstack/hstack/SKILL.md'
}
$links = @(Get-ChildItem -LiteralPath $Src -Recurse -Force | Where-Object { $_.Attributes -band [System.IO.FileAttributes]::ReparsePoint })
if ($links.Count -gt 0) {
    Die 'refusing to copy a link or special file from the skill tree'
}

$Parent = Split-Path -Parent $Dest
if (-not (Test-Path -LiteralPath $Parent)) {
    New-Item -ItemType Directory -Path $Parent | Out-Null
}
$Stage = Join-Path $Parent ('.hstack-stage.' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $Stage | Out-Null
Copy-Item -Path (Join-Path $Src '*') -Destination $Stage -Recurse -Force
if (-not (Test-Path -LiteralPath (Join-Path $Stage 'hstack\SKILL.md'))) {
    Die 'install tree is missing hstack/SKILL.md'
}
Set-Content -LiteralPath (Join-Path $Stage '.hstack-managed') -Value "managed-by: hstack install.sh`nversion: 0.1.0`n" -NoNewline -Encoding ascii

if (Test-Path -LiteralPath $Dest) {
    $Prev = Join-Path $Parent ('.hstack-prev.' + $PID)
    if (Test-Path -LiteralPath $Prev) { Die "temporary path already exists: $Prev" }
    Rename-Item -LiteralPath $Dest -NewName (Split-Path -Leaf $Prev)
    try {
        Rename-Item -LiteralPath $Stage -NewName (Split-Path -Leaf $Dest)
        Remove-Item -LiteralPath $Prev -Recurse -Force
    } catch {
        if (-not (Test-Path -LiteralPath $Dest) -and (Test-Path -LiteralPath $Prev)) {
            Rename-Item -LiteralPath $Prev -NewName (Split-Path -Leaf $Dest)
        }
        Die 'could not move the new tree into place'
    }
} else {
    Rename-Item -LiteralPath $Stage -NewName (Split-Path -Leaf $Dest)
}

Say "installed into $Dest"
Invoke-Addons 'install'
if ($Mode -eq 'remote') {
    $downloaded = Split-Path -Parent $AddonRoot
    if ($downloaded -and (Test-Path -LiteralPath $downloaded)) {
        Remove-Item -LiteralPath $downloaded -Recurse -Force -ErrorAction SilentlyContinue
    }
}
