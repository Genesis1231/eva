from config import logger
from threading import Thread

from config import eva_configuration
from core.functions import get_timestamp, initialize_modules


def eva_initialize(state):
    """Initialize Eva, load all the modules"""

    modules = initialize_modules(eva_configuration)
    modules["LLM"].set_tools(modules["toolbox"].get_tools_info())
    
    return {
        "status": "active", 
        "agent": modules["LLM"],
        "client": modules["client"],
        "memory": modules["memory"],
        "toolbox": modules["toolbox"],
        "sense": modules["client"].start(),
        "action": [],
        "action_results": [],
        "num_conv": 0
    }

def eva_conversate(state):
    """
    The main execution node of eva.
    first build the prompt for the agent, then save the conversation to memory, finally send the response to the user.
    
    """
    
    sense = state["sense"]
    memory = state["memory"]
    agent = state["agent"]
    action_results = state["action_results"]

    history = memory.recall_conversation()
    timestamp = get_timestamp()
    
    # get response from the LLM agent
    response = agent.respond(
        timestamp=timestamp,
        sense=sense,
        history=history,
        action_results=action_results, 
    )
    
    speech = response.get("response")
    action = response.get("action")
    
    # thread the memory creation to save time
    thread = Thread(target=memory.create_memory, daemon=True, 
                              kwargs={"timestamp": timestamp, "user_response": sense, "response": response })
    thread.start()
    
    # send the response to the client device
    client = state["client"]
    eva_response = {
        "speech": speech,
        "wait": True if not action else False # determine if waiting for user, only for desktop client
    }
    client.send(eva_response)
    thread.join()
    
    return {"status": "active", "action": action, "last_conv": timestamp}

def eva_action(state):
    """ Execute the actions and return some intermediate output"""
    actions = state["action"]
    toolbox = state["toolbox"]
    client = state["client"]
    
    results = toolbox.execute(client, actions)
    
    return {"status": "active", "action_results": results, "action": [], "sense": {}}
    
def eva_sense(state):
    """ Get the user input"""

    # if state["status"] == "inactive":
        # if EVA is inactive, then we only need to watch for changes periodically
        # while True:
        #     watcher = state["watcher"]
        #     sight = watcher.get_observation()
        #     # if sight has a significant change
        #     #     break
        #     time.sleep(60)
    
    num = state["num_conv"]
    client = state["client"]
    client.send_over()
    client_feedback = client.receive()

    return {"status": "responding",  "num_conv": num + 1, "sense": client_feedback, "action_results": [] }


def eva_end(state):
    """End the conversation."""
    
    client = state["client"]
    num = state["num_conv"]
    
    client.speak("NOW EXITING E.V.A.")
    logger.info(f"EVA is shutting down after {num} conversations.")
    client.deactivate()
    
    return {"status": "end"}

#### Router functions ####

def router_sense(state):
    """ Determine the next node based on the user input """

    message = state["sense"].get("user_message")
    
    if message is None:
        return "node_conversate"

    if "bye" in message.lower() or "exit" in message.lower():
        return "node_end"
    else:
        return "node_conversate"


def router_action(state):
    """ Determine the next node based on if there is any action to execute """
    return "node_action" if state["action"] else "node_sense"

def router_action_results(state):
    """ Determine the next node based on if there are any action results """
    return "node_conversate" if any(state["action_results"]) else "node_sense"