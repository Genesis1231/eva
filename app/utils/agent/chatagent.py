from config import logger, validate_language
import json
from functools import partial
from typing import Callable, Dict, Any, List

from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseLanguageModel

from utils.agent.constructor import PromptConstructor
from utils.agent.models import (
    create_groq_model,
    create_ollama_model,
    create_openai_model,
    create_mistral_model,
    create_google_model,
    create_anthropic_model,
)

class ChatAgent:
    """
    A class representing a chat agent that interacts with different language models.
    
    Attributes:
        model_selection (str): The name of the selected language model.
        model_temperature (float): The temperature parameter for generating responses.
        model_factory (dict): A dictionary mapping model names to their corresponding creation methods.
        llm: The initialized language model.
        chat_history (list): A list of chat messages exchanged between the agent and the user.
    
    Functions:
        switch_model: Switch to a different language model.
        respond: Get a response from the language model.
        clear_chat_history: Clear the chat history.
    """
    
    def __init__(self, model_name: str = "llama", base_url: str = "http://localhost:11434", language: str = "english")-> None:
        self.model_selection: str = model_name.upper()
        self.base_url: str = base_url
        self.language: str = language
        
        self.constructor = PromptConstructor()
        self.llm: BaseLanguageModel = self._initialize_model()
        self.tool_info: List[Dict[str, Any]] = []
        
        logger.info(f"Agent: {self.model_selection} is ready.")

    def _get_model_factory(self) -> Dict[str, Callable[[], BaseLanguageModel]]:
        """ Get the model factory for creating LLM models. """
        return {
            "GROQ" : partial(create_groq_model, model_name="llama-3.1-70b-versatile"),
            "ANTHROPIC": create_anthropic_model,
            "MISTRAL":  create_mistral_model,
            "GOOGLE": create_google_model,
            "OPENAI" : create_openai_model,
            "LLAMA" : partial(create_ollama_model, base_url=self.base_url, model_name="llama3.1:70b"),
            "QWEN": partial(create_ollama_model, base_url=self.base_url, model_name="qwen2.5:72b"),
        }
        
    def _initialize_model(self)-> BaseLanguageModel:
        """ Initialize the ChatAgent LLM model """
        
        model_factory = self._get_model_factory()
        model = model_factory.get(self.model_selection)
        if model is None:
            raise ValueError(f"Error: Model {self.model_selection} is not supported")
    
        return model() 
    
    def _get_output_format(self, language: str | None) -> BaseModel:
        """Pydantic output format for the response"""
        
        # Validate the language  
        language = validate_language(language) 
        if not language:
            language = self.language
        
        verbal_language = f"(RESPOND ONLY IN NATIVE {language.upper()})" if language.upper() not in {"ENGLISH", "MULTILINGUAL"} else ""
        
        class AgentOutput(BaseModel):
            analysis: str = Field(description="My reflection and analysis")
            strategy: str = Field(description="My response strategy")
            response: str = Field(description=f"My verbal response {verbal_language}")
            premeditation: str = Field(description="My predetermined information")
            action: List[Dict[str, Any]] = Field(description="The name of the tools I choose to use and the args for input.")
        
        return AgentOutput
    
    def set_tools(self, tool_info: List[Dict])-> None:
        self.tool_info = tool_info
    
    def _format_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """ Deals with the inconsistent response parsing format from various models"""
         
        if response.get("properties"):
            response = response.get("properties")
        
        if isinstance(response['action'], str):
            try:
                response['action'] = json.loads(response['action'])
            except json.JSONDecodeError:
                response['action'] = [] # if the action was not properly formatted, ignore 
            
        return response
    
    def respond(
        self, 
        timestamp : str, 
        sense: Dict, 
        history: List[Dict], 
        action_results: List[Dict], 
        language: str | None
    ) -> Dict:
        """Main response function that build the prompt and get response from the language model"""
        
        prompt = self.constructor.build_prompt(
            timestamp=timestamp, 
            sense=sense, 
            history=history, 
            action_results=action_results
        )
        
        parser = JsonOutputParser(pydantic_object=self._get_output_format(language))
        
        prompt_template = PromptTemplate(
            input_variables=["tools"],
            template = prompt,
            partial_variables={"format_instructions": parser.get_format_instructions()},
        )
            
        chain = prompt_template | self.llm | parser
        
        try: 
            response = chain.invoke({"tools": json.dumps(self.tool_info)})
            logger.debug(json.dumps(response, indent=2))
            response = self._format_response(response)
            
        except Exception as e:
            raise Exception(f"ChatAgent: Failed to get response from model: {str(e)}")
            
        return response
