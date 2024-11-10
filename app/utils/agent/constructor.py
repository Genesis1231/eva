from config import logger
from typing import List, Dict
from pydantic import BaseModel, Field
from utils.prompt import load_prompt

class PromptConstructor:
    """
    Class for constructing the prompt for the LLM.
    """
    
    def __init__(self):
        self.system_prompt: str = load_prompt("persona")
        self.instruction_prompt: str = load_prompt("instructions")
        
    @staticmethod
    def _format_history(history: List[Dict] | None) -> str:
        """ format the the chat history into string for LLM """
        if not history:
            return ""
    
        messages = []
        messages.append("<CONVERSATION_HISTORY>")
        
        for chat in history:
            for role, message in [("user", chat.get("user_message")),
                                  ("assistant", chat.get("eva_message")),
                                  ("memory", chat.get("premeditation"))
                                  ]:
                if not message:
                    continue
            
                if role == "memory":
                    message = f"<assistant>I remember {message} </assistant>"
                else:
                    message = f"<{role}>{message}</{role}>"
                
                messages.append(message)
                
        messages.append("</CONVERSATION_HISTORY>")
        return "\n".join(messages)

    @staticmethod
    def _format_observation(observation: str | None) -> str:
        return "" if not observation else f"<observation>I see {observation} </observation>"

    @staticmethod
    def _format_message(user_message: str | None) -> str:
        return "" if not user_message else f"<human_reply>I hear {user_message} </human_reply>"

    @staticmethod
    def _format_action_results(results: List[Dict] | None) -> str:
        """ Format the action results into string for LLM """
        if not results:
            return ""
    
        action_results = []
        action_results.append("<action_results>I received the following results from my previous actions:")
        
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
            
            if additional_info:=result_item.get("additional"):
                action_results.append(additional_info)
            
        action_results.append("</action_results>")
        return "\n".join(action_results)

    def build_prompt(self, timestamp : str, sense: Dict, history: List[Dict], action_results: List[Dict]) -> str:
        """
        Builds the prompt for LLM.
        There are 3 main sections:
        1. System prompt: the persona,  and goal of EVA
        2. Context: the current context of the conversation
        3. Instructions: the steps for the LLM to follow
        
        """
        
        user_message = sense.get("user_message")
        observation = sense.get("observation")
        system_prompt: str = self.system_prompt
        instructions: str = self.instruction_prompt
        
        action_results = self._format_action_results(action_results)
        user_message = self._format_message(user_message)
        observation = self._format_observation(observation)
        history_prompt = self._format_history(history)
        
        PROMPT_TEMPLATE = f"""  
            <PERSONA>
            {system_prompt}
            </PERSONA>
            
            <TOOLS>
            I have the access to the following tools for action:
            {{tools}}
            </TOOLS>
            
            {history_prompt}
            
            <CONTEXT>
            <current_time>{timestamp}</current_time>
            {observation} 
            {user_message} 
            {action_results}
            </CONTEXT>

            <INSTRUCTIONS>
            {instructions}
            </INSTRUCTIONS>
            
            Based on the above context and instructions, craft appropriate response with the following Json format.
            
            <FORMATTING>
            {{format_instructions}}
            </FORMATTING>
    
            <ASSISTANT>
        """
    
        logger.debug(PROMPT_TEMPLATE) 
        return PROMPT_TEMPLATE
