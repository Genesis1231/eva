from config import logger
import os
import threading
import secrets
from typing import Optional

from elevenlabs.client import ElevenLabs
from elevenlabs import stream
    
class ElevenLabsSpeaker:
    def __init__(self, voice: str = None) -> None:
        self.model = ElevenLabs()
        self.voice = voice if voice else "Ana" # voice could be configured in the future
        
    def eva_speak(self, text: str, wait: bool = True) -> None:
        """ Speak the given text using ElevenLabs """
        
        try:
            audio_stream = self.model.generate(
                text=text,
                voice=self.voice,
                stream=True,
            )
            
            if wait:
                stream(audio_stream)
            else:
                threading.Thread(
                    target=lambda: stream(audio_stream),
                    daemon=True
                ).start()

        except Exception as e:
            logger.error(f"Error during text to speech synthesis: {e}")
            
    def generate_audio(self, text: str, media_folder: str) -> Optional[str]:
        """ Generate mp3 from text using ElevenLabs """
        
        filename = f"{secrets.token_hex(16)}.mp3"
        file_path = os.path.join(media_folder, "audio", filename)
        
        try:
            audio_stream = self.model.generate(
                output_format="mp3_22050_32",
                model="eleven_multilingual_v2",                           
                text=text,
                voice=self.voice,
                optimize_streaming_latency = 1,
                stream = True
            )
        
            with open(file_path, 'wb') as f:
                for chunk in audio_stream:
                    if chunk:
                        f.write(chunk)     
            
            return f"audio/{filename}"
        
        except Exception as e:
            logger.error(f"Error during text to speech synthesis: {e}")
            return None
