import os
from config import logger
from typing import Dict, Callable

from torch import cuda
import scipy.io.wavfile as sf

def create_groq_model():
    from groq import Groq
    
    try: 
        class TransModel:   
            def __init__(self):
                self.model = Groq()
                self.model_name = "whisper-large-v3-turbo"
                self.language = "en"
            
            def transcribe_audio(self, audioclip):
                """ Transcribe the given audio clip using the OpenAI Whisper model """
                
                audio_path = os.path.join(os.path.dirname(__file__), "temp", "recog.wav")
                
                try:
                    #write the audioclip to a temporary file
                    sf.write(audio_path, 16000, audioclip)
                    
                    #transcribe the audio file  
                    with open(audio_path, 'rb') as audio_file:
                        response = self.model.audio.transcriptions.create(
                            model=self.model_name,
                            file=audio_file,
                            response_format="text",
                            prompt="Specify punctuations.",
                            language=self.language
                        )
                
                except Exception as e:
                    logger.error(f"Error: Failed to transcribe audio: {str(e)}")
                    return None
                finally:
                    #delete the temporary file
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                
                return response
            
        model = TransModel()
        
    except Exception as e:
        raise Exception(f"Error: failed to load Whisper Model {str(e)}")
    
    return model

def create_fasterwhisper_model():
    from faster_whisper import WhisperModel
    
    try:
        class TransModel:   
            def __init__(self):
                self.model_size = "distil-medium.en"   # choose a medium size english to improve speed
                self.device = "cuda" if cuda.is_available() else "cpu"
                self.model = WhisperModel(self.model_size, device=self.device, compute_type="float16")
                
            def transcribe_audio(self, audioclip):
                """ Transcribe the given audio clip using the Faster Whisper model """
    
                try:
                    segments, _ = self.model.transcribe(
                        audioclip,
                        beam_size=5,
                        vad_filter=True,
                        vad_parameters=dict(min_silence_duration_ms=100)
                    )

                except Exception as e:
                    logger.error(f"Error: Failed to transcribe audio: {str(e)}")
                    return None
                
                text = ""
                for segment in segments:
                    text += segment.text
                
                return text

        model = TransModel()
    except Exception as e:
        raise Exception(f"Error: Fail to load Faster Whisper Model {str(e)}")
        
    return model
    
def create_whisper_model():
    from openai import OpenAI
    
    try: 
        class TransModel:   
            def __init__(self):
                self.model = OpenAI()
                self.language = "en"
            
            def transcribe_audio(self, audioclip):
                """ Transcribe the given audio clip using the OpenAI Whisper model """
                
                audio_path = os.path.join(os.path.dirname(__file__), "temp", "recog.wav")
                
                try:
                    #write the audioclip to a temporary file
                    sf.write(audio_path, 16000, audioclip)
                    
                    #transcribe the audio file  
                    with open(audio_path, 'rb') as audio_file:
                        response = self.model.audio.transcriptions.create(
                            model="whisper-1",
                            file=audio_file,
                            response_format="text",
                            language=self.language
                        )
                
                except Exception as e:
                    logger.error(f"Error: Failed to transcribe audio: {str(e)}")
                    return None
                finally:
                    if os.path.exists(audio_path):
                        os.remove(audio_path)
                
                return response
            
        model = TransModel()
        
    except Exception as e:
        raise Exception(f"Error: failed to load Whisper Model {str(e)}")
    
    return model
