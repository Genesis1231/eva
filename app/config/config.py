################################################################################################ 
# EVA CONFIGURATION v0.1
# This file contains the configuration for EVA's models and services.
# (this might be moved to a database in the future)
# 
# Current supporting models:
#
# LLM: 
#   - Options: "Anthropic", "Groq", "OpenAI", "Mistral", "Google", "llama"
#   - Default: Llama3-8b (local)
#   - Recommended: Anthropic-claude
#   - Groq-llama3.1-70b, OpenAI-ChatGPT-4o, Mistral Large, Google Gemini 1.5 Pro
#   - Ollama all models (as long as they are pulled)
# 
# Image-to-Text:
#   - Options: "OpenAI", "Llava13b", "Llava-phi3"
#   - Default: Llava-phi3 (local)
#   - Recommended: Chatgpt-4o-mini
#   - Could support more models in the future
#
# Speech-to-Text:
#   - Options: "Whisper", "Groq", "Faster-whisper"
#   - Default: Faster-whisper (Local)
#   - OpenAI Whisper API, Groq Whisper API
#
# Text-to-Speech:
#   - Options: "Coqui", "Elevenlabs", "Groq"
#   - Default: Coqui TTS (local)
#   - Recommended: Elevenlabs
#
# Summarization: 
#   - Options: "Groq", "llama", "OpenAI"
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
