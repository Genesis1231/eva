from typing import TypedDict, Union, Dict, List
from enum import Enum

from client import WSLClient, MobileClient
from utils.agent import ChatAgent 
from utils.memory import Memory
from tools import ToolManager

class EvaStatus(Enum):
    """EVA operational status."""
    ACTIVE = "active" # EVA is active
    THINKING = "thinking" # EVA is thinking
    WAITING = "waiting" # EVA is waiting for user response
    ACTION = "action" # EVA is performing an action
    END = "end" # EVA is shutting down
    ERROR = "error" # EVA has encountered an error
    SETUP = "setup" # EVA is setting up
    
class EvaState(TypedDict):
    """Langraph EVA state."""
    status: EvaStatus
    agent: ChatAgent 
    toolbox: ToolManager 
    client: Union[WSLClient, MobileClient] 
    memory : Memory
    sense : Dict | None
    action : List[Dict]
    action_results: List[Dict]
    num_conv: int

