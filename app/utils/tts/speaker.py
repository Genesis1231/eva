import os
from config import logger
from typing import Dict, Callable

class Speaker:
    """
    The Speaker class is responsible for initializing and managing the text-to-speech models.
    It provides methods to create different speaker models and speak the given text.

    Attributes:
        model_selection (str): The selected speaker model name.
        model_factory (dict): A dictionary mapping model names to their corresponding creation methods.
        model: The initialized speaker model instance.
    Methods:
        _initialize_model: Initialize the selected speaker model.
        _get_model_factory: Get the model factory dictionary.
        speak: Speak the given text using the selected speaker model.
    """
    
    def __init__(self, speaker_model: str = "coqui", media_folder: str = "/media"):
        self._model_selection: str = speaker_model.upper()
        self._media_folder: str = media_folder
        self.model = self._initialize_model()
        
        logger.info(f"Speaker: {self._model_selection} is ready.")
    
    def _get_model_factory(self) -> Dict[str, Callable]:
        return {
            "COQUI" : self._create_coqui_model,
            "ELEVENLABS" : self._create_elevenlab_model,
            "OPENAI" : self._create_openai_model,
        }

    def _create_coqui_model(self):
        from utils.tts.model_coqui import CoquiSpeaker
        
        try:
            return CoquiSpeaker()
        except Exception as e:
            raise Exception(f"Error: Failed to initialize Coqui TTS model {str(e)} ")

    def _create_elevenlab_model(self):
        from utils.tts.model_elevenlabs import ElevenLabsSpeaker
        
        try:
            return ElevenLabsSpeaker()
        except Exception as e:
            raise Exception(f"Error: Failed to initialize ElevenLabs model {str(e)} ")

    def _create_openai_model(self):
        from utils.tts.model_openai import OpenAISpeaker
        
        try:
            return OpenAISpeaker()
        except Exception as e:
            raise Exception(f"Error: Failed to initialize OpenAI model {str(e)}")
    
    def _initialize_model(self):
        model_factory = self._get_model_factory()
        model = model_factory.get(self._model_selection)
        if model is None:
            raise ValueError(f"Error: Model {self._model_selection} is not supported.")
        
        return model()

    def stop_speaking(self) -> None:
        """ Stop the speaker model """
        self.model.stop_playback()
        
    def speak(self, answer: str, wait: bool) -> None:
        """ Speak the given text using the selected speaker model """
        try:
            self.model.eva_speak(answer, wait)
            
        except Exception as e:
            raise Exception(f"Error: Failed to speak {str(e)} ")
        
    def get_audio(self, text: str) -> str:
        """ Generate audio from text and save it to the media folder """
        return self.model.generate_audio(text, self._media_folder)
