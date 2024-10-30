import os
from config import logger
import time
import secrets
import threading

from torch import cuda
from queue import Queue, Empty
from typing import List, Dict, Callable

import nltk
import pyrubberband as pyrb
import numpy as np
from pydub import AudioSegment

from utils.tts.audio_player import AudioPlayer

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
        }
        
    def _create_coqui_model(self):
        from TTS.api import TTS
        try:
            class AudioSpeaker:
                def __init__(self, model_name: str = None)-> None:
                    self.model_name = model_name if model_name else "tts_models/en/vctk/vits" # can be configured in the future
                    self.device = "cuda" if cuda.is_available() else "cpu"
                    self.model = TTS(model_name=self.model_name).to(self.device)
                    self.player = AudioPlayer()
                    
                    self.audio_queue = Queue()
                    self.play_thread = None
                      
                def play(self) -> None:
                    while True:
                        try:
                            wav = self.audio_queue.get(timeout=0.1)  # 1 second timeout
                            if wav is None:
                                break

                            # newwav = np.array(wav) #speed up the audio
                            # wav = pyrb.time_stretch(newwav, 16000, 1.1)                            
                            self.player.play_audio(wav)
                            time.sleep(0.3)  # pause between sentences
                            self.audio_queue.task_done()
                        except Empty:
                            continue  # If queue is empty, continue the loop
            
                def eva_speak(self,  text: str, wait: bool = True) -> None:
                    """ Speak the given text using Coqui TTS """
                    sentences = nltk.sent_tokenize(text)
                    if not self.play_thread:
                        self.play_thread = threading.Thread(target=self.play, daemon=True)
                        self.play_thread.start()
                              
                    for sentence in sentences:
                        wav = self.model.tts(text=sentence, speaker="p306")
                        self.audio_queue.put(wav)
                    
                    if wait:
                        self.audio_queue.put(None)
                        self.stop_playback()
                
                def stop_playback(self) -> None:
                    if self.play_thread:
                        self.play_thread.join()
                        self.play_thread = None
                        
                def __del__(self):        
                    self.stop_playback()
                    
                def generate_audio(self, text: str, media_folder: str) -> str:
                    """ Generate mp3 from text using Coqui TTS """
                    audio_files = []
                    try:
                        sentences = nltk.sent_tokenize(text)
                        for sentence in sentences:
                            wav = self.model.tts(text=sentence, speaker="p306")
                            audio_data = (np.array(wav) * 32767).astype(np.int16)
                            filename = f"{secrets.token_hex(16)}.mp3"
                            
                            # Create AudioSegment from raw audio data
                            audio = AudioSegment(
                                audio_data.tobytes(),
                                frame_rate=22050,
                                sample_width=2,
                                channels=1
                            )
                            file_path = os.path.join(media_folder, "audio", filename)
                            audio.export(file_path, format="mp3")
                            audio_files.append(f"audio/{filename}")
                                            
                        return audio_files
                
                    except Exception as e:
                        logger.error(f"Error during text to speech synthesis: {e}")
                        return None
                
            model = AudioSpeaker()
        except Exception as e:
            raise Exception(f"Error: Failed to initialize Coqui TTS model {str(e)} ")
        
        return model

    def _create_elevenlab_model(self):
        from elevenlabs.client import ElevenLabs
        from elevenlabs import stream
        
        try:        
            class AudioSpeaker:
                def __init__(self, voice: str = None) -> None:
                    self.model = ElevenLabs()
                    self.voice = voice if voice else "Ana" # voice could be configured in the future
                    
                def eva_speak(self, text: str) -> None:
                    audio_stream = self.model.generate(
                        text=text,
                        voice=self.voice,
                        stream=True,
                    )
                    stream(audio_stream)
                                    
                def generate_audio(self, text: str, media_folder: str, filename: str) -> str:
                    """ Generate mp3 from text using ElevenLabs """
                    file_path = os.path.join(media_folder, "audio", filename)
                    
                    try:
                        audio_stream = self.model.generate(
                            output_format="mp3_22050_32",
                            model="eleven_multilingual_v2",                           
                            text=text,
                            voice="Ana",
                            optimize_streaming_latency = 1,
                            stream = True
                        )
                    
                        with open(file_path, 'wb') as f:
                            for chunk in audio_stream:
                                if chunk:
                                    f.write(chunk)                       
                    
                    except Exception as e:
                        logger.error(f"Error during text to speech synthesis: {e}")

                    
                    return f"audio/{filename}"
                
            model = AudioSpeaker()
            
        except Exception as e:
            raise Exception(f"Error: Failed to initialize ElevenLabs model {str(e)} ")
        
        return model
        
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
