"""Vosk 中文离线识别模型（与 fetch 脚本、打包路径共用）。"""

# 小型中文模型，约 40MB zip / ~130MB 解压；见 https://alphacephei.com/vosk/models
VOSK_CN_MODEL_NAME = "vosk-model-small-cn-0.22"
VOSK_MODEL_DOWNLOAD_URL = f"https://alphacephei.com/vosk/models/{VOSK_CN_MODEL_NAME}.zip"
