import requests
import os
import time
from config import logger
from typing import List, Dict, Optional

import cv2
import numpy as np

class DiscordMJ():
    """
    A class for sending prompts to discord midjourney and getting the image url.
    simple implementation to retrieve images from midjourney.
    """
    def __init__(self):
        self.application_id = os.environ.get("MJ_Application_ID")
        self.guild_id = os.environ.get("MJ_Guild_ID")
        self.channel_id = os.environ.get("MJ_Channel_ID")
        self.version = os.environ.get("MJ_Version")
        self.id = os.environ.get("MJ_ID")
        self.authorization = os.environ.get("MJ_Authorization")
        
        self._url = "https://discord.com/api/v9/interactions"
        self._msg_url = f'https://discord.com/api/v9/channels/{self.channel_id}/messages'
        self._headers = {
            'Authorization': self.authorization,
            'Content-Type': 'application/json',
        }

        self.prev_message_id = self._load_previous()
        
    def _load_previous(self) -> Optional[str]:
        """Load the previous message id"""
        try:
            with requests.get(self._msg_url, headers=self._headers) as response:
                response.raise_for_status()
                messages = response.json()
                if messages:
                    return messages[0].get('id')
        except Exception as e:
            logger.error(f"Error loading previous message: {e}")
            
        return None
        
    def _get_data(self, prompt: str)-> Dict:
        return {
            "type": 2,
            "application_id": self.application_id,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "session_id": "d7cf82a1fbdb21dc5b06b47eeb2ed32d",
            "data": {
                "version": self.version,
                "id": self.id,
                "name": "imagine",
                "type": 1,
                "options": [
                    {
                        "type": 3,
                        "name": "prompt",
                        "value": prompt
                    }
                ],
                "application_command": {
                    "id": self.id,
                    "application_id": self.application_id,
                    "version": self.version,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "imagine",
                    "description": "Create images with Midjourney",
                    "dm_permission": True,
                    "contexts": None,
                    "options": [
                        {
                            "type": 3,
                            "name": "prompt",
                            "description": "The prompt to imagine",
                            "required": True
                        }
                    ]
                },
                "attachments": []
            },
        }
        
    def send_message(self, prompt: str) -> Optional[List[str]]:
        """ Send a prompt to discord and get the image url """
        try:
            with requests.post(self._url, headers=self._headers, json=self._get_data(prompt)) as response:
                response.raise_for_status()
        except requests.RequestException as e:
            return None

        logger.info(f"Sent midjourney prompt: {prompt}")
        for i in range(60):
            time.sleep(1)
            print(f"waiting for midjourney to complete ... {i}s", end="\r")
            
            try:
                with requests.get(self._msg_url, headers=self._headers) as response:
                    response.raise_for_status()
                    messages = response.json()
                    if not messages or messages[0]['id'] == self.prev_message_id or not messages[0]['components'][0]['components']:
                        continue
                    
                    image_url = messages[0]['attachments'][0]['proxy_url']
                    with requests.get(image_url) as image_response:
                        image_response.raise_for_status()
                        image_data = image_response.content
                    break
            except (KeyError, IndexError):
                continue
            except Exception as e:
                logger.error(f"Error getting image: {e}")
                return None
        else:
            logger.error("Timeout waiting for creating image.")
            return None

        self.prev_message_id = messages[0]['id']
        return self._process_image(image_data, self.prev_message_id)

    def _process_image(self, image_data: bytes, image_id: str) -> List[str]:
        """Process the image data and save it"""
        png_data = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(png_data, cv2.IMREAD_COLOR)
            
        height, width = img.shape[:2]
        mid_h, mid_w = height // 2, width // 2
        
        # Split the image into 4 parts
        parts = [img[:mid_h, :mid_w], img[:mid_h, mid_w:], 
                 img[mid_h:, :mid_w], img[mid_h:, mid_w:]]
        
        base_filename = os.path.join(os.getcwd(), "data", "images", image_id)
        image_paths = [f"{base_filename}_{i+1}.jpg" for i in range(4)]
        
        for i, part in enumerate(parts):
            cv2.imwrite(image_paths[i], part)
   
        return image_paths
    