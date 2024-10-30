from config import logger
from typing import Type, Dict, List, Optional

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.tools import BaseTool

from utils.agent import SmallAgent
from utils.extension import DiscordMJ

class PainterInput(BaseModel):
    """Input for painter tool."""
    query: str = Field(description="Input for painter tool, should be the idea or subject of the picture.")

class Painter(BaseTool):
    """
    Tool for creating images with midjourney
    Requires having a midjourney account and a discord channel set up.
    Using the discordMJ module, include discord information in the .env file.
    
    Methods:
        generate_prompt: Generates a prompt for the midjourney tool.
        _run: Main method for running the tool.

    """
    name: str = "image_maker"
    description: str = "Tool for creating pictures. This process might take a while."
    type: str = "chat" # can be used in chatbot
    client: str = "all"
    prompter : SmallAgent = SmallAgent("llama")
    generator : DiscordMJ = DiscordMJ()
    args_schema: Type[BaseModel] = PainterInput

    def _run(
        self,
        query: str,
    ) -> Dict:

        prompt = self.generate_prompt(query)
        if not prompt:
            return {"error": "Failed to generate prompt, try again later."}
      
        if image_urls := self.generator.send_message(f"{prompt} --c 20 --ar 3:4 --s 300"):
            content = f"I have created images with the query: {query}"
            return {"action": content, "image_urls": image_urls}
        
        return {"error": "Failed to create images."}

    def filter_prompt(self, prompt: str) -> str:
        """ Filter the query to remove banned words"""
        banned_words = ("corpse", "naked", "nude", "patriotic", "organ", "lingerie", "sexy", "lolita")
        
        for word in banned_words:
            prompt = prompt.replace(word, '*')
        
        return prompt
    
    def generate_prompt(self, query: str) -> Optional[str]:
        """ Generate a prompt for the midjourney tool"""
        
        try:
            response = self.prompter.generate(template="painter", input=query)
            
            return self.filter_prompt(response.lower())
        except Exception as e:
            logger.error(f"Error: Failed to generate prompt: {str(e)}.")
            return None   
        
        
    def run_client(self, client, **kwargs: Dict) -> Optional[Dict]:
        return client.launch_gallery(image_urls=kwargs.get("image_urls"))

