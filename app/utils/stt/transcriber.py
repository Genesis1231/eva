from config import logger
import os
import threading
import secrets
from queue import Queue
from typing_extensions import Dict, Optional, Callable

from torch import cuda
from utils.stt.voiceid import VoiceIdentifier
class Transcriber:
    """
    The Transcriber class is responsible for transcribing audio clips using different models.
    Args:
        model_name (str): The name of the model to use for transcription. Default is "faster-whisper".
    Attributes:
        _model_selection (str): The selected model name.
        model_factory (dict): A dictionary mapping model names to their corresponding creation methods.
        model: The initialized transcription model instance.
    Methods:
        _initialize_model: Initialize the selected transcription model.
        transcribe: Combine the transcription and identification of the speaker.
        transcribe_audio: Transcribe the given audio clip using the selected model.
    """
    
    def __init__(self, model_name: str = "faster-whisper"):
        self._model_selection: str = model_name.upper()
        self.model = self._initialize_model()
        self.identifier = VoiceIdentifier()
        self.name_queue = Queue()
        
        logger.info(f"Transcriber: {self._model_selection} is ready.")
    
    def _get_model_factory(self) -> Dict[str, Callable]:
        return {
            "SENSEVOICE" : self._create_sensevoice_model,
            "FASTER-WHISPER" : self._create_fasterwhisper_model,
            "WHISPER" : self._create_whisper_model,
        }
        
    def _create_sensevoice_model(self):
        from .model import SenseVoiceSmall
        
        model_dir = "iic/SenseVoiceSmall"
        model, kwargs = SenseVoiceSmall.from_pretrained(model=model_dir)
        self.kwargs = kwargs
        
        return model
        
    def _create_fasterwhisper_model(self):
        from faster_whisper import WhisperModel
        
        model_size = "distil-medium.en"   
        device = "cuda" if cuda.is_available() else "cpu"
        
        # Run on GPU with Float16 (Float32)
        try:
            model = WhisperModel(model_size, device=device, compute_type="float16")
        except Exception as e:
            raise Exception(f"Error: Fail to load Faster Whisper Model {str(e)}")
            
        return model
     
    def _create_whisper_model(self):
        import whisper
        try: 
            model = whisper.load_model("base").to("cuda")
        except Exception as e:
            raise Exception(f"Error: failed to load Whisper Model {str(e)}")
        
        return model
    
    def _initialize_model(self):
        model_factory = self._get_model_factory()
        model = model_factory.get(self._model_selection)
        if model is None:
            raise ValueError(f"Error: Model {self._model_selection} is not supported")
        
        return model()
    
    def transcribe_audio(self, audioclip) -> Optional[str]:
        """ transcribe audio to text using the selected model """
        
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

    def transcribe(self, audioclip) -> Optional[str]:  
        """ Transcribe the given audio clip and identify the speaker """
        thread = threading.Thread(target=self.identifier.identify, args=(audioclip, self.name_queue))
        thread.start()
        
        transcription = self.transcribe_audio(audioclip)
        if not transcription:
            thread.join()
            return None
        
        # Get the speaker identification result
        name = self.name_queue.get()   
        thread.join()
        
        # if the name is unknown, return content with a new line, there is a new person speaking, save it into a database
        if name == "unknown":
            content = f"{transcription.strip()} (I couldn't tell whose voice it is.)"
        else:
            content = f"{name}:: {transcription.strip()}"
        # if name == "unknown person":
        #     speaker_id = secrets.token_hex(4)
        #     filepath = os.path.join(os.getcwd(), "data", "voids", f"{speaker_id}.wav")
        #     self.identifier.save_audio_file(audioclip, filepath)
        #     content += f" (<speaker_id>{speaker_id}</speaker_id>)"

        return content