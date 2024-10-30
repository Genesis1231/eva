from config import logger
from typing_extensions import Optional, List


from utils.stt.transcriber import Transcriber
from utils.stt.mic import Microphone

class Listener:
    """
    The Listener class is responsible for listening to audio input and recognizing a specific wake phrase.
    Utilizes the Microphone and Transcriber classes to listen to audio input and transcribe it.
    this is for PC / Laptop use only.
    """

    def __init__(self, model_name: str = "whisper"):
        self.microphone = Microphone()
        self.transcriber = Transcriber(model_name)

    def listen(self) -> Optional[str]:  
        """ listening to microphone and transcribing it. / for PC use only """
        
        while True:
            audiodata = self.microphone.listen()
            if audiodata is None:
                return None
        
            content = self.transcriber.transcribe(audiodata)
            if not content:
                logger.warning("Listener: No content is transcribed back to listen.")
                continue
        
            return content