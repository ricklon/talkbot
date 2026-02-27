"""Text-to-speech module with edge-tts as primary and pyttsx3 as fallback."""

import asyncio
import contextlib
import logging
import os
import queue
import subprocess
import sys
import tempfile
import threading
from pathlib import Path
from typing import Optional

# Keep startup noise low when local HF-backed libraries initialize without a token.
logging.getLogger("huggingface_hub").setLevel(logging.ERROR)
# Avoid hf-xet token warning noise in default local setup.
os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
# Disable HF download progress bars: tqdm crashes when stdout is fd-redirected during
# KittenTTS init (_suppress_stdio_fds sends fd 1 to devnull before hf_hub_download runs).
os.environ.setdefault("HF_HUB_DISABLE_PROGRESS_BARS", "1")
# Suppress Windows symlink warning — HF cache works fine without symlinks.
os.environ.setdefault("HF_HUB_DISABLE_SYMLINKS_WARNING", "1")

# Try to import edge-tts, fall back to pyttsx3
try:
    import edge_tts
    from edge_tts import VoicesManager

    EDGE_TTS_AVAILABLE = True
except ImportError:
    EDGE_TTS_AVAILABLE = False

try:
    import pyttsx3

    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False

import importlib.util as _importlib_util
KITTENTTS_AVAILABLE = _importlib_util.find_spec("kittentts") is not None


def _configure_phonemizer_espeak_library() -> None:
    """Set PHONEMIZER_ESPEAK_LIBRARY when Homebrew libs are not auto-detected."""
    if os.getenv("PHONEMIZER_ESPEAK_LIBRARY"):
        return

    candidates = [
        "/opt/homebrew/lib/libespeak-ng.dylib",
        "/opt/homebrew/lib/libespeak.dylib",
        "/usr/local/lib/libespeak-ng.dylib",
        "/usr/local/lib/libespeak.dylib",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            os.environ["PHONEMIZER_ESPEAK_LIBRARY"] = candidate
            return


def _kittentts_error_hint(error: Exception) -> str:
    """Return a short actionable hint for common KittenTTS init failures."""
    text = str(error).lower()
    if "espeak" not in text:
        return ""

    if sys.platform.startswith("linux"):
        return (
            " Install eSpeak NG (for example: "
            "`sudo apt install espeak-ng espeak-ng-data` or "
            "`sudo dnf install espeak-ng`)."
        )
    if sys.platform == "darwin":
        return " Install eSpeak NG with Homebrew: `brew install espeak-ng`."
    if sys.platform.startswith("win"):
        return " Install eSpeak NG and ensure `espeak-ng.exe` is on PATH."
    return " Install eSpeak and ensure it is available on PATH."


class EdgeTTS:
    """Microsoft Edge TTS backend (online, high quality)."""

    # Voice mapping for common languages
    DEFAULT_VOICES = {
        "en": "en-US-AriaNeural",
        "en-gb": "en-GB-SoniaNeural",
        "es": "es-ES-ElviraNeural",
        "fr": "fr-FR-DeniseNeural",
        "de": "de-DE-KatjaNeural",
        "it": "it-IT-ElsaNeural",
        "ja": "ja-JP-NanamiNeural",
        "ko": "ko-KR-SunHiNeural",
        "pt": "pt-BR-FranciscaNeural",
        "ru": "ru-RU-SvetlanaNeural",
        "zh": "zh-CN-XiaoxiaoNeural",
    }

    def __init__(self, voice: Optional[str] = None):
        """Initialize Edge TTS.

        Args:
            voice: Voice ID to use. Uses default if not specified.
        """
        self.voice = voice or "en-US-AriaNeural"
        self._voices_cache: Optional[list] = None

    async def _get_voices(self) -> list:
        """Get available voices asynchronously."""
        if self._voices_cache is None:
            voices_manager = await VoicesManager.create()
            self._voices_cache = voices_manager.voices
        return self._voices_cache

    def speak(self, text: str, rate: str = "+0%", volume: str = "+0%") -> None:
        """Speak text using Edge TTS.

        Args:
            text: Text to speak.
            rate: Speech rate adjustment (e.g., "+0%", "+50%", "-20%").
            volume: Volume adjustment (e.g., "+0%", "+50%", "-20%").
        """
        # Create temporary mp3 file
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
            temp_path = f.name

        try:
            # Run async synthesis
            asyncio.run(self._synthesize(text, temp_path, rate, volume))

            # Play the audio
            self._play_audio(temp_path)
        finally:
            # Cleanup
            if Path(temp_path).exists():
                Path(temp_path).unlink()

    async def _synthesize(
        self, text: str, output_file: str, rate: str, volume: str
    ) -> None:
        """Async synthesis."""
        communicate = edge_tts.Communicate(text, self.voice, rate=rate, volume=volume)
        await communicate.save(output_file)

    def _play_audio(self, audio_file: str) -> None:
        """Play audio file using pygame (supports MP3)."""
        import pygame
        import time

        try:
            pygame.mixer.init()
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()

            # Wait for playback to finish
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)

            pygame.mixer.quit()
        except Exception as e:
            raise RuntimeError(f"Failed to play audio: {e}")

    def save_to_file(
        self, text: str, filename: str, rate: str = "+0%", volume: str = "+0%"
    ) -> None:
        """Save speech to audio file.

        Args:
            text: Text to speak.
            filename: Output filename.
            rate: Speech rate adjustment.
            volume: Volume adjustment.
        """
        asyncio.run(self._synthesize(text, filename, rate, volume))

    @property
    def available_voices(self) -> list[dict]:
        """Get list of available Edge TTS voices."""
        try:
            voices = asyncio.run(self._get_voices())
            return [
                {
                    "id": voice["ShortName"],
                    "name": f"{voice['FriendlyName']} ({voice['Locale']})",
                    "languages": [voice["Locale"]],
                    "gender": voice.get("Gender", "Unknown"),
                    "backend": "edge-tts",
                }
                for voice in voices
            ]
        except Exception:
            # Return default voices if we can't fetch the list
            return [
                {"id": v, "name": k, "languages": [k], "backend": "edge-tts"}
                for k, v in self.DEFAULT_VOICES.items()
            ]


