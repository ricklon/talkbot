"""Local half-duplex voice pipeline with VAD, STT, LLM, and TTS playback."""

from __future__ import annotations

import queue
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

import numpy as np

from talkbot.llm import create_llm_client, supports_tools
from talkbot.thinking import apply_thinking_system_prompt
from talkbot.text_utils import strip_thinking
from talkbot.tts import TTSManager
from talkbot.tools import register_all_tools


class MissingVoiceDependencies(RuntimeError):
    """Raised when optional voice dependencies are not installed."""


@dataclass
class VoiceConfig:
    """Configuration for the local voice pipeline."""

    sample_rate: int = 16000
    channels: int = 1
    block_duration_ms: int = 32
    vad_threshold: float = 0.3
    min_speech_ms: int = 250
    min_silence_ms: int = 1200
    max_utterance_sec: float = 12.0
    stt_model: str = "small.en"
    stt_language: str = "en"
    stt_beam_size: int = 1
    stt_compute_type: str = "int8"
    min_transcript_chars: int = 2
    energy_threshold: float = 0.003
    device_in: int | str | None = None
    device_out: int | str | None = None
    allow_barge_in: bool = True

    @property
    def block_size(self) -> int:
        return int(self.sample_rate * self.block_duration_ms / 1000)


class VoicePipeline:
    """Half-duplex local voice chat pipeline."""

    def __init__(
        self,
        api_key: Optional[str],
        model: str,
        *,
        provider: str = "local",
        enable_thinking: bool = False,
        local_model_path: Optional[str] = None,
        llamacpp_bin: Optional[str] = None,
        site_url: Optional[str] = None,
        site_name: Optional[str] = None,
        tts_backend: Optional[str] = None,
        tts_voice: Optional[str] = None,
        tts_rate: int = 175,
        tts_volume: float = 1.0,
        speak: bool = True,
        system_prompt: Optional[str] = None,
        use_tools: bool = False,
        config: Optional[VoiceConfig] = None,
    ) -> None:
        self.api_key = api_key
        self.provider = provider
        self.enable_thinking = enable_thinking
        self.model = model
        self.local_model_path = local_model_path
        self.llamacpp_bin = llamacpp_bin
        self.site_url = site_url
        self.site_name = site_name
        self.tts_backend = tts_backend
        self.tts_voice = tts_voice
        self.tts_rate = tts_rate
        self.tts_volume = tts_volume
        self.speak = speak
        self.system_prompt = system_prompt
        self.use_tools = use_tools
        self.config = config or VoiceConfig()

        self._stop_event = threading.Event()
        self._history: list[dict] = []

        self._sd = None
        self._sf = None
        self._whisper_model = None
        self._vad_model = None
        self._get_speech_timestamps = None

    @staticmethod
    def list_audio_devices() -> list[dict]:
        """Return discovered audio devices."""
        try:
            import sounddevice as sd
        except Exception as e:
            raise MissingVoiceDependencies(
                "Voice dependencies missing. Install with: uv sync --extra voice"
            ) from e

        devices = []
        for idx, dev in enumerate(sd.query_devices()):
            devices.append(
                {
                    "index": idx,
                    "name": str(dev.get("name", f"Device {idx}")),
                    "max_input_channels": int(dev.get("max_input_channels", 0)),
                    "max_output_channels": int(dev.get("max_output_channels", 0)),
                }
            )
        return devices

    def stop(self) -> None:
        """Request the pipeline to stop."""
        self._stop_event.set()

    def _ensure_dependencies(self) -> None:
        if self._sd is None:
            try:
                import sounddevice as sd  # type: ignore
                import soundfile as sf  # type: ignore
                from faster_whisper import WhisperModel  # type: ignore
                from silero_vad import (  # type: ignore
                    get_speech_timestamps,
                    load_silero_vad,
                )
            except Exception as e:
                raise MissingVoiceDependencies(
                    "Voice dependencies missing. Install with: uv sync --extra voice"
                ) from e

            self._sd = sd
            self._sf = sf
            self._whisper_model = WhisperModel(
                self.config.stt_model,
                device="cpu",
                compute_type=self.config.stt_compute_type,
            )
            self._vad_model = load_silero_vad()
            self._get_speech_timestamps = get_speech_timestamps

    def _chunk_has_speech(self, chunk: np.ndarray) -> bool:
        if self._get_speech_timestamps is None:
            return False

        audio = chunk.astype(np.float32).flatten()
        if audio.size == 0:
            return False

        try:
            ts = self._get_speech_timestamps(
                audio,
                self._vad_model,
                sampling_rate=self.config.sample_rate,
                threshold=self.config.vad_threshold,
            )
        except TypeError:
            ts = self._get_speech_timestamps(
                audio, self._vad_model, sampling_rate=self.config.sample_rate
            )
        return bool(ts)

    def _capture_until_pause(
        self, on_event: Optional[Callable[[dict], None]] = None
    ) -> Optional[np.ndarray]:
        assert self._sd is not None

        q: queue.Queue[np.ndarray] = queue.Queue()

        def callback(indata, _frames, _time_info, status):
            if status:
                return
            q.put(indata.copy().reshape(-1))

        speech_started = False
        speech_ms = 0
        silence_ms = 0
        max_rms = 0.0
        captured: list[np.ndarray] = []
        start = time.monotonic()

        with self._sd.InputStream(
            samplerate=self.config.sample_rate,
            channels=self.config.channels,
            dtype="float32",
            blocksize=self.config.block_size,
            device=self.config.device_in,
            callback=callback,
        ):
            while not self._stop_event.is_set():
                if time.monotonic() - start > self.config.max_utterance_sec:
                    break

                try:
                    chunk = q.get(timeout=0.2)
                except queue.Empty:
                    continue

                if on_event:
                    # Simple RMS-based mic activity level for UI metering.
                    rms = float(np.sqrt(np.mean(np.square(chunk)))) if chunk.size else 0.0
                    level = max(0.0, min(1.0, rms * 8.0))
                    on_event({"type": "mic_level", "level": level})
                else:
                    rms = float(np.sqrt(np.mean(np.square(chunk)))) if chunk.size else 0.0

                max_rms = max(max_rms, rms)

                captured.append(chunk)
                has_speech = self._chunk_has_speech(chunk) or rms >= self.config.energy_threshold

                if has_speech:
                    speech_ms += self.config.block_duration_ms
                    silence_ms = 0
                    if not speech_started:
                        speech_started = True
                        if on_event:
                            on_event({"type": "speech_started"})
                else:
                    silence_ms += self.config.block_duration_ms

                if speech_started and speech_ms >= self.config.min_speech_ms:
                    if silence_ms >= self.config.min_silence_ms:
                        if on_event:
                            on_event({"type": "speech_ended"})
                        break

        if not captured or not speech_started:
            if on_event:
                on_event({"type": "no_speech_detected", "max_rms": max_rms})
            return None
        return np.concatenate(captured).astype(np.float32)

    def _transcribe(self, audio: np.ndarray) -> str:
        assert self._whisper_model is not None

        segments, _ = self._whisper_model.transcribe(
            audio,
            language=self.config.stt_language,
            beam_size=self.config.stt_beam_size,
            vad_filter=False,
        )
        text = " ".join(seg.text.strip() for seg in segments if seg.text.strip())
        return text.strip()

    def _chat_with_context(self, client, user_text: str) -> str:
        if not self._history:
            effective_system = apply_thinking_system_prompt(
                self.system_prompt, self.enable_thinking
            )
            if effective_system:
                self._history.append({"role": "system", "content": effective_system})
        self._history.append({"role": "user", "content": user_text})
        if self.use_tools:
            content = client.chat_with_tools(self._history).strip()
        else:
            response = client.chat_completion(self._history)
            content = response["choices"][0]["message"].get("content", "").strip()
        # Keep history compact so long chain-of-thought content doesn't exhaust context.
        assistant_visible = strip_thinking(content).strip() or content
        self._history.append({"role": "assistant", "content": assistant_visible})
        self._trim_history()
        return content

    def _trim_history(self, max_dialog_messages: int = 12) -> None:
        """Retain system prompt and the most recent dialog messages."""
        if len(self._history) <= max_dialog_messages + 1:
            return
        system_messages = [m for m in self._history if m.get("role") == "system"][:1]
        dialog_messages = [m for m in self._history if m.get("role") != "system"]
        self._history = system_messages + dialog_messages[-max_dialog_messages:]

    def _start_barge_in_monitor(
        self,
        interrupted: threading.Event,
        on_event: Optional[Callable[[dict], None]] = None,
    ) -> threading.Thread:
        assert self._sd is not None

        def monitor() -> None:
            try:
                q: queue.Queue[np.ndarray] = queue.Queue()

                def callback(indata, _frames, _time_info, status):
                    if status:
                        return
                    q.put(indata.copy().reshape(-1))

                with self._sd.InputStream(
                    samplerate=self.config.sample_rate,
                    channels=self.config.channels,
                    dtype="float32",
                    blocksize=self.config.block_size,
                    device=self.config.device_in,
                    callback=callback,
                ):
                    while not interrupted.is_set() and not self._stop_event.is_set():
                        try:
                            chunk = q.get(timeout=0.2)
                        except queue.Empty:
                            continue
                        if on_event:
                            rms = (
                                float(np.sqrt(np.mean(np.square(chunk))))
                                if chunk.size
                                else 0.0
                            )
                            level = max(0.0, min(1.0, rms * 8.0))
                            on_event({"type": "mic_level", "level": level})
                        if self._chunk_has_speech(chunk):
                            interrupted.set()
                            return
            except Exception as e:
                if on_event:
                    on_event({"type": "barge_in_unavailable", "error": str(e)})
                return

        t = threading.Thread(target=monitor, daemon=True)
        t.start()
        return t

    def _play_audio_interruptible(
        self, audio: np.ndarray, sample_rate: int, interrupted: threading.Event
    ) -> None:
        assert self._sd is not None

        if audio.ndim == 1:
            audio = audio.reshape(-1, 1)

        # Adapt to output device capabilities to avoid ALSA/PortAudio stream setup failures.
        try:
            dev_info = self._sd.query_devices(self.config.device_out, "output")
            target_sr = int(float(dev_info.get("default_samplerate", sample_rate)))
            max_out_channels = int(dev_info.get("max_output_channels", audio.shape[1]))
        except Exception:
            target_sr = int(sample_rate)
            max_out_channels = audio.shape[1]

        if target_sr > 0 and target_sr != sample_rate:
            old_n = audio.shape[0]
            new_n = max(1, int(round(old_n * (target_sr / float(sample_rate)))))
            old_x = np.linspace(0.0, 1.0, old_n, endpoint=False, dtype=np.float32)
            new_x = np.linspace(0.0, 1.0, new_n, endpoint=False, dtype=np.float32)
            resampled = np.zeros((new_n, audio.shape[1]), dtype=np.float32)
            for c in range(audio.shape[1]):
                resampled[:, c] = np.interp(new_x, old_x, audio[:, c]).astype(np.float32)
            audio = resampled
            sample_rate = target_sr

        if max_out_channels <= 0:
            raise RuntimeError("Selected output device has no output channels")
        if audio.shape[1] > max_out_channels:
            # Downmix to the device's channel count.
            mono = np.mean(audio, axis=1, keepdims=True, dtype=np.float32)
            if max_out_channels == 1:
                audio = mono
            else:
                audio = np.repeat(mono, max_out_channels, axis=1)

        with self._sd.OutputStream(
            samplerate=sample_rate,
            channels=audio.shape[1],
            dtype="float32",
            device=self.config.device_out,
        ) as stream:
            chunk_size = max(1, sample_rate // 10)
            for start in range(0, audio.shape[0], chunk_size):
                if interrupted.is_set() or self._stop_event.is_set():
                    break
                stream.write(audio[start : start + chunk_size])

    def _speak_response(
        self, tts: TTSManager, text: str, on_event: Optional[Callable[[dict], None]] = None
    ) -> bool:
        if not self.speak:
            return False

        interrupted = threading.Event()
        monitor_thread = None

        try:
            suffix = ".mp3" if tts.backend_name == "edge-tts" else ".wav"
            with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as f:
                out_path = f.name

            try:
                tts.save_to_file(text, out_path)

                if self.config.allow_barge_in:
                    monitor_thread = self._start_barge_in_monitor(
                        interrupted, on_event=on_event
                    )
                assert self._sf is not None
                audio, sr = self._sf.read(out_path, dtype="float32", always_2d=False)
                self._play_audio_interruptible(np.asarray(audio), int(sr), interrupted)
            finally:
                Path(out_path).unlink(missing_ok=True)
        except Exception:
            # Preserve existing behavior as fallback if sounddevice-file playback fails.
            tts.speak(text)
            return False
        finally:
            if monitor_thread and monitor_thread.is_alive():
                interrupted.set()
                monitor_thread.join(timeout=0.5)

        if interrupted.is_set() and on_event:
            on_event({"type": "tts_interrupted"})
        return interrupted.is_set()

    def run(
        self,
        on_event: Optional[Callable[[dict], None]] = None,
    ) -> None:
        """Run conversational voice loop until stopped."""
        self._ensure_dependencies()

        tts = TTSManager(rate=self.tts_rate, volume=self.tts_volume, backend=self.tts_backend)
        if self.tts_voice:
            tts.set_voice(self.tts_voice)

        with create_llm_client(
            provider=self.provider,
            model=self.model,
            api_key=self.api_key,
            site_url=self.site_url,
            site_name=self.site_name,
            local_model_path=self.local_model_path,
            llamacpp_bin=self.llamacpp_bin,
            enable_thinking=self.enable_thinking,
        ) as client:
            if self.use_tools and supports_tools(client):
                register_all_tools(client)
            if on_event:
                on_event({"type": "ready"})

            while not self._stop_event.is_set():
                if on_event:
                    on_event({"type": "listening"})
                audio = self._capture_until_pause(on_event=on_event)
                if self._stop_event.is_set():
                    return
                if audio is None:
                    continue

                if on_event:
                    on_event({"type": "transcribing"})
                transcript = self._transcribe(audio)
                if not transcript.strip():
                    if on_event:
                        on_event({"type": "transcript_empty"})
                    continue
                if len(transcript.strip()) < self.config.min_transcript_chars:
                    if on_event:
                        on_event({"type": "transcript_rejected", "text": transcript})
                    continue
                if on_event:
                    on_event({"type": "transcript", "text": transcript})

                if on_event:
                    on_event({"type": "thinking"})
                response = self._chat_with_context(client, transcript)
                if on_event:
                    on_event({"type": "response", "text": response})

                if self.speak and not self._stop_event.is_set():
                    if on_event:
                        on_event({"type": "speaking"})
                    self._speak_response(tts, strip_thinking(response), on_event=on_event)

    def transcribe_once(
        self, on_event: Optional[Callable[[dict], None]] = None
    ) -> Optional[str]:
        """Capture one utterance from mic and return transcript text."""
        self._ensure_dependencies()
        if on_event:
            on_event({"type": "listening"})
        audio = self._capture_until_pause(on_event=on_event)
        if audio is None:
            return None
        if on_event:
            on_event({"type": "transcribing"})
        transcript = self._transcribe(audio).strip()
        if len(transcript) < self.config.min_transcript_chars:
            return None
        return transcript


def transcribe_audio_file(
    path: str,
    *,
    stt_model: str = "small.en",
    language: str = "en",
    compute_type: str = "int8",
    beam_size: int = 1,
) -> str:
    """Transcribe an existing audio file using faster-whisper on CPU."""
    try:
        import soundfile as sf  # type: ignore
        from faster_whisper import WhisperModel  # type: ignore
    except Exception as e:
        raise MissingVoiceDependencies(
            "Voice dependencies missing. Install with: uv sync --extra voice"
        ) from e

    audio, _sr = sf.read(path, dtype="float32", always_2d=False)
    audio_np = np.asarray(audio, dtype=np.float32)
    model = WhisperModel(stt_model, device="cpu", compute_type=compute_type)
    segments, _ = model.transcribe(
        audio_np,
        language=language,
        beam_size=beam_size,
        vad_filter=False,
    )
    text = " ".join(seg.text.strip() for seg in segments if seg.text.strip())
    return text.strip()


def run_voice_diagnostics(stt_model: str = "small.en") -> dict:
    """Run one-pass local voice diagnostics."""
    report = {
        "dependencies_ok": False,
        "input_devices": 0,
        "output_devices": 0,
        "default_input": None,
        "default_output": None,
        "vad_loaded": False,
        "stt_loaded": False,
    }

    pipeline = VoicePipeline(api_key="diagnostic", model="diagnostic", speak=False)
    pipeline.config.stt_model = stt_model
    pipeline._ensure_dependencies()

    report["dependencies_ok"] = True

    devices = VoicePipeline.list_audio_devices()
    report["input_devices"] = len([d for d in devices if d["max_input_channels"] > 0])
    report["output_devices"] = len([d for d in devices if d["max_output_channels"] > 0])

    if pipeline._sd is not None:
        default_in, default_out = pipeline._sd.default.device
        report["default_input"] = default_in
        report["default_output"] = default_out

    report["vad_loaded"] = pipeline._vad_model is not None
    report["stt_loaded"] = pipeline._whisper_model is not None
    return report
