import os
from config import logger
import sqlite3
from typing import Type, Dict

from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_community.tools import BaseTool
 

class VoidInput(BaseModel):
    speaker_id: str = Field(description="Input for Void tool, Only input the speaker ID.")
    name: str = Field(description="Input for Void tool, Only input the speaker's name. ")
    
class Void(BaseTool):
    """Tool for identify the speaker"""
    name: str = "voice_register"
    description: str = "Tool for registering the unknown speaker, requires his/her real name and speaker ID."
    type: str = "conversational"
    client: str = "None"
    args_schema: Type[BaseModel] = VoidInput
    
    def _run(
        self,
        speaker_id: str,
        name: str
    ) -> Dict:
        if not name or "unknown" in name.lower():
            return {"error": "Speaker name cannot be unknown, Please ask for speaker's name."}
        
        if not speaker_id or len(speaker_id) != 8:
            return {"error": "Speaker ID is not valid, unable to register the speaker."}
        
        dblink = os.path.join(os.getcwd(), "data", "database", "eva.db")
        logger.info(f"Void tool: saving {speaker_id} as {name}")
        try:
            with sqlite3.connect(dblink) as conn:
                cursor = conn.cursor()
            cursor.execute(f'''
                INSERT INTO ids (void, user_name) VALUES (?, ?);
            ''', (speaker_id, name)
            )
            conn.commit()
        except Exception as e:
            logger.error(f"Error: Failed to connect to database: {str(e)}")

        return {}

