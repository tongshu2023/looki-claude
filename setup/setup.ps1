# looki-claude · Windows 初始化脚本
# 用法:powershell ./setup/setup.ps1

$ErrorActionPreference = 'Stop'

Write-Host "===== looki-claude setup (Windows) =====" -ForegroundColor Cyan

# 1. 检查 Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "[x] 未找到 python,请先装 Python 3.8+" -ForegroundColor Red
    exit 1
}
Write-Host "[√] Python: $($py.Source)" -ForegroundColor Green

# 2. 检查 ffmpeg(可选,用于视频抽帧)
$ff = Get-Command ffmpeg -ErrorAction SilentlyContinue
if (-not $ff) {
    $winget = Get-ChildItem "$env:LOCALAPPDATA\Microsoft\WinGet\Packages" -Filter "Gyan.FFmpeg*" -ErrorAction SilentlyContinue
    if ($winget) {
        Write-Host "[√] ffmpeg (winget): 已装,但未加入 PATH(代码会自动查找)" -ForegroundColor Green
    } else {
        Write-Host "[!] 未装 ffmpeg — 如需视频抽帧,运行:winget install Gyan.FFmpeg" -ForegroundColor Yellow
    }
} else {
    Write-Host "[√] ffmpeg: $($ff.Source)" -ForegroundColor Green
}

# 3. 要 API Key
Write-Host ""
Write-Host "===== 配置 API Key =====" -ForegroundColor Cyan
Write-Host "获取 Key 的位置:登录 https://web.looki.tech/api-keys → 申请访问权限 → 创建 Key"
Write-Host "Key 形如 'lk-xxxxxxxxxxxxxxxxxxxx'(只显示一次,请妥善保管)"
Write-Host ""
$key = Read-Host "粘贴你的 Looki API Key"
if (-not $key -or -not $key.StartsWith("lk-")) {
    Write-Host "[x] Key 格式不对,应以 lk- 开头" -ForegroundColor Red
    exit 1
}

# 4. 写入 credentials.json
$credDir = Join-Path $env:USERPROFILE ".looki"
if (-not (Test-Path $credDir)) { New-Item -ItemType Directory -Path $credDir | Out-Null }
$credPath = Join-Path $credDir "credentials.json"
$data = @{
    base_url = "https://open.looki.tech/api/v1"
    api_key = $key
    created_at = (Get-Date -Format "yyyy-MM-dd")
    note = "Looki API credentials. 永远不要提交到 git。"
} | ConvertTo-Json -Depth 3
[System.IO.File]::WriteAllText($credPath, $data, [System.Text.UTF8Encoding]::new($false))
Write-Host "[√] 凭证已写入: $credPath" -ForegroundColor Green

# 5. 验证
Write-Host ""
Write-Host "===== 验证连接 =====" -ForegroundColor Cyan
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$clientPy = Join-Path (Split-Path -Parent $scriptDir) "src\looki_client.py"
$result = & python $clientPy me 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "[√] 连接成功" -ForegroundColor Green
    Write-Host $result
    Write-Host ""
    Write-Host "安装完成!试试:" -ForegroundColor Cyan
    Write-Host "  python src\looki_client.py search 薄荷"
    Write-Host "  python src\looki_client.py calendar 2026-04-01 2026-04-22"
} else {
    Write-Host "[x] 连接失败:" -ForegroundColor Red
    Write-Host $result
    exit 1
}
