import os
import subprocess
import sys

import pytest

from talkbot.tts import TTSManager


pytestmark = [
    pytest.mark.integration,
    pytest.mark.skipif(
        os.getenv("TALKBOT_RUN_TTS_INTEGRATION") != "1",
        reason="Set TALKBOT_RUN_TTS_INTEGRATION=1 to run real backend checks",
    ),
]


@pytest.mark.parametrize(
    ("backend", "filename"),
    [
        ("edge-tts", "edge_sample.mp3"),
        ("kittentts", "kitten_sample.wav"),
    ],
)
def test_tts_backend_can_synthesize_to_file(tmp_path, backend, filename):
    out = tmp_path / filename

    tts = TTSManager(backend=backend)
    tts.save_to_file("Hello from TalkBot integration test.", str(out))

    assert out.exists(), f"{backend} did not create output file"
    assert out.stat().st_size > 0, f"{backend} created an empty output file"


@pytest.mark.parametrize("backend", ["edge-tts", "kittentts"])
def test_tts_backend_reports_voices(backend):
    tts = TTSManager(backend=backend)
    voices = tts.available_voices

    assert isinstance(voices, list)
    assert len(voices) > 0
    assert isinstance(voices[0].get("id"), str)


def test_pyttsx3_backend_smoke_subprocess():
    script = """
from talkbot.tts import TTSManager
t = TTSManager(backend='pyttsx3')
print(len(t.available_voices))
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, (
        "pyttsx3 backend failed in subprocess\\n"
        f"stdout:\\n{result.stdout}\\n"
        f"stderr:\\n{result.stderr}"
    )
