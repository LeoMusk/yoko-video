# Convert an M3 script to remotion/props.json and preview or render a Remotion video.

param(
    [string]$Date = "",
    [int]$Index = 1,
    [string]$Composition = "YokoShort",
    [switch]$Preview
)

$ErrorActionPreference = "Stop"
$proj = $PSScriptRoot
. "$proj\scripts\pipeline_common.ps1"
Initialize-YokoPipeline $proj

if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js was not found. Remotion requires Node.js 18+." -ForegroundColor Red
    exit 2
}

$bridgeArgs = @()
if ($Date) {
    $bridgeArgs += @("--date", $Date)
} else {
    $bridgeArgs += "--latest"
}
$bridgeArgs += @("--index", [string]$Index, "--out", "remotion\props.json")

python scripts\script_to_remotion_props.py @bridgeArgs
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

Push-Location (Join-Path $proj "remotion")
try {
    if (-not (Test-Path "node_modules")) {
        Write-Host "Installing Remotion npm dependencies for the first run..." -ForegroundColor Yellow
        npm install
    }

    if ($Preview) {
        npm run studio
    } else {
        $outDir = Join-Path $proj "out\remotion"
        New-Item -ItemType Directory -Force -Path $outDir | Out-Null
        $stamp = if ($Date) { $Date } else { (Get-Date).ToString("yyyyMMdd-HHmmss") }
        $outFile = Join-Path $outDir "$stamp-$Composition-$Index.mp4"
        npx remotion render src/index.ts $Composition $outFile
        Write-Host "Video rendered: $outFile" -ForegroundColor Green
    }
} finally {
    Pop-Location
}
