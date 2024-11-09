from config import logger
import numpy as np
import base64
import threading
from functools import partial
from queue import Queue
from typing import Dict, Callable, Union, Optional

import cv2
from utils.vision.identifier import Identifier


class Describer:
    """
    A module that describes an image.

    Attributes:
        model: The vision model used to describe the image.
        host: The base URL for the vision model.
        identifier: The Identifier object used to identify individuals in the image.
        
    Methods:
        describe(image): Describes the image using the Ollama. this model should be small and local.
        create_ollama_model(model_name): Creates an Ollama model instance for vision.
        create_openai_model(): Creates an OpenAI model instance for vision.

    """
    
    def __init__(self, model_name: str = "llava-phi3", base_url: str = 'http://localhost:11434/'):
        self._model_selection: str = model_name.upper()
        self._base_url: str = base_url
        self.name_queue = Queue()
        
        self.identifier = Identifier()
        self.model = self._initialize_model()

        logger.info(f"Describer: {self._model_selection} is ready.")
        
    def _get_model_factory(self) -> Dict[str, Callable]:
        return {
            "LLAVA-PHI3" : partial(self._create_ollama_model, "llava-phi3"),
            "LLAVA:13B" : partial(self._create_ollama_model, "llava:13b"),
            "OPENAI" : self._create_openai_model,
            "GROQ" : self._create_groq_model
        }
        
    def _create_ollama_model(self, model_name: str):
        from utils.vision.model_ollama import OllamaVision
        
        return OllamaVision(model_name, self._base_url)
    
    def _create_openai_model(self):
        from utils.vision.model_openai import OpenAIVision
        
        return OpenAIVision()
    
    def _create_groq_model(self):
        from utils.vision.model_groq import GroqVision
        
        return GroqVision()
    
    def _initialize_model(self):
        model_factory = self._get_model_factory()
        model = model_factory.get(self._model_selection)
        if model is None:
            raise ValueError(f"Error: Model {self._model_selection} is not supported")

        return model()
    
    def _convert_base64(self, image_data: Union[np.ndarray, str]) -> str:
        """ Convert image data to base64. """
        
        if isinstance(image_data, np.ndarray):
            _, buffer = cv2.imencode('.jpg', image_data)
            image_data = base64.b64encode(buffer).decode('utf-8')
        
        return image_data
    
    def describe_screenshot(self, image_data: Union[np.ndarray, str], query: str) -> Optional[str]:
        """ Describe a screenshot using the vision model. """
        
        image_base64 = self._convert_base64(image_data)
        
        try:
            result = self.model.generate(template_name="screenshot",
                                        image=image_base64,
                                        query=query)
        except Exception as e:
            logger.error(f"Error: Failed to describe screenshot: {str(e)}")
            return None
        
        return result
        
    def describe(self, template_name: str, image_data: Union[np.ndarray, str]) -> Optional[str]:
        """ 
        Describe an image using the vision model.
        Image data could be a numpy array or a base64 encoded string.
        Attributes:
            template_name: The name of the template to use for generating the description.
            image_data: The image data to describe.
            identity: A boolean flag to identify individuals in the image.
            **kwarg: Additional keyword arguments to replace strings in the template.
        """
        try:    
            thread = threading.Thread(target=self.identifier.identify, args=(image_data, self.name_queue))
            thread.start()
            
            image_base64 = self._convert_base64(image_data)
            sight = self.model.generate(template_name=template_name,
                                        image=image_base64)
        except Exception as e:
            logger.error(f"Error: Failed to describe image: {str(e)}")
            return None
        
        name = self.name_queue.get()
        thread.join()
        
        return sight if name == "unknown" else sight + f" I recognize it's {name}."
    
