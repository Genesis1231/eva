################################################################################################ 
# EVA CONFIGURATION v0.1
# This file contains the configuration for EVA's models and services.
# (this might be moved to a database in the future)
# 
# Current supporting models:
#
# LLM: 
#   - Default: Llama3-8b (local)
#   - Recommended: Anthropic
#   - Groq-llama3-70b, OpenAI-ChatGPT-4o, Mistral Large, Google Gemini
#   - Ollama all models (as long as they are pulled)
# 
# Image-to-Text: 
#   - Default: Llava-phi3 (local)
#   - Recommended: Chatgpt-4o-mini
#   - Llava 1.5 through Ollama (local)
#   - Could support more models in the future
#
# Speech-to-Text:
#   - Default: Faster-Whisper (local)
#   - Whisper, Sensevoice
#
# Text-to-Speech:
#   - Default: Coqui TTS (local)
#   - Recommended: Elevenlabs
#
# Summarization: 
#   - Default: Llama3-8b (local)
#
# Current supporting devices:
# - Default device: WSL - Linux
# - Mobile with API
#
################################################################################################

eva_configuration = {
    "DEVICE": "desktop",
    "LANGUAGE": "en",
    "BASE_URL": "http://localhost:11434",
    "CHAT_MODEL": "anthropic",
    "IMAGE_MODEL": "llava-phi3",
    "STT_MODEL": "faster-whisper",
    "TTS_MODEL": "coqui",
    "SUMMARIZE_MODEL": "llama"
}
