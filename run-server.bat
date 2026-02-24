@echo off
setlocal

set MODEL=models\qwen3-1.7b-q4_k_m.gguf
set HOST=127.0.0.1
set PORT=8000
set CTX=8192
set MAX_TOKENS=256

if not exist "%MODEL%" (
    echo Model not found: %MODEL%
    echo Run: scripts\download-model.bat
    exit /b 1
)

:: Kill any existing process listening on this port
netstat -ano 2>nul | findstr ":%PORT% " | findstr "LISTENING" > "%TEMP%\talkbot_port.txt"
for /f "tokens=5" %%P in (%TEMP%\talkbot_port.txt) do (
    echo Stopping existing server on port %PORT% ^(PID %%P^)...
    taskkill /PID %%P /F >nul 2>&1
)
del "%TEMP%\talkbot_port.txt" >nul 2>&1

echo Starting llama-server on http://%HOST%:%PORT%
echo Model: %MODEL%
echo Context: %CTX% tokens
echo.
echo Keep this window open while using talkbot.
echo Press Ctrl+C to stop the server.
echo.

tools\llama-cpp\llama-server.exe ^
  -m %MODEL% ^
  --jinja ^
  -c %CTX% ^
  -n %MAX_TOKENS% ^
  --temp 0.7 ^
  --top-k 20 ^
  --top-p 0.8 ^
  --min-p 0 ^
  --presence-penalty 1.5 ^
  --host %HOST% ^
  --port %PORT%
