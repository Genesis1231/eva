import os
import threading
from typing_extensions import Union, Optional

import sounddevice as sd
import soundfile as sf
import numpy as np
import mpv

class AudioPlayer:
    """
    A class to play audio data.
    
    Attributes:
    device (str): The device used to play audio.
    sample_rate (int): The sample rate of the audio data.
    speaking (bool): A flag to indicate if audio is currently speaking.
    audio_thread (threading.Thread): A thread to play audio.
    
    Methods:
    play_audio: Play audio data from a file or numpy array.
    play_mp3_stream: Play an mp3 stream.
    stream: Stream an mp3 url.
    
    """
    def __init__(self):
        self._device = "WSL/PC"
        self._sample_rate = 22050
        self._audio_thread = None
        self.mpv_player = None
            
    def play_audio(self, audio_data: Optional[Union[str, np.ndarray]], from_file: bool = False)-> None:
        if audio_data is None:
            return
        
        try:
            if from_file:
                if not os.path.exists(audio_data):
                    raise FileNotFoundError(f"File not found: {audio_data}")
                
                audio_data, sample_rate = sf.read(audio_data) 
                
                # Ensure audio data is in float32 format for compatibility with sounddevice
                if audio_data.dtype != np.float32:
                    # Normalize the data by the maximum value of its type
                    max_val = np.iinfo(audio_data.dtype).max if np.issubdtype(audio_data.dtype, np.integer) else 1.0
                    audio_data = (audio_data / max_val).astype(np.float32)
            else:
                sample_rate = self._sample_rate
            
            # Play the audio
            sd.play(audio_data, sample_rate)
            sd.wait()
            
        except Exception as e:
            raise Exception(f"Error: Failed to play audio: {e}")
        
    def _play_mp3_stream(self, mp3_url: str)-> None:
        try:
            self.mpv_player = mpv.MPV(ytdl=True)
            self.mpv_player.volume = 50
            self.mpv_player.play(mp3_url)
            self.mpv_player.wait_for_playback()
            
        except Exception as e:
            raise Exception(f"Error: Failed to play mp3 stream: {e}")

            
    def stream(self, url: str)-> None:
        if not url:
            return
        
        if self._audio_thread and self._audio_thread.is_alive():
            self._audio_thread.join()
            
        self._audio_thread = threading.Thread(target=self._play_mp3_stream, daemon=True, args=(url,))
        self._audio_thread.start()
    
    
 
