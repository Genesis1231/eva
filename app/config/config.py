################################################################################################ 
# EVA CONFIGURATION v0.1
# This file contains the configuration for EVA's models and services.
# (this might be moved to a database in the future)
# 
# DEVICE:
#   The client device that EVA is running with.
#   Options: "desktop", "mobile"
#   Default: desktop
#   Mobile will work with a local API server. (Testing)
#
# CHAT_MODEL:
#   Main model for reasoning and conversation.
#   Options: "Anthropic", "Groq", "OpenAI", "Mistral", "Google", "llama"
#   Recommended: Anthropic-claude
#   Factory: Groq-llama3.1-70b, OpenAI-ChatGPT-4o, Mistral Large, Google Gemini 1.5 Pro, Anthropic-claude-sonnet-3.5
#   Ollama all models (as long as they are pulled, you can edit the options in utils/agent/chatagent.py)
# 
# VISION_MODEL:
#   Model for vision interpretation.
#   Options: "OpenAI", "llama3.2", "Llava-phi3", "Groq"
#   Recommended: Chatgpt-4o-mini
#   Factory: OpenAI-ChatGPT-4o-mini, Groq-llama3.2-vision-11b, Ollama-llava-phi3(local)
#
# STT_MODEL:
#   Model for speech-to-text transcription.
#   Options: "Whisper", "Groq", "Faster-whisper"
#   Recommended: faster-whisper
#   Factory: Groq-whisper, faster-whisper(local), OpenAI-whisper
#
# TTS_MODEL:
#   Model for text-to-speech generation.
#   Options: "Coqui"(local), "Elevenlabs", "Openai"
#   Recommended: Elevenlabs
#   Factory: Elevenlabs, Coqui TTS(local), OpenAI-TTS
#
# SUMMARIZE_MODEL:
#   Model for text summarization during conversation.
#   Options: "Groq", "llama", "OpenAI", Anthropic-claude-3-haiku
#   Factory: Groq-llama3.1-8b, OpenAI-ChatGPT-4o-mini, Anthropic-claude-3-haiku, ollama-llama3.1-8b
#
#
################################################################################################

eva_configuration = {
    "DEVICE": "desktop", 
    "LANGUAGE": "en",
    "BASE_URL": "http://localhost:11434",
    "CHAT_MODEL": "anthropic",
    "VISION_MODEL": "groq",
    "STT_MODEL": "faster-whisper",
    "TTS_MODEL": "elevenlabs",
    "SUMMARIZE_MODEL": "llama"
}
