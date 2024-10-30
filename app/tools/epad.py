from config import logger
import re
from typing import Optional, Type, Dict

from pydantic import BaseModel, Field
from langchain_community.tools import BaseTool
from utils.agent import SmallAgent
 

class EpadInput(BaseModel):
    query: str = Field(description="Input for Epad tool. Query should be accurate keywords of my feeling.")
    
class Epad(BaseTool):
    """Tool that generate additional content on a client pad."""
    
    name: str = "emo_pad"
    description: str = "Tool to use when I have strong emotion or feelings."
    type: str = "conversational"
    client: str = "None"
    generator : SmallAgent = SmallAgent("anthropic") # Only chatgpt and anthropic work good for for the epad
    args_schema: Type[BaseModel] = EpadInput
    
    def _run(
        self,
        query: str,
    ) -> Dict:
        try:
            logger.info(f"Generating emotion HTML for query: {query}")
            response = self.generator.generate(template="epad", input=query)
        
        except Exception as e:
            logger.error(f"Error: Failed to generate emotion content: {str(e)}.")
            return {"error": f"Failed to generate emotion content. Try again later."}

        if html := re.search(r'<html>(.*?)</html>', response, re.DOTALL):
            content = "I have expressed through the design."
            return  {"action": content, "html_url" : html }
        
        return {"error": f"Error: Failed to generate content. Try again later."}
    
    def run_client(self, client, **kwargs: Dict) -> Optional[Dict]:
        return client.launch_epad(html=kwargs.get("html_url"))
