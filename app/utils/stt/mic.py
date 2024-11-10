from config import logger
from datetime import datetime
from typing_extensions import Optional

import numpy as np
import speech_recognition as sr

class Microphone:
    """
    The Microphone class is responsible for listening to audio input and recognizing a specific wake phrase.
    
    Attributes:
        recognizer.energy_threshold (int): The energy threshold for silence detection.
        recognizer.dynamic_energy_threshold (bool): Whether to dynamically adjust the energy threshold.
        
        max_listen_time (int): The maximum time to wait for silence in seconds.
        speech_limit (int): The maximum time for a single session of speech in seconds. on average people speak
                                90-120 words per minute. this is to conserve the input token.                
    Methods:
        detect: Start listening for the wake phrase and return the recognized text.
        listen: Listen for audio input and return the numpy array of audio data
    
    """

    def __init__(self)-> None:
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        self.recognizer.pause_threshold = 1.3 # for longer sentence
        self.recognizer.dynamic_energy_threshold = True    
        self.max_listen_time = 300 # Listen for 5 minutes maximum
        self.speech_limit = 60  # Speak for 1 minute maximum

    def detect(self)->bool:
        """ Detect if there is any speech """
        
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
            self.recognizer.energy_threshold = 2000
            logger.info(f"Detecting for the speech...")
            while True:
                audio = self.recognizer.listen(source, phrase_time_limit=1)
                try:
                    if audio and len(audio.frame_data) > 10:
                        return True

                except Exception as e:
                    raise Exception(f"Error: Failed to recognize audio: {str(e)}")
        
    def listen(self) -> Optional[np.ndarray]:
        """
        Listens for audio input from the microphone and returns the audio data as a numpy array.

        Returns:
            Optional[np.ndarray]: The audio data as a numpy array if speech is detected, otherwise None.
        """
    
        with self.microphone as source:
            print(f"\n({datetime.now().strftime('%H:%M:%S')}) EVA is listening audio now...", end="\r")
            self.recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            self.recognizer.energy_threshold = 1000
            audio_buffer = self.recognizer.listen(source, timeout=self.max_listen_time, phrase_time_limit=self.speech_limit)
            print("                                                                          ") # clear the line
            
            try:
                raw_data = np.frombuffer(audio_buffer.get_raw_data(convert_rate=16000), dtype=np.int16)
                audiodata = raw_data.astype(np.float32) / 32768.0
                return audiodata
                
            except sr.WaitTimeoutError:
                logger.warning("Listener: No speech detected in the waiting period.")
                return None
            
            except Exception as e:
                logger.error(f"Listener: Failed to listen to audio: {str(e)}")
                return None