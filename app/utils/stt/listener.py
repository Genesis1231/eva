from config import logger
from typing_extensions import Optional


from utils.stt.transcriber import Transcriber
from utils.stt.mic import Microphone

class Listener:
    """
    The Listener class is for PC / Laptop use only.
    Utilizes the Microphone and Transcriber classes to listen to audio input and transcribe it.
    
    Attributes:
        microphone: The microphone instance.
        transcriber: The transcriber instance.
    """

    def __init__(self, model_name: str = "faster-whisper"):
        self.microphone: Microphone = Microphone()
        self.transcriber: Transcriber = Transcriber(model_name)

    def listen(self) -> Optional[str]:  
        """ listening to microphone and transcribing it. / for PC use only """
        
        while True:
            audiodata = self.microphone.listen()
            if audiodata is None:
                return None
        
            content = self.transcriber.transcribe(audiodata)
            if not content:
                logger.warning("Listener: No content is detected. Back to listening.")
                continue
        
            return content