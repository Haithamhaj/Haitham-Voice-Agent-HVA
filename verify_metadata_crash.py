import sys
import os

# Ensure project root is in path
sys.path.append(os.getcwd())

from finetune.haithm_style.infer_haithm_style_core import chat_with_model

def test_metadata_crash():
    print("Testing chat with metadata in history...")
    
    # Simulate history from frontend
    history = [
        {"role": "user", "content": "hello"},
        {
            "role": "assistant", 
            "content": "Hi there", 
            "metadata": {"duration": 1.2, "model": "base"} # Extra field
        },
        {"role": "user", "content": "How are you?"}
    ]
    
    try:
        res = chat_with_model(messages=history, mode="base")
        print("Success:", res)
    except Exception as e:
        print("CRASHED as expected:", e)
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_metadata_crash()
