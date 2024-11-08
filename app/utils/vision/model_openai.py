from config import logger
from typing import Optional
from openai import OpenAI

from utils.prompt import load_prompt

class OpenAIVision:
    def __init__(
        self,
        model_name: str = "gpt-4o-mini",
        temperature: float = 0.1
    ):
        self.client = OpenAI()
        self.model_name = model_name
        self.temperature = temperature

    def generate(self, template_name: str, image: str, **kwarg) -> Optional[str]:
        """ Generate image description from the model."""
        
        prompt_template = load_prompt(f"{template_name}_ollama").format(**kwarg)
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_template,
                        },
                        {
                            "type": "image_url",
                            "image_url": { "url":  f"data:image/jpeg;base64,{image}" }
                        }],
                    }],
                temperature=self.temperature
                )

        except Exception as e:
            logger.error(f"Error: Failed to complete from openai: {str(e)}")
            return None
        
        return response.choices[0].message.content
