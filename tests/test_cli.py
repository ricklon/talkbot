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

    def chat_with_system_tools(self, message, system_prompt=None):
        return f"tool-reply:{message}:{system_prompt}"


def fake_create_client(**kwargs):
    return FakeClient(api_key=kwargs.get("api_key"), model=kwargs.get("model"))


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


class FakeVoicePipeline:
    calls = []

    def __init__(
        self,
        api_key,
        model,
        provider="local",
        enable_thinking=False,
        local_model_path=None,
        llamacpp_bin=None,
        site_url=None,
        site_name=None,
        tts_backend=None,
        tts_voice=None,
        tts_rate=175,
        tts_volume=1.0,
        speak=True,
        system_prompt=None,
        use_tools=False,
        config=None,
    ):
        FakeVoicePipeline.calls.append(
            {
                "api_key": api_key,
                "model": model,
                "provider": provider,
                "enable_thinking": enable_thinking,
                "local_model_path": local_model_path,
                "llamacpp_bin": llamacpp_bin,
                "site_url": site_url,
                "site_name": site_name,
                "tts_backend": tts_backend,
                "tts_voice": tts_voice,
                "tts_rate": tts_rate,
                "tts_volume": tts_volume,
                "speak": speak,
                "system_prompt": system_prompt,
                "use_tools": use_tools,
                "config": config,
            }
        )

    def run(self, on_event=None):
        if on_event:
            on_event({"type": "transcript", "text": "hello"})
            on_event({"type": "response", "text": "world"})

    def transcribe_once(self, on_event=None):
        if on_event:
            on_event({"type": "listening"})
        return "mic transcript"

    def stop(self):
        return None


def test_chat_command_no_speak(monkeypatch):
    monkeypatch.setattr(cli_module, "create_llm_client", fake_create_client)

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

    monkeypatch.setattr(cli_module, "create_llm_client", fake_create_client)
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
    assert len(tts_instances[0].spoken) == 1
    assert tts_instances[0].spoken[0].startswith("reply:Hi:")


def test_chat_command_tools_mode(monkeypatch):
    monkeypatch.setattr(cli_module, "create_llm_client", fake_create_client)
    monkeypatch.setattr(cli_module, "register_all_tools", lambda _client: None)

    runner = CliRunner()
    result = runner.invoke(
        cli_module.cli,
        ["--api-key", "k", "chat", "Hi", "--no-speak", "--tools", "--system", "sys"],
    )

    assert result.exit_code == 0
    assert "AI: tool-reply:Hi:sys" in result.output


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


def test_voice_chat_command_uses_pipeline(monkeypatch):
    monkeypatch.setattr(cli_module, "VoicePipeline", FakeVoicePipeline)
    FakeVoicePipeline.calls = []

    runner = CliRunner()
    result = runner.invoke(
        cli_module.cli,
        [
            "--api-key",
            "k",
            "--model",
            "m",
            "voice-chat",
            "--backend",
            "kittentts",
            "--stt-model",
            "base.en",
            "--language",
            "en",
            "--device-in",
            "2",
            "--device-out",
            "3",
            "--vad-threshold",
            "0.6",
            "--vad-min-speech-ms",
            "300",
            "--vad-min-silence-ms",
            "800",
            "--max-utterance-sec",
            "10",
            "--no-speak",
        ],
    )

    assert result.exit_code == 0
    assert "Voice chat started." in result.output
    assert "You (voice): hello" in result.output
    assert "AI: world" in result.output
    assert len(FakeVoicePipeline.calls) == 1
    call = FakeVoicePipeline.calls[0]
    assert call["api_key"] == "k"
    assert call["provider"] == "local"
    assert call["enable_thinking"] is False
    assert call["model"] == "m"
    assert call["tts_backend"] == "kittentts"
    assert call["speak"] is False
    assert call["config"].stt_model == "base.en"
    assert call["config"].device_in == 2
    assert call["config"].device_out == 3


def test_doctor_voice_success(monkeypatch):
    monkeypatch.setattr(
        cli_module,
        "run_voice_diagnostics",
        lambda stt_model="small.en": {
            "dependencies_ok": True,
            "input_devices": 1,
            "output_devices": 2,
            "default_input": 0,
            "default_output": 1,
            "vad_loaded": True,
            "stt_loaded": True,
        },
    )

    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["doctor-voice", "--stt-model", "small.en"])

    assert result.exit_code == 0
    assert "Voice Diagnostics" in result.output
    assert "dependencies: OK" in result.output
    assert "silero-vad model: OK" in result.output
    assert "faster-whisper model: OK" in result.output
    assert "failed: 0" in result.output


def test_doctor_voice_failure(monkeypatch):
    def fail(*_args, **_kwargs):
        raise RuntimeError("boom")

    monkeypatch.setattr(cli_module, "run_voice_diagnostics", fail)

    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["doctor-voice"])

    assert result.exit_code == 1
    assert "diagnostic run: FAILED (boom)" in result.output
    assert "failed: 1" in result.output


def test_test_stt_from_mic(monkeypatch):
    monkeypatch.setattr(cli_module, "VoicePipeline", FakeVoicePipeline)
    runner = CliRunner()
    result = runner.invoke(cli_module.cli, ["test-stt", "--stt-model", "small.en"])
    assert result.exit_code == 0
    assert "Speak once, then pause..." in result.output
    assert "Transcript: mic transcript" in result.output


def test_test_stt_from_file(monkeypatch):
    monkeypatch.setattr(
        cli_module,
        "transcribe_audio_file",
        lambda path, stt_model="small.en", language="en": f"from:{path}:{stt_model}:{language}",
    )
    runner = CliRunner()
    result = runner.invoke(
        cli_module.cli,
        ["test-stt", "--file", "sample.wav", "--stt-model", "base.en", "--language", "en"],
    )
    assert result.exit_code == 0
    assert "Transcript: from:sample.wav:base.en:en" in result.output


def test_test_stt_simulate_uses_tts(monkeypatch):
    monkeypatch.setattr(cli_module, "VoicePipeline", FakeVoicePipeline)
    tts_instances = []

    def fake_tts_factory(rate=175, volume=1.0, backend=None):
        obj = FakeTTS(rate=rate, volume=volume, backend=backend)
        tts_instances.append(obj)
        return obj

    monkeypatch.setattr(cli_module, "TTSManager", fake_tts_factory)

    runner = CliRunner()
    result = runner.invoke(
        cli_module.cli,
        [
            "test-stt",
            "--simulate",
            "--prompt-text",
            "Can you hear this prompt?",
            "--backend",
            "pyttsx3",
            "--voice",
            "v1",
        ],
    )

    assert result.exit_code == 0
    assert "Prompt: Can you hear this prompt?" in result.output
    assert len(tts_instances) == 1
    assert tts_instances[0].backend == "pyttsx3"
    assert tts_instances[0].voice == "v1"
    assert tts_instances[0].spoken == ["Can you hear this prompt?"]
