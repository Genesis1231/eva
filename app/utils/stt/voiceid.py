import os
from pathlib import Path
from config import logger
import sqlite3
from queue import Queue
from typing import List, Dict

import wespeaker as wp
import scipy.io.wavfile as sf
from numpy import ndarray

class VoiceIdentifier:
    """ 
    The VoiceIdentifier class is responsible for identifying the speaker using voice recognition.
    It uses the wespeaker library to identify the speaker from the audio clip.
    """
    def __init__(self):
        self._dblink: str = self._get_database_path()
        self._void_list: Dict = self._initialize_database()
        self.voice_recognizer = self._initialize_recognizer()
    
    def _initialize_recognizer(self):
        try:
            vmodel = wp.load_model('english') # or chinese
            vmodel.set_gpu(0)
            num = 0
            
            vid_directory =Path(__file__).resolve().parents[2] / 'data' / 'voids'
            for filename in os.listdir(vid_directory):
                if filename.lower().endswith('.wav'):
                    name = os.path.splitext(filename)[0]
                    if name in self._void_list:
                        filepath = os.path.join(vid_directory, filename)
                        vmodel.register(name, filepath)
                        num += 1
            
        except Exception as e:
            raise Exception(f"Error: Failed to set up voice recognizer: {str(e)}")
        
        logger.info(f"Voice Identifier: {num} Voice ID loaded.")
        
        return vmodel    
   
    def _initialize_database(self)-> Dict:
        """ Initialize the database and create the voice id table """
        
        with sqlite3.connect(self._dblink) as conn:
            conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
            cursor = conn.cursor()

            try:
                cursor.execute(f'SELECT void, user_name FROM ids;')
                rows = cursor.fetchall()
                return {row[0]: row[1] for row in rows}

            except sqlite3.Error as e:
                # If table doesn't exist, create it and return an empty list
                self._create_table(conn)
                return {}
            
    def _create_table(self, conn)-> None:    
        """ Create a new voiceid table """
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                void TEXT,
                pid TEXT,
                user_name TEXT NOT NULL
            )
        ''')
        conn.commit()
        
        # cursor = conn.cursor()
        # cursor.execute(f'''
        #     INSERT INTO ids (void, user_name) VALUES (?, ?);
        # ''', ('V000001', 'Initial User'))
        # conn.commit()
        
    def get_name(self, void: str) -> str:
        """ Get the name from the List """
        try:
            return self._void_list[void]
        except KeyError:
            logger.error(f"Error: Database error, failed to get name from void list: {void}")
            return "unknown person"
    
    def save_audio_file(self, audioclip: ndarray, filepath: str) -> None:
        try:
            sf.write(filepath, 16000, audioclip)
        except Exception as e:
            logger.error(f"Error: Failed to save audio: {str(e)}")
    
    def _get_database_path(self) -> str:
        """Return the path to the memory log database."""
        return Path(__file__).resolve().parents[2] / 'data' / 'database' / 'eva.db'
    
    def identify(self, audioclip: ndarray, name_queue: Queue) -> None:
        """
        Voice identification using wespeaker cli. 
        this could be improved by importing a whole voice dict from the directory
        and comparing the cosine similarity of the voice embeddings one by one
        """
        
        filepath = os.path.join(os.path.dirname(__file__), "temp", "recog.wav")
        self.save_audio_file(audioclip, filepath)
        
        try:
            recog = self.voice_recognizer.recognize(filepath)
              
        except Exception as e:
            logger.error(f"Error: Failed to recognize process: {str(e)}")
            name_queue.put("unknown")
            return
        
        name = f"{self.get_name(recog['name'])} (ID:{recog['name']})"  if recog["confidence"] > 0.6 else "unknown"
        
        if name_queue:
            name_queue.put(name)
