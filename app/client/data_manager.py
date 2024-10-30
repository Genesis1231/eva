from config import logger
import json
import asyncio
from typing_extensions import Dict, Optional, List
import secrets

from utils.stt.transcriber import Transcriber
from utils.vision.describer import Describer
from client.functions import convert_audio_data 

class DataManager:
    def __init__(self, stt_model: str, vision_model: str, base_url: str) -> None:
        self.session_data = asyncio.Queue()
        self.session_data_list : List[Dict] = []
        
        self.transcriber = Transcriber(stt_model)
        self.img_describer = Describer(vision_model, base_url)
        self.processing_task = None
        
    async def start_queue(self):
        self.processing_task = asyncio.create_task(self._process_queue())
        
    async def stop(self):
        """Stop the processing task."""
        if self.processing_task:
            self.processing_task.cancel()
            try:
                await self.processing_task
                
            except asyncio.CancelledError:
                pass
            
    async def process_message(self, message: str, client_id: Optional[str] = None) -> str:
        """Process incoming messages and handle them accordingly."""
        message_json = json.loads(message)
        session_id = message_json.get("session_id")
        message_type = message_json.get("type")
         
        # try:

            
        #     response_json = []
             
        #     for data in message_json["data"]:
        #         msg_type = data["type"]
                
        #         if msg_type == "heart":
        #             content = "success"
                    
        #         elif msg_type == "over":
        #             await self.session_data.put(message_json)
        #             session_id = self.generate_session_id()
        #             content = "success"
                    
        #         else:
        #             if not await validate_data(message_json):
        #                 content = "error"
        #             else:
        #                 # await self.session_data.put(message_json)
        #                 content = "success"

        #         response_json.append({"type": msg_type, "content": content})
            
        # except json.JSONDecodeError as e:
        #     logger.error(f"Error decoding JSON: {message_json} {str(e)}")
        #     response_json = [{"type" : "Json data", "content": "error"}]
        
        response_data = {
            "session_id" : session_id,
            "type" : f"validation-{message_type}",
            "content" : "success"
            }
        
        await self.session_data.put(message_json) # put data in the queue for process
        
        return json.dumps(response_data)
    
    async def _process_queue(self):
        while True:
            try:
                data = await self.session_data.get()
                if data == None:
                    continue
            
                data_type = data["type"]
                content = data["content"]
            
                if data_type == "audio":
                    audio_data = convert_audio_data(content)
                    result = self.transcriber.transcribe(audio_data)
                    
                elif data_type == "frontImage" or data_type == "backImage":
                    result = self.img_describer.describe("vision", content, identity=True)
                    
                elif data_type == "over":
                    result = "success"
                    
                else:
                    logger.error(f"Unsupported data type: {data_type}")
                    result = "error"
                    continue

                data["content"] = result
                self.session_data_list.append(data)
                logger.info(f"Session data: {self.session_data_list}")
                await asyncio.sleep(0.5)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in processing data queue: {e}")
            
            
    def generate_session_id(self) -> str:
        return secrets.token_urlsafe(16)
    

    def get_session_data(self) -> str:
        
        data_json = { 
                        "session_id": self.generate_session_id(), 
                        "type": "receive_start", 
                        "content": "success"
        }
        
        return json.dumps(data_json)

    # return the first session data in the list
    def get_first_data(self) -> Optional[Dict]:
        if len(self.session_data_list) == 0:
            return None
        
        first_session_data = None
        for idx, session in enumerate(self.session_data_list):
            if session.get("type") == "over":
                first_session_data = {"session_id": session["session_id"]}
                break
        
        if first_session_data is None:
            return None
    
        type_mapping = {
            'frontImage': 'observation',
            'backImage': 'view',
            'audio': 'user_message'
        }
        
        for i in range(idx):
            data_type = self.session_data_list[i].get('type')
            if data_type in type_mapping:
                first_session_data[type_mapping[data_type]] = self.session_data_list[i].get('content')
        
        self.session_data_list = self.session_data_list[idx+1:]  # Remove processed data after processing
        
        return first_session_data
            

                





