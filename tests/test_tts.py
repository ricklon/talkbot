from types import SimpleNamespace

import pytest

from talkbot import tts


def test_edge_tts_save_to_file_calls_synthesize(monkeypatch):
    backend = tts.EdgeTTS(voice="en-US-Test")
    captured = {}

    async def fake_synthesize(text, filename, rate, volume):
        captured["text"] = text
        captured["filename"] = filename
        captured["rate"] = rate
        captured["volume"] = volume

    monkeypatch.setattr(backend, "_synthesize", fake_synthesize)

    backend.save_to_file("hello", "out.mp3", rate="+10%", volume="-20%")

    assert captured == {
        "text": "hello",
        "filename": "out.mp3",
        "rate": "+10%",
        "volume": "-20%",
    }


def test_edge_tts_available_voices_success(monkeypatch):
    backend = tts.EdgeTTS()

    async def fake_get_voices():
        return [
            {
                "ShortName": "en-US-AriaNeural",
                "FriendlyName": "Aria",
                "Locale": "en-US",
                "Gender": "Female",
            }
        ]

    monkeypatch.setattr(backend, "_get_voices", fake_get_voices)

    voices = backend.available_voices

    assert voices == [
        {
            "id": "en-US-AriaNeural",
            "name": "Aria (en-US)",
            "languages": ["en-US"],
            "gender": "Female",
            "backend": "edge-tts",
        }
    ]


def test_edge_tts_available_voices_fallback(monkeypatch):
    backend = tts.EdgeTTS()

    async def fail_get_voices():
        raise RuntimeError("network unavailable")

    monkeypatch.setattr(backend, "_get_voices", fail_get_voices)

    voices = backend.available_voices

    assert len(voices) == len(tts.EdgeTTS.DEFAULT_VOICES)
    assert all(voice["backend"] == "edge-tts" for voice in voices)


def test_pyttsx3_backend_speak_and_save(monkeypatch):
    class FakeEngine:
        def __init__(self):
            self.calls = []

        def setProperty(self, key, value):
            self.calls.append(("setProperty", key, value))

        def say(self, text):
            self.calls.append(("say", text))

        def runAndWait(self):
            self.calls.append(("runAndWait",))

        def save_to_file(self, text, filename):
            self.calls.append(("save_to_file", text, filename))

        def getProperty(self, name):
            assert name == "voices"
            return [SimpleNamespace(id="id1", name="Voice 1", languages=["en-US"])]

    fake_engine = FakeEngine()

    monkeypatch.setattr(tts, "PYTTSX3_AVAILABLE", True)
    monkeypatch.setattr(tts, "pyttsx3", SimpleNamespace(init=lambda: fake_engine))

    backend = tts.Pyttsx3TTS(voice_id="voice-id")
    backend.speak("hello", rate=120, volume=0.5)
    backend.save_to_file("bye", "out.wav", rate=150)

    assert ("setProperty", "voice", "voice-id") in fake_engine.calls
    assert ("say", "hello") in fake_engine.calls
    assert ("save_to_file", "bye", "out.wav") in fake_engine.calls
    assert ("setProperty", "rate", 120) in fake_engine.calls
    assert ("setProperty", "volume", 0.5) in fake_engine.calls
    assert ("setProperty", "rate", 150) in fake_engine.calls

    voices = backend.available_voices
    assert voices[0]["id"] == "id1"
    assert voices[0]["backend"] == "pyttsx3"


