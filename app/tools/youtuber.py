import json
from config import logger
from random import choice
from typing import Type, Dict, Optional

from pydantic import BaseModel, Field
from langchain_community.tools import BaseTool
from youtube_search import YoutubeSearch

class YoutubeInput(BaseModel):
    query: str = Field(description="Input for Youtube tool, normally no more than 4 words.")
    
class Youtuber(BaseTool):
    """
    Tool that queries YouTube, supports both video and shorts.
    Methods:
        _run: Main method to run the tool.
        run_client: Method to display the video in the client.
    
    """
    name: str = "youtube_search"
    description: str = "Tool for searching youtube videos. the input should be short keyword query."
    type: str = "conversational"
    client: str = "all"
    args_schema: Type[BaseModel] = YoutubeInput
    
    def _run(
        self,
        query: str,
    ) -> Dict:

        try:
            results = YoutubeSearch(query).to_json()
        except Exception as e:
            logger.error(f"Error: Failed to find video: {str(e)}.")
            return {"error": f"Failed to get Youtube video, please try again."}
    
        if not results:
            return {"error": f"No search results with query: {query}, please revise and try again."}
        
        video_data = choice(json.loads(results)["videos"])
        url = video_data.get("url_suffix")
        
        if "shorts" in url:
            video_id = url.split("shorts/")[1]
        else:
            video_id = url.split('?v=')[1].split('&')[0]
    
        video_title = video_data.get("title")
        content = f"I have found a video on YouTube by {video_data.get('channel')} and published {video_data.get('publish_time')}."

        return  {"action": content, "url" : video_id, "title": video_title}

    def run_client(self, client, **kwargs: Dict) -> Optional[Dict]:
        return client.launch_youtube(id=kwargs.get("url"), title=kwargs.get("title"))
