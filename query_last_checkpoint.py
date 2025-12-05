import sqlite3
import json
from datetime import datetime

DB_PATH = "/Users/haitham/.hva/memory/hva_memory.db"

def get_last_checkpoint():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='checkpoints'")
        if not cursor.fetchone():
            print("Checkpoints table not found.")
            return

        cursor.execute("""
            SELECT id, timestamp, action_type, description, data 
            FROM checkpoints 
            ORDER BY timestamp DESC 
            LIMIT 1
        """)
        
        row = cursor.fetchone()
        if row:
            print(json.dumps({
                "id": row[0],
                "timestamp": row[1],
                "action_type": row[2],
                "description": row[3],
                "data": json.loads(row[4]) if row[4] else {}
            }, indent=2))
        else:
            print("No checkpoints found.")
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    get_last_checkpoint()
