# TalkBot End-to-End Pipeline Leaderboard

- Generated: 2026-03-01T21:50:32Z
- STT configs: 2
- TTS configs: 1
- LLM models: 24

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
| google/gemini-2.5-flash-lite | openrouter | 100.0% | 910 | 100.0% |
| google/gemini-2.5-pro | openrouter | 100.0% | 4900 | 100.0% |
| openai/gpt-4o-mini | openrouter | 90.0% | 1880 | 95.5% |
| anthropic/claude-3.5-sonnet | openrouter | 90.0% | 7073 | 100.0% |
| anthropic/claude-sonnet-4-6 | openrouter | 90.0% | 3026 | 100.0% |
| qwen/qwen3-1.7b | local | 85.7% | 1582 | 93.3% |
| mistralai/ministral-3b-2512 | openrouter | 80.0% | 785 | 95.5% |
| anthropic/claude-haiku-4-5 | openrouter | 80.0% | 2010 | 90.9% |
| qwen/qwen3-8b | local | 71.4% | 1867 | 86.7% |
| google/gemini-2.5-flash | openrouter | 60.0% | 3304 | 90.9% |
| llama3.2:3b | local_server | 50.0% | 969 | 81.8% |
| deepseek/deepseek-chat | openrouter | 42.9% | 4288 | 86.7% |
| meta-llama/llama-3.1-8b-instruct | openrouter | 42.9% | 7615 | 86.7% |
| mistral-nemo:latest | local_server | 40.0% | 7093 | 68.2% |
| qwen3-vl:8b | local_server | 30.0% | 20257 | 77.3% |
| minimax/minimax-01 | openrouter | 28.6% | 2168 | 66.7% |
| qwen/qwen-2.5-7b-instruct | openrouter | 28.6% | 2987 | 86.7% |
| google/gemini-2.0-flash-lite-001 | openrouter | 14.3% | 852 | 53.3% |
| gemma3:4b | local_server | 10.0% | 1754 | 0.0% |
| phi4-mini:latest | local_server | 10.0% | 3304 | 0.0% |
| ibm-granite/granite-4.0-h-micro | openrouter | 0.0% | 24 | 100.0% |
| mistralai/mistral-small-3.1-24b-instruct:free | openrouter | 0.0% | 69 | 0.0% |
| ministral-3b | local_server | 0.0% | 3159 | 0.0% |
| deepseek-r1:1.5b | local_server | 0.0% | 35 | 0.0% |

### TTS

| Config | Avg Synth ms | P95 Synth ms | Avg Audio ms | Avg RTF |
|---|---:|---:|---:|---:|
| kittentts/(default) | 1524 | 2563 | 4566 | 0.34x |

## TTFA Estimates (Composed)

Each row is one possible STT × LLM × TTS configuration.
Sorted by TTFA ascending (fastest first).

