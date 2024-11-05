from tqdm import tqdm
from typing_extensions import Dict, List

from client import WSLClient, MobileClient
from utils.agent import ChatAgent 
from utils.memory import Memory
from tools import ToolManager


def load_classes(class_dict)-> Dict:
    """ Load the classes from the dictionary, using tqdm to show progress """
    
    instances = {}
    with tqdm(total=len(class_dict), desc="Initializing EVA...") as pbar:
        for name, class_init in class_dict.items():
            pbar.set_description(f"Loading module: {name}")
            instances[name] = class_init()
            pbar.update(1)
            
    return instances

def initialize_modules(config : dict):
    """ Initialize the modules for Eva """
    
    base_url = config.get("BASE_URL")
    stt_model = config.get("STT_MODEL")
    tts_model = config.get("TTS_MODEL")
    image_model = config.get("IMAGE_MODEL")
    
    modules = {
        "LLM": lambda: ChatAgent(config.get("CHAT_MODEL"), base_url),
        "memory" : lambda: Memory(config.get("SUMMARIZE_MODEL"), base_url),
        "toolbox" : lambda: ToolManager(config.get("DEVICE"))
    }
    
    client_type = config.get("DEVICE").upper()
    if client_type == "DESKTOP":
        modules["client"] = lambda: WSLClient(stt_model, image_model, tts_model, base_url)
    elif client_type == "MOBILE":
        modules["client"] = lambda: MobileClient(stt_model, image_model, tts_model, base_url)
    else:
        raise ValueError(f"Client type {client_type} not supported.")

    return load_classes(modules)