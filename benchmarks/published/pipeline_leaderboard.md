# TalkBot End-to-End Pipeline Leaderboard

- Generated: 2026-03-01T20:19:17Z
- STT configs: 2
- TTS configs: 1
- LLM models: 6

```
TTFA = STT_ms + LLM_ms + TTS_ms
       (transcribe) (infer+tools) (synthesise)
```

TTFA = time from end-of-speech to first audio byte.
All values are averages over benchmark runs on this machine.

## Stage Latencies

### STT

| Config | Pass% | Avg ms | P95 ms | Avg RTF |
|---|---:|---:|---:|---:|
| tiny.en/int8/cpu | 85.4% | 312 | 351 | 0.10x |
| small.en/int8/cpu | 93.8% | 1991 | 2272 | 0.64x |

### LLM

| Model | Provider | Success% | Avg ms | Tool Sel% |
|---|---|---:|---:|---:|
| llama3.2:3b | local_server | 50.0% | 969 | 81.8% |
| mistral-nemo:latest | local_server | 30.0% | 3383 | 72.7% |
| qwen3-vl:8b | local_server | 30.0% | 20257 | 77.3% |
| phi4-mini:latest | local_server | 10.0% | 647 | 0.0% |
| gemma3:4b | local_server | 0.0% | 625 | 0.0% |
| deepseek-r1:1.5b | local_server | 0.0% | 2221 | 0.0% |

### TTS

| Config | Avg Synth ms | P95 Synth ms | Avg Audio ms | Avg RTF |
|---|---:|---:|---:|---:|
| kittentts/(default) | 1524 | 2563 | 4566 | 0.34x |

## TTFA Estimates (Composed)

Each row is one possible STT × LLM × TTS configuration.
Sorted by TTFA ascending (fastest first).

| STT | LLM | TTS | STT ms | LLM ms | TTS ms | **TTFA ms** | LLM Success% |
|---|---|---|---:|---:|---:|---:|---:|
| tiny.en/int8/cpu | gemma3:4b | kittentts/(default) | 312 | 625 | 1524 | **2461** | 0.0% |
| tiny.en/int8/cpu | phi4-mini:latest | kittentts/(default) | 312 | 647 | 1524 | **2483** | 10.0% |
| tiny.en/int8/cpu | llama3.2:3b | kittentts/(default) | 312 | 969 | 1524 | **2805** | 50.0% |
| tiny.en/int8/cpu | deepseek-r1:1.5b | kittentts/(default) | 312 | 2221 | 1524 | **4057** | 0.0% |
| small.en/int8/cpu | gemma3:4b | kittentts/(default) | 1991 | 625 | 1524 | **4140** | 0.0% |
| small.en/int8/cpu | phi4-mini:latest | kittentts/(default) | 1991 | 647 | 1524 | **4162** | 10.0% |
| small.en/int8/cpu | llama3.2:3b | kittentts/(default) | 1991 | 969 | 1524 | **4484** | 50.0% |
| tiny.en/int8/cpu | mistral-nemo:latest | kittentts/(default) | 312 | 3383 | 1524 | **5219** | 30.0% |
| small.en/int8/cpu | deepseek-r1:1.5b | kittentts/(default) | 1991 | 2221 | 1524 | **5736** | 0.0% |
| small.en/int8/cpu | mistral-nemo:latest | kittentts/(default) | 1991 | 3383 | 1524 | **6898** | 30.0% |
| tiny.en/int8/cpu | qwen3-vl:8b | kittentts/(default) | 312 | 20257 | 1524 | **22093** | 30.0% |
| small.en/int8/cpu | qwen3-vl:8b | kittentts/(default) | 1991 | 20257 | 1524 | **23772** | 30.0% |

## Recommended Configs

**Fastest:** tiny.en/int8/cpu + gemma3:4b + kittentts/(default)  
→ TTFA ~2461 ms | LLM success 0.0%

**Best balanced** (highest success within 1.5× min TTFA):  
tiny.en/int8/cpu + llama3.2:3b + kittentts/(default)  
→ TTFA ~2805 ms | LLM success 50.0%
