"""仅供 PyInstaller 分析：拉 vosk / sounddevice 进 TOC。

`mic.py` 在模块顶层对 sounddevice 使用 try/except，且 vosk 仅在函数内 import，
分析器容易漏掉二进制依赖，导致勾选「会议纪要」安装后仍无法 import vosk。
"""

from __future__ import annotations

import sounddevice  # noqa: F401
import vosk  # noqa: F401
