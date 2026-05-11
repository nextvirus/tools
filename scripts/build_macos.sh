#!/usr/bin/env bash
# 在 macOS 本机生成 tools.app（Docker 无法提供 macOS 基础镜像，必须本机打包）
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

if [[ "$(uname -s)" != "Darwin" ]]; then
  echo "请在 macOS 上执行本脚本。" >&2
  exit 1
fi

python3 -m venv .venv-build
# shellcheck disable=SC1091
source .venv-build/bin/activate
pip install -U pip
pip install -r requirements.txt

python3 scripts/package_tools.py

mkdir -p release
rm -rf release/tools.app
cp -R dist/tools.app release/
echo "已生成 release/tools.app，可直接双击或拖入「应用程序」。"
