@echo off
set UV_SKIP_WHEEL_FILENAME_CHECK=1
set UV_PROJECT_ENVIRONMENT=%LOCALAPPDATA%\talkbot\.venv
set VIRTUAL_ENV=
uv run talkbot-gui %*
