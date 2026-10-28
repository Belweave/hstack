# Install HStack into Hermes Agent on Windows.
#   powershell -File install.ps1 [--dry-run] [--uninstall] [--with name,name]
# Skills go to $env:HERMES_HOME\skills\hstack, or $env:USERPROFILE\.hermes\skills\hstack.
# A second run replaces an install this script created. It will not touch
# any other skill, and it will not delete a directory it did not mark.

$ErrorActionPreference = 'Stop'

$Dry = $false
$Uninstall = $false
$AddonNames = @('browser', 'github', 'docs', 'search', 'perf', 'test', 'security', 'trail')
$HookNames = @('hermes-hooks', 'hermes-hooks-guard', 'hermes-hooks-save', 'hermes-hooks-suggest')
$AddonWith = New-Object System.Collections.Generic.List[string]
$HookWith = New-Object System.Collections.Generic.List[string]

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
--with hermes-hooks adds optional shell hooks. Subsets are
hermes-hooks-guard, hermes-hooks-save, and hermes-hooks-suggest.
The download form fetches the archive from hstack.sh.
HSTACK_BASE_URL overrides that host. HSTACK_VERSION pins a release.
Running this file from a git checkout installs that checkout.
'@
}

function Add-WithNames([string]$Raw) {
    if ([string]::IsNullOrWhiteSpace($Raw)) {
        Die '--with needs a comma-separated list'
    }
    foreach ($name in $Raw.Split(',')) {
        $trimmed = $name.Trim()
        if (-not $trimmed) {
            Die 'unknown addon: empty'
        }
        if ($AddonNames -contains $trimmed) {
            if (-not $AddonWith.Contains($trimmed)) { [void]$AddonWith.Add($trimmed) }
        } elseif ($HookNames -contains $trimmed) {
            if (-not $HookWith.Contains($trimmed)) { [void]$HookWith.Add($trimmed) }
        } else {
            Die "unknown addon: $trimmed"
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
        Add-WithNames $arg.Substring(7)
    } elseif ($arg -eq '--with') {
        $index++
        if ($index -ge $args.Count) {
            Die '--with needs a comma-separated list'
        }
        Add-WithNames ([string]$args[$index])
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

function Invoke-PythonTool([string]$Kind, [string]$ScriptName, $Names, [string]$ModeName) {
    if ($ModeName -ne 'uninstall' -and $Names.Count -eq 0) {
        return
    }
    $toolDir = Join-Path $FullHome 'hstack'
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $python = Get-Command python3 -ErrorAction SilentlyContinue
    }
    if (-not $python) {
        Die "python is required for $Kind"
    }
    $py = $null
    $repoPy = if ($AddonRoot) { Join-Path $AddonRoot "scripts\$ScriptName" } else { $null }
    $homePy = Join-Path $toolDir $ScriptName
    $scriptPy = if ($ScriptDir) { Join-Path $ScriptDir "scripts\$ScriptName" } else { $null }
    foreach ($candidate in @($repoPy, $homePy, $scriptPy)) {
        if ($candidate -and (Test-Path -LiteralPath $candidate)) {
            $py = $candidate
            break
        }
    }
    if (-not $py) {
        if ($Dry) {
            $shown = if ($Names.Count -gt 0) { $Names -join ',' } else { 'all' }
            Say "dry-run: would configure ${Kind}: $shown"
            return
        }
        if ($ModeName -eq 'uninstall' -and -not (Test-Path -LiteralPath $toolDir)) {
            return
        }
        Die "missing scripts/$ScriptName"
    }
    $pyArgs = @($py, '--hermes-home', $FullHome)
    if ($AddonRoot) {
        $pyArgs += @('--source', $AddonRoot)
    }
    if ($Dry) { $pyArgs += '--dry-run' }
    if ($ModeName -eq 'uninstall') { $pyArgs += '--uninstall' }
    if ($Names.Count -gt 0) { $pyArgs += @('--with', ($Names -join ',')) }
    & $python.Source @pyArgs
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}

function Invoke-Addons([string]$ModeName) {
    $marker = Join-Path (Join-Path $FullHome 'hstack') '.hstack-addons'
    if ($ModeName -eq 'uninstall' -and $AddonWith.Count -eq 0 -and -not (Test-Path -LiteralPath $marker)) {
        return
    }
    Invoke-PythonTool 'addons' 'apply_addons.py' $AddonWith $ModeName
}

function Invoke-Hooks([string]$ModeName) {
    $root = Join-Path $FullHome 'hstack'
    $marker = Join-Path $root '.hstack-hooks'
    $state = Join-Path $root 'hooks.json'
    if ($ModeName -eq 'uninstall' -and $HookWith.Count -eq 0 -and -not (Test-Path -LiteralPath $marker) -and -not (Test-Path -LiteralPath $state)) {
        return
    }
    Invoke-PythonTool 'hooks' 'apply_hooks.py' $HookWith $ModeName
}

function Test-CreatedConfig {
    foreach ($name in @('addons.json', 'hooks.json')) {
        $state = Join-Path (Join-Path $FullHome 'hstack') $name
        if (Test-Path -LiteralPath $state) {
            $text = [System.IO.File]::ReadAllText($state)
            if ($text.Contains('"created_config": true')) { return $true }
        }
    }
    return $false
}

if ($Uninstall -and ($AddonWith.Count -gt 0 -or $HookWith.Count -gt 0)) {
    if ($AddonWith.Count -gt 0) { Invoke-Addons 'uninstall' }
    if ($HookWith.Count -gt 0) { Invoke-Hooks 'uninstall' }
    exit 0
}

if ($Uninstall) {
    $configWasOurs = Test-CreatedConfig
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
    Invoke-Hooks 'uninstall'
    if (-not $Dry -and $configWasOurs) {
        $configPath = Join-Path $FullHome 'config.yaml'
        if (Test-Path -LiteralPath $configPath) {
            $flat = ([System.IO.File]::ReadAllText($configPath) -replace '\s', '')
            if (-not $flat) { Remove-Item -LiteralPath $configPath -Force }
        }
    }
    exit 0
}

if ((Test-Path -LiteralPath $Dest) -and -not (Test-Path -LiteralPath $Marker)) {
    $entries = @(Get-ChildItem -LiteralPath $Dest -Force)
    if ($entries.Count -gt 0) {
        Die "refusing to overwrite non-empty $Dest (not an HStack install)"
    }
}

$Url = ''
$Sum = ''
if (-not $Mode) {
    $Mode = 'remote'
    $Base = if ($env:HSTACK_BASE_URL) { $env:HSTACK_BASE_URL.TrimEnd('/') } else { 'https://hstack.sh' }
    if ($Base -notmatch '^https?://' -or $Base -match '\s|<|>|\.\.') {
        Die 'refusing HSTACK_BASE_URL'
    }
    $Name = 'hstack.tar.gz'
    if ($env:HSTACK_VERSION) {
        if ($env:HSTACK_VERSION -notmatch '^[0-9.]+$' -or $env:HSTACK_VERSION.Contains('..')) {
            Die 'refusing HSTACK_VERSION'
        }
        $Name = "hstack-v$($env:HSTACK_VERSION).tar.gz"
    }
    $Url = "$Base/dl/$Name"
    $Sum = "$Base/dl/$Name.sha256"
}

if ($Dry) {
    Say "dry-run: would install into $Dest"
    if ($Mode -eq 'local') {
        Say "dry-run: source tree $Src"
    } else {
        Say "dry-run: would download $Url"
        Say "dry-run: would verify $Sum"
    }
    Invoke-Addons 'install'
    Invoke-Hooks 'install'
    exit 0
}

if ($Mode -eq 'remote') {
    $Work = Join-Path ([System.IO.Path]::GetTempPath()) ("hstack-" + [guid]::NewGuid().ToString('N'))
    New-Item -ItemType Directory -Path $Work | Out-Null
    $RemoteOk = $false
    try {
        $archive = Join-Path $Work 'hstack.tar.gz'
        $sumfile = Join-Path $Work 'hstack.tar.gz.sha256'
        Invoke-WebRequest -Uri $Url -OutFile $archive -UseBasicParsing
        Invoke-WebRequest -Uri $Sum -OutFile $sumfile -UseBasicParsing
        if ((Get-Item -LiteralPath $archive).Length -lt 1 -or (Get-Item -LiteralPath $sumfile).Length -lt 1) {
            Die 'download was empty'
        }
        $stream = [System.IO.File]::OpenRead($archive)
        try {
            $b0 = $stream.ReadByte()
            $b1 = $stream.ReadByte()
        } finally {
            $stream.Dispose()
        }
        if ($b0 -ne 0x1f -or $b1 -ne 0x8b) {
            Die 'download was not a gzip archive'
        }
        $expected = ((Get-Content -LiteralPath $sumfile -TotalCount 1) -split '\s+', 2)[0]
        if ($expected -notmatch '^[0-9A-Fa-f]{64}$') {
            Die 'checksum was not a sha256 digest'
        }
        $actual = (Get-FileHash -LiteralPath $archive -Algorithm SHA256).Hash
        if ($actual.ToLowerInvariant() -ne $expected.ToLowerInvariant()) {
            Die 'checksum mismatch'
        }
        $members = & tar -tzf $archive
        if ($LASTEXITCODE -ne 0) { Die 'could not read archive' }
        foreach ($member in $members) {
            if (-not $member -or $member.StartsWith('/') -or $member.StartsWith('\') -or $member.Contains('..')) {
                Die 'archive member is absolute or contains ..'
            }
        }
        $listing = & tar -tvzf $archive
        if ($LASTEXITCODE -ne 0) { Die 'could not list archive' }
        foreach ($line in $listing) {
            if ($line.StartsWith('l') -or $line.StartsWith('h')) {
                Die 'archive contains a link; refusing to extract it'
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
        $RemoteOk = $true
    } finally {
        if (-not $RemoteOk -and (Test-Path -LiteralPath $Work)) {
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

$ver = '0.2.1'
$versionFile = if ($AddonRoot) { Join-Path $AddonRoot 'VERSION' } else { $null }
if ($versionFile -and (Test-Path -LiteralPath $versionFile)) {
    $digits = ([System.IO.File]::ReadAllText($versionFile) -replace '[^0-9.]', '')
    if ($digits) { $ver = $digits }
}
$Parent = Split-Path -Parent $Dest
if (-not (Test-Path -LiteralPath $Parent)) {
    New-Item -ItemType Directory -Path $Parent | Out-Null
}
$Stage = Join-Path $Parent ('.hstack-stage.' + [guid]::NewGuid().ToString('N').Substring(0, 8))
New-Item -ItemType Directory -Path $Stage | Out-Null
Copy-Item -Path (Join-Path $Src '*') -Destination $Stage -Recurse -Force
$stagedVersion = Join-Path $Stage 'VERSION'
if (Test-Path -LiteralPath $stagedVersion) {
    $digits = ([System.IO.File]::ReadAllText($stagedVersion) -replace '[^0-9.]', '')
    if ($digits) { $ver = $digits }
    Remove-Item -LiteralPath $stagedVersion -Force
}
if (-not (Test-Path -LiteralPath (Join-Path $Stage 'hstack\SKILL.md'))) {
    Die 'install tree is missing hstack/SKILL.md'
}
Set-Content -LiteralPath (Join-Path $Stage '.hstack-managed') -Value "managed-by: hstack install.sh`nversion: $ver`n" -NoNewline -Encoding ascii

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
Invoke-Hooks 'install'
if ($Mode -eq 'remote') {
    $downloaded = Split-Path -Parent $AddonRoot
    if ($downloaded -and (Test-Path -LiteralPath $downloaded)) {
        Remove-Item -LiteralPath $downloaded -Recurse -Force -ErrorAction SilentlyContinue
    }
}
