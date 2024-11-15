from typing import Dict, Any
from datetime import datetime
from core.nodes import EvaStatus

def eva_setup(state: Dict[str, Any]) -> Dict[str, Any]:
    """ Initialize the setup for the first time user """
    from utils.agent.setup_agent import SetupAgent

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
    
    # if any(action):
    #     return {"status": EvaStatus.ACTION, "action": action}
    # else:
    #     return {"status": EvaStatus.WAITING}

    
    return {"status": EvaStatus.SETUP, "agent": agent}
