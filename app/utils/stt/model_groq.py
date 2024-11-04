import tempfile
from config import logger
from typing import Optional, List
from numpy import ndarray

from groq import Groq
import scipy.io.wavfile as sf

class GroqTranscriber:   
    def __init__(self, language: str = "en"):
        self.language: str = language
        self.model: Groq = Groq()
        self.sample_rate: int = 16000
     
    def transcribe_audio(self, audioclip) -> Optional[str]:
        """ Transcribe the given audio clip using the OpenAI Whisper model """
        
        if not isinstance(audioclip, (List, ndarray)):
            raise ValueError("Invalid audio format provided for transcription.") 
        
        model_name = "distil-whisper-large-v3-en" if self.language == "en" else "whisper-large-v3-turbo "
        
        try:
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=True) as temp_file:
                sf.write(temp_file.name, self.sample_rate, audioclip)
            
                #transcribe the audio file  
                with open(temp_file.name, 'rb') as audio_file:
                    api_params = {
                        "model": model_name,
                        "file": audio_file,
                        "response_format": "text",
                        "prompt": "Specify punctuations.",
                    }
                    if self.language == "en":
                        response = self.model.audio.transcriptions.create(**api_params)
                    else:
                        response = self.model.audio.translations.create(**api_params)
        
        except Exception as e:
            logger.error(f"Error: Failed to transcribe audio: {str(e)}")
            return None

        
        return response