def test_pyttsx3_autosets_espeak_data_path_when_missing(monkeypatch):
    class FakeEngine:
        def setProperty(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr(tts, "PYTTSX3_AVAILABLE", True)
    monkeypatch.setattr(tts, "pyttsx3", SimpleNamespace(init=lambda: FakeEngine()))
    monkeypatch.delenv("ESPEAK_DATA_PATH", raising=False)
    monkeypatch.setattr(tts.Path, "exists", lambda p: str(p) == "/usr/lib/espeak-ng-data")
    monkeypatch.setattr(
        tts.Pyttsx3TTS,
        "ESPEAK_DATA_CANDIDATES",
        ["/does-not-exist", "/usr/lib/espeak-ng-data"],
    )

    tts.Pyttsx3TTS()

    assert tts.os.getenv("ESPEAK_DATA_PATH") == "/usr/lib/espeak-ng-data"


def test_pyttsx3_keeps_existing_espeak_data_path(monkeypatch):
    class FakeEngine:
        def setProperty(self, *_args, **_kwargs):
            return None

    monkeypatch.setattr(tts, "PYTTSX3_AVAILABLE", True)
    monkeypatch.setattr(tts, "pyttsx3", SimpleNamespace(init=lambda: FakeEngine()))
    monkeypatch.setenv("ESPEAK_DATA_PATH", "/custom/espeak-data")
    monkeypatch.setattr(tts.Path, "exists", lambda _p: False)

    tts.Pyttsx3TTS()

    assert tts.os.getenv("ESPEAK_DATA_PATH") == "/custom/espeak-data"


def test_kitten_backend_save_to_file(monkeypatch):
    created = {}

    class FakeModel:
        def __init__(self, model_name):
            created["model_name"] = model_name

        def generate(self, text, voice):
            created["text"] = text
            created["voice"] = voice
            return "fake-audio"

    monkeypatch.setattr(tts, "KITTENTTS_AVAILABLE", True)
    monkeypatch.setattr(tts, "_KittenTTS", FakeModel)

    backend = tts.KittenTTSBackend(voice="Bella", model="test-model")
    written = {}
    monkeypatch.setattr(
        backend,
        "_write_wav",
        lambda path, audio: written.update({"path": path, "audio": audio}),
    )

    backend.save_to_file("hello kitten", "kitten.wav")

    assert created["model_name"] == "test-model"
    assert created["text"] == "hello kitten"
    assert created["voice"] == "Bella"
    assert written == {"path": "kitten.wav", "audio": "fake-audio"}
    assert backend.available_voices[0]["backend"] == "kittentts"


def test_kitten_backend_uses_library_default_model_when_unspecified(monkeypatch):
    created = {"args": None}

    class FakeModel:
        def __init__(self, *args):
            created["args"] = args

    monkeypatch.setattr(tts, "KITTENTTS_AVAILABLE", True)
    monkeypatch.setattr(tts, "_KittenTTS", FakeModel)

    tts.KittenTTSBackend()

    assert created["args"] == ()


def test_tts_manager_prefers_edge_backend(monkeypatch):
    class FakeEdge:
        def __init__(self, voice_id):
            self.voice_id = voice_id

    monkeypatch.setattr(tts, "EDGE_TTS_AVAILABLE", True)
    monkeypatch.setattr(tts, "KITTENTTS_AVAILABLE", True)
    monkeypatch.setattr(tts, "PYTTSX3_AVAILABLE", True)
    monkeypatch.setattr(tts, "EdgeTTS", FakeEdge)

    manager = tts.TTSManager(voice_id="voice-x")

    assert manager.backend_name == "edge-tts"
    assert isinstance(manager.backend, FakeEdge)
    assert manager.backend.voice_id == "voice-x"


def test_tts_manager_forced_kitten_raises_if_init_fails(monkeypatch):
    monkeypatch.setattr(tts, "EDGE_TTS_AVAILABLE", True)
    monkeypatch.setattr(tts, "KITTENTTS_AVAILABLE", True)
    monkeypatch.setattr(tts, "PYTTSX3_AVAILABLE", True)
    monkeypatch.setattr(
        tts, "KittenTTSBackend", lambda _voice_id: (_ for _ in ()).throw(Exception("boom"))
    )

    with pytest.raises(RuntimeError, match="Failed to initialize kittentts"):
        tts.TTSManager(backend="kittentts")


def test_tts_manager_edge_rate_and_volume_conversion(monkeypatch):
    class FakeEdge:
        def __init__(self, _voice_id):
            self.calls = []

        def speak(self, text, rate, volume):
            self.calls.append({"text": text, "rate": rate, "volume": volume})

    monkeypatch.setattr(tts, "EDGE_TTS_AVAILABLE", True)
    monkeypatch.setattr(tts, "KITTENTTS_AVAILABLE", False)
    monkeypatch.setattr(tts, "PYTTSX3_AVAILABLE", False)
    monkeypatch.setattr(tts, "EdgeTTS", FakeEdge)

    manager = tts.TTSManager(rate=350, volume=0.5)
    manager._do_speak("edge text")

    assert manager.backend.calls == [
        {"text": "edge text", "rate": "+100%", "volume": "-50%"}
    ]


def test_tts_manager_pyttsx3_speak_passthrough(monkeypatch):
    class FakePyttsx3:
        def __init__(self, _voice_id):
            self.calls = []

        def speak(self, text, rate, volume):
            self.calls.append({"text": text, "rate": rate, "volume": volume})

    monkeypatch.setattr(tts, "EDGE_TTS_AVAILABLE", False)
    monkeypatch.setattr(tts, "KITTENTTS_AVAILABLE", False)
    monkeypatch.setattr(tts, "PYTTSX3_AVAILABLE", True)
    monkeypatch.setattr(tts, "Pyttsx3TTS", FakePyttsx3)

    manager = tts.TTSManager(rate=200, volume=0.8)
    manager._do_speak("offline text")

    assert manager.backend_name == "pyttsx3"
    assert manager.backend.calls == [
        {"text": "offline text", "rate": 200, "volume": 0.8}
    ]


def test_tts_manager_edge_falls_back_to_pyttsx3(monkeypatch):
    monkeypatch.setattr(tts, "EDGE_TTS_AVAILABLE", True)
    monkeypatch.setattr(tts, "KITTENTTS_AVAILABLE", False)
    monkeypatch.setattr(tts, "PYTTSX3_AVAILABLE", True)
    monkeypatch.setattr(
        tts, "EdgeTTS", lambda _voice_id: (_ for _ in ()).throw(Exception("edge down"))
    )

    class FakePyttsx3:
        def __init__(self, _voice_id):
            pass

    monkeypatch.setattr(tts, "Pyttsx3TTS", FakePyttsx3)

    manager = tts.TTSManager(backend="edge-tts")

    assert manager.backend_name == "pyttsx3"
