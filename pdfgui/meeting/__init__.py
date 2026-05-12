"""会议纪要：DeepSeek、本地配置、麦克风转写。"""

from pdfgui.meeting.deepseek import summarize_meeting_minutes
from pdfgui.meeting.settings import load_settings, save_settings

__all__ = ["summarize_meeting_minutes", "load_settings", "save_settings"]
