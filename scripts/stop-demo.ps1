$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$processFile = Join-Path $repo 'tmp/hello-world/processes.json'
if (-not (Test-Path -LiteralPath $processFile)) {
    Write-Output 'Khong co danh sach dich vu cua demo.'
    exit 0
}

foreach ($saved in (Get-Content -LiteralPath $processFile -Raw | ConvertFrom-Json)) {
    $process = Get-Process -Id $saved.Id -ErrorAction SilentlyContinue
    if ($process -and $process.StartTime.ToUniversalTime().Ticks -eq $saved.StartTime) {
        # Dung ca Python con cua venv; chi thao tac tren cay tien trinh da ghi nhan.
        taskkill /PID $process.Id /T /F | Out-Null
    }
}
Remove-Item -LiteralPath $processFile
Write-Output 'Da dung cac dich vu cua demo.'
