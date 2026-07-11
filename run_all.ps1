# Generate news brief and short-video scripts

$ErrorActionPreference = "Continue"
$proj = $PSScriptRoot

& "$proj\run_news.ps1"
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& "$proj\run_script.ps1"
exit $LASTEXITCODE
