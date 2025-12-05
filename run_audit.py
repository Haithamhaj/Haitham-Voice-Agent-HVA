import asyncio
import logging
from haitham_voice_agent.intelligence.adaptive_sync import AdaptiveSync

logging.basicConfig(level=logging.INFO)

async def run_audit():
    print("🚀 Starting Digital Fingerprint Audit (SHA-256 Upgrade)...")
    sync = AdaptiveSync()
    stats = await sync.audit_fingerprints()
    print(f"✅ Audit Results: {stats}")

if __name__ == "__main__":
    asyncio.run(run_audit())
