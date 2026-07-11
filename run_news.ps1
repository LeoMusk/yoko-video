# Generate AI news brief: M1 collect -> M2 score -> open brief

$ErrorActionPreference = "Continue"
$proj = $PSScriptRoot
. "$proj\scripts\pipeline_common.ps1"
Initialize-YokoPipeline $proj
Assert-PythonModule "feedparser" "Run: pip install -r requirements.txt"
Assert-DeepSeekKey

$sinceDays = Get-YokoIntConfig "NEWS_SINCE_DAYS" 3
$maxUnscored = Get-YokoIntConfig "MAX_UNSCORED" 120
$briefTopN = Get-YokoIntConfig "BRIEF_TOP_N" 40

$sourceCount = python -c "from yoko_video.m1.sources import SOURCES; print(len(SOURCES))"
Write-Host "=== [1/2] M1 collect (last $sinceDays days, $sourceCount sources) ===" -ForegroundColor Cyan
python -m yoko_video.m1.collect --since-days $sinceDays
$m1Code = $LASTEXITCODE
if ($m1Code -ne 0) {
    Write-Host "Some M1 sources failed. Continuing with collected data." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "=== [2/2] M2 score (incremental, max $maxUnscored items, top $briefTopN) ===" -ForegroundColor Cyan
python -m yoko_video.m2.score --only-unscored --max-unscored $maxUnscored --top-n $briefTopN
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

$today = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
$brief = Join-Path $proj "data\scored\$($today)_brief.md"
if (-not (Test-Path $brief)) {
    $latest = Get-LatestFile (Join-Path $proj "data\scored\*_brief.md")
    if ($latest) {
        $brief = $latest.FullName
    }
}

Write-Host ""
if (Test-Path $brief) {
    Write-Host "Brief generated: $brief" -ForegroundColor Green
    Invoke-Item $brief
} else {
    Write-Host "Brief was not found. Check data\scored\ or the errors above." -ForegroundColor Yellow
}
