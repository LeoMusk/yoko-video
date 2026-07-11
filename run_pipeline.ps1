# Backward-compatible alias. Prefer run_news.bat / run_all.bat for public usage.

$proj = $PSScriptRoot
& "$proj\run_news.ps1"
exit $LASTEXITCODE
