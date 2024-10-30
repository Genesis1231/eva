import os
from config import logger
import sqlite3
import json

from typing import List, Dict, Optional, Any
from utils.agent import SmallAgent


class Memory:
    def __init__(self, model_name: str, base_url: str):
        self._dblink: str = os.path.join(os.getcwd(), "data", "database", "eva.db")
        self._session_memory: List[Dict] = []
        
        self.summarizer = SmallAgent(model_name=model_name, base_url=base_url, model_temperature=0)
        self._initialize_log()
    
    def _initialize_log(self) -> None:
        """ Initialize the memory log database. """
        
        with sqlite3.connect(self._dblink) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS memorylog (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    time TEXT NOT NULL,
                    user_name TEXT,
                    user_message TEXT,
                    eva_message TEXT,
                    observation TEXT,
                    analysis TEXT,
                    strategy TEXT,
                    premeditation TEXT,
                    action TEXT
                )
            ''')
            conn.commit()

    def create_memory(self, timestamp: str, user_response: Dict, response: Dict) -> None:
        """
        Create a single entry of memory. timestamp, user_name, user_message, speech, sight, analysis, strategy, expectation
        save it to the database and if the conversation is more than 10, summarize them.
        """
        
        # split the user message into user_name and user_message
        user_name = None
        if user_message := user_response.get("user_message"):
            message_parts = user_message.split(":: ", 1)
            if len(message_parts) > 1:
                user_name = message_parts[0]
        
        observation = user_response.get("observation")
        eva_message = response.get("response")
        action = response.get("action")
        analysis = response.get("analysis")
        strategy = response.get("strategy")
        premeditation = response.get("premeditation")      
        
        entry = {
            "time": timestamp,
            "user_name": user_name,
            "user_message": user_message,
            "eva_message": eva_message,
            "observation": observation,
            "analysis": analysis,
            "strategy": strategy,
            "premeditation": premeditation,
            "action": action
        }
        
        self.save_memory_to_db(entry)
        self._session_memory.append(entry)
        
        if len(self._session_memory) > 10:
            summary_entry = self._pack_memory()
            self._session_memory = self._session_memory[5:]
            self._session_memory.insert(0, summary_entry)
            
    def _pack_memory(self) -> List[Dict]:
        """pack the first 5 memory for summarization"""
        chat_memory = []
        for entry in self._session_memory[:5]:
            if entry["user_message"] is not None:
                chat_memory.append(f"{entry['user_name']}: {entry['user_message']}")
            chat_memory.append(f"EVA01: {entry['eva_message']}")
        
        # summarize the chat_memory by calling the summarizer
        summary = self.summarizer.generate(template="summarize", conversation="\n".join(chat_memory))
        
        return {
            "time": self._session_memory[0].get("timestamp"),
            "user_name": None,
            "user_message": None,
            "eva_message": summary,
            "strategy": None,
            "premeditation": None
        }
        
    def save_memory_to_db(self, memory: Dict) -> None:
        """Save a single memory entry to the SQLite database."""
        try:
            with sqlite3.connect(self._dblink) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO memorylog (time, user_name, user_message, eva_message, observation, analysis, strategy, premeditation, action)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (memory["time"], memory["user_name"], memory["user_message"], memory["eva_message"], 
                    memory["observation"], memory["analysis"], memory["strategy"], memory["premeditation"], json.dumps(memory["action"])))
                conn.commit()
                
        except Exception as e:
            logger.error(f"Error: Failed to save memory to database: {str(e)}")
        finally:
            conn.close()  
            
        logger.info(f"Memory: Entry created at { memory['time'] }")
        
    def remember(self, time: str = None) -> Optional[Dict]:
        """Return a single entry of memory."""
        for memory in self._session_memory:
            if memory["time"] == time:
                return memory

        return None

    def recall_conversation(self) -> Optional[List[Dict]]:
        """Return only the conversation between user and eva."""
        if not self._session_memory:
            return None
        
        conversation = []
        for entry in self._session_memory:
            conversation.append({
                "user_name": entry["user_name"],
                "user_message": entry["user_message"],
                "eva_message": entry["eva_message"],
            })
        
        # add the premeditation to the last entry
        conversation[-1]["premeditation"] = self._session_memory[-1].get("premeditation")
        
        return conversation

    def __len__(self) -> int:
        return len(self._session_memory)
        

    