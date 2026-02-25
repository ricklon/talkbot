from pathlib import Path

from talkbot import llm as llm_module


def test_local_provider_uses_repo_default_model_path(monkeypatch, tmp_path):
    model_dir = tmp_path / "models"
    model_dir.mkdir(parents=True)
    model_path = model_dir / "default.gguf"
    model_path.write_bytes(b"gguf")

    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("TALKBOT_LOCAL_MODEL_PATH", raising=False)
    monkeypatch.delenv("TALKBOT_LOCAL_N_CTX", raising=False)

    captured = {}

    class DummyLocalClient:
        def __init__(
            self,
            *,
            model_path,
            binary="llama-cli",
            n_ctx=2048,
            enable_thinking=False,
            temperature=0.7,
            max_tokens=512,
        ):
            captured["model_path"] = model_path
            captured["binary"] = binary
            captured["n_ctx"] = n_ctx
            captured["enable_thinking"] = enable_thinking

    monkeypatch.setattr(llm_module, "LocalLlamaCppClient", DummyLocalClient)

    llm_module.create_llm_client(provider="local", model="qwen/qwen3-1.7b")

    assert Path(captured["model_path"]).resolve() == model_path.resolve()
    assert captured["binary"] == "llama-cli"
    assert captured["n_ctx"] == 2048
    assert captured["enable_thinking"] is False
