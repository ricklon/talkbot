# TODO

Updated: 2026-03-11

## Confirmed Issues

- [x] Fix CLI default model selection for `provider=local_server`.
  Tracker: GitHub issue `#46`.
  Today `src/talkbot/cli.py` returns an empty model unless `TALKBOT_LOCAL_SERVER_MODEL` is set, even though the repo default provider is now `local_server`.
  `create_llm_client()` then falls back to `TALKBOT_LOCAL_MODEL_PATH` or an empty string, which does not match the documented default `qwen3.5-0.8b-q8_0`.
  Local fix implemented in `src/talkbot/cli.py` with regression coverage in `tests/test_cli.py`.

- [ ] Verify `/no_think` removal does not regress older Intel llama-server `b8248` setups.
  Tracker: GitHub issue `#43`.

## Validation Gaps

- [x] Add CLI tests that cover the new default path:
  invoking `talkbot chat ...` with no model env vars should pass the recommended `local_server` model, not `""`.
  Covered locally in `tests/test_cli.py`.
- [ ] Add one integration-style smoke check for `local_server` startup assumptions:
  verify the configured model name matches the server's `/models` response or fail with a clearer error.

## PR Review Follow-up

- [ ] PR `#45`: avoid forcing a single tool on multi-intent turns.
  Current review finding: the new intent detector claims it returns `None` for ambiguous multi-tool requests, but the implementation appears to return the first regex match instead.
- [ ] PR `#45`: avoid forcing keyed tools that need clarification, especially `cancel_timer` and `recall`.
  Their schemas require exact `timer_id` / `key` values, so `tool_choice="required"` can push the model to invent identifiers instead of asking a follow-up.
- [ ] PR `#45`: add unit tests for intent routing.
  Minimum coverage should include multi-intent detection, first-turn `tool_choice="required"` behavior, and clarification cases for ambiguous keyed-tool requests.

## Cleanup

- [ ] Decide whether to standardize `localhost` vs `127.0.0.1` defaults across CLI, GUI, benchmark code, and docs.
  It is not a current failing test, but the defaults are inconsistent and make troubleshooting noisier.
- [ ] Remove the duplicate `from talkbot.ui.components import ModernStyle, RoundedButton` import in `src/talkbot/ui/app.py`.
