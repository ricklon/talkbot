# Voice Benchmark Recording Guide

This guide explains how to record spoken benchmark audio for dates, times, years, and STEM notation.

## Goal

Create a repeatable voice dataset for TTS/STT validation:
- TTS backends: `pyttsx3`, `kittentts`, `piper`, `edge-tts`
- STT scorer: `faster-whisper` (current baseline)

## Prerequisites

Install voice extras:

```bash
uv sync --extra voice
```

Check audio devices:

```bash
uv run -- python scripts/record_voice_benchmark.py --list-devices --speaker-id temp
```

## Prompt Set

Template prompts are in:
- `benchmarks/voice_prompts.template.json`

You can copy and edit this file for your own sessions.

## Recording Command

```bash
uv run -- python scripts/record_voice_benchmark.py \
  --prompts benchmarks/voice_prompts.template.json \
  --output-dir benchmarks/voice_dataset/raw \
  --manifest benchmarks/voice_dataset/manifest.json \
  --speaker-id speaker_a \
  --takes 2
```

Optional flags:
- `--device <id-or-name>`: choose microphone input
- `--sample-rate 16000`: default sample rate
- `--max-seconds 20`: hard stop per take
- `--min-seconds 0.5`: reject too-short clips
- `--session-id <name>`: stable session name

## Recording Workflow

For each prompt/take:
1. Read prompt on screen.
2. Press `ENTER` to arm recording.
3. Press `ENTER` again to stop recording.
4. Repeat for next prompt.

Commands during prompt loop:
- `ENTER`: record
- `s`: skip current take
- `q`: quit and save progress

Manifest is saved after each successful take.

## Output Files

- WAV clips:
  - `benchmarks/voice_dataset/raw/<session>__<speaker>__<prompt>__takeNN.wav`
- Manifest:
  - `benchmarks/voice_dataset/manifest.json`

Each manifest entry includes:
- prompt id/text/category
- expected variants
- speaker/session ids
- sample rate/channels/duration
- recorded timestamp

## Recording Quality Tips

- Record in a quiet room.
- Keep mic distance stable (about 10-20 cm).
- Speak naturally (not robotic).
- Keep pace consistent.
- If you cough/noise, re-record the take.

## Suggested Coverage

Include at least:
- 2 speakers
- 2 takes per prompt
- quiet + mildly noisy session

This gives enough variation for initial spoken-text benchmarking while keeping setup manageable.

