
import os
import shutil
import hashlib
import json
import subprocess
from datetime import datetime

# --- CONFIGURATION ---
BASE_DIR = os.getcwd()
BUNDLE_ROOT = os.path.join(BASE_DIR, "v3_audit")
ZIP_NAME = "v3_audit_bundle.zip"

DIRS = [
    "repo_snapshot/hva_router",
    "repo_snapshot/hva_fallback",
    "repo_snapshot/hva_validation",
    "repo_snapshot/training_v2_5",
    "repo_snapshot/eval_v2_5",
    "data_snapshot/raw_clean_inputs",
    "data_snapshot/extra_found",
    "data_snapshot/raw_sources_samples",
    "reports"
]

def setup_dirs():
    if os.path.exists(BUNDLE_ROOT):
        shutil.rmtree(BUNDLE_ROOT)
    os.makedirs(BUNDLE_ROOT)
    for d in DIRS:
        os.makedirs(os.path.join(BUNDLE_ROOT, d))
    print("✅ Created directory structure.")

def copy_file(src, dest_folder):
    if os.path.exists(src):
        shutil.copy2(src, os.path.join(BUNDLE_ROOT, dest_folder))
        print(f"   Copied {os.path.basename(src)} -> {dest_folder}")
    else:
        print(f"⚠️ Warning: Source {src} not found.")

