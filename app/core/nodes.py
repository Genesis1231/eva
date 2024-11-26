from config import logger, eva_configuration
from datetime import datetime
from typing import Dict, Any

from core.classes import EvaStatus 
from core.functions import initialize_modules
from core.ids import id_manager


def eva_initialize(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Initialize Eva, load all the modules.
    if no user is registered, set the next status to INIT, otherwise set it to ACTIVE.
    """

    modules = initialize_modules(eva_configuration) 
    status = EvaStatus.SETUP if id_manager.is_empty() else EvaStatus.THINKING
    
    return {
        "status": status, 
        "agent": modules["agent"],
        "client": modules["client"],
        "memory": modules["memory"],
        "toolbox": modules["toolbox"],
        "sense": modules["client"].start(),
        "action": [],
        "action_results": [],
        "num_conv": 0
    }

def eva_conversate(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    The main execution node of eva.
    first build the prompt for the agent, then save the conversation to memory, finally send the response to the user.
    
    """
    sense = state["sense"]
    language = sense.get("language")
    memory = state["memory"]
    agent = state["agent"]
    action_results = state["action_results"]

    history = memory.recall_conversation()
    timestamp = datetime.now()
    
    # get response from the LLM agent
    response = agent.respond(
        timestamp=timestamp,
        sense=sense,
        history=history,
        action_results=action_results,
        language=language
    )
    
    memory.create_memory(timestamp=timestamp, user_response=sense, response=response)
    action = response.get("action", [])
    speech = response.get("response")
    
    # send the response to the client device
    eva_response = {
        "speech": speech,
        "language": language,
        "wait": True if not action else False # determine if waiting for user, only for desktop client
    }
    state["client"].send(eva_response)
    
    if any(action):
        return {"status": EvaStatus.ACTION, "action": action}
    else:
        return {"status": EvaStatus.WAITING}

def eva_action(state: Dict[str, Any]) -> Dict[str, Any]:
    """ Execute the actions and return some intermediate output"""
    actions = state["action"]
    toolbox = state["toolbox"]
    client = state["client"]
    
    action_results = toolbox.execute(client, actions)
    if any(action_results):
        return {"status": EvaStatus.THINKING, "action_results": action_results, "action": [], "sense": {}}
    else:
        return {"status": EvaStatus.WAITING, "action": [], "sense": {}}
    
def eva_sense(state: Dict[str, Any]) -> Dict[str, Any]:
    """ receive input from the client """
    
    num = state["num_conv"]
    client = state["client"]
    client.send_over()
    client_feedback = client.receive()

    user_message = client_feedback.get("user_message")

    if user_message and any(word in user_message.lower() for word in ['bye', 'exit']):
        return {"status": EvaStatus.END}
    else:
        return {"status": EvaStatus.THINKING, "num_conv": num + 1, "sense": client_feedback, "action_results": [] }


def eva_end(state: Dict[str, Any]) -> Dict[str, Any]:
    """End the conversation."""
    
    client = state["client"]
    num = state["num_conv"]
    
    client.speak("Now exiting E.V.A.")
    logger.info(f"EVA is shutting down after {num} conversations.")
    client.deactivate()
    
    return {"status": EvaStatus.END}

##### Router nodes #####

def router_initialize(state: Dict[str, Any]) -> str:
    """ Initialize the setup if no user is registered """  
    return "node_setup" if state["status"] == EvaStatus.SETUP else "node_conversate"

def router_sense(state: Dict[str, Any]) -> str:
    """ Determine the next node based on the user input """
    return "node_end" if state["status"] == EvaStatus.END else "node_conversate"

def router_action(state: Dict[str, Any]) -> str:
    """ Determine the next node based on if there is any action to execute """
    return "node_action" if state["status"] == EvaStatus.ACTION else "node_sense"

def router_action_results(state: Dict[str, Any]) -> str:
    """ Determine the next node based on if there are any action results """
    return "node_conversate" if state["status"] == EvaStatus.THINKING else "node_sense"