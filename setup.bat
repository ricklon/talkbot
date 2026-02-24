@echo off
setlocal enabledelayedexpansion

set download_model=0
set with_llama_python=0

:parse_args
if "%~1"=="" goto :install
if /i "%~1"=="--download-model" (
    set download_model=1
    shift
    goto :parse_args
)
if /i "%~1"=="--with-llama-python" (
    set with_llama_python=1
    shift
    goto :parse_args
)
if /i "%~1"=="-h" goto :help
if /i "%~1"=="--help" goto :help

echo Unknown option: %~1 1>&2
echo Run setup.bat --help 1>&2
exit /b 1

:help
echo Usage: setup.bat [--download-model] [--with-llama-python]
echo.
echo Options:
echo   --download-model      Install tool + voice deps, then download default GGUF
echo   --with-llama-python   Also install llama-cpp-python (requires MSVC build tools)
echo   -h, --help            Show this help
echo.
echo NOTE: llama-cpp-python requires MSVC (Visual Studio C++ build tools) to compile.
echo       Without it, use a pre-built llama-cli.exe and set TALKBOT_LLAMACPP_BIN in .env.
exit /b 0

:install
set UV_PROJECT_ENVIRONMENT=%LOCALAPPDATA%\talkbot\.venv
if "%with_llama_python%"=="1" (
    uv tool install --reinstall ^
      --python 3.12 . ^
      --with llama-cpp-python ^
      --with faster-whisper ^
      --with silero-vad ^
      --with sounddevice ^
      --with soundfile
) else (
    uv tool install --reinstall ^
      --python 3.12 . ^
      --with faster-whisper ^
      --with silero-vad ^
      --with sounddevice ^
      --with soundfile
)
if %errorlevel% neq 0 (
    echo Install failed. 1>&2
    exit /b %errorlevel%
)

echo Installed talkbot and talkbot-gui with voice extras.
if "%download_model%"=="1" (
    call scripts\download-model.bat
) else (
    echo Place your GGUF at .\models\default.gguf (or set TALKBOT_LOCAL_MODEL_PATH).
    echo Optional: run setup.bat --download-model
)