def get_file_info(filepath):
    """Returns dict with SHA256, bytes, lines, and samples."""
    info = {
        "filename": os.path.basename(filepath),
        "sha256": "N/A",
        "bytes": 0,
        "line_count": 0,
        "sample_lines": []
    }
    
    if os.path.exists(filepath):
        # Stats
        info["bytes"] = os.path.getsize(filepath)
        
        # SHA256 & Content
        sha256_hash = hashlib.sha256()
        lines = []
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        info["sha256"] = sha256_hash.hexdigest()
        
        # Line specific (text mode)
        try:
            with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                lines = f.readlines()
                info["line_count"] = len(lines)
                if lines:
                    info["sample_lines"] = [
                        lines[0].strip()[:100],
                        lines[len(lines)//2].strip()[:100],
                        lines[-1].strip()[:100]
                    ]
        except:
            pass
            
    return info

def create_bundle():
    print("🚀 Starting V3 Audit Bundle Creation...")
    setup_dirs()
    
    # --- A. REPO SNAPSHOT ---
    print("\n📦 [A] Exporting Repo Routing/Fallback/Validation...")
    # These are the files that handle routing, fallback, and validation
    copy_file("haitham_voice_agent/ollama_orchestrator.py", "repo_snapshot/hva_router")
    copy_file("haitham_voice_agent/dispatcher.py", "repo_snapshot/hva_router")
    
    copy_file("haitham_voice_agent/dispatcher.py", "repo_snapshot/hva_fallback")
    
    copy_file("haitham_voice_agent/ollama_orchestrator.py", "repo_snapshot/hva_validation")
    
    # Create Flow Report
    with open(os.path.join(BUNDLE_ROOT, "reports/hva_runtime_flow.md"), "w") as f:
        f.write("# HVA Runtime Flow Analysis\n\n")
        f.write("## 1. Schema Injection\n- Location: `OllamaOrchestrator._classify_with_ollama`\n- The System Prompt is injected with strict JSON schema instructions before every request.\n\n")
        f.write("## 2. Retries\n- Logic: `OllamaOrchestrator.classify_request`\n- Retry Count: 2 attempts on JSON parse failure.\n\n")
        f.write("## 3. Fallback Trigger\n- Location: `Dispatcher.dispatch`\n- If `OllamaOrchestrator` returns `None` or fails after retries, the Dispatcher falls back to `LLMRouter` (Cloud-based).\n\n")
        f.write("## 4. Error Handling\n- Errors are caught in `Dispatcher`, logged, and returned as a safe error message to the user.\n")

    # --- B. TRAINING ARTIFACTS ---
    print("\n🎓 [B] Exporting Training Artifacts...")
    copy_file("colab_notebooks/HVA_Finetune_V2_5_L4_Method2_Success.py", "repo_snapshot/training_v2_5")
    copy_file("scripts/evaluate_v2_5_full.py", "repo_snapshot/eval_v2_5")
    copy_file("scripts/evaluate_v2_5_deep.py", "repo_snapshot/eval_v2_5")

    # --- C. DATA INVENTORY ---
    print("\n📊 [C] Generating Data Inventory...")
    
    # Inventory Text
    inv_path = os.path.join(BUNDLE_ROOT, "reports/data_inventory.txt")
    with open(inv_path, "w") as f:
        f.write("=== LS LAH DATA ===\n")
        try:
            ls_out = subprocess.check_output("ls -lah data/", shell=True).decode()
            f.write(ls_out)
        except:
            f.write("Error running ls\n")
            
        f.write("\n=== WC -L JSONL ===\n")
        try:
            wc_out = subprocess.check_output("wc -l data/*.jsonl", shell=True).decode()
            f.write(wc_out)
        except:
             f.write("Error running wc\n")

    # Manifest Logic
    manifest = []
    
    # Define Core sets
    CORE_SETS = [
        "dataset_haithm_style_natural.jsonl",
        "dataset_haithm_style_prompts.jsonl",
        "dataset_haithm_persona_qa.jsonl",
        "dataset_haithm_cognitive_qa.jsonl"
    ]
    
    all_data_files = [f for f in os.listdir("data") if f.endswith(".jsonl")]
    
    print("   Processing datasets...")
    for filename in all_data_files:
        src_path = os.path.join("data", filename)
        info = get_file_info(src_path)
        manifest.append(info)
        
        if filename in CORE_SETS:
            copy_file(src_path, "data_snapshot/raw_clean_inputs")
        elif "raw" not in filename: # Don't copy huge raw files to extra unless small
            copy_file(src_path, "data_snapshot/extra_found")
            
    with open(os.path.join(BUNDLE_ROOT, "reports/data_manifest.json"), "w") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    # --- D. RAW SOURCES ---
    print("\n🕵️ [D] Handling Raw Sources...")
    RAW_FILES = [
        "data/haithm_corpus_raw_gpt_2025-12-11.jsonl",
        "data/haithm_corpus_whatsapp_haithm_only.jsonl"
    ]
    
    loc_report = "# Raw Source Data Locations\n\n"
    
    for rf in RAW_FILES:
        if os.path.exists(rf):
            dest_name = os.path.basename(rf) + "_head200.jsonl"
            dest_path = os.path.join(BUNDLE_ROOT, "data_snapshot/raw_sources_samples", dest_name)
            
            # Sample first 200 lines
            with open(rf, "r") as fin, open(dest_path, "w") as fout:
                for i, line in enumerate(fin):
                    if i < 200:
                        fout.write(line)
                    else:
                        break
            print(f"   Sampled 200 lines from {rf}")
            loc_report += f"- **File:** `{os.path.abspath(rf)}`\n"
        else:
            print(f"⚠️ Raw source not found: {rf}")
            loc_report += f"- **MISSING:** `{rf}`\n"
            
    with open(os.path.join(BUNDLE_ROOT, "reports/raw_sources_locations.md"), "w") as f:
        f.write(loc_report)

    # --- SUMMARY ---
    with open(os.path.join(BUNDLE_ROOT, "reports/summary.md"), "w") as f:
        f.write(f"# V3 Audit Bundle Summary\n\nGenerated: {datetime.now()}\n\n")
        f.write("This bundle contains snapshots of the V2.5/V3 transition state.\n")
        f.write("- **Repo Snapshot:** Router, Fallback, and Validation logic code.\n")
        f.write("- **Training:** V2.5 scripts and Full Evaluation tools.\n")
        f.write("- **Data:** Clean inputs, found extras, and samples of raw sources.\n")
        f.write("- **Reports:** Runtime flow, Data Manifest, and Inventory.\n")

    # --- ZIP ---
    print("\n🤐 Zipping Bundle...")
    shutil.make_archive("v3_audit_bundle", 'zip', BASE_DIR, "v3_audit")
    print(f"✅ Created: {ZIP_NAME}")
    
    # Cleanup
    shutil.rmtree(BUNDLE_ROOT)
    print("🧹 Cleaned up temp directory.")

if __name__ == "__main__":
    create_bundle()
