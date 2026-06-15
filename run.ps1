$ErrorActionPreference = "Stop"

Set-Location $PSScriptRoot

function Test-PythonCommand {
    param([string[]]$CommandParts)
    try {
        $args = @()
        if ($CommandParts.Length -gt 1) {
            $args = $CommandParts[1..($CommandParts.Length - 1)]
        }
        & $CommandParts[0] @args -c "import sys" *> $null
        return $LASTEXITCODE -eq 0
    }
    catch {
        return $false
    }
}

$pythonCommand = $null
if (Test-PythonCommand @("python")) {
    $pythonCommand = @("python")
}
elseif (Test-PythonCommand @("py", "-3")) {
    $pythonCommand = @("py", "-3")
}

if (-not $pythonCommand) {
    Write-Host "[ERROR] Python was not found. Please install Python 3.10+ and try again." -ForegroundColor Red
    exit 1
}

$venvPython = Join-Path $PSScriptRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "[INFO] Creating virtual environment..."
    $pythonArgs = @()
    if ($pythonCommand.Length -gt 1) {
        $pythonArgs = $pythonCommand[1..($pythonCommand.Length - 1)]
    }
    & $pythonCommand[0] @pythonArgs -m venv .venv
}

Write-Host "[INFO] Installing or updating dependencies..."
& $venvPython -m pip install --upgrade pip
& $venvPython -m pip install -r requirements.txt

Write-Host "[INFO] Starting Streamlit at http://localhost:8501 ..."
& $venvPython -m streamlit run app.py --server.headless=false
