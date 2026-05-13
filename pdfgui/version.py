"""应用版本与 GitHub 仓库（用于「检查更新」）。

发版时请与 Git tag（如 v0.3.1）对齐修改 APP_VERSION。
默认查询官方仓库 nextvirus/tools；环境变量 TOOLS_GITHUB_REPO 可覆盖为 fork 等。
"""

from __future__ import annotations

# 与发布 tag 对应，例如 tag v0.3.1 则写 "0.3.1"
APP_VERSION = "0.0.0"

# 官方 GitHub 仓库（固定，勿改）；fork 可通过 TOOLS_GITHUB_REPO 覆盖
GITHUB_REPO = "nextvirus/tools"
