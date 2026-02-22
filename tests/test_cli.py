from click.testing import CliRunner

from talkbot import cli as cli_module


class FakeClient:
    def __init__(self, api_key=None, model=None):
        self.api_key = api_key
        self.model = model

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def simple_chat(self, message, system_prompt=None):
        return f"reply:{message}:{system_prompt}"


class FakeTTS:
    def __init__(self, rate=175, volume=1.0, backend=None):
        self.rate = rate
        self.volume = volume
        self.backend = backend
        self.voice = None
        self.spoken = []
        self.listed = False

    def set_voice(self, voice):
        self.voice = voice

    def speak(self, text):
        self.spoken.append(text)

    def list_voices(self):
        self.listed = True

    @property
    def available_voices(self):
        return [{"id": "v1", "name": "Voice 1", "languages": ["en"], "backend": "fake"}]

    @property
    def backend_name(self):
        return self.backend or "edge-tts"

    def save_to_file(self, text, output):
        with open(output, "wb") as f:
            f.write(b"audio")


def test_chat_command_no_speak(monkeypatch):
    monkeypatch.setattr(cli_module, "OpenRouterClient", FakeClient)

    runner = CliRunner()
    result = runner.invoke(
        cli_module.cli,
        ["--api-key", "k", "chat", "Hello", "--no-speak", "--system", "sys"],
    )

    assert result.exit_code == 0
    assert "You: Hello" in result.output
    assert "AI: reply:Hello:sys" in result.output


def test_chat_command_speak_uses_tts(monkeypatch):
    tts_instances = []

    def fake_tts_factory(rate=175, volume=1.0, backend=None):
        obj = FakeTTS(rate=rate, volume=volume, backend=backend)
        tts_instances.append(obj)
        return obj

    monkeypatch.setattr(cli_module, "OpenRouterClient", FakeClient)
    monkeypatch.setattr(cli_module, "TTSManager", fake_tts_factory)

    runner = CliRunner()
    result = runner.invoke(
        cli_module.cli,
        [
            "--api-key",
            "k",
            "chat",
            "Hi",
            "--speak",
            "--voice",
            "demo-voice",
            "--rate",
            "160",
            "--volume",
            "0.7",
            "--backend",
            "pyttsx3",
        ],
    )

    assert result.exit_code == 0
    assert len(tts_instances) == 1
    assert tts_instances[0].backend == "pyttsx3"
    assert tts_instances[0].voice == "demo-voice"
    assert tts_instances[0].spoken == ["reply:Hi:None"]


def test_voices_command_passes_backend(monkeypatch):
    tts_instances = []

    def fake_tts_factory(rate=175, volume=1.0, backend=None):
        obj = FakeTTS(rate=rate, volume=volume, backend=backend)
        tts_instances.append(obj)
        return obj

    monkeypatch.setattr(cli_module, "TTSManager", fake_tts_factory)

    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["voices", "--backend", "kittentts"])

    assert result.exit_code == 0
    assert len(tts_instances) == 1
    assert tts_instances[0].backend == "kittentts"
    assert tts_instances[0].listed is True


def test_doctor_tts_success(monkeypatch):
    monkeypatch.setattr(cli_module, "TTSManager", FakeTTS)

    runner = CliRunner()
    result = runner.invoke(
        cli_module.cli,
        ["doctor-tts", "--backend", "edge-tts", "--no-synthesize"],
    )

    assert result.exit_code == 0
    assert "TTS Diagnostics" in result.output
    assert "[edge-tts]" in result.output
    assert "init: OK" in result.output
    assert "voices: OK" in result.output
    assert "failed: 0" in result.output


def test_doctor_tts_failure_sets_exit_code(monkeypatch):
    class MixedTTS(FakeTTS):
        def __init__(self, rate=175, volume=1.0, backend=None):
            if backend == "kittentts":
                raise RuntimeError("boom")
            super().__init__(rate=rate, volume=volume, backend=backend)

    monkeypatch.setattr(cli_module, "TTSManager", MixedTTS)

    runner = CliRunner()
    result = runner.invoke(
        cli_module.cli,
        [
            "doctor-tts",
            "--backend",
            "edge-tts",
            "--backend",
            "kittentts",
            "--no-synthesize",
        ],
    )

    assert result.exit_code == 1
    assert "[edge-tts]" in result.output
    assert "[kittentts]" in result.output
    assert "FAILED: boom" in result.output
    assert "failed: 1" in result.output
