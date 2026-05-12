"""麦克风录音 + 离线语音转文字（Vosk，本地运行，无需外网）。"""

from __future__ import annotations

import json
import os
import queue
import sys
import tempfile
import threading
import wave
from pathlib import Path

import numpy as np

from pdfgui.meeting.vosk_config import VOSK_CN_MODEL_NAME

try:
    import sounddevice as sd
except ImportError as e:
    sd = None  # type: ignore[misc, assignment]
    _SD_ERR = e
else:
    _SD_ERR = None

_vosk_model = None
_vosk_lock = threading.Lock()


def vosk_model_dir() -> Path:
    """开发：pdfgui/meeting/vosk_models/<name>；打包：_MEIPASS/pdfgui/meeting/vosk_models/<name>。"""
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / "pdfgui" / "meeting" / "vosk_models" / VOSK_CN_MODEL_NAME
    return Path(__file__).resolve().parent / "vosk_models" / VOSK_CN_MODEL_NAME


def vosk_model_ready() -> bool:
    return (vosk_model_dir() / "am" / "final.mdl").is_file()


def _load_vosk_model():
    from vosk import Model

    global _vosk_model
    root = vosk_model_dir()
    if not vosk_model_ready():
        raise FileNotFoundError(
            "未找到 Vosk 中文模型。请在项目根目录执行：\n  python scripts/fetch_vosk_cn_model.py"
        )
    with _vosk_lock:
        if _vosk_model is None:
            _vosk_model = Model(str(root))
        return _vosk_model


class MicRecorder:
    """使用 sounddevice 从默认输入设备连续采集单声道 float32，直到 stop。"""

    def __init__(self, samplerate: int = 16000) -> None:
        if sd is None:
            raise ImportError("请安装 sounddevice：pip install sounddevice") from _SD_ERR
        self.samplerate = samplerate
        self._stream = None
        self._q: queue.Queue[np.ndarray] = queue.Queue()

    def _callback(self, indata, frames, time, status) -> None:  # type: ignore[no-untyped-def]
        if status:
            if getattr(status, "input_overflow", False):
                pass
        self._q.put(indata.copy())

    def start(self) -> None:
        while not self._q.empty():
            try:
                self._q.get_nowait()
            except queue.Empty:
                break
        self._stream = sd.InputStream(
            channels=1,
            dtype="float32",
            samplerate=self.samplerate,
            callback=self._callback,
        )
        self._stream.start()

    def stop(self) -> Path | None:
        if self._stream is None:
            return None
        try:
            self._stream.stop()
            self._stream.close()
        finally:
            self._stream = None

        blocks: list[np.ndarray] = []
        while True:
            try:
                blocks.append(self._q.get_nowait())
            except queue.Empty:
                break
        if not blocks:
            return None
        audio = np.concatenate(blocks, axis=0)
        if audio.size < self.samplerate // 4:
            return None
        audio = np.clip(audio.squeeze(), -1.0, 1.0)
        pcm = (audio * 32767.0).astype(np.int16)

        from scipy.io import wavfile

        fd, path = tempfile.mkstemp(suffix=".wav", prefix="tools_meeting_")
        os.close(fd)
        p = Path(path)
        wavfile.write(str(p), self.samplerate, pcm)
        return p


def transcribe_meeting_wav(wav_path: Path) -> str:
    """使用 Vosk 在本地将 16-bit 单声道 WAV 转为中文文本（无需联网）。"""
    from vosk import KaldiRecognizer

    wf = wave.open(str(wav_path), "rb")
    try:
        if wf.getnchannels() != 1:
            raise ValueError("需要单声道录音。")
        if wf.getsampwidth() != 2:
            raise ValueError("需要 16-bit PCM WAV。")
        rate = wf.getframerate()
        if rate != 16000:
            # 与 MicRecorder 一致；若将来支持重采样可在此扩展
            raise ValueError(f"当前仅支持 16 kHz 采样率录音，实际为 {rate} Hz。")

        model = _load_vosk_model()
        rec = KaldiRecognizer(model, rate)
        parts: list[str] = []
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            if rec.AcceptWaveform(data):
                j = json.loads(rec.Result())
                t = str(j.get("text", "")).strip()
                if t:
                    parts.append(t)
        j = json.loads(rec.FinalResult())
        t = str(j.get("text", "")).strip()
        if t:
            parts.append(t)
    finally:
        wf.close()

    text = "".join(parts).replace(" ", "").strip()
    if not text:
        raise ValueError("未能识别出有效语音，请靠近麦克风、提高音量或缩短片段后重试。")
    return text
