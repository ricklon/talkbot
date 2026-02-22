# Local Models

This folder is the project-default location for local GGUF weights.

- Default path used in `.env.example`: `./models/default.gguf`
- Keep GGUF files out of git (see `.gitignore`)
- You can override at runtime with:
  - `TALKBOT_LOCAL_MODEL_PATH=/absolute/path/to/model.gguf`
  - or CLI: `talkbot --local-model-path /absolute/path/to/model.gguf ...`

