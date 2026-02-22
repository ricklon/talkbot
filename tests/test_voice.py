import numpy as np

from talkbot import voice as voice_module


class DummyClient:
    def __init__(self, *args, **kwargs):
        self.calls = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def chat_completion(self, messages):
        self.calls.append(messages)
        return {"choices": [{"message": {"content": "assistant reply"}}]}


class DummyTTS:
    def __init__(self, *args, **kwargs):
        self.backend_name = kwargs.get("backend") or "pyttsx3"

    def set_voice(self, _voice):
        return None


def test_voice_config_block_size():
    cfg = voice_module.VoiceConfig(sample_rate=16000, block_duration_ms=20)
    assert cfg.block_size == 320


def test_chat_with_context_maintains_messages():
    pipeline = voice_module.VoicePipeline(
        api_key="k",
        model="m",
        system_prompt="sys",
        speak=False,
    )
    client = DummyClient()

    out1 = pipeline._chat_with_context(client, "hello")
    out2 = pipeline._chat_with_context(client, "second")

    assert out1 == "assistant reply"
    assert out2 == "assistant reply"
    assert pipeline._history[0]["role"] == "system"
    assert pipeline._history[0]["content"].startswith("sys")
    assert pipeline._history[1]["role"] == "user"
    assert pipeline._history[2]["role"] == "assistant"
    assert pipeline._history[3]["role"] == "user"


def test_run_emits_transcript_and_response(monkeypatch):
    pipeline = voice_module.VoicePipeline(api_key="k", model="m", speak=True)

    monkeypatch.setattr(voice_module, "create_llm_client", lambda **_kwargs: DummyClient())
    monkeypatch.setattr(voice_module, "TTSManager", DummyTTS)
    monkeypatch.setattr(pipeline, "_ensure_dependencies", lambda: None)

    state = {"count": 0}

    def fake_capture(on_event=None):
        state["count"] += 1
        if state["count"] == 1:
            return np.array([0.1, 0.2], dtype=np.float32)
        pipeline.stop()
        return None

    monkeypatch.setattr(pipeline, "_capture_until_pause", fake_capture)
    monkeypatch.setattr(pipeline, "_transcribe", lambda _audio: "hi there")
    monkeypatch.setattr(pipeline, "_chat_with_context", lambda _client, _t: "hello back")
    monkeypatch.setattr(pipeline, "_speak_response", lambda _tts, _text, on_event=None: False)

    events = []
    pipeline.run(on_event=lambda e: events.append(e))

    event_types = [e["type"] for e in events]
    assert "listening" in event_types
    assert "transcribing" in event_types
    assert "thinking" in event_types
    assert {"type": "transcript", "text": "hi there"} in events
    assert {"type": "response", "text": "hello back"} in events
