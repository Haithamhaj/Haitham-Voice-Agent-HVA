import asyncio
import aiosqlite
from pathlib import Path

DB_PATH = Path.home() / ".hva" / "memory" / "hva_memory.db"

async def reset_pricing():
    if not DB_PATH.exists():
        print(f"❌ Database not found at {DB_PATH}")
        return

    print(f"🔄 Connecting to database at {DB_PATH}...")
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            # Clear token_usage table
            await db.execute("DELETE FROM token_usage")
            await db.commit()
            print("✅ Successfully cleared 'token_usage' table.")
            
            # Verify
            async with db.execute("SELECT COUNT(*) FROM token_usage") as cursor:
                count = await cursor.fetchone()
                print(f"📊 Remaining records: {count[0]}")
                
    except Exception as e:
        print(f"❌ Error resetting pricing data: {e}")

if __name__ == "__main__":
    asyncio.run(reset_pricing())
