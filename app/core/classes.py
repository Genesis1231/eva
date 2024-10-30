import time

from typing_extensions import TypedDict, Optional, Union, Dict, List

from client import WSLClient, MobileClient
from utils.agent import ChatAgent 
from utils.memory import Memory
from tools import ToolManager

class EvaState(TypedDict):
    status: str 
    agent: ChatAgent
    toolbox: ToolManager
    client: Optional[Union[WSLClient, MobileClient]]
    memory : Memory
    sense : Optional[Dict]
    action : List[Optional[Dict]]
    action_results: List[Optional[Dict]]
    num_conv: int
    last_conv: time.struct_time
 