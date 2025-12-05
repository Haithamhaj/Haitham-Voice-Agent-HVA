import asyncio
import aiosqlite
from pathlib import Path

DB_PATH = Path.home() / ".hva" / "memory" / "hva_memory.db"

async def check_memory():
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return

    print(f"🔄 Connecting to {DB_PATH}...")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Check File Index
            async with db.execute("SELECT COUNT(*) FROM file_index") as cursor:
                count = await cursor.fetchone()
                print(f"📂 Indexed Files: {count[0]}")
                
            # Check recent entries
            async with db.execute("SELECT path, project_id FROM file_index ORDER BY last_modified DESC LIMIT 5") as cursor:
                rows = await cursor.fetchall()
                if rows:
                    print("\n📝 Recent Files:")
                    for row in rows:
                        print(f"  - {row[0]} (Project: {row[1]})")
                else:
                    print("\n⚠️ No files found in index.")

            # Check Token Usage
            print("\n💰 Recent Token Usage:")
            async with db.execute("SELECT timestamp, model, cost FROM token_usage ORDER BY id DESC LIMIT 5") as cursor:
                rows = await cursor.fetchall()
                if rows:
                    for row in rows:
                        print(f"  - {row[0]}: {row[1]} (${row[2]:.4f})")
                else:
                    print("  No usage recorded.")

    except Exception as e:
        print(f"❌ Error checking memory: {e}")

if __name__ == "__main__":
    asyncio.run(check_memory())
