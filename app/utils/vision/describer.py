import os
from config import logger
import numpy as np
import base64
import requests
import threading
from queue import Queue
from typing import List, Dict, Callable, Union

import cv2
from utils.vision.identifier import Identifier
from utils.prompt import load_prompt

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

    def _get_model_factory(self) -> Dict[str, Callable]:
        return {
            "LLAVA-PHI3" : lambda: self._create_ollama_model("llava-phi3"),
            "LLAVA:13B" : lambda: self._create_ollama_model("llava:13b"),
            "CHATGPT" : self._create_openai_model
        }
        
    def _create_ollama_model(self, model_name: str):
        """ Create an Ollama model instance for vision. """
        from ollama import Client
        
        class VisionClient:
            def __init__(self, model_name: str, base_url: str):
                self.client = Client(base_url)
                self.model = model_name
                
            def generate(self, template_name: str, image: str, **kwargs) -> str:
                prompt_template = load_prompt(f"{template_name}_ollama").format(**kwargs)
                response = self.client.generate(
                    model=self.model,
                    keep_alive="1h",
                    prompt=prompt_template, 
                    images=[image],
                    options=dict(temperature=0.1)
                )
                return response['response']

        return VisionClient(model_name, self._base_url)
    
    def _create_openai_model(self):
        """ Create an OpenAI model instance for vision. """
        class VisionClient:
            def __init__(self):
                self.api_key = os.environ.get("OPENAI_API_KEY")
                self.model = "gpt-4o-mini"
            
            def generate(self, template_name: str, image: str, **kwarg) -> str:
                prompt_template = load_prompt(f"{template_name}_chatgpt").format(**kwarg)
                headers = { "Content-Type": "application/json", "Authorization": f"Bearer {self.api_key}" }
                payload = {
                    "model": self.model,
                    "messages": [{
                        "role": "user",
                        "content": [{
                                "type": "text",
                                "text": prompt_template,
                            },
                            {
                                "type": "image_url",
                                "image_url": { "url": f"data:image/jpeg;base64,{image}" }
                            }]
                        }],
                    "max_tokens": 300,
                    "temperature": 0.1
                    }
            
                try:
                    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                except Exception as e:
                    raise Exception(f"Error: Failed to complete from openai: {str(e)}")
                
                return response.json()["choices"][0]["message"]["content"]
        
        return VisionClient()
    
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
    
    def describe_screenshot(self, image_data: Union[np.ndarray, str], query: str) -> str:
        image_base64 = self._convert_base64(image_data)
        
        return self.model.generate(template_name="screenshot",
                                    image=image_base64,
                                    query=query)
        
        
    def describe(self, template_name: str, image_data: Union[np.ndarray, str]) -> str:
        """ 
        Describe an image using the vision model.
        Image data could be a numpy array or a base64 encoded string.
        Attributes:
            template_name: The name of the template to use for generating the description.
            image_data: The image data to describe.
            identity: A boolean flag to identify individuals in the image.
            **kwarg: Additional keyword arguments to replace strings in the template.
        """
        
        thread = threading.Thread(target=self.identifier.identify, args=(image_data, self.name_queue))
        thread.start()
        
        image_base64 = self._convert_base64(image_data)
        sight = self.model.generate(template_name=template_name,
                                    image=image_base64)
        
        name = self.name_queue.get()
        thread.join()
        
        return sight if name == "unknown" else sight + f" I recognize it's {name}."
    
