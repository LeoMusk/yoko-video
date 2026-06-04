# yoko-video 一键管道：M1 信息采集 → M2 选题评分 → 打开当日简报
# 用法：双击 run_pipeline.bat，或在项目根右键"用 PowerShell 运行"

$ErrorActionPreference = "Continue"
$proj = $PSScriptRoot
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONPATH = $proj
Set-Location $proj

Write-Host "=== [1/2] M1 信息采集（近 7 天，22 源）===" -ForegroundColor Cyan
python -m yoko_video.m1.collect --since-days 7

Write-Host ""
Write-Host "=== [2/2] M2 选题评分（增量，仅评新条目）===" -ForegroundColor Cyan
python -m yoko_video.m2.score --only-unscored --top-n 40

# 当日 brief 用 UTC 日期命名（与 collect.py 一致）
$today = (Get-Date).ToUniversalTime().ToString("yyyy-MM-dd")
$brief = Join-Path $proj "data\scored\$($today)_brief.md"

Write-Host ""
if (Test-Path $brief) {
    Write-Host "选题简报已生成: $brief" -ForegroundColor Green
    Invoke-Item $brief
} else {
    Write-Host "未找到当日 brief: $brief" -ForegroundColor Yellow
    Write-Host "（可能今天暂无新数据，或 UTC 日期与预期不同，去 data\scored\ 看最新文件）" -ForegroundColor Yellow
}
