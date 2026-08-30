#Requires -Version 5.1
<#
.SYNOPSIS
    Windows launcher for the CLS RAG+CAG Streamlit prototype.

    Mirrors scripts/launch_cls.sh: create .venv if needed, install packages,
    load cls.env, pick a free port, open the browser, run Streamlit.

    Double-click scripts/launch_cls.bat, or the Desktop shortcut this script
    can install with -InstallShortcut.
#>
[CmdletBinding()]
param(
    [switch]$InstallShortcut,
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"

$AppName = "CLS RAG+CAG Prototype"
$RootDir = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$VenvDir = Join-Path $RootDir ".venv"
$VenvPython = Join-Path $VenvDir "Scripts\python.exe"
$VenvStreamlit = Join-Path $VenvDir "Scripts\streamlit.exe"
$RequirementsMarker = Join-Path $VenvDir ".requirements-installed"
$RequirementsFile = Join-Path $RootDir "requirements.txt"
$Port = if ($env:STREAMLIT_PORT) { [int]$env:STREAMLIT_PORT } else { 8501 }

if ($env:LAUNCHER_DRY_RUN -eq "1") {
    $DryRun = $true
}

Set-Location $RootDir

function Say([string]$Message) {
    Write-Host ""
    Write-Host "[$AppName] $Message"
}

function Die([string]$Message) {
    Write-Host ""
    Write-Host "[$AppName] ERROR: $Message" -ForegroundColor Red
    Write-Host ""
    if ([Environment]::UserInteractive -and -not $DryRun) {
        Read-Host "Press Enter to close this window" | Out-Null
    }
    exit 1
}

function Get-Flag([string]$Name, [string]$Default = "1") {
    $value = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($value)) { return $Default }
    return $value
}

function Test-FlagOff([string]$Name) {
    $value = (Get-Flag $Name "1").Trim().ToLowerInvariant()
    return ($value -eq "0" -or $value -eq "false")
}

function Pick-Python {
    $py = Get-Command py -ErrorAction SilentlyContinue
    if ($py) {
        try {
            & py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" | Out-Null
            if ($LASTEXITCODE -eq 0) {
                return @{ File = "py"; Args = @("-3") }
            }
        } catch { }
    }

    foreach ($name in @("python", "python3")) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if (-not $cmd) { continue }
        $resolved = $cmd.Source
        if ($resolved -match "WindowsApps") { continue }
        try {
            & $resolved -c "import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)" | Out-Null
            if ($LASTEXITCODE -eq 0) {
                return @{ File = $resolved; Args = @() }
            }
        } catch { }
    }

    Die "Python 3.10+ was not found. Install Python from python.org, then run this launcher again."
}

function Invoke-Python($Python, [string[]]$Arguments) {
    & $Python.File @($Python.Args + $Arguments)
    if ($LASTEXITCODE -ne 0) {
        throw "Python command failed: $($Arguments -join ' ')"
    }
}

function Load-EnvFile {
    $envFile = Join-Path $RootDir "cls.env"
    if (-not (Test-Path $envFile)) { return }

    Say "Loading config from cls.env"
    Get-Content -Path $envFile -Encoding UTF8 | ForEach-Object {
        $line = $_.Trim()
        if ($line -eq "" -or $line.StartsWith("#")) { return }
        if ($line.StartsWith("export ")) {
            $line = $line.Substring(7).Trim()
        }
        $eq = $line.IndexOf("=")
        if ($eq -lt 1) { return }
        $name = $line.Substring(0, $eq).Trim()
        $value = $line.Substring($eq + 1).Trim()
        if (($value.StartsWith('"') -and $value.EndsWith('"')) -or
            ($value.StartsWith("'") -and $value.EndsWith("'"))) {
            $value = $value.Substring(1, $value.Length - 2)
        }
        if ($name -match "^[A-Za-z_][A-Za-z0-9_]*$") {
            Set-Item -Path "Env:$name" -Value $value
        }
    }
}

function Ensure-Venv($Python) {
    if (Test-Path $VenvPython) { return }
    Say "Creating the local Python environment..."
    try {
        Invoke-Python $Python @("-m", "venv", $VenvDir)
    } catch {
        Die "Could not create .venv."
    }
}

