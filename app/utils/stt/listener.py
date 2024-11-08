from config import logger
from typing_extensions import Optional
from numpy import ndarray

from utils.stt.transcriber import Transcriber
from utils.stt.mic import Microphone

class PCListener:
    """
    The Listener class is for PC / Laptop use only.
    Utilizes the Microphone and Transcriber classes to listen to audio input and transcribe it.
    
    Attributes:
        microphone: The microphone instance.
        transcriber: The transcriber instance.
    """

    def __init__(self, model_name: str, language: str):
        self.microphone: Microphone = Microphone()
        self.transcriber: Transcriber = Transcriber(model_name, language)

    def listen(self) -> Optional[tuple[str, str]]:  
        """ listening to microphone and transcribing it. / for PC use only """
        
        while True:
            audio_data = self.microphone.listen()
            if audio_data is None:
                logger.warning("Listener: Speech audio data is not valid. Back to listening.")
                continue
        
            content, language = self.transcriber.transcribe(audio_data)
            if not content:
                logger.warning("Listener: No speech is detected in the audio. Back to listening.")
                continue
        
            return content, language