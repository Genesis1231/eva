# E.V.A. 🎙️

<div align="center">

![EVA Logo](logo.png)

*Experimental Voice Assistant*

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![GitHub Issues](https://img.shields.io/github/issues/Genesis1231/EVA)](https://github.com/Genesis1231/EVA/issues)
[![GitHub Stars](https://img.shields.io/github/stars/Genesis1231/EVA)](https://github.com/Genesis1231/EVA/stargazers)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

</div>

## 🎯 Overview of EVA

Hello Github wizards! Thanks for stopping by~ 🤗

So, here's the story - I used to sling code back in the days (like, when Perl was still cool), but then a year ago AI came along and stroke me with awe. I became very interested in human-AI interaction and how it can be applied in our daily life. However, most of the online projects only focused on a few specific tasks. So I spent a few months to develop EVA myself. 

EVA is an experimental voice assistant that explores human-AI experience through proactive engagement and autonomous behavior. Built with a modular architecture, it aims to provide a more natural and dynamic interaction experience to users, include an extensive tool framework that allows for continuous enhancement of its capabilities.

<div align="center">
  <img src="path/to/demo.gif" alt="EVA Demo" width="600px"/>
</div>


## ✨ Key Features

EVA is built on LangGraph framework, with some customized modules and tools. You can run it purely local with no cost.

### 🎙️ Cross platform modular design
- Configurable model selection for LLM, TTS, STT, etc.
- Integrated with OpenAI, Anthropic, Groq, Google, and Ollama.
- Easy modification of prompts and tools.
- Supports both desktop and mobile app

### 🖼️ Interactive experience
- Voice ID and vision ID for personalized interaction.
- Proactive style communication (varies between models)
- Multi-modal outputs with asynchronous action.

### 🔌 Dynamic Tool system
- Web search through DuckDuckGo/Tavily
- Youtube video search
- Discord Midjourney AI image generation
- Suno music generation
- Screenshot and analysis 
- Compatible with all Langchain tools
- Easy implementation of new tool with single file.


## 📁 Project Structure

```
EVA/
├── app/
│   ├── client/          # Client-side implementation
│   ├── config/          # Configuration files and log
│   ├── core/            # Core process
│   ├── data/            # Data storage
│   ├── tools/           # Tool implementations
│   └── utils/           # Utility functions
│       ├── agent/       # LLM agent classes and functions
│       ├── memory/      # Mmeory module classes 
│       ├── prompt/      # Utility prompts
│       ├── stt/         # Speech recognition models and classes
│       ├── tts/         # Text-to-Speech models and classes
│       └── vision/      # Vision models and functions
├── tests/               # Test cases (😢)
└── docs/                # Documentation (😩)

```

## 💻 System Requirements

- Python 3.10+
- CUDA-compatible GPU (If you want to run locally)
- 10GB free disk space
- Linux/macOS

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/EVA.git
cd EVA

# Create virtual environment
python -m venv eva_env
source eva_env/bin/activate  

# Install dependencies
pip install -r requirements.txt

# Configure .env with your API keys
cp .env.example .env

# Run EVA
cd app
python main.py

```
## 🛠️ Configuration
configure EVA setting in app/config/config.py
```python
eva_configuration = {
    "DEVICE": "desktop",
    "LANGUAGE": "en",
    "BASE_URL": "http://localhost:11434",
    "CHAT_MODEL": "chatgpt",
    "IMAGE_MODEL": "llava-phi3",
    "STT_MODEL": "faster-whisper",
    "TTS_MODEL": "coqui",
    "SUMMARIZE_MODEL": "llama"
}
```

## 🔧 Tool Setup

- Music generation tool Requires a Suno-API docker running on the base_url. 
  Install from https://github.com/gcui-art/suno-api

- Image generation tool requires a midjourney account and a private discord server.
  Need include the discord channel information in .env file.

If you want to disable some tools, just change the client setting in related .py file.

```python
    client: str = "none"
```
But I like to leave them all on since it is very interesting to observe how AI select tools.


## 🤝 Contribution

Due to my limited time, the code is far from perfect. I would be very grateful if anyone is willing to contribute🍝

### How You Can Help

1. **Code Contributions**
   - Found a bug? Report it and fix it.
   - Got a cool feature idea? Build it.
   - Fork, branch, commit, PR - you know the drill.

2. **Documentation**
   - Help me turn my late-night code comments into actual docs.
   - Spot a typo? Fix it.
   - Think something needs more explanation? Add it.

3. **Ideas & Feedback**
   - All ideas welcome, from "what if..." to "why didn't you..."
   - Share your use cases.
   - Tell me what breaks (hopefully not everything)
   

## 🗺️ Future Roadmap

- [ ] More tools for EVA to use
- [ ] Long term memory
- [ ] Self-motivation through reflections
- [ ] Complete Mobile SDK (WIP)


## 📜 License

This project is licensed under the MIT License.


## 📊 Credits & Acknowledgments

This project wouldn't be possible without these amazing open-source projects:

### Core & Language Models
- [LangChain](https://github.com/langchain-ai/) - Amazing AI Dev Framework 
- [Groq](https://github.com/groq/) - Free LLM access and really fast
- [Ollama](https://github.com/ollama/) - Best local model deployment
- [Numpy](https://github.com/numpy/) - The Numpy
- [FastAPI](https://github.com/fastapi/) - Excellent API framework
- [Tqdm](https://github.com/tqdm/) - Great progress bar

### Utility modules
- [OpenCV](https://github.com/opencv/) - Legendary Vision Library
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Fastest Speech transcription
- [Coqui TTS](https://github.com/coqui-ai/TTS) - Admirable text-to-speech synthesis
- [Face Recognition](https://github.com/ageitgey/face_recognition) - Face detection
- [Speech Recognition](https://github.com/Uberi/speech_recognition) - Easy-to-use Speech detection
- [PyAudio](https://github.com/jleb/pyaudio) - Powerful Audio I/O 
- [Wespeaker](https://github.com/wenet-e2e/wespeaker) - Speaker verification
- [NLTK](https://github.com/nltk/) - Natural Language Toolkit

### Tools development
- [Chromium](https://github.com/chromium/) - Best open-source web browser
- [DuckDuckGo](https://github.com/duckduckgo/) - Free Web search
- [Youtube_search](https://github.com/joetats/youtube_search) - YouTube search
- [Suno-API](https://github.com/suno-ai/suno-api) - Music generation API for Suno
- [PyautoGUI](https://github.com/asweigart/pyautogui) - cross-platform GUI automation


<div align="center">
  <sub>Built with ❤️ by the Adam</sub>
</div>
