"""DeepSeek Chat API（OpenAI 兼容 /chat/completions），仅用标准库。"""

from __future__ import annotations

import json
import ssl
import urllib.error
import urllib.request
from typing import Any

DEFAULT_BASE_URL = "https://api.deepseek.com"
# V4（OpenAI 兼容）；旧版 deepseek-chat / deepseek-reasoner 已弃用，见平台公告。
DEFAULT_MODEL = "deepseek-v4-flash"
MEETING_MODEL_OPTIONS: tuple[str, ...] = ("deepseek-v4-pro", "deepseek-v4-flash")


def chat_completion(
    api_key: str,
    messages: list[dict[str, str]],
    *,
    model: str = DEFAULT_MODEL,
    base_url: str | None = None,
    timeout: int = 120,
) -> str:
    if not api_key.strip():
        raise ValueError("请填写 DeepSeek API Key。")
    root = (base_url or DEFAULT_BASE_URL).rstrip("/")
    url = f"{root}/v1/chat/completions"
    body = json.dumps(
        {
            "model": model,
            "messages": messages,
            "temperature": 0.3,
        },
        ensure_ascii=False,
    ).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=body,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key.strip()}",
        },
        method="POST",
    )
    ctx = ssl.create_default_context()
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        err = e.read().decode("utf-8", errors="replace")
        raise ValueError(f"DeepSeek API 错误 HTTP {e.code}: {err[:800]}") from e
    except urllib.error.URLError as e:
        raise ValueError(f"网络错误: {e.reason}") from e

    data: dict[str, Any] = json.loads(raw)
    choices = data.get("choices")
    if not choices or not isinstance(choices, list):
        raise ValueError(f"API 返回异常: {raw[:500]}")
    msg = choices[0].get("message") or {}
    content = msg.get("content")
    if not isinstance(content, str):
        raise ValueError(f"API 无正文: {raw[:500]}")
    return content.strip()


MEETING_SYSTEM_PROMPT = """你是一名专业的会议纪要助手。用户会粘贴会议录音转写或随手记的要点。
请整理成结构清晰的中文纪要，建议包含（有则写、无则略）：
1. 会议主题与基本信息（若文中能推断）
2. 讨论要点（分条）
3. 决议 / 待办（责任人或时间若文中有则保留）
4. 需跟进事项

要求：忠实于原文，不编造未出现的事实；条理清楚、便于转发。"""


def summarize_meeting_minutes(api_key: str, raw_text: str, *, model: str | None = None) -> str:
    text = raw_text.strip()
    if not text:
        raise ValueError("请先粘贴会议内容。")
    m = model or DEFAULT_MODEL
    messages = [
        {"role": "system", "content": MEETING_SYSTEM_PROMPT},
        {"role": "user", "content": text},
    ]
    return chat_completion(api_key, messages, model=m)