function Ensure-Requirements {
    $needsInstall = $false
    if (-not (Test-Path $VenvStreamlit)) { $needsInstall = $true }
    if (-not (Test-Path $RequirementsMarker)) { $needsInstall = $true }
    if ((Test-Path $RequirementsMarker) -and (Test-Path $RequirementsFile)) {
        if ((Get-Item $RequirementsFile).LastWriteTime -gt (Get-Item $RequirementsMarker).LastWriteTime) {
            $needsInstall = $true
        }
    }
    if (-not $needsInstall) { return }

    Say "Installing or refreshing Python packages (first run can take several minutes)..."
    & $VenvPython -m pip install -r $RequirementsFile
    if ($LASTEXITCODE -ne 0) {
        Die "Package installation failed."
    }
    New-Item -ItemType File -Path $RequirementsMarker -Force | Out-Null
}

function Pick-Port {
    $finder = @'
import socket
import sys

start = int(sys.argv[1])
for port in range(start, start + 50):
    sock = socket.socket()
    try:
        sock.bind(("127.0.0.1", port))
    except OSError:
        continue
    finally:
        sock.close()
    print(port)
    break
else:
    raise SystemExit("No open Streamlit port found.")
'@
    $chosen = $finder | & $VenvPython - $Port
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace("$chosen")) {
        Die "Could not find an open local port."
    }
    $line = @($chosen)[-1].ToString().Trim()
    return [int]$line
}

function Install-DesktopShortcut {
    $desktop = [Environment]::GetFolderPath("Desktop")
    if ([string]::IsNullOrWhiteSpace($desktop) -or -not (Test-Path $desktop)) {
        Die "Could not find the Windows Desktop folder."
    }

    $batPath = Join-Path $PSScriptRoot "launch_cls.bat"
    if (-not (Test-Path $batPath)) {
        Die "launch_cls.bat is missing next to this script."
    }

    $lnkPath = Join-Path $desktop "CLS RAG+CAG.lnk"
    $shell = New-Object -ComObject WScript.Shell
    $shortcut = $shell.CreateShortcut($lnkPath)
    $shortcut.TargetPath = $batPath
    $shortcut.WorkingDirectory = $RootDir
    $shortcut.WindowStyle = 1
    $shortcut.Description = "Launch the CLS RAG+CAG Streamlit prototype"
    if (Test-Path $VenvPython) {
        $shortcut.IconLocation = "$VenvPython,0"
    } else {
        $python = Pick-Python
        if ($python.File -ne "py" -and (Test-Path $python.File)) {
            $shortcut.IconLocation = "$($python.File),0"
        }
    }
    $shortcut.Save()
    Say "Desktop shortcut saved to $lnkPath"
    return $lnkPath
}

if ($InstallShortcut) {
    $null = Install-DesktopShortcut
    if (-not $DryRun -and -not $PSBoundParameters.ContainsKey("DryRun")) {
        # Installing the icon alone is a valid invocation.
        exit 0
    }
}

Say "Preparing launch from $RootDir"
Load-EnvFile
$Python = Pick-Python
Ensure-Venv $Python
Ensure-Requirements

if (Test-FlagOff "CLS_RETRIEVAL_ONLY") {
    Say "Carrier synthesis/cleanup use CLS_DLLM_API_URL when configured."
} else {
    Say "Retrieval-only mode active. LLM synthesis/cleanup are disabled."
}

if (Test-FlagOff "CLS_KEYWORD_ONLY") {
    Say "Hybrid semantic+keyword retrieval active."
} else {
    Say "Keyword-only retrieval active for fastest deterministic searches."
}

$Port = Pick-Port
$Url = "http://localhost:$Port"

if ($DryRun) {
    Say "Dry run complete. Streamlit would launch on $Url"
    exit 0
}

Say "Launching Streamlit at $Url"
if ((Get-Flag "CLS_USE_API" "0") -eq "1") {
    $apiUrl = Get-Flag "CLS_API_URL" "http://127.0.0.1:8010"
    Say "API bridge enabled via CLS_API_URL=$apiUrl"
}

try {
    Start-Process $Url | Out-Null
} catch { }

# Do not invoke streamlit.exe directly.  Windows console-script launchers embed
# the virtualenv path that existed when pip installed them; this workspace has
# been moved, so that path can become stale.  Running the module through this
# venv's current python.exe remains valid after a folder move or rename.
& $VenvPython -m streamlit run (Join-Path $RootDir "app.py") `
    --server.port $Port `
    --server.headless true `
    --browser.gatherUsageStats false

if ($LASTEXITCODE -ne 0) {
    Die "Streamlit exited with code $LASTEXITCODE."
}
