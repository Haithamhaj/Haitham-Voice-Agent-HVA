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
    Migrate the SQLite database to v1.2
    Adds 'nag_count' column to 'memories' table.
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
        
        # Add 'nag_count' column
        if "nag_count" not in columns:
            logger.info("Adding 'nag_count' column...")
            cursor.execute("ALTER TABLE memories ADD COLUMN nag_count INTEGER DEFAULT 0")
            logger.info("'nag_count' column added.")
        else:
            logger.info("'nag_count' column already exists.")
            
        conn.commit()
        conn.close()
        logger.info("Migration v1.2 completed successfully.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    migrate_db()
