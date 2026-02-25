@echo off
set UV_PROJECT_ENVIRONMENT=%LOCALAPPDATA%\talkbot\.venv
set VIRTUAL_ENV=
uv run talkbot-gui %*
