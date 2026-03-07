# STT Benchmark Leaderboard

- Generated: 2026-03-07T22:16:56Z
- Configs: 2
- WER pass threshold: 10%

## Overall Rank

Sorted by average WER (lower = better). RTF = realtime factor (synthesis time / audio duration; < 1.0 means faster than realtime).

| Config | Entries | Pass% | Avg WER | Median WER | Avg ms | P95 ms | Avg RTF | Load ms |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| small.en / int8 / cpu | 48 | 100.0% | 0.0% | 0.0% | 4283 | 4682 | 1.33x | 1034 |
| tiny.en / int8 / cpu | 48 | 85.4% | 6.6% | 0.0% | 312 | 351 | 0.10x | 540 |

## Category Breakdown — small.en / int8 / cpu

| Category | Count | Pass% | Avg WER | Avg ms |
|---|---:|---:|---:|---:|
| date | 4 | 100.0% | 0.0% | 4351 |
| llm_conversion | 2 | 100.0% | 0.0% | 4363 |
| llm_history | 4 | 100.0% | 0.0% | 4390 |
| llm_math | 2 | 100.0% | 0.0% | 4349 |
| llm_science | 6 | 100.0% | 0.0% | 4332 |
| numeric | 2 | 100.0% | 0.0% | 4400 |
| stem | 8 | 100.0% | 0.0% | 4425 |
| time | 6 | 100.0% | 0.0% | 3630 |
| tool_calculator | 4 | 100.0% | 0.0% | 4301 |
| tool_date | 2 | 100.0% | 0.0% | 4299 |
| tool_time | 4 | 100.0% | 0.0% | 4282 |
| year | 4 | 100.0% | 0.0% | 4572 |

## Entry Detail — small.en / int8 / cpu

Rows sorted by WER descending (worst first).

