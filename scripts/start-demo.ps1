$ErrorActionPreference = 'Stop'
$repo = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $repo 'tmp/hello-world'
$python = Join-Path $repo 'services/ai/.venv/Scripts/python.exe'
$backend = Join-Path $repo 'backend/JobShield.Api/bin/Release/net10.0/JobShield.Api.dll'
$vite = Join-Path $repo 'frontend/node_modules/vite/bin/vite.js'

$nodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeCmd) {
    $fnmDir = Join-Path $env:APPDATA 'fnm\node-versions'
    $fnmNode = if (Test-Path -LiteralPath $fnmDir) {
        Get-ChildItem -Path $fnmDir -Filter 'node.exe' -Recurse -Depth 2 -ErrorAction SilentlyContinue | Select-Object -First 1
    }
    if ($fnmNode) {
        $env:PATH = "$($fnmNode.DirectoryName);$env:PATH"
        $nodeCmd = Get-Command node -ErrorAction SilentlyContinue
    }
}
if (-not $nodeCmd) {
    throw 'Khong tim thay node.exe trong PATH hoac fnm.'
}

if (-not $env:JOBSHIELD_MODEL_DIR) {
    $env:JOBSHIELD_MODEL_DIR = Join-Path $repo 'models/v3/jobshield-phobert-v3-typeA'
}
if (-not $env:JOBSHIELD_VNCORENLP_DIR) {
    $env:JOBSHIELD_VNCORENLP_DIR = Join-Path $repo 'models/vncorenlp'
}
if (-not $env:JAVA_HOME) {
    $defaultJdk = 'C:/Program Files/Microsoft/jdk-21.0.13.21-hotspot'
    if (Test-Path -LiteralPath $defaultJdk) {
        $env:JAVA_HOME = $defaultJdk
    }
}

foreach ($required in @(
    $python,
    $backend,
    $vite,
    (Join-Path $repo 'frontend/dist/index.html'),
    (Join-Path $env:JOBSHIELD_MODEL_DIR 'model_meta.json'),
    (Join-Path $env:JOBSHIELD_VNCORENLP_DIR 'VnCoreNLP-1.2.jar')
)) {
    if (-not (Test-Path -LiteralPath $required)) {
        throw "Thieu file $required. Hay cai dat, build va kiem tra duong dan model/VnCoreNLP truoc."
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
    $started += Start-Process -FilePath (Get-Command dotnet).Source -ArgumentList ('"' + $backend + '" --environment Development --urls http://127.0.0.1:5000') -WorkingDirectory (Join-Path $repo 'backend/JobShield.Api') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'backend.log') -RedirectStandardError (Join-Path $runtime 'backend-error.log')
    $started += Start-Process -FilePath (Get-Command node).Source -ArgumentList ('"' + $vite + '" preview') -WorkingDirectory (Join-Path $repo 'frontend') -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $runtime 'frontend.log') -RedirectStandardError (Join-Path $runtime 'frontend-error.log')

    $ready = $false
    for ($attempt = 0; $attempt -lt 60; $attempt++) {
        foreach ($process in $started) {
            if ($process.HasExited) { throw 'Dich vu da thoat. Xem log trong tmp/hello-world.' }
        }
        try {
            $health = Invoke-RestMethod -Uri 'http://127.0.0.1:8001/health' -TimeoutSec 2
            if ($health.status -ne 'ok') { throw 'AI health not ok' }
            $null = Invoke-WebRequest -Uri 'http://127.0.0.1:5173' -TimeoutSec 2 -UseBasicParsing
            $bodyJson = @{ text = 'Tuyển nhân viên bán hàng, phỏng vấn trực tiếp.' } | ConvertTo-Json
            $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($bodyJson)
            $null = Invoke-RestMethod -Method Post -Uri 'http://127.0.0.1:5173/api/analyze' -ContentType 'application/json; charset=utf-8' -Body $bodyBytes -TimeoutSec 15
            $ready = $true
            break
        } catch {
            Start-Sleep -Milliseconds 500
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
