import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.getcwd())

from haitham_voice_agent.tools.system_sentry import SystemSentry

async def main():
    print("Initializing SystemSentry...")
    try:
        sentry = SystemSentry()
        print("Running check_health()...")
        health = await sentry.check_health()
        print(f"Health Result: {health}")
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