| ID | Category | Dur s | WER | ms | RTF | Reference | Hypothesis |
|---|---|---:|---:|---:|---:|---|---|
| time_12h__take01 | time | 3.9 | 0% | 2144 | 0.55x | The train leaves at three oh five PM. | The train leaves at 3.05 pm. |
| time_12h__take02 | time | 2.5 | 0% | 2192 | 0.87x | The train leaves at three oh five PM. | The train leaves at 3.05pm. |
| time_24h__take02 | time | 2.8 | 0% | 4563 | 1.66x | Maintenance starts at fifteen forty five. | Maintenance starts at 1545. |
| year_1905__take01 | year | 3.7 | 0% | 4695 | 1.25x | The building was completed in nineteen oh five. | The building was completed in 1905 |
| year_2001__take01 | year | 2.4 | 0% | 4737 | 1.94x | The mission launched in two thousand one. | The mission launched in 2001. |
| year_2001__take02 | year | 2.9 | 0% | 4560 | 1.55x | The mission launched in two thousand one. | The mission launched in 2001. |
| stem_units__take01 | stem | 4.1 | 0% | 4666 | 1.14x | Acceleration is nine point eight one meters per second squar | Acceleration is 9.81 m per second squared. |
| stem_units__take02 | stem | 5.6 | 0% | 4392 | 0.79x | Acceleration is nine point eight one meters per second squar | Acceleration is 9.81 meters per second squared. |
| timezone__take01 | time | 2.8 | 0% | 4225 | 1.50x | Deadline is seventeen thirty UTC. | Deadline is 1730 UTC. |
| timezone__take02 | time | 2.7 | 0% | 4262 | 1.58x | Deadline is seventeen thirty UTC. | Deadline is 1730 UTC. |
| date_iso__take01 | date | 4.8 | 0% | 4391 | 0.91x | The due date is February twenty sixth twenty twenty six. | The due date is 2026-0226. |
| date_iso__take02 | date | 4.0 | 0% | 4367 | 1.10x | The due date is February twenty sixth twenty twenty six. | The due date is 2026-0226. |
| time_24h__take01 | time | 4.0 | 0% | 4395 | 1.10x | Maintenance starts at fifteen forty five. | maintenance starts at 1545. |
| year_1905__take02 | year | 3.5 | 0% | 4296 | 1.23x | The building was completed in nineteen oh five. | The building was completed in 1905 |
| date_us_short__take01 | date | 4.1 | 0% | 4319 | 1.06x | Meeting is on March seventh twenty twenty six. | Meeting is on 3-7-2026 |
| date_us_short__take02 | date | 2.9 | 0% | 4328 | 1.50x | Meeting is on March seventh twenty twenty six. | meeting is on 3-7-2026. |
| currency_and_percent__take01 | numeric | 7.0 | 0% | 4414 | 0.63x | Revenue grew by twelve point five percent to four point two  | revenue grew by 12.5% to 4.2 million dollars. |
| currency_and_percent__take02 | numeric | 5.8 | 0% | 4386 | 0.76x | Revenue grew by twelve point five percent to four point two  | revenue grew by 12.5% to 4.2 million dollars |
| stem_scientific_notation__take01 | stem | 5.0 | 0% | 4490 | 0.90x | The concentration is three point two times ten to the minus  | The concentration is 3.2 times 10 to the power of negative 5 |
| stem_scientific_notation__take02 | stem | 5.1 | 0% | 4493 | 0.88x | The concentration is three point two times ten to the minus  | The concentration is 3.2 times 10 to the power of negative 5 |
| stem_expression__take01 | stem | 4.1 | 0% | 4363 | 1.07x | Solve x two plus y two equals z two. | Solve x squared plus y squared equals z squared. |
| stem_expression__take02 | stem | 3.8 | 0% | 4370 | 1.16x | Solve x two plus y two equals z two. | Solve x squared plus y squared equals z squared. |
| chemical_formula__take01 | stem | 5.5 | 0% | 4303 | 0.78x | The sample contains H two S O four. | The sample contains H2SO4. |
| chemical_formula__take02 | stem | 3.5 | 0% | 4324 | 1.24x | The sample contains H two S O four. | The sample contains H2SO4. |
| tool_current_time__take01 | tool_time | 2.8 | 0% | 4273 | 1.55x | What time is it right now? | What time is it right now? |
| tool_current_time__take02 | tool_time | 2.8 | 0% | 4326 | 1.55x | What time is it right now? | What time is it right now? |
| tool_current_date__take01 | tool_date | 3.2 | 0% | 4370 | 1.38x | What is today's date? | What is today's date? |
| tool_current_date__take02 | tool_date | 2.1 | 0% | 4228 | 2.06x | What is today's date? | What is today's date? |
| tool_math_divide__take01 | tool_calculator | 3.8 | 0% | 4274 | 1.13x | What is 144 divided by 12? | What is 144 divided by 12? |
| tool_math_divide__take02 | tool_calculator | 3.4 | 0% | 4300 | 1.25x | What is 144 divided by 12? | What is 144 divided by 12? |
| tool_math_percent__take01 | tool_calculator | 3.5 | 0% | 4318 | 1.24x | What is 15% of 200? | What is 15% of 200? |
| tool_math_percent__take02 | tool_calculator | 3.0 | 0% | 4313 | 1.46x | What is 15% of 200? | What is 15% of 200? |
| tool_time_until__take01 | tool_time | 2.3 | 0% | 4260 | 1.86x | How long until midnight? | How long until midnight? |
| tool_time_until__take02 | tool_time | 1.9 | 0% | 4270 | 2.22x | How long until midnight? | How long until midnight? |
| llm_history_apollo__take01 | llm_history | 5.4 | 0% | 4362 | 0.81x | What year did the Apollo 11 moon landing happen? | What year did the Apollo 11 moon landing happen? |
| llm_history_apollo__take02 | llm_history | 4.0 | 0% | 4442 | 1.10x | What year did the Apollo 11 moon landing happen? | What year did the Apollo 11 moon landing happen? |
| llm_history_ww2__take01 | llm_history | 2.7 | 0% | 4361 | 1.64x | What year did World War II end? | What year did World War II end? |
| llm_history_ww2__take02 | llm_history | 2.6 | 0% | 4395 | 1.69x | What year did World War II end? | What year did World War II end? |
| llm_science_formula__take01 | llm_science | 3.0 | 0% | 4306 | 1.42x | What is the chemical formula for water? | What is the chemical formula for water? |
| llm_science_formula__take02 | llm_science | 2.4 | 0% | 4357 | 1.84x | What is the chemical formula for water? | What is the chemical formula for water? |
| llm_science_speed_of_light__take01 | llm_science | 3.0 | 0% | 4373 | 1.44x | What is the speed of light in meters per second? | What is the speed of light in meters per second? |
| llm_science_speed_of_light__take02 | llm_science | 3.0 | 0% | 4354 | 1.47x | What is the speed of light in meters per second? | What is the speed of light in meters per second? |
| llm_conversion_seconds__take01 | llm_conversion | 2.5 | 0% | 4341 | 1.74x | How many seconds are in an hour? | How many seconds are in an hour? |
| llm_conversion_seconds__take02 | llm_conversion | 2.8 | 0% | 4386 | 1.56x | How many seconds are in an hour? | How many seconds are in an hour? |
| llm_acronym_dna__take01 | llm_science | 2.3 | 0% | 4302 | 1.90x | What does DNA stand for? | What does DNA stand for? |
| llm_acronym_dna__take02 | llm_science | 2.7 | 0% | 4298 | 1.59x | What does DNA stand for? | What does DNA stand for? |
| llm_math_pi__take01 | llm_math | 2.8 | 0% | 4375 | 1.54x | What is pi to two decimal places? | What is pi to two decimal places? |
| llm_math_pi__take02 | llm_math | 3.0 | 0% | 4323 | 1.46x | What is pi to two decimal places? | What is pi to two decimal places? |

## Pipeline Timing Context

These STT latencies are one stage of the full voice pipeline:

```
TTFA = VAD_ms + STT_ms + LLM_ms + TTS_ms
         ~0ms   ^^^here   see LLM leaderboard
```

Subtract `avg_latency_ms` above from the LLM benchmark's `Avg ms` to see how much of end-to-end latency comes from STT vs inference.
