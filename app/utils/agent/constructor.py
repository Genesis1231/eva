from config import logger
from typing import List, Dict, Optional

from utils.prompt import load_prompt

def format_history(history: Optional[List[Dict]]) -> str:
    """ format the the chat history into string for LLM """
    if not history:
        return ""
    
    messages = []
    messages.append("<|start_header_id|>Conversation History:<|end_header_id|>")
        
    for chat in history:
        for role, message in [("user", chat.get("user_message")),
                              ("assistant", chat.get("eva_message")),
                              ("memory", chat.get("premeditation"))
                              ]:
            if message and message is not None:
                if role == "memory":
                    message = "" if not message  else f"<|start_header_id|>assistant<|end_header_id|>I remember {message}"
                else:
                    message = f"<|start_header_id|>{role}<|end_header_id|>{message}"
               
                message += "<|eot_id|>\n"
                messages.append(message)
        
    return "\n".join(messages)

def format_observation(observation: str) -> str:
    return "" if observation == "<|same|>" or observation is None else f"I see {observation} "

def format_message(user_message: str) -> str:
    return "" if not user_message else f"I hear {user_message} "

def format_action_results(results: Optional[List[Dict]]) -> str:
    """ Format the action results into string for LLM """
    if not results:
        return ""
    
    action_results = []
    # simple way to format the results
    for result_item in results:
        result = result_item.get("result")
        if isinstance(result, List):
            for item in result:
                action_results.append("\n".join([f"{k}: {v}" for k, v in item.items() if "url" not in k])) # dont show urls to avoid speaking them
        elif isinstance(result, Dict):
            action_results.append("\n".join([f"{k}: {v}" for k, v in result.items() if "url" not in k]))
        else:
            action_results.append(result)
            
    action_results = "\n".join(action_results)
        
    return f"\n <|start_header_id|>ipython<|end_header_id|>My previous action results:\n <action results>{action_results} </action results><|eot_id|>"

def build_prompt(timestamp : str, sense: Dict, history: List[Dict], action_results: List[Dict]) -> str:
    """
    Builds the prompt for LLM.
    There are 3 main sections:
        1. System prompt: the persona,  and goal of EVA
        2. Context: the current context of the conversation
        3. Instructions: the steps for the LLM to follow
    """
    
    user_message = sense.get("user_message")
    observation = sense.get("observation")
    system_prompt = load_prompt("persona")
    
    action_results = format_action_results(action_results)
    user_message = format_message(user_message)
    observation = format_observation(observation)
    history_prompt = format_history(history)
    
    PROMPT_TEMPLATE = f"""
        <|begin_of_text|><|start_header_id|>system<|end_header_id|>
        {system_prompt}
        
        I have the access to the following tools:
        {{tools}}
        
        <|eot_id|>
        
        {history_prompt}
        
        <|start_header_id|>user<|end_header_id|>
        ### <Context> ###
        - Current time is {timestamp}.
        - {observation} 
        - {user_message} 
        {action_results}


        ### <Instructions> ###
        Step 1: Analysis:
        - Analyze the conversation history and current context to form a cohesive understanding of my situation.
        - Consider potential misspoken words or typos by users.
        
        Step 2: Planning:
        - Formulate the best response strategy. 
        - Encourage creativity while maintaining the conversation flow.
        - Predetermine information in only required scenarios, but do not tell the user. For example: (the final answer of guessing games). 

        Step 3: Action:
        - Assess the need for using tools based on the analysis. 
        - If tools are needed, carefully generate the tool input according to the provided schema.
        - If I have enough information from the action results, use it in the response appropriately, avoid new actions.
        
        Step 4: Verbal Response: 
        - Craft a cohesive verbal response. No emojis or reaction description.
        - If action is planned, inform the user about the action and remove questions in the verbal response.
        
        ### Final Generation and formatting: ###
        Based on the above context and instructions, craft appropriate response with the following Json format.
        
        {{format_instructions}}
        
        <|eot_id|>
        <|start_header_id|>assistant<|end_header_id|>
    """
    logger.info(PROMPT_TEMPLATE)
    return PROMPT_TEMPLATE