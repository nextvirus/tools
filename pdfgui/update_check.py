"""查询 GitHub Releases 是否有新版本（仅检测 + 打开浏览器，不自动下载安装）。"""

from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path

from pdfgui.version import APP_VERSION, GITHUB_REPO


_STATE_NAME = "update_state.json"


def effective_github_repo() -> str:
    return (os.environ.get("TOOLS_GITHUB_REPO") or "").strip() or (GITHUB_REPO or "").strip()


def _state_path() -> Path:
    if os.name == "nt":
        base = os.environ.get("APPDATA") or str(Path.home())
        return Path(base) / "tools" / _STATE_NAME
    return Path.home() / ".config" / "tools" / _STATE_NAME


def load_update_state() -> dict[str, object]:
    p = _state_path()
    if not p.is_file():
        return {}
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def save_update_state(data: dict[str, object]) -> None:
    p = _state_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def _version_tuple(s: str) -> tuple[int, ...]:
    s = s.strip().lstrip("v").lstrip("V")
    parts: list[int] = []
    for seg in s.split("."):
        m = re.match(r"^(\d+)", seg)
        parts.append(int(m.group(1)) if m else 0)
    return tuple(parts) if parts else (0,)


def is_remote_newer(latest_tag: str, current: str) -> bool:
    return _version_tuple(latest_tag) > _version_tuple(current)


@dataclass(frozen=True)
class UpdateCheckResult:
    ok: bool
    current: str
    latest_tag: str | None
    latest_url: str | None
    message: str


def check_github_release() -> UpdateCheckResult:
    repo = effective_github_repo()
    cur = APP_VERSION.strip().lstrip("v")
    if not repo:
        return UpdateCheckResult(
            False,
            cur,
            None,
            None,
            "未配置 GitHub 仓库（已清空默认或环境变量 TOOLS_GITHUB_REPO）。\n"
            "请恢复官方仓库或设置 TOOLS_GITHUB_REPO 为「用户名/仓库名」。",
        )
    url = f"https://api.github.com/repos/{repo}/releases/latest"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "tools-desktop-release-check (Python urllib)",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=18) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return UpdateCheckResult(
                False,
                cur,
                None,
                None,
                f"未找到仓库的 Latest Release（404）。请确认仓库名正确且已发布 Release：\n{repo}",
            )
        return UpdateCheckResult(False, cur, None, None, f"GitHub 返回 HTTP {e.code}：{e.reason or str(e)}")
    except urllib.error.URLError as e:
        return UpdateCheckResult(False, cur, None, None, f"网络错误：{e.reason or e}")
    except Exception as e:
        return UpdateCheckResult(False, cur, None, None, f"检查失败：{e}")

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return UpdateCheckResult(False, cur, None, None, "GitHub 响应不是合法 JSON。")

    tag = str(payload.get("tag_name") or "").strip()
    html_url = str(payload.get("html_url") or "").strip()
    if not tag:
        return UpdateCheckResult(False, cur, None, None, "Release 中缺少 tag_name。")
    return UpdateCheckResult(True, cur, tag, html_url or None, "")


def should_run_periodic_auto_check() -> bool:
    if not effective_github_repo():
        return False
    st = load_update_state()
    last = float(st.get("last_auto_check_ts", 0) or 0)
    return (time.time() - last) >= 86400.0


def open_release_page(url: str | None) -> None:
    if url:
        webbrowser.open(url)
