# STT Benchmark Leaderboard

- Generated: 2026-03-07T19:53:48Z
- Configs: 2
- WER pass threshold: 10%

## Overall Rank

Sorted by average WER (lower = better). RTF = realtime factor (synthesis time / audio duration; < 1.0 means faster than realtime).

| Config | Entries | Pass% | Avg WER | Median WER | Avg ms | P95 ms | Avg RTF | Load ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| small.en / int8 / cpu | 48 | 95.8% | 4.2% | 0.0% | 2803 | 3026 | 0.90x | 1187 |
| tiny.en / int8 / cpu | 48 | 85.4% | 6.6% | 0.0% | 312 | 351 | 0.10x | 540 |

## Category Breakdown — small.en / int8 / cpu

| Category | Count | Pass% | Avg WER | Avg ms |
|---|---:|---:|---:|---:|
| date | 4 | 100.0% | 0.0% | 2954 |
| llm_conversion | 2 | 100.0% | 0.0% | 2897 |
| llm_history | 4 | 100.0% | 0.0% | 2928 |
| llm_math | 2 | 100.0% | 0.0% | 2932 |
| llm_science | 6 | 100.0% | 0.0% | 2901 |
| numeric | 2 | 100.0% | 0.0% | 3017 |
| stem | 8 | 75.0% | 25.0% | 2902 |
| time | 6 | 100.0% | 0.0% | 2488 |
| tool_calculator | 4 | 100.0% | 0.0% | 2858 |
| tool_date | 2 | 100.0% | 0.0% | 2911 |
| tool_time | 4 | 100.0% | 0.0% | 2838 |
| year | 4 | 100.0% | 0.0% | 2289 |

## Entry Detail — small.en / int8 / cpu

Rows sorted by WER descending (worst first).

