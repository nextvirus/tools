"""Detect optional install components (partial PyInstaller tree)."""

from __future__ import annotations


def photo_module_available() -> bool:
    try:
        import onnxruntime  # noqa: F401
        import rembg  # noqa: F401
    except ImportError:
        return False
    return True


def meeting_module_available() -> bool:
    try:
        import sounddevice  # noqa: F401
        import vosk  # noqa: F401
    except ImportError:
        return False
    return True
