#!/usr/bin/env python3
"""
Enhanced Auto-update README.md
Scans the codebase, extracts docstrings, and intelligently updates the README.
"""

import os
import sys
import re
import ast
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from haitham_voice_agent.llm_router import LLMRouter

def scan_codebase(root_dir: Path) -> List[Dict[str, Any]]:
    """Scan codebase for Python modules and extract docstrings"""
    modules = []
    
    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):
                path = Path(root) / file
                rel_path = path.relative_to(project_root)
                
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        content = f.read()
                        
                    # Parse AST to get docstring and classes/functions
                    tree = ast.parse(content)
                    docstring = ast.get_docstring(tree)
                    
                    classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
                    functions = [node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) if not node.name.startswith("_")]
                    
                    modules.append({
                        "path": str(rel_path),
                        "name": file,
                        "docstring": docstring or "No description",
                        "classes": classes,
                        "functions": functions[:5] # Top 5 functions
                    })
                except Exception as e:
                    print(f"Error parsing {rel_path}: {e}")
                    
    return modules

async def update_readme():
    print("🔍 Scanning codebase...")
    modules = scan_codebase(project_root / "haitham_voice_agent")
    
    # Prepare context for LLM
    modules_summary = "\n".join([
        f"- **{m['path']}**\n  Description: {m['docstring']}\n  Classes: {', '.join(m['classes'])}\n  Functions: {', '.join(m['functions'])}"
        for m in modules
    ])
    
    print(f"✅ Found {len(modules)} modules.")
    
    readme_path = project_root / "README.md"
    current_readme = readme_path.read_text(encoding="utf-8")
    
    prompt = f"""
    You are an expert technical writer maintaining the README.md for the Haitham Voice Agent (HVA) project.
    
    **GOAL**: Update the README.md to reflect the current state of the codebase.
    
    **CURRENT CODEBASE STATE**:
    {modules_summary}
    
    **CURRENT README CONTENT**:
    {current_readme}
    
    **INSTRUCTIONS**:
    1. Analyze the "Modules & Tools" section. Does it include all the new modules (e.g., secretary.py, advisor.py, memory/graph_store.py, gui_process.py)?
    2. Analyze the "Key Features" section. Does it reflect the capabilities of these new modules?
    3. Analyze the "Usage" section. Does it mention the new 'HVA.app' or 'Start HVA.command'?
    
    **OUTPUT**:
    Return the FULL updated README.md content. 
    - Keep the existing bilingual format (Arabic | English) where possible, or add English descriptions if Arabic translation is difficult.
    - Ensure the "Project Structure" tree is accurate.
    - Ensure "Executive Secretary", "Honest Advisor", and "Living Memory" are well-documented.
    """
    
    print("🤖 Asking LLM to generate updates (this may take a moment)...")
    
    # Use LLMRouter (Gemini) for this heavy lifting
    router = LLMRouter()
    updated_content = await router.generate_with_gemini(prompt)
    
    # Clean up response (remove markdown code blocks if present)
    updated_content = re.sub(r'^```markdown\s*', '', updated_content)
    updated_content = re.sub(r'^```\s*', '', updated_content)
    updated_content = re.sub(r'\s*```$', '', updated_content)
    
    if len(updated_content) < len(current_readme) * 0.5:
        print("⚠️  Safety check failed: Generated content is too short.")
        return
        
    # Backup
    backup_path = readme_path.with_suffix(".md.bak")
    readme_path.rename(backup_path)
    
    # Write new
    readme_path.write_text(updated_content, encoding="utf-8")
    print(f"✅ README.md updated successfully! Backup saved to {backup_path.name}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(update_readme())
