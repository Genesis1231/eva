from config import logger
import os
from threading import Thread
import secrets
from typing import Optional

from elevenlabs.client import ElevenLabs
from elevenlabs import stream, VoiceSettings
    
class ElevenLabsSpeaker:
    def __init__(self, voice: str = "Ana") -> None:
        self.model: ElevenLabs = ElevenLabs()
        self.audio_thread: Optional[Thread] = None
        self.voice: str = voice # voice could be configured in the future
        
    def eva_speak(self, text: str, language: Optional[str] = None, wait: bool = True) -> None:
        """ Speak the given text using ElevenLabs """
        
        model_name = "eleven_monolingual_v1" if language == "en" else "eleven_turbo_v2_5"
        
        try:
            audio_stream = self.model.generate(
                model=model_name,
                output_format="mp3_22050_32",
                text=text,
                voice=self.voice,
                stream=True,
                optimize_streaming_latency = 1,
                voice_settings=VoiceSettings(
                    stability=0.4,
                    similarity_boost=0.7,
                    use_speaker_boost=True
                )
            )
            
            if self.audio_thread and self.audio_thread.is_alive():
                self.audio_thread.join()
                
            if wait:
                stream(audio_stream)
            else:   
                self.audio_thread = Thread(target=lambda: stream(audio_stream), daemon=True)
                self.audio_thread.start()

        except Exception as e:
            logger.error(f"Error during text to speech synthesis: {e}")
            
    def generate_audio(self, text: str, language: Optional[str], media_folder: str) -> Optional[str]:
        """ Generate mp3 from text using ElevenLabs """
        
        model_name: str = "eleven_monolingual_v1" if self.language == "en" else "eleven_turbo_v2_5"
        
        filename = f"{secrets.token_hex(16)}.mp3"
        file_path = os.path.join(media_folder, "audio", filename)
        
        try:
            audio_stream = self.model.generate(
                model=model_name,
                output_format="mp3_22050_32",                      
                text=text,
                voice=self.voice
            )
        
            with open(file_path, 'wb') as f:
                f.write(audio_stream)
            
            return f"audio/{filename}"
        
        except Exception as e:
            logger.error(f"Error during text to speech synthesis: {e}")
            return None