class Pyttsx3TTS:
    """pyttsx3 TTS backend (offline fallback)."""

    ESPEAK_DATA_CANDIDATES = [
        "/usr/lib/x86_64-linux-gnu/espeak-ng-data",
        "/usr/lib/aarch64-linux-gnu/espeak-ng-data",
        "/usr/lib64/espeak-ng-data",
        "/usr/lib/espeak-ng-data",
        "/usr/share/espeak-ng-data",
    ]

    def __init__(self, voice_id: Optional[str] = None):
        """Initialize pyttsx3 TTS.

        Args:
            voice_id: Voice ID to use.
        """
        if not PYTTSX3_AVAILABLE:
            raise RuntimeError("pyttsx3 not available")

        self._ensure_espeak_data_path()
        self.engine = pyttsx3.init()
        self.voice_id = voice_id

        if voice_id:
            self.engine.setProperty("voice", voice_id)

    def _ensure_espeak_data_path(self) -> None:
        """Set ESPEAK_DATA_PATH automatically when available on system."""
        if os.getenv("ESPEAK_DATA_PATH"):
            return

        for candidate in self.ESPEAK_DATA_CANDIDATES:
            if Path(candidate).exists():
                os.environ["ESPEAK_DATA_PATH"] = candidate
                return

    def speak(self, text: str, rate: int = 175, volume: float = 1.0) -> None:
        """Speak text using pyttsx3.

        Args:
            text: Text to speak.
            rate: Speech rate (words per minute).
            volume: Volume level (0.0 to 1.0).
        """
        self.engine.setProperty("rate", rate)
        self.engine.setProperty("volume", volume)
        self.engine.say(text)
        self.engine.runAndWait()

    def save_to_file(self, text: str, filename: str, rate: int = 175) -> None:
        """Save speech to audio file.

        Args:
            text: Text to speak.
            filename: Output filename.
            rate: Speech rate.
        """
        self.engine.setProperty("rate", rate)
        self.engine.save_to_file(text, filename)
        self.engine.runAndWait()

    @property
    def available_voices(self) -> list[dict]:
        """Get list of available pyttsx3 voices."""
        voices = self.engine.getProperty("voices")
        return [
            {
                "id": voice.id,
                "name": voice.name,
                "languages": getattr(voice, "languages", ["unknown"]),
                "backend": "pyttsx3",
            }
            for voice in voices
        ]


