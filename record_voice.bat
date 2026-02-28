@echo off
set SPEAKER=%1
if "%SPEAKER%"=="" set SPEAKER=ricklon

set DEVICE=%2
if "%DEVICE%"=="" set DEVICE=3

set TAKES=%3
if "%TAKES%"=="" set TAKES=2

uv run -- python scripts/record_voice_benchmark.py ^
  --prompts benchmarks/voice_prompts.template.json ^
  --output-dir benchmarks/voice_dataset/raw ^
  --manifest benchmarks/voice_dataset/manifest.json ^
  --speaker-id %SPEAKER% ^
  --device %DEVICE% ^
  --takes %TAKES%
