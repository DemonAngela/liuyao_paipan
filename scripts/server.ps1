[CmdletBinding()]
param(
    [Parameter(Position = 0)]
    [ValidateSet("start", "stop", "status")]
    [string]$Action = "start",

    [string]$ListenHost = "127.0.0.1",

    [ValidateRange(1, 65535)]
    [int]$Port = 8000,

    [switch]$Reload,
    [switch]$OpenBrowser
)

$ErrorActionPreference = "Stop"
$ProjectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$Python = Join-Path $ProjectRoot "venv\Scripts\python.exe"
$RuntimeDir = Join-Path $ProjectRoot "runtime"
$PidFile = Join-Path $RuntimeDir "server.json"
$StdoutLog = Join-Path $RuntimeDir "server.out.log"
$StderrLog = Join-Path $RuntimeDir "server.err.log"

function Get-ServerRecord {
    if (-not (Test-Path -LiteralPath $PidFile -PathType Leaf)) {
        return $null
    }
    try {
        return Get-Content -LiteralPath $PidFile -Raw -Encoding UTF8 |
            ConvertFrom-Json
    }
    catch {
        return $null
    }
}

function Get-MatchedProcess {
    param([object]$Record)

    if ($null -eq $Record) {
        return $null
    }
    $Process = Get-Process -Id ([int]$Record.pid) -ErrorAction SilentlyContinue
    if ($null -eq $Process) {
        return $null
    }
    if ($Process.StartTime.Ticks -ne [long]$Record.startTimeTicks) {
        return $null
    }
    $CimProcess = Get-CimInstance Win32_Process -Filter "ProcessId = $($Process.Id)"
    if ($CimProcess.CommandLine -notlike "*uvicorn*backend.main:app*") {
        return $null
    }
    return $Process
}

function Stop-ProcessTree {
    param([int]$ProcessId)

    $Children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $ProcessId"
    foreach ($Child in $Children) {
        Stop-ProcessTree -ProcessId ([int]$Child.ProcessId)
    }
    Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
}

function Remove-StaleRecord {
    if (Test-Path -LiteralPath $PidFile) {
        Remove-Item -LiteralPath $PidFile -Force
    }
}

$Record = Get-ServerRecord
$Existing = Get-MatchedProcess -Record $Record

if ($Action -eq "status") {
    if ($null -ne $Existing) {
        Write-Host "服务运行中：PID $($Existing.Id)，http://$($Record.host):$($Record.port)/"
        exit 0
    }
    Write-Host "服务未运行。"
    exit 1
}

if ($Action -eq "stop") {
    if ($null -eq $Existing) {
        Remove-StaleRecord
        Write-Host "服务未运行。"
        exit 0
    }
    Stop-ProcessTree -ProcessId $Existing.Id
    Remove-StaleRecord
    Write-Host "服务已停止。"
    exit 0
}

if ($null -ne $Existing) {
    $Url = "http://$($Record.host):$($Record.port)/"
    Write-Host "服务已在运行：$Url"
    if ($OpenBrowser) {
        Start-Process $Url
    }
    exit 0
}

Remove-StaleRecord
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "未找到虚拟环境 Python：$Python；请先按 README 安装依赖。"
}

New-Item -ItemType Directory -Path $RuntimeDir -Force | Out-Null
$Arguments = @(
    "-m", "uvicorn", "backend.main:app",
    "--host", $ListenHost,
    "--port", $Port.ToString()
)
if ($Reload) {
    $Arguments += "--reload"
}

$Server = Start-Process `
    -FilePath $Python `
    -ArgumentList $Arguments `
    -WorkingDirectory $ProjectRoot `
    -WindowStyle Hidden `
    -RedirectStandardOutput $StdoutLog `
    -RedirectStandardError $StderrLog `
    -PassThru

$ServerRecord = [ordered]@{
    pid = $Server.Id
    startTimeTicks = $Server.StartTime.Ticks
    host = $ListenHost
    port = $Port
}
$ServerRecord | ConvertTo-Json | Set-Content -LiteralPath $PidFile -Encoding UTF8

$HealthHost = if ($ListenHost -in @("0.0.0.0", "::")) {
    "127.0.0.1"
}
else {
    $ListenHost
}
$UrlHost = if ($HealthHost.Contains(":")) {
    "[$HealthHost]"
}
else {
    $HealthHost
}
$Url = "http://${UrlHost}:$Port/"
$Ready = $false
for ($Attempt = 0; $Attempt -lt 40; $Attempt += 1) {
    if ($Server.HasExited) {
        break
    }
    try {
        $Response = Invoke-WebRequest -UseBasicParsing -Uri "${Url}healthz" -TimeoutSec 1
        if ($Response.StatusCode -eq 200) {
            $Ready = $true
            break
        }
    }
    catch {
        Start-Sleep -Milliseconds 250
    }
}

if (-not $Ready) {
    Stop-ProcessTree -ProcessId $Server.Id
    Remove-StaleRecord
    $ErrorTail = if (Test-Path -LiteralPath $StderrLog) {
        Get-Content -LiteralPath $StderrLog -Tail 20 -Encoding UTF8
    }
    throw "服务未能就绪。`n$($ErrorTail -join "`n")"
}

Write-Host "服务已启动：$Url"
Write-Host "日志目录：$RuntimeDir"
if ($OpenBrowser) {
    Start-Process $Url
}