class KittenTTSBackend:
    """KittenTTS backend (local, neural, no internet required)."""

    VOICES = [
        "Bella",
        "Jasper",
        "Luna",
        "Bruno",
        "Rosie",
        "Hugo",
        "Kiki",
        "Leo",
    ]
    DEFAULT_MODEL = "KittenML/kitten-tts-nano-0.8-int8"

    @staticmethod
    @contextlib.contextmanager
    def _suppress_stdio_fds():
        """Suppress low-level stdout/stderr noise from native deps during init.

        On Windows, os.dup() raises OSError for console handles — suppression is
        skipped gracefully and KittenTTS initialises normally (just with HF noise
        visible on first model download).
        """
        try:
            stdout_fd = os.dup(1)
            stderr_fd = os.dup(2)
        except OSError:
            # Windows: fd duplication not supported for console handles.
            # Continue without suppression — TTS is fully functional.
            yield
            return

        try:
            with open(os.devnull, "w", encoding="utf-8") as devnull:
                os.dup2(devnull.fileno(), 1)
                os.dup2(devnull.fileno(), 2)
                yield
        finally:
            try:
                os.dup2(stdout_fd, 1)
                os.dup2(stderr_fd, 2)
            finally:
                os.close(stdout_fd)
                os.close(stderr_fd)

    def __init__(self, voice: Optional[str] = None, model: Optional[str] = None):
        if not KITTENTTS_AVAILABLE:
            raise RuntimeError("kittentts not available")
        _configure_phonemizer_espeak_library()
        from kittentts import KittenTTS as _KittenTTS  # lazy: avoids torch at startup
        # Let KittenTTS select its own default model unless explicitly overridden.
        with self._suppress_stdio_fds():
            if model or self.DEFAULT_MODEL:
                self._model = _KittenTTS(model or self.DEFAULT_MODEL)
            else:
                self._model = _KittenTTS()
        model_voices = self._get_model_voices()
        self.voice = voice or (model_voices[0] if model_voices else self.VOICES[0])

        if model_voices and self.voice not in model_voices:
            raise RuntimeError(
                f"Invalid kittentts voice '{self.voice}'. Choose from: {model_voices}"
            )

    def _get_model_voices(self) -> list[str]:
        voices = getattr(self._model, "available_voices", None)
        if isinstance(voices, list) and voices:
            return [str(v) for v in voices]
        return []

    def speak(self, text: str) -> None:
        import wave

        audio = self._model.generate(text, voice=self.voice)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            temp_path = f.name
        try:
            self._write_wav(temp_path, audio)
            self._play_audio(temp_path)
        finally:
            if Path(temp_path).exists():
                Path(temp_path).unlink()

    def _write_wav(self, path: str, audio) -> None:
        import wave

        import numpy as np

        audio_int16 = (audio * 32767).astype(np.int16)
        with wave.open(path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_int16.tobytes())

    def _play_audio(self, path: str) -> None:
        import time

        import pygame

        pygame.mixer.init(frequency=24000)
        pygame.mixer.music.load(path)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.05)
        pygame.mixer.quit()

    def save_to_file(self, text: str, filename: str) -> None:
        audio = self._model.generate(text, voice=self.voice)
        self._write_wav(filename, audio)

    @property
    def available_voices(self) -> list[dict]:
        voices = self._get_model_voices() or self.VOICES
        return [
            {"id": v, "name": v, "languages": ["en"], "backend": "kittentts"}
            for v in voices
        ]


