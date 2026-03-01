# TTS Benchmark Leaderboard

- Generated: 2026-03-01T20:16:52Z
- Configs: 1

RTF = synthesis time / audio duration. < 1.0 means faster than realtime.
Avg synthesis ms is the time from `save_to_file()` call to file written — this is the TTS contribution to TTFA.

## Overall Rank

| Config | Prompts | Avg Synth ms | P95 Synth ms | Avg Audio ms | Avg RTF | Init ms |
|---|---:|---:|---:|---:|---:|---:|
| kittentts / (default) / rate=175 | 15 | 1524 | 2563 | 4566 | 0.34x | 9348 |

## Category Breakdown — kittentts / (default) / rate=175

| Category | Count | Avg Synth ms | Avg RTF |
|---|---:|---:|---:|
| llm_conversion | 1 | 1118 | 0.34x |
| llm_history | 2 | 1391 | 0.33x |
| llm_math | 1 | 1536 | 0.32x |
| llm_science | 3 | 1782 | 0.33x |
| tool_calculator | 2 | 1448 | 0.34x |
| tool_date | 1 | 1524 | 0.34x |
| tool_time | 2 | 1418 | 0.34x |
| ux | 3 | 1605 | 0.34x |

## Entry Detail — kittentts / (default) / rate=175

| ID | Category | Words | Synth ms | Audio ms | RTF |
|---|---|---:|---:|---:|---:|
| speed_of_light | llm_science | 23 | 2531 | 7817 | 0.32x |
| long_sentence | ux | 17 | 2372 | 7408 | 0.32x |
| tool_error | ux | 9 | 1902 | 5658 | 0.34x |
| math_result | tool_calculator | 10 | 1624 | 4717 | 0.34x |
| year_apollo | llm_history | 10 | 1615 | 4742 | 0.34x |
| pi_decimal | llm_math | 10 | 1536 | 4767 | 0.32x |
| date_spoken | tool_date | 8 | 1524 | 4542 | 0.34x |
| dna_acronym | llm_science | 5 | 1512 | 4392 | 0.34x |
| duration_spoken | tool_time | 9 | 1480 | 4417 | 0.34x |
| time_spoken | tool_time | 8 | 1356 | 3842 | 0.35x |
| formula_water | llm_science | 9 | 1304 | 3942 | 0.33x |
| percent_result | tool_calculator | 7 | 1273 | 3892 | 0.33x |
| year_ww2 | llm_history | 8 | 1167 | 3617 | 0.32x |
| seconds_in_hour | llm_conversion | 10 | 1118 | 3267 | 0.34x |
| short_ack | ux | 2 | 542 | 1467 | 0.37x |

## Pipeline Timing Context

TTS synthesis latency is one stage of the full voice pipeline:

```
TTFA = VAD_ms + STT_ms + LLM_ms + TTS_ms
                                   ^^^here
```

Add `avg_synthesis_ms` above to the STT and LLM leaderboard latencies to estimate total TTFA for a given config.