| STT | LLM | TTS | STT ms | LLM ms | TTS ms | **TTFA ms** | LLM Success% |
|---|---|---|---:|---:|---:|---:|---:|
| tiny.en/int8/cpu | ibm-granite/granite-4.0-h-micro | kittentts/(default) | 312 | 24 | 1524 | **1859** | 0.0% |
| tiny.en/int8/cpu | deepseek-r1:1.5b | kittentts/(default) | 312 | 35 | 1524 | **1871** | 0.0% |
| tiny.en/int8/cpu | mistralai/mistral-small-3.1-24b-instruct:free | kittentts/(default) | 312 | 69 | 1524 | **1905** | 0.0% |
| tiny.en/int8/cpu | mistralai/ministral-3b-2512 | kittentts/(default) | 312 | 785 | 1524 | **2621** | 80.0% |
| tiny.en/int8/cpu | google/gemini-2.0-flash-lite-001 | kittentts/(default) | 312 | 852 | 1524 | **2688** | 14.3% |
| tiny.en/int8/cpu | google/gemini-2.5-flash-lite | kittentts/(default) | 312 | 910 | 1524 | **2746** | 100.0% |
| tiny.en/int8/cpu | llama3.2:3b | kittentts/(default) | 312 | 969 | 1524 | **2805** | 50.0% |
| tiny.en/int8/cpu | qwen/qwen3-1.7b | kittentts/(default) | 312 | 1582 | 1524 | **3418** | 85.7% |
| small.en/int8/cpu | ibm-granite/granite-4.0-h-micro | kittentts/(default) | 1991 | 24 | 1524 | **3539** | 0.0% |
| small.en/int8/cpu | deepseek-r1:1.5b | kittentts/(default) | 1991 | 35 | 1524 | **3550** | 0.0% |
| small.en/int8/cpu | mistralai/mistral-small-3.1-24b-instruct:free | kittentts/(default) | 1991 | 69 | 1524 | **3584** | 0.0% |
| tiny.en/int8/cpu | gemma3:4b | kittentts/(default) | 312 | 1754 | 1524 | **3590** | 10.0% |
| tiny.en/int8/cpu | qwen/qwen3-8b | kittentts/(default) | 312 | 1867 | 1524 | **3703** | 71.4% |
| tiny.en/int8/cpu | openai/gpt-4o-mini | kittentts/(default) | 312 | 1880 | 1524 | **3716** | 90.0% |
| tiny.en/int8/cpu | anthropic/claude-haiku-4-5 | kittentts/(default) | 312 | 2010 | 1524 | **3846** | 80.0% |
| tiny.en/int8/cpu | minimax/minimax-01 | kittentts/(default) | 312 | 2168 | 1524 | **4004** | 28.6% |
| small.en/int8/cpu | mistralai/ministral-3b-2512 | kittentts/(default) | 1991 | 785 | 1524 | **4300** | 80.0% |
| small.en/int8/cpu | google/gemini-2.0-flash-lite-001 | kittentts/(default) | 1991 | 852 | 1524 | **4367** | 14.3% |
| small.en/int8/cpu | google/gemini-2.5-flash-lite | kittentts/(default) | 1991 | 910 | 1524 | **4425** | 100.0% |
| small.en/int8/cpu | llama3.2:3b | kittentts/(default) | 1991 | 969 | 1524 | **4484** | 50.0% |
| tiny.en/int8/cpu | qwen/qwen-2.5-7b-instruct | kittentts/(default) | 312 | 2987 | 1524 | **4823** | 28.6% |
| tiny.en/int8/cpu | anthropic/claude-sonnet-4-6 | kittentts/(default) | 312 | 3026 | 1524 | **4862** | 90.0% |
| tiny.en/int8/cpu | ministral-3b | kittentts/(default) | 312 | 3159 | 1524 | **4995** | 0.0% |
| small.en/int8/cpu | qwen/qwen3-1.7b | kittentts/(default) | 1991 | 1582 | 1524 | **5097** | 85.7% |
| tiny.en/int8/cpu | phi4-mini:latest | kittentts/(default) | 312 | 3304 | 1524 | **5140** | 10.0% |
| tiny.en/int8/cpu | google/gemini-2.5-flash | kittentts/(default) | 312 | 3304 | 1524 | **5140** | 60.0% |
| small.en/int8/cpu | gemma3:4b | kittentts/(default) | 1991 | 1754 | 1524 | **5269** | 10.0% |
| small.en/int8/cpu | qwen/qwen3-8b | kittentts/(default) | 1991 | 1867 | 1524 | **5382** | 71.4% |
| small.en/int8/cpu | openai/gpt-4o-mini | kittentts/(default) | 1991 | 1880 | 1524 | **5395** | 90.0% |
| small.en/int8/cpu | anthropic/claude-haiku-4-5 | kittentts/(default) | 1991 | 2010 | 1524 | **5525** | 80.0% |
| small.en/int8/cpu | minimax/minimax-01 | kittentts/(default) | 1991 | 2168 | 1524 | **5683** | 28.6% |
| tiny.en/int8/cpu | deepseek/deepseek-chat | kittentts/(default) | 312 | 4288 | 1524 | **6124** | 42.9% |
| small.en/int8/cpu | qwen/qwen-2.5-7b-instruct | kittentts/(default) | 1991 | 2987 | 1524 | **6502** | 28.6% |
| small.en/int8/cpu | anthropic/claude-sonnet-4-6 | kittentts/(default) | 1991 | 3026 | 1524 | **6541** | 90.0% |
| small.en/int8/cpu | ministral-3b | kittentts/(default) | 1991 | 3159 | 1524 | **6674** | 0.0% |
| tiny.en/int8/cpu | google/gemini-2.5-pro | kittentts/(default) | 312 | 4900 | 1524 | **6736** | 100.0% |
| small.en/int8/cpu | phi4-mini:latest | kittentts/(default) | 1991 | 3304 | 1524 | **6819** | 10.0% |
| small.en/int8/cpu | google/gemini-2.5-flash | kittentts/(default) | 1991 | 3304 | 1524 | **6819** | 60.0% |
| small.en/int8/cpu | deepseek/deepseek-chat | kittentts/(default) | 1991 | 4288 | 1524 | **7803** | 42.9% |
| small.en/int8/cpu | google/gemini-2.5-pro | kittentts/(default) | 1991 | 4900 | 1524 | **8415** | 100.0% |
| tiny.en/int8/cpu | anthropic/claude-3.5-sonnet | kittentts/(default) | 312 | 7073 | 1524 | **8909** | 90.0% |
| tiny.en/int8/cpu | mistral-nemo:latest | kittentts/(default) | 312 | 7093 | 1524 | **8929** | 40.0% |
| tiny.en/int8/cpu | meta-llama/llama-3.1-8b-instruct | kittentts/(default) | 312 | 7615 | 1524 | **9451** | 42.9% |
| small.en/int8/cpu | anthropic/claude-3.5-sonnet | kittentts/(default) | 1991 | 7073 | 1524 | **10588** | 90.0% |
| small.en/int8/cpu | mistral-nemo:latest | kittentts/(default) | 1991 | 7093 | 1524 | **10608** | 40.0% |
| small.en/int8/cpu | meta-llama/llama-3.1-8b-instruct | kittentts/(default) | 1991 | 7615 | 1524 | **11130** | 42.9% |
| tiny.en/int8/cpu | qwen3-vl:8b | kittentts/(default) | 312 | 20257 | 1524 | **22093** | 30.0% |
| small.en/int8/cpu | qwen3-vl:8b | kittentts/(default) | 1991 | 20257 | 1524 | **23772** | 30.0% |

## Recommended Configs

**Fastest:** tiny.en/int8/cpu + ibm-granite/granite-4.0-h-micro + kittentts/(default)  
→ TTFA ~1859 ms | LLM success 0.0%

**Best balanced** (highest success within 1.5× min TTFA):  
tiny.en/int8/cpu + google/gemini-2.5-flash-lite + kittentts/(default)  
→ TTFA ~2746 ms | LLM success 100.0%
