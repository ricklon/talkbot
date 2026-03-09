# TTS Benchmark Leaderboard

- Generated: 2026-03-07T23:34:31Z
- Configs: 3

RTF = synthesis time / audio duration. < 1.0 means faster than realtime.
Avg synthesis ms is the time from `save_to_file()` call to file written — this is the TTS contribution to TTFA.

## Overall Rank

| Config | Prompts | Avg Synth ms | P95 Synth ms | Avg Audio ms | Avg RTF | Init ms |
|---|---:|---:|---:|---:|---:|---:|
| pyttsx3 / (default) / rate=175 | 15 | 14 | 32 | 3313 | 0.01x | 20 |
| kittentts / (default) / rate=175 | 15 | 1524 | 2563 | 4566 | 0.34x | 9348 |
| kittentts / Bella / rate=175 | 15 | 2297 | 4238 | 4566 | 0.50x | 4250 |

## Category Breakdown — pyttsx3 / (default) / rate=175

| Category | Count | Avg Synth ms | Avg RTF |
|---|---:|---:|---:|
| llm_conversion | 1 | 10 | 0.00x |
| llm_history | 2 | 15 | 0.01x |
| llm_math | 1 | 10 | 0.00x |
| llm_science | 3 | 17 | 0.00x |
| tool_calculator | 2 | 15 | 0.01x |
| tool_date | 1 | 10 | 0.00x |
| tool_time | 2 | 10 | 0.00x |
| ux | 3 | 16 | 0.01x |

## Entry Detail — pyttsx3 / (default) / rate=175

| ID | Category | Words | Synth ms | Audio ms | RTF |
|---|---|---:|---:|---:|---:|
| speed_of_light | llm_science | 23 | 30 | 7589 | 0.00x |
| long_sentence | ux | 17 | 21 | 4820 | 0.00x |
| math_result | tool_calculator | 10 | 20 | 3792 | 0.01x |
| year_apollo | llm_history | 10 | 20 | 3531 | 0.01x |
| tool_error | ux | 9 | 17 | 3785 | 0.01x |
| time_spoken | tool_time | 8 | 10 | 2583 | 0.00x |
| date_spoken | tool_date | 8 | 10 | 3332 | 0.00x |
| percent_result | tool_calculator | 7 | 10 | 2570 | 0.00x |
| duration_spoken | tool_time | 9 | 10 | 3021 | 0.00x |
| year_ww2 | llm_history | 8 | 10 | 2662 | 0.00x |
| formula_water | llm_science | 9 | 10 | 2402 | 0.00x |
| seconds_in_hour | llm_conversion | 10 | 10 | 3078 | 0.00x |
| dna_acronym | llm_science | 5 | 10 | 2771 | 0.00x |
| pi_decimal | llm_math | 10 | 10 | 3068 | 0.00x |
| short_ack | ux | 2 | 10 | 692 | 0.01x |

## Pipeline Timing Context

TTS synthesis latency is one stage of the full voice pipeline:

```
TTFA = VAD_ms + STT_ms + LLM_ms + TTS_ms
                                   ^^^here
```

Add `avg_synthesis_ms` above to the STT and LLM leaderboard latencies to estimate total TTFA for a given config.
