function Initialize-YokoPipeline {
    param([string]$ProjectRoot)

    [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    $env:PYTHONIOENCODING = "utf-8"
    $env:PYTHONPATH = $ProjectRoot
    Set-Location $ProjectRoot

    if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
        Write-Host "Python was not found. Install Python 3.10+ and make sure python is in PATH." -ForegroundColor Red
        exit 2
    }
}

function Get-YokoConfig {
    param(
        [string]$Name,
        [string]$Default = ""
    )

    $existing = [Environment]::GetEnvironmentVariable($Name)
    if ($existing) {
        return $existing
    }

    $envFile = Join-Path (Get-Location) ".env"
    if (Test-Path $envFile) {
        $pattern = "^\s*$([regex]::Escape($Name))\s*=\s*(.*)\s*$"
        foreach ($line in Get-Content -Encoding UTF8 $envFile) {
            $trimmed = $line.Trim()
            if (-not $trimmed -or $trimmed.StartsWith("#")) {
                continue
            }
            if ($line -match $pattern) {
                return $Matches[1].Trim().Trim('"').Trim("'")
            }
        }
    }

    return $Default
}

function Get-YokoIntConfig {
    param(
        [string]$Name,
        [int]$Default
    )

    $value = Get-YokoConfig $Name ([string]$Default)
    $parsed = 0
    if ([int]::TryParse($value, [ref]$parsed)) {
        return $parsed
    }
    return $Default
}

function Assert-PythonModule {
    param(
        [string]$ModuleName,
        [string]$InstallHint
    )

    python -c "import $ModuleName" *> $null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Missing Python dependency: $ModuleName" -ForegroundColor Red
        Write-Host $InstallHint -ForegroundColor Yellow
        exit 2
    }
}

function Assert-DeepSeekKey {
    $key = Get-YokoConfig "DEEPSEEK_API_KEY" ""
    if (-not $key -or $key -eq "your_deepseek_api_key_here") {
        Write-Host "DEEPSEEK_API_KEY is not configured." -ForegroundColor Red
        Write-Host "Copy .env.example to .env and fill in your DeepSeek API key." -ForegroundColor Yellow
        exit 2
    }
}

function Get-LatestFile {
    param([string]$Pattern)

    return Get-ChildItem -Path $Pattern -ErrorAction SilentlyContinue |
        Sort-Object LastWriteTime |
        Select-Object -Last 1
}
