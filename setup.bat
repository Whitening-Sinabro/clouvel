@echo off
chcp 65001 >nul
title Clouvel 설치

echo.
echo   ╔═══════════════════════════════════════╗
echo   ║         Clouvel 설치 스크립트         ║
echo   ╚═══════════════════════════════════════╝
echo.

set "CONFIG_PATH=%APPDATA%\Claude\claude_desktop_config.json"
set "CONFIG_DIR=%APPDATA%\Claude"

echo   설정 파일: %CONFIG_PATH%
echo.

:: 폴더 생성
if not exist "%CONFIG_DIR%" (
    echo   → 설정 폴더 생성 중...
    mkdir "%CONFIG_DIR%"
)

:: PowerShell로 JSON 처리
powershell -ExecutionPolicy Bypass -Command ^
    "$configPath = '%CONFIG_PATH%'; " ^
    "$config = @{}; " ^
    "if (Test-Path $configPath) { " ^
    "    $backup = $configPath + '.backup.' + (Get-Date -Format 'yyyyMMddHHmmss'); " ^
    "    Copy-Item $configPath $backup; " ^
    "    Write-Host '  → 기존 설정 백업: ' $backup; " ^
    "    try { $config = Get-Content $configPath -Raw | ConvertFrom-Json -AsHashtable } catch { $config = @{} } " ^
    "} " ^
    "if (-not $config.ContainsKey('mcpServers')) { $config['mcpServers'] = @{} }; " ^
    "$config['mcpServers']['clouvel'] = @{ command = 'uvx'; args = @('clouvel') }; " ^
    "$config | ConvertTo-Json -Depth 10 | Set-Content $configPath -Encoding UTF8; " ^
    "Write-Host ''; " ^
    "Write-Host '  ✓ Clouvel MCP 서버 등록 완료!' -ForegroundColor Green"

echo.
echo   다음 단계:
echo   1. Claude Desktop 완전히 종료 (트레이에서도)
echo   2. Claude Desktop 다시 시작
echo   3. Claude한테 "docs 폴더 분석해줘" 하면 끝
echo.
echo   설정 파일: %CONFIG_PATH%
echo.
pause
