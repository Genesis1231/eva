
import os
import threading
import asyncio
from config import logger
import time
import json
import secrets

from typing import Dict, List

from utils.tts import Speaker
from client.connection import ConnectionManager

class MobileClient:
    def __init__(self, stt_model: str, vision_model: str, tts_model: str, base_url: str):   
        self.session_id = None
        self.server_thread = None
        
        self.server = ConnectionManager(stt_model, vision_model, base_url)
        self.speaker = Speaker(tts_model)
        
        self.initialize_client()

    def initialize_client(self) -> None:
        try:
            self.server_thread = threading.Thread(target=self.server.run_server, daemon=True)
            self.server_thread.start()

        except Exception as e:
            raise Exception(f"Error initializing server: {str(e)}")

    def send_data(self, data_str: str) -> None:
        async def send_message():
            await self.server.send_message(data_str)

        try:
            asyncio.run(send_message())
        except RuntimeError as e:
            logger.error(f"Error in sending message: {str(e)}")
            
        
    def send(self, data: Dict) -> None:
        if not data:
            logger.warning("No data is sent to client.")
            return

        audio_path = self.speaker.get_audio(data["speech"])
        data_json = []
        for path in audio_path:
            data_json.append({ 
                    "session_id": self.session_id, 
                    "type": "audio", 
                    "content": path,
            })
    
        self.send_data(json.dumps(data_json))
    
    def send_over(self) -> None:
        data_json = {
            "type": "over",
            "content": self.generate_session_id(),
        }
        
        self.send_data(json.dumps(data_json))
        
    def receive(self) -> Dict:
        while True:
            user_input = self.server.get_message()            
            if user_input:
                break
            
            time.sleep(1)
            continue
                
        self.session_id = user_input.get("session_id")
        
        if not user_input.get("observation"):
            user_input["observation"] = "<|same|>"
            
        if not user_input.get("user_message"):
            user_input["user_message"] = None
                            
        return user_input
    
    def start(self) -> Dict:
        while True:
            user_input = self.server.get_message()
            
            if not user_input:
                time.sleep(1)
                continue
            
            observation = user_input.get("observation")
            if observation:
                break
            
        self.session_id = user_input.get("session_id")
        
        return {"observation": observation}

    def generate_session_id(self) -> str:
        return secrets.token_urlsafe(16)
    
    def __del__(self):
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()
        
    def __repr__(self) -> str:
        return "MobileClient"
    
    def load_html(self, template: str, **kwargs) -> str:
    # load the html from the html directory
        
        dir = os.path.dirname(__file__)
        html_path = os.path.join(dir, "html", f"{template}.html")
        
        try:
            with open(html_path, 'r') as f:
                html = f.read().strip()

        except FileNotFoundError:
            raise FileNotFoundError(f"template file {html_path} not found.")

        for key, value in kwargs.items():
            html = html.replace(f"<{key}>", value)

        return html
    
    def stream_music(self, mp3_url: str, cover_url: str, title: str) -> None:
        # stream a music and cover image to mobile client
        try: 
            page = self.load_html(template="music", image_url=cover_url, music_title=title)
            data_json = [{
                "session_id": self.session_id, 
                "type": "mp3",
                "content": mp3_url,
            },
            {
                "type": "html",
                "content": page
            }]
        
            self.send_data(json.dumps(data_json))
            return {"user_message": f"Media Player:: The song '{title}' is playing."}
        
        except Exception as e:
            logger.error(f"Error: Failed to stream to client: {str(e)}")
            return {}
        
    def launch_youtube(self, id: str, title: str) -> bool:
        """ Stream the youtube video to the client """
        try:
            page = self.load_html("youtube", video_id=id, video_title=title)
            data_json = {
                "session_id": self.session_id, 
                "type": "html",
                "content": page
            }
            
            self.send_data(json.dumps(data_json))
            return {"observation": "The video player is launched."}
        
        except Exception as e:
            logger.error(f"Error: Failed to stream youtube video to client: {str(e)}")
            return {}
          
    def launch_epad(self, html: str) -> Dict:
        try:
            page = self.load_html("blank", full_html=html)
            data_json = {
                "session_id": self.session_id, 
                "type": "html",
                "content": page
            }
            
            self.send_data(json.dumps(data_json))
            return {"observation": "The epad is launched."}
        except Exception as e:
            logger.error(f"Error: Failed to launch epad to client: {str(e)}")
            return {}