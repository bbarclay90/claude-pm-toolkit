# Runs /brief for the active product and logs the result.
# Schedule with Windows Task Scheduler. On macOS or Linux, see README for a cron line.

$ProjectDir = Split-Path -Parent $PSScriptRoot
$LogDir = Join-Path $ProjectDir "logs"
$LogFile = Join-Path $LogDir "brief-$(Get-Date -Format 'yyyy-MM-dd').log"

if (-not (Test-Path $LogDir)) { New-Item -ItemType Directory -Path $LogDir | Out-Null }

function Log($msg) {
    $line = "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $msg"
    Add-Content -Path $LogFile -Value $line
    Write-Output $line
}

Set-Location $ProjectDir
$Product = (& python -c "import sys; sys.path.insert(0, 'scripts'); import config; print(config.active_product())" 2>&1)
Log "Starting daily brief for $Product..."

# Headless runs cannot prompt for permission, so allow the tools /brief needs.
$output = & claude --print "/brief" --allowedTools "WebSearch,WebFetch,Read,Write,Edit,Glob" 2>&1
$exitCode = $LASTEXITCODE

if ($exitCode -eq 0) {
    Log "Brief completed successfully."
} else {
    Log "Brief failed (exit code $exitCode)."
    Log "Output: $output"
}
