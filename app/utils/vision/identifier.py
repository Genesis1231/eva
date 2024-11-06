from config import logger
import os
import base64
import sqlite3
from pathlib import Path
from queue import Queue
from typing import Dict, List, Union

import face_recognition as fr
import numpy as np
import cv2

class Identifier:
    """
    Class to identify individuals from frames using face recognition.

    Attributes:
        _ids (dict): A dictionary containing the photo IDs and corresponding face encodings.

    Methods:
        __init__(): Initializes the Identifier object.
        initialize_ids(): Initializes the photo IDs and face encodings.
        identify(frames): Identifies individuals from the given frames.
    """
    def __init__(self):
        self._ids: List[Dict] = self._initialize_ids()
        logger.info(f"Identifier: Personal Identifier is Ready. {len(self._ids)} IDs loaded.")
        
    def _initialize_ids(self)-> List[Dict]:
        """ Load the photo IDs and corresponding face encodings. """
        pid_directory = Path(__file__).resolve().parents[2] / 'data' / 'pids'
        photo_ids = {}
        
        for filename in os.listdir(pid_directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
                filepath = os.path.join(pid_directory, filename)
                try:
                    id = str(len(photo_ids) + 1).zfill(3)
                    # Extract name from filename (assuming format: "id_name.extension")
                    name = os.path.splitext(filename)[0]
                    image = fr.load_image_file(filepath)
                    face_encoding = fr.face_encodings(image)
                    
                    if face_encoding:
                        photo_ids[id] = (name, face_encoding[0])
                    else:
                        logger.warning(f"Photo Identifier: No faces found in the image: {filename}")
                        
                except Exception as e:
                    raise Exception(f"Error processing {filename}: {str(e)}")

        return photo_ids
    
    def _base64_to_numpy(self, base64_str: str)-> np.ndarray:
        """ Convert a base64 string to a numpy array. """
        img_array = np.frombuffer(base64.b64decode(base64_str), dtype=np.uint8)
        return cv2.imdecode(img_array, cv2.IMREAD_COLOR)
    
    def identify(self, frames: Union[np.ndarray, str], name_queue: Queue) -> None:
        """ Identify individuals from the given frames. """
        if isinstance(frames, str):
            frames = self._base64_to_numpy(frames)
            
        frames = cv2.cvtColor(cv2.resize(frames, (0, 0), fx=0.5, fy=0.5), cv2.COLOR_BGR2RGB)

        face_locations = fr.face_locations(frames)
        face_encodings = fr.face_encodings(frames, face_locations)

        names = []
        # Compare the captured face encoding with known face encodings
        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            for name, face_id in self._ids.values():
                matches = fr.compare_faces([face_id], face_encoding)
                if True in matches:
                    names.append(f"{name},")
                    break

        name = "unknown" if not names else ", ".join(names)
        
        if name_queue:
            name_queue.put(name)