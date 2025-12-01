import sqlite3
import logging
from pathlib import Path
import sys

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_PATH = Path.home() / ".hva" / "memory" / "hva_memory.db"

def migrate_db():
    """
    Migrate the SQLite database to v1.1
    Adds 'status' and 'structured_data' columns to 'memories' table.
    """
    if not DB_PATH.exists():
        logger.error(f"Database not found at {DB_PATH}")
        return

    logger.info(f"Connecting to database at {DB_PATH}")
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check existing columns
        cursor.execute("PRAGMA table_info(memories)")
        columns = [info[1] for info in cursor.fetchall()]
        
        # 1. Add 'status' column
        if "status" not in columns:
            logger.info("Adding 'status' column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN status TEXT DEFAULT 'active'")
            logger.info("'status' column added.")
        else:
            logger.info("'status' column already exists.")
            
        # 2. Add 'structured_data' column
        if "structured_data" not in columns:
            logger.info("Adding 'structured_data' column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN structured_data TEXT")
            logger.info("'structured_data' column added.")
        else:
            logger.info("'structured_data' column already exists.")
            
        conn.commit()
        conn.close()
        logger.info("Migration completed successfully.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_db()
