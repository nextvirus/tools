"""会议纪要功能：本地保存 API 配置（不落仓库）。"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

_CONFIG_NAME = "meeting_settings.json"


def _config_path() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "tools" / _CONFIG_NAME
    return Path.home() / ".config" / "tools" / _CONFIG_NAME


def load_settings() -> dict[str, Any]:
    p = _config_path()
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_settings(data: dict[str, Any]) -> None:
    p = _config_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
