from config import logger
import os
import threading
import secrets
from typing import Optional

from openai import OpenAI
from pyaudio import PyAudio, paInt16

class OpenAISpeaker:
    """ 
    Audio speaker using OpenAI TTS
    
    Attributes:
        model (OpenAI): The OpenAI model.
        voice (str): The voice to use for the TTS model.
        player_stream (PyAudio): The audio stream.
    Methods:
        eva_speak: Speak the given text using OpenAI.
        generate_audio: Generate audio files from text using OpenAI TTS.
    """
    
    def __init__(self, voice: str = None) -> None:
        self.model = OpenAI()
        self.voice = voice if voice else "nova"  # default OpenAI voice
        self.player = PyAudio()
        self.player_stream = self.player.open(
            format=paInt16, 
            channels=1, 
            rate=24000, 
            output=True
        )
        
    def eva_speak(self, text: str, wait: bool = True) -> None:
        """ Speak the given text using OpenAI """  
                                
        def stream_audio():
            try:
                with self.model.audio.speech.with_streaming_response.create(
                    model="tts-1",
                    voice=self.voice,
                    response_format="pcm",
                    input=text
                ) as response:
                    for chunk in response.iter_bytes(chunk_size=1024):
                        self.player_stream.write(chunk)
            except Exception as e:
                logger.error(f"Error during text to speech synthesis: {e}")
                return None

        if wait:
            stream_audio()
        else:
            threading.Thread(target=stream_audio, daemon=True).start()
                
    def generate_audio(self, text: str, media_folder: str) -> Optional[str]:
        """ Generate mp3 from text using OpenAI TTS """
        
        filename = f"{secrets.token_hex(16)}.mp3"
        file_path = os.path.join(media_folder, "audio", filename)
        
        try:
            response = self.model.audio.speech.create(
                model="tts-1",
                voice=self.voice,
                response_format="mp3",
                input=text
            )
            
            with open(file_path, 'wb') as f:
                response.write_to_file(file_path)
            
            return f"audio/{filename}"
        
        except Exception as e:
            logger.error(f"Error during text to speech synthesis: {e}")
            return None

            
    def __del__(self) -> None:
        if hasattr(self, 'player_stream'):
            self.player_stream.stop_stream()
            self.player_stream.close()
            
        if hasattr(self, 'player'):
            self.player.terminate()