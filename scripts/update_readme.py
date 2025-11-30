#!/usr/bin/env python3
"""
Auto-update README.md based on codebase changes
Uses GPT to intelligently update relevant sections
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def get_project_structure():
    """Get current project structure"""
    structure = []
    
    # Scan haitham_voice_agent directory
    hva_dir = project_root / "haitham_voice_agent"
    
    for root, dirs, files in os.walk(hva_dir):
        # Skip __pycache__ and .pyc files
        dirs[:] = [d for d in dirs if d != '__pycache__']
        files = [f for f in files if f.endswith('.py') and not f.startswith('__')]
        
        if files:
            rel_path = Path(root).relative_to(project_root)
            structure.append({
                'path': str(rel_path),
                'files': files
            })
    
    return structure

def get_recent_changes():
    """Get recent git changes"""
    import subprocess
    
    try:
        # Get last commit message
        result = subprocess.run(
            ['git', 'log', '-1', '--pretty=%B'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        last_commit = result.stdout.strip()
        
        # Get changed files
        result = subprocess.run(
            ['git', 'diff', '--name-only', 'HEAD~1', 'HEAD'],
            capture_output=True,
            text=True,
            cwd=project_root
        )
        changed_files = result.stdout.strip().split('\n')
        
        return {
            'last_commit': last_commit,
            'changed_files': [f for f in changed_files if f]
        }
    except Exception as e:
        print(f"Error getting git changes: {e}")
        return None

def update_readme_with_gpt(changes):
    """Use GPT to suggest README updates"""
    try:
        import openai
        
        client = openai.OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        
        # Read current README
        readme_path = project_root / 'README.md'
        current_readme = readme_path.read_text(encoding='utf-8')
        
        prompt = f"""You are updating a README.md file for a voice agent project.

Recent changes:
- Commit: {changes['last_commit']}
- Changed files: {', '.join(changes['changed_files'])}

Current README sections that might need updating:
1. Voice Control System (STT/TTS)
2. Project Structure
3. Prerequisites
4. Features

Based on the changes, suggest MINIMAL updates to README. Only update if there's a significant change.
If no update needed, return "NO_UPDATE".

Return your response in this format:
SECTION: [section name]
UPDATE: [specific update text]

Or just:
NO_UPDATE
"""
        
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a technical documentation expert."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        suggestion = response.choices[0].message.content.strip()
        
        if suggestion == "NO_UPDATE":
            print("✅ No README updates needed")
            return False
        
        print(f"📝 Suggested updates:\n{suggestion}")
        
        # For now, just log suggestions
        # In production, you'd parse and apply them
        return False
        
    except Exception as e:
        print(f"Error updating README: {e}")
        return False

def main():
    print("=" * 60)
    print("README Auto-Update Script")
    print("=" * 60)
    
    # Get recent changes
    changes = get_recent_changes()
    
    if not changes:
        print("⚠️  Could not get git changes")
        return
    
    print(f"\n📝 Last commit: {changes['last_commit']}")
    print(f"📁 Changed files: {len(changes['changed_files'])}")
    
    # Check if README update is needed
    if 'README.md' in changes['changed_files']:
        print("✅ README was already updated in this commit")
        return
    
    # Check if any Python files changed
    py_changes = [f for f in changes['changed_files'] if f.endswith('.py')]
    
    if not py_changes:
        print("✅ No Python files changed, README likely up-to-date")
        return
    
    print(f"\n🔍 Analyzing {len(py_changes)} Python file changes...")
    
    # Use GPT to suggest updates
    updated = update_readme_with_gpt(changes)
    
    if updated:
        print("\n✅ README updated successfully")
    else:
        print("\n✅ No README updates needed")

if __name__ == "__main__":
    main()
