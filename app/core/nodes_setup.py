from config import logger, eva_configuration, validate_language
from typing import Dict, Any
from datetime import datetime
from core.classes import EvaStatus

def eva_setup(state: Dict[str, Any]) -> Dict[str, Any]:
    """ Initialize the setup for the first time user """
    from utils.agent.setup_agent import SetupAgent

    # initialize the setup agent
    model_name = eva_configuration.get("CHAT_MODEL")
    base_url = eva_configuration.get("BASE_URL")
    if not (full_lang := validate_language(language)):
        language = full_lang = "multilingual"
    
    setup_agent = SetupAgent(
        model_name=model_name, 
        base_url=base_url, 
        language=full_lang
    )
    
    return {"agent": setup_agent}

def eva_setup_name(state: Dict[str, Any]) -> Dict[str, Any]:
    """ Setup the User Name """
    
    agent = state["agent"]
    sense = state["sense"]
    language = sense.get("language")
    memory = state["memory"]

    history = memory.recall_conversation()
    timestamp = datetime.now()
    
    # get response from the LLM agent
    response = agent.respond(
        timestamp=timestamp,
        sense=sense,
        history=history,
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