| ID | Category | Dur s | WER | ms | RTF | Reference | Hypothesis |
|---|---|---:|---:|---:|---:|---|---|
| chemical_formula__take01 | stem | 2.1 | 100% | 2902 | 1.36x | The sample contains H two S O four. |  |
| chemical_formula__take02 | stem | 2.4 | 100% | 2802 | 1.15x | The sample contains H two S O four. |  |
| time_12h__take01 | time | 3.9 | 0% | 2117 | 0.54x | The train leaves at three oh five PM. | The train leaves at 3.05 pm. |
| time_12h__take02 | time | 2.5 | 0% | 2095 | 0.83x | The train leaves at three oh five PM. | The train leaves at 3.05pm. |
| time_24h__take02 | time | 2.8 | 0% | 2094 | 0.76x | Maintenance starts at fifteen forty five. | Maintenance starts at 1545. |
| year_1905__take01 | year | 3.7 | 0% | 2088 | 0.56x | The building was completed in nineteen oh five. | The building was completed in 1905 |
| year_2001__take01 | year | 2.4 | 0% | 2070 | 0.85x | The mission launched in two thousand one. | The mission launched in 2001. |
| year_2001__take02 | year | 2.9 | 0% | 2116 | 0.72x | The mission launched in two thousand one. | The mission launched in 2001. |
| stem_units__take01 | stem | 4.1 | 0% | 2729 | 0.66x | Acceleration is nine point eight one meters per second squar | Acceleration is 9.81 m per second squared. |
| stem_units__take02 | stem | 5.6 | 0% | 2950 | 0.53x | Acceleration is nine point eight one meters per second squar | Acceleration is 9.81 meters per second squared. |
| timezone__take01 | time | 2.8 | 0% | 2874 | 1.02x | Deadline is seventeen thirty UTC. | Deadline is 1730 UTC. |
| timezone__take02 | time | 2.7 | 0% | 2906 | 1.07x | Deadline is seventeen thirty UTC. | Deadline is 1730 UTC. |
| date_iso__take01 | date | 4.8 | 0% | 2932 | 0.61x | The due date is February twenty sixth twenty twenty six. | The due date is 2026-0226. |
| date_iso__take02 | date | 4.0 | 0% | 2857 | 0.72x | The due date is February twenty sixth twenty twenty six. | The due date is 2026-0226. |
| time_24h__take01 | time | 4.0 | 0% | 2842 | 0.71x | Maintenance starts at fifteen forty five. | maintenance starts at 1545. |
| year_1905__take02 | year | 3.5 | 0% | 2883 | 0.83x | The building was completed in nineteen oh five. | The building was completed in 1905 |
| date_us_short__take01 | date | 4.1 | 0% | 2938 | 0.72x | Meeting is on March seventh twenty twenty six. | Meeting is on 3-7-2026 |
| date_us_short__take02 | date | 2.9 | 0% | 3090 | 1.07x | Meeting is on March seventh twenty twenty six. | meeting is on 3-7-2026. |
| currency_and_percent__take01 | numeric | 7.0 | 0% | 3055 | 0.43x | Revenue grew by twelve point five percent to four point two  | revenue grew by 12.5% to 4.2 million dollars. |
| currency_and_percent__take02 | numeric | 5.8 | 0% | 2978 | 0.52x | Revenue grew by twelve point five percent to four point two  | revenue grew by 12.5% to 4.2 million dollars |
| stem_scientific_notation__take01 | stem | 5.0 | 0% | 2991 | 0.60x | The concentration is three point two times ten to the minus  | The concentration is 3.2 times 10 to the power of negative 5 |
| stem_scientific_notation__take02 | stem | 5.1 | 0% | 2970 | 0.58x | The concentration is three point two times ten to the minus  | The concentration is 3.2 times 10 to the power of negative 5 |
| stem_expression__take01 | stem | 4.1 | 0% | 2948 | 0.72x | Solve x two plus y two equals z two. | Solve x squared plus y squared equals z squared. |
| stem_expression__take02 | stem | 3.8 | 0% | 2922 | 0.78x | Solve x two plus y two equals z two. | Solve x squared plus y squared equals z squared. |
| tool_current_time__take01 | tool_time | 2.8 | 0% | 2867 | 1.04x | What time is it right now? | What time is it right now? |
| tool_current_time__take02 | tool_time | 2.8 | 0% | 2906 | 1.04x | What time is it right now? | What time is it right now? |
| tool_current_date__take01 | tool_date | 3.2 | 0% | 2881 | 0.91x | What is today's date? | What is today's date? |
| tool_current_date__take02 | tool_date | 2.1 | 0% | 2940 | 1.43x | What is today's date? | What is today's date? |
| tool_math_divide__take01 | tool_calculator | 3.8 | 0% | 2803 | 0.74x | What is 144 divided by 12? | What is 144 divided by 12? |
| tool_math_divide__take02 | tool_calculator | 3.4 | 0% | 2886 | 0.84x | What is 144 divided by 12? | What is 144 divided by 12? |
| tool_math_percent__take01 | tool_calculator | 3.5 | 0% | 2878 | 0.83x | What is 15% of 200? | What is 15% of 200? |
| tool_math_percent__take02 | tool_calculator | 3.0 | 0% | 2864 | 0.97x | What is 15% of 200? | What is 15% of 200? |
| tool_time_until__take01 | tool_time | 2.3 | 0% | 2804 | 1.23x | How long until midnight? | How long until midnight? |
| tool_time_until__take02 | tool_time | 1.9 | 0% | 2774 | 1.44x | How long until midnight? | How long until midnight? |
| llm_history_apollo__take01 | llm_history | 5.4 | 0% | 2926 | 0.55x | What year did the Apollo 11 moon landing happen? | What year did the Apollo 11 moon landing happen? |
| llm_history_apollo__take02 | llm_history | 4.0 | 0% | 2929 | 0.73x | What year did the Apollo 11 moon landing happen? | What year did the Apollo 11 moon landing happen? |
| llm_history_ww2__take01 | llm_history | 2.7 | 0% | 2917 | 1.10x | What year did World War II end? | What year did World War II end? |
| llm_history_ww2__take02 | llm_history | 2.6 | 0% | 2942 | 1.13x | What year did World War II end? | What year did World War II end? |
| llm_science_formula__take01 | llm_science | 3.0 | 0% | 2943 | 0.97x | What is the chemical formula for water? | What is the chemical formula for water? |
| llm_science_formula__take02 | llm_science | 2.4 | 0% | 2939 | 1.24x | What is the chemical formula for water? | What is the chemical formula for water? |
| llm_science_speed_of_light__take01 | llm_science | 3.0 | 0% | 2965 | 0.97x | What is the speed of light in meters per second? | What is the speed of light in meters per second? |
| llm_science_speed_of_light__take02 | llm_science | 3.0 | 0% | 2917 | 0.98x | What is the speed of light in meters per second? | What is the speed of light in meters per second? |
| llm_conversion_seconds__take01 | llm_conversion | 2.5 | 0% | 2870 | 1.15x | How many seconds are in an hour? | How many seconds are in an hour? |
| llm_conversion_seconds__take02 | llm_conversion | 2.8 | 0% | 2924 | 1.04x | How many seconds are in an hour? | How many seconds are in an hour? |
| llm_acronym_dna__take01 | llm_science | 2.3 | 0% | 2832 | 1.25x | What does DNA stand for? | What does DNA stand for? |
| llm_acronym_dna__take02 | llm_science | 2.7 | 0% | 2812 | 1.04x | What does DNA stand for? | What does DNA stand for? |
| llm_math_pi__take01 | llm_math | 2.8 | 0% | 2894 | 1.02x | What is pi to two decimal places? | What is pi to two decimal places? |
| llm_math_pi__take02 | llm_math | 3.0 | 0% | 2970 | 1.00x | What is pi to two decimal places? | What is pi to two decimal places? |

## Pipeline Timing Context

These STT latencies are one stage of the full voice pipeline:

```
TTFA = VAD_ms + STT_ms + LLM_ms + TTS_ms
         ~0ms   ^^^here   see LLM leaderboard
```

Subtract `avg_latency_ms` above from the LLM benchmark's `Avg ms` to see how much of end-to-end latency comes from STT vs inference.
