from functools import partial
from tqdm import tqdm
from config import validate_language
from typing import Dict

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
    """ Initialize the modules for EVA """
    
    base_url = config.get("BASE_URL")
    language = config.get("LANGUAGE")

    # Initialize the modules
    module_list = {
        "agent": partial(ChatAgent, config.get("CHAT_MODEL"), base_url, validate_language(language)),
        "memory" : partial(Memory, config.get("SUMMARIZE_MODEL"), base_url),
        "toolbox" : partial(ToolManager, config.get("DEVICE"))
    } 
    
    # Pre-configure client parameters
    client_params = {
        'stt_model': config.get("STT_MODEL"),
        'vision_model': config.get("IMAGE_MODEL"),
        'tts_model': config.get("TTS_MODEL"),
        'base_url': base_url,
        'language': language
    }
    
    client_type = config.get("DEVICE").upper()
    if client_type == "DESKTOP":
        module_list["client"] = partial(WSLClient, **client_params)
    elif client_type == "MOBILE":
        module_list["client"] = partial(MobileClient, **client_params)
    else:
        raise ValueError(f"Client type {client_type} not supported.")

    # Load the modules
    modules = load_classes(module_list)
    modules["agent"].set_tools(modules["toolbox"].get_tools_info())
    
    return modules