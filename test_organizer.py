import asyncio
import logging
import shutil
import time
from pathlib import Path
from datetime import datetime, timedelta
from haitham_voice_agent.tools.smart_organizer import get_organizer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_smart_organizer():
    print("\n--- Starting Smart Organizer Verification ---\n")
    
    organizer = get_organizer()
    downloads_dir = organizer.downloads
    documents_dir = organizer.documents
    
    # Ensure directories exist
    downloads_dir.mkdir(exist_ok=True)
    documents_dir.mkdir(exist_ok=True)
    
    # 1. Create Dummy Files
    print("Creating dummy files...")
    
    # Old File (Should be moved) - Financial content
    old_file = downloads_dir / "old_invoice.txt"
    old_file.write_text("INVOICE #12345\nAmount: $500.00\nDate: 2023-01-01\nService: Consulting")
    
    # Modify mtime to be 4 days ago
    four_days_ago = time.time() - (4 * 24 * 3600)
    os.utime(old_file, (four_days_ago, four_days_ago))
    print(f"Created old file: {old_file} (4 days old)")
    
    # New File (Should stay)
    new_file = downloads_dir / "new_notes.txt"
    new_file.write_text("Meeting notes for today.\nTopic: AI Agents.")
    print(f"Created new file: {new_file} (Just now)")
    
    # 2. Run Organizer
    print("\nRunning organize_old_downloads(hours=72)...")
    report = await organizer.organize_old_downloads(hours=72)
    print("Report:", report)
    
    # 3. Verify Results
    print("\nVerifying results...")
    
    # Check Old File
    # It should be moved to Documents/Financials (or similar)
    # We search in Documents recursively
    found_old = False
    for path in documents_dir.rglob("old_invoice.txt"):
        print(f"SUCCESS: Found old file at: {path}")
        found_old = True
        # Check category folder
        parent = path.parent.name
        print(f"Category Folder: {parent}")
        if parent not in ["Downloads", "Documents"]: # Should be a category name
             print("Category seems valid.")
        break
        
    if not found_old:
        print("FAILURE: Old file not found in Documents.")
        
    # Check New File
    if new_file.exists():
        print("SUCCESS: New file remains in Downloads.")
    else:
        print("FAILURE: New file was moved!")

    # Cleanup
    if new_file.exists(): new_file.unlink()
    if found_old: path.unlink()
    # Remove category folder if empty?
    
    print("\n--- Verification Complete ---")

import os
if __name__ == "__main__":
    asyncio.run(test_smart_organizer())
