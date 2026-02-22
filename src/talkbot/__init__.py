"""TalkBot - A talking AI assistant using OpenRouter and pyttsx3."""

from talkbot import tools
from talkbot.openrouter import OpenRouterClient
from talkbot.tts import TTSManager

__version__ = "0.1.0"
__all__ = ["OpenRouterClient", "TTSManager", "tools"]