class TTSManager:
    """Manager for text-to-speech operations with edge-tts as primary and pyttsx3 as fallback."""

    def __init__(
        self,
        voice_id: Optional[str] = None,
        rate: int = 175,
        volume: float = 1.0,
        backend: Optional[str] = None,
    ):
        """Initialize the TTS manager.

        Args:
            voice_id: Voice ID to use. Uses default if not specified.
            rate: Speech rate (words per minute for pyttsx3, percent for edge-tts).
            volume: Volume level (0.0 to 1.0).
            backend: Force specific backend ('edge-tts', 'kittentts', or 'pyttsx3'). Auto-detect if None.
        """
        self.voice_id = voice_id
        self.rate = rate
        self.volume = volume
        self.backend_name = backend

        # Initialize backend
        self.backend = None
        self._init_backend()

        # Queue for async speaking
        self.speak_queue = queue.Queue()
        self.speaking = False
        self.speak_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()

    def _init_backend(self) -> None:
        """Initialize the TTS backend."""
        requested_backend = self.backend_name
        self.backend = None

        # Try edge-tts first unless an explicit local backend is requested.
        if requested_backend in (None, "edge-tts") and EDGE_TTS_AVAILABLE:
            try:
                self.backend = EdgeTTS(self.voice_id)
                self.backend_name = "edge-tts"
                return
            except Exception as e:
                print(f"Warning: Could not initialize edge-tts: {e}")

        # Try kittentts (local neural TTS)
        if requested_backend in (None, "edge-tts", "kittentts") and KITTENTTS_AVAILABLE:
            try:
                self.backend = KittenTTSBackend(self.voice_id)
                self.backend_name = "kittentts"
                return
            except Exception as e:
                hint = _kittentts_error_hint(e)
                if requested_backend == "kittentts":
                    raise RuntimeError(f"Failed to initialize kittentts: {e}{hint}")
                print(f"Warning: Could not initialize kittentts: {e}{hint}")

        # Try pyttsx3
        if requested_backend in (None, "edge-tts", "pyttsx3") and PYTTSX3_AVAILABLE:
            try:
                self.backend = Pyttsx3TTS(self.voice_id)
                self.backend_name = "pyttsx3"
                return
            except Exception as e:
                raise RuntimeError(f"Failed to initialize TTS backend: {e}")

        raise RuntimeError("No TTS backend available. Install edge-tts, kittentts, or pyttsx3.")

    @property
    def available_voices(self) -> list[dict]:
        """Get list of available voices.

        Returns:
            List of voice info dicts with 'id', 'name', 'languages', and 'backend'.
        """
        if self.backend:
            return self.backend.available_voices
        return []

    def list_voices(self) -> None:
        """Print available voices."""
        voices = self.available_voices

        # Group by backend
        edge_voices = [v for v in voices if v.get("backend") == "edge-tts"]
        pyttsx3_voices = [v for v in voices if v.get("backend") == "pyttsx3"]

        print(f"Available voices (using {self.backend_name} backend):")
        print()

        if edge_voices:
            print(f"Microsoft Edge Voices ({len(edge_voices)} available):")
            # Show first 10 voices as examples
            for voice in edge_voices[:10]:
                print(f"  {voice['id']:<30} - {voice['name']}")
            if len(edge_voices) > 10:
                print(f"  ... and {len(edge_voices) - 10} more voices")
            print()

        if pyttsx3_voices:
            print(f"System Voices ({len(pyttsx3_voices)} available):")
            for voice in pyttsx3_voices[:10]:
                print(f"  {voice['id']:<30} - {voice['name']}")
            if len(pyttsx3_voices) > 10:
                print(f"  ... and {len(pyttsx3_voices) - 10} more voices")
            print()

    def set_voice(self, voice_id: str) -> None:
        """Set the voice by ID.

        Args:
            voice_id: The voice ID to use.
        """
        self.voice_id = voice_id
        # Reinitialize backend with new voice
        self._init_backend()

    def set_rate(self, rate: int) -> None:
        """Set speech rate.

        Args:
            rate: Words per minute (pyttsx3) or rate adjustment (edge-tts).
        """
        self.rate = rate

    def set_volume(self, volume: float) -> None:
        """Set volume level.

        Args:
            volume: Volume from 0.0 to 1.0.
        """
        self.volume = max(0.0, min(1.0, volume))

    def speak(self, text: str, block: bool = True) -> None:
        """Speak the given text.

        Args:
            text: Text to speak.
            block: If True, block until speaking is done.
        """
        if block:
            self._do_speak(text)
        else:
            self.speak_queue.put(text)
            if (
                not self.speaking
                or not self.speak_thread
                or not self.speak_thread.is_alive()
            ):
                self._start_speaking()

    def _do_speak(self, text: str) -> None:
        """Internal speak method."""
        if not self.backend:
            raise RuntimeError("No TTS backend available")

        if self.backend_name == "edge-tts":
            rate_pct = f"{((self.rate - 175) / 175) * 100:+.0f}%"
            vol_pct = f"{(self.volume - 1.0) * 100:+.0f}%"
            self.backend.speak(text, rate=rate_pct, volume=vol_pct)
        elif self.backend_name == "kittentts":
            self.backend.speak(text)
        else:
            # pyttsx3 uses rate as words per minute
            self.backend.speak(text, rate=self.rate, volume=self.volume)

    def _speak_worker(self) -> None:
        """Worker thread for async speaking."""
        self.speaking = True

        while not self.stop_event.is_set():
            try:
                text = self.speak_queue.get(timeout=0.1)
                self._do_speak(text)
            except queue.Empty:
                continue
            except Exception:
                break

        self.speaking = False

    def _start_speaking(self) -> None:
        """Start the speaking thread."""
        self.stop_event.clear()
        self.speak_thread = threading.Thread(target=self._speak_worker)
        self.speak_thread.daemon = True
        self.speak_thread.start()

    def stop(self) -> None:
        """Stop speaking and clear queue."""
        self.stop_event.set()

        # Clear queue
        while not self.speak_queue.empty():
            try:
                self.speak_queue.get_nowait()
            except queue.Empty:
                break

        if self.backend_name == "pyttsx3":
            self.backend.engine.stop()

        if self.speak_thread and self.speak_thread.is_alive():
            self.speak_thread.join(timeout=1.0)

    def save_to_file(self, text: str, filename: str) -> None:
        """Save speech to audio file.

        Args:
            text: Text to speak.
            filename: Output filename.
        """
        if not self.backend:
            raise RuntimeError("No TTS backend available")

        if self.backend_name == "edge-tts":
            rate_pct = f"{((self.rate - 175) / 175) * 100:+.0f}%"
            vol_pct = f"{(self.volume - 1.0) * 100:+.0f}%"
            self.backend.save_to_file(text, filename, rate=rate_pct, volume=vol_pct)
        elif self.backend_name == "kittentts":
            self.backend.save_to_file(text, filename)
        else:
            self.backend.save_to_file(text, filename, rate=self.rate)
