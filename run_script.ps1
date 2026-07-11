# Generate short-video scripts from scored items

$ErrorActionPreference = "Continue"
$proj = $PSScriptRoot
. "$proj\scripts\pipeline_common.ps1"
Initialize-YokoPipeline $proj
Assert-DeepSeekKey

if ($args.Count -gt 0) {
    Write-Host "=== M3 script generation (custom args) ===" -ForegroundColor Cyan
    python -m yoko_video.m3.script @args
} else {
    $scriptTop = Get-YokoIntConfig "SCRIPT_TOP" 2
    Write-Host "=== M3 script generation (top $scriptTop) ===" -ForegroundColor Cyan
    python -m yoko_video.m3.script --top $scriptTop
}

if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$latest = Get-LatestFile (Join-Path $proj "data\scripts\*_scripts.md")
if ($latest) {
    Write-Host "Script generated: $($latest.FullName)" -ForegroundColor Green
    Invoke-Item $latest.FullName
} else {
    Write-Host "Script file was not found. Check data\scripts\ or the errors above." -ForegroundColor Yellow
}
