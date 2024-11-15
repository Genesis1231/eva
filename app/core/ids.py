import sqlite3
from config import logger
from pathlib import Path
from typing import Dict

class IDManager:
    """ Manage the ID of the EVA """
    
    def __init__(self):
        self._pid_list, self._void_list, self._id_list = self._initialize_database()
    
    def get_pid_list(self) -> Dict:
        """ Get the pid list """
        return self._pid_list
            
    def get_void_list(self) -> Dict:
        """ Get the void list """
        return self._void_list
    
    def is_empty(self) -> bool:
        """ Check if the ID manager is empty """
        return len(self._id_list) == 0
    
    def _initialize_database(self):
        """ Initialize the database and create the voice id table """
        
        db_path = self._get_database_path()
        
        with sqlite3.connect(db_path) as conn:
            conn.row_factory = sqlite3.Row  # Enable dictionary-like row access
            cursor = conn.cursor()

            try:
                cursor.execute(f'SELECT user_name, void, pid FROM ids;')
                rows = cursor.fetchall()
                
                # Create main mapping and reverse mappings
                pid_list = {row["pid"]: row["user_name"] for row in rows if row["pid"]}
                void_list = {row["void"]: row["user_name"] for row in rows if row["void"]}
                id_list = {row["user_name"]: {"void": row["void"], "pid": row["pid"]} for row in rows}
                return pid_list, void_list, id_list

            except sqlite3.Error as e:
                # If table doesn't exist, create it and return an empty list
                logger.error(f"Failed to initialize ID manager: {str(e)}")
                self._create_table(conn)
                return {}

    @staticmethod
    def _create_table(conn)-> None:    
        """ Create a new voiceid table """
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ids (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_name TEXT NOT NULL
                void TEXT,
                pid TEXT
            )
        ''')
        conn.commit()
        
        # cursor = conn.cursor()
        # cursor.execute(f'''
        #     INSERT INTO ids (void, user_name) VALUES (?, ?);
        # ''', ('V000001', 'Initial User'))
        # conn.commit()

    @staticmethod
    def _get_database_path() -> str:
        """Return the path to the memory log database."""
        return Path(__file__).resolve().parents[1] / 'data' / 'database' / 'eva.db'

id_manager = IDManager()
