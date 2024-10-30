import os
from config import logger
import asyncio
from typing_extensions import Dict, List, Optional
 
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi import File, UploadFile, HTTPException
from fastapi.responses import FileResponse
import uvicorn

from client.data_manager import DataManager


class ConnectionManager:
    def __init__(self, stt_model: str, vision_model: str, base_url: str):
        self.app = FastAPI()
        self.data_manager = DataManager(stt_model, vision_model, base_url) 
        
        self.media_folder: str = "/media" # TODO: make this configurable
        self.client_id: Optional[str] = None
        self.active_connections: Dict[str, WebSocket] = {}
        self.setup_routes()

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()

        websocket.receive_limit = None
        websocket.send_limit = None
        self.active_connections[client_id] = websocket
        self.client_id = client_id # manage the client_id later
        
        initial_data = self.data_manager.get_session_data()
        await self.send_message(initial_data)

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)

    async def send_message(self, message: str, client_id: str = None):
        # manage the client id later.
        if client_id is None:
            client_id = self.client_id
        
        #logger.info(f"Sending message to client: {client_id} :: {message}")
        
        if client_id in self.active_connections:
            await self.active_connections[client_id].send_text(message)
        
    async def broadcast(self, message: str):
        for websocket in self.active_connections.values():
            await websocket.send_text(message)

            
    def setup_routes(self):
        @self.app.websocket("/ws/{client_id}")
        async def websocket_endpoint(websocket: WebSocket, client_id: str):
            await self.connect(websocket, client_id)
            await self.data_manager.start_queue()
            try:
                while True:
                    message = await websocket.receive_text()

                    response = await self.data_manager.process_message(message, client_id)

                    await self.send_message(response)
                    await asyncio.sleep(0.3)
                    
            except WebSocketDisconnect:
                self.disconnect(client_id)
            except Exception as e:
                raise Exception(f"Error handling connection: {str(e)}")
            finally:
                self.disconnect(client_id)
                await self.data_manager.stop()
        
        # @self.app.post("/upload/")
        # async def upload_file(file: UploadFile = File(...)):
        #     if is_valid(file.filename, [".jpg", ".jpeg"]):
        #         save_dir = "user_images"
        #     elif is_valid(file.filename, [".mp3"]):
        #         save_dir = "user_audio"
        #     else:
        #         raise HTTPException(status_code=400, detail="Invalid file type. Only .jpg, .jpeg, and .mp3 files are allowed.")

        #     file_path = os.path.join(self.media_folder, save_dir, file.filename)
            
        #     try:
        #         with open(file_path, "wb") as buffer:
        #             content = await file.read()
        #             buffer.write(content)
        #     except Exception as e:
        #         raise HTTPException(status_code=500, detail=f"Failed to save file: {str(e)}")

        #     return {"url": file_path}

        @self.app.get("/download/{file_type}/{filename}")
        async def download_file(file_type: str, filename: str):
            if file_type not in ["images", "audio"]:
                raise HTTPException(status_code=400, detail="Invalid file type.")
            
            file_path = os.path.join("/media", file_type, filename)
                
            if not os.path.isfile(file_path):
                raise HTTPException(status_code=404, detail=f"File: {filename} not found")

            try:
                return FileResponse(file_path, filename=filename, media_type="application/octet-stream")
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error accessing file: {str(e)}")

        @staticmethod
        def is_valid(filename: str, allowed_extensions: List[str]) -> bool:
            return any(filename.lower().endswith(ext) for ext in allowed_extensions)

    def get_message(self):
        return self.data_manager.get_first_data()

    # def run_server(self):
    #     config = uvicorn.Config(self.server.get_app(), host="0.0.0.0", port=8080)
    #     server = uvicorn.Server(config)
    #     server.serve()

    def run_server(self):
        uvicorn.run(self.app, host="0.0.0.0", port=8080)

