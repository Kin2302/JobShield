$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $repo 'tmp/hello-world'
$python = Join-Path $repo 'services/ai/.venv/Scripts/python.exe'
$backend = Join-Path $repo 'backend/bin/Release/net10.0/backend.dll'
$vite = Join-Path $repo 'frontend/node_modules/vite/bin/vite.js'

foreach ($required in @($python, $backend, $vite, (Join-Path $repo 'frontend/dist/index.html'))) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Thieu file $required. Hay cai dat va build theo README truoc."
    }
}

foreach ($port in @(5000, 5173, 8001)) {
    $socket = [System.Net.Sockets.TcpClient]::new()
    try {
        if ($socket.ConnectAsync('127.0.0.1', $port).Wait(300) -and $socket.Connected) {
            throw "Cong $port dang duoc su dung. Dung demo cu hoac kiem tra dich vu truoc."
        }
    } catch [System.AggregateException] {
        # Chua co dich vu lang nghe: co the khoi dong.
    } finally {
        $socket.Dispose()
    }
}

New-Item -ItemType Directory -Force -Path $runtime | Out-Null
$started = @()
try {
    $started += Start-Process -FilePath $python -ArgumentList '-m uvicorn main:app --host 127.0.0.1 --port 8001' -WorkingDirectory (Join-Path $repo 'services/ai') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'ai.log') -RedirectStandardError (Join-Path $runtime 'ai-error.log')
    $started += Start-Process -FilePath (Get-Command dotnet).Source -ArgumentList ('"' + $backend + '" --urls http://127.0.0.1:5000') -WorkingDirectory (Join-Path $repo 'backend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'backend.log') -RedirectStandardError (Join-Path $runtime 'backend-error.log')
    $started += Start-Process -FilePath (Get-Command node).Source -ArgumentList ('"' + $vite + '" preview') -WorkingDirectory (Join-Path $repo 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'frontend.log') -RedirectStandardError (Join-Path $runtime 'frontend-error.log')

    $ready = $false
    for ($attempt = 0; $attempt -lt 30; $attempt++) {
        foreach ($process in $started) {
            if ($process.HasExited) { throw 'Dich vu da thoat. Xem log trong tmp/hello-world.' }
        }
        try {
            $null = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -TimeoutSec 2 -UseBasicParsing
            $body = @{ text = 'Hello World' } | ConvertTo-Json
            $null = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:5173/api/analyze' -ContentType 'application/json' -Body $body -TimeoutSec 3
            $ready = $true
            break
        } catch {
            Start-Sleep -Milliseconds 300
        }
    }
    if (-not $ready) { throw 'Demo khong san sang. Xem log trong tmp/hello-world.' }

    $started | ForEach-Object {
        @{ Id = $_.Id; StartTime = $_.StartTime.ToUniversalTime().Ticks }
    } | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $runtime 'processes.json')
    Write-Output 'Demo san sang: http://127.0.0.1:5173'
    Write-Output 'Dung demo: powershell -File scripts/stop-demo.ps1'
} catch {
    $started | Where-Object { -not $_.HasExited } | Stop-Process -Force
    throw
}
