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
#   Default: Llama3-8b (local)
#   Recommended: Anthropic-claude
#   Groq-llama3.1-70b, OpenAI-ChatGPT-4o, Mistral Large, Google Gemini 1.5 Pro
#   Ollama all models (as long as they are pulled, you can edit the options in utils/agent/chatagent.py)
# 
# IMAGE_MODEL:
#   Model for vision interpretation.
#   Options: "OpenAI", "Llava13b", "Llava-phi3"
#   Default: Llava-phi3 (local)
#   Recommended: Chatgpt-4o-mini
#   - Could support more models in the future
#
# STT_MODEL:
#   Model for speech-to-text transcription.
#   Options: "Whisper", "Groq", "Faster-whisper"
#   Default: Faster-whisper (Local)
#   OpenAI Whisper API, Groq Whisper API
#
# TTS_MODEL:
#   Model for text-to-speech generation.
#   - Options: "Coqui", "Elevenlabs", "Groq"
#   Default: Coqui TTS (local)
#   Recommended: Elevenlabs
#
# SUMMARIZE_MODEL:
#   Model for text summarization during conversation.
#   Options: "Groq", "llama", "OpenAI"
#   Default: Llama3-8b (local)
#
#
################################################################################################

eva_configuration = {
    "DEVICE": "desktop", 
    "LANGUAGE": "en",
    "BASE_URL": "http://localhost:11434",
    "CHAT_MODEL": "anthropic",
    "IMAGE_MODEL": "llava-phi3",
    "STT_MODEL": "faster-whisper",
    "TTS_MODEL": "elevenlabs",
    "SUMMARIZE_MODEL": "llama"
}
