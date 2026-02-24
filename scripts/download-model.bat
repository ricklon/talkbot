@echo off
setlocal enabledelayedexpansion

set DEFAULT_URL=https://huggingface.co/unsloth/Qwen3-1.7B-GGUF/resolve/main/Qwen3-1.7B-Q4_K_M.gguf
set DEFAULT_OUTPUT=models\default.gguf

set url=%DEFAULT_URL%
set output=%DEFAULT_OUTPUT%
set force=0

:parse_args
if "%~1"=="" goto :check_args
if /i "%~1"=="--output" (
    set output=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--url" (
    set url=%~2
    shift
    shift
    goto :parse_args
)
if /i "%~1"=="--force" (
    set force=1
    shift
    goto :parse_args
)
if /i "%~1"=="-h" goto :help
if /i "%~1"=="--help" goto :help

echo Unknown option: %~1 1>&2
goto :usage_err

:help
echo Download a default local GGUF model for TalkBot.
echo.
echo Usage:
echo   scripts\download-model.bat [--output PATH] [--url URL] [--force]
echo.
echo Options:
echo   --output PATH   Destination file path (default: models\default.gguf)
echo   --url URL       Direct GGUF URL (default: official Qwen3-1.7B Q8_0)
echo   --force         Overwrite existing destination file
echo   -h, --help      Show help
exit /b 0

:usage_err
echo.
echo Usage:
echo   scripts\download-model.bat [--output PATH] [--url URL] [--force]
exit /b 1

:check_args
if "%output%"=="" (
    echo Error: output must be non-empty. 1>&2
    exit /b 1
)
if "%url%"=="" (
    echo Error: url must be non-empty. 1>&2
    exit /b 1
)

:: Create parent directory if needed
for %%F in ("%output%") do set output_dir=%%~dpF
if not exist "%output_dir%" mkdir "%output_dir%"

:: Check if model already exists and force is not set
if exist "%output%" (
    for %%F in ("%output%") do if %%~zF gtr 0 (
        if "%force%"=="0" (
            echo Model already exists at %output%
            echo Use --force to overwrite.
            exit /b 0
        )
    )
)

set tmp_file=%output%.part
if exist "%tmp_file%" del /f "%tmp_file%"

echo Downloading GGUF model...
echo URL: %url%
echo OUT: %output%

:: Try curl first (built-in on Windows 10+), then PowerShell
where curl >nul 2>&1
if %errorlevel%==0 (
    if defined HF_TOKEN (
        curl -L --fail --retry 5 --retry-delay 2 --connect-timeout 30 ^
            -H "Authorization: Bearer %HF_TOKEN%" ^
            -o "%tmp_file%" "%url%"
    ) else (
        curl -L --fail --retry 5 --retry-delay 2 --connect-timeout 30 ^
            -o "%tmp_file%" "%url%"
    )
    if %errorlevel% neq 0 (
        echo curl download failed. 1>&2
        if exist "%tmp_file%" del /f "%tmp_file%"
        exit /b 1
    )
) else (
    echo curl not found, falling back to PowerShell...
    if defined HF_TOKEN (
        powershell -NoProfile -Command ^
            "$headers = @{ Authorization = 'Bearer %HF_TOKEN%' }; Invoke-WebRequest -Uri '%url%' -OutFile '%tmp_file%' -Headers $headers"
    ) else (
        powershell -NoProfile -Command ^
            "Invoke-WebRequest -Uri '%url%' -OutFile '%tmp_file%'"
    )
    if %errorlevel% neq 0 (
        echo PowerShell download failed. 1>&2
        if exist "%tmp_file%" del /f "%tmp_file%"
        exit /b 1
    )
)

move /y "%tmp_file%" "%output%" >nul
echo Model saved to %output%
echo Set TALKBOT_LOCAL_MODEL_PATH=%output% (or keep .env.example default).
