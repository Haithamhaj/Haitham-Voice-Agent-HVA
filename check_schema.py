import sqlite3

DB_PATH = "/Users/haitham/.hva/memory/hva_memory.db"

def check_schema():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(checkpoints)")
        columns = cursor.fetchall()
        
        print("Columns in checkpoints table:")
        for col in columns:
            print(col)
            
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_schema()
