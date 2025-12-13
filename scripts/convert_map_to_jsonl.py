import re
import json

INPUT_FILE = "data/haithm_v3_cognitive_map.md"
OUTPUT_FILE = "data/dataset_haithm_v3_cognitive_map.jsonl"

def parse_markdown_map(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    dataset = []
    
    # Track current section for context
    current_section = ""
    section_buffer = []
    
    # Mappings for Section Titles -> Instructions
    section_map = {
        "Identity": "من أنت؟ عرف عن هويتك ودورك.",
        "بطاقة تعريف": "من أنت؟ عرف عن هويتك ودورك.",
        "القيم": "ما هي قيمك وفلسفتك في العمل والحياة؟",
        "السلوك": "كيف تتصرف وتتخذ القرارات في العمل؟",
        "التواصل": "ما هو أسلوبك في التواصل والشرح؟",
        "DO / DON’T": "ما هي قواعد DO و DON'T التي تلتزم بها؟",
        "Boundaries": "ما هي حدودك الأخلاقية والمهنية؟",
        "الحدود": "ما هي حدودك الأخلاقية والمهنية؟"
    }

    qa_regex = re.compile(r"^\s*\*\s*س:\s*(.*?)\s*ج:\s*(.*)$")

    for line in lines:
        line = line.strip()
        if not line: continue

        # Check for Section Headers
        if line.startswith("#"):
            # Flush previous section buffer if any
            if current_section and section_buffer:
                full_text = "\n".join(section_buffer)
                dataset.append({
                    "instruction": section_map.get(current_section, f"تحدث عن {current_section}"),
                    "input": "",
                    "output": full_text
                })
                section_buffer = []
                current_section = ""

            # Check if this new header matches a known section
            for key in section_map:
                if key in line:
                    current_section = key
                    break
            continue

        # Check for Q&A Lines (The High Value Data)
        qa_match = qa_regex.match(line)
        if qa_match:
            q = qa_match.group(1).strip()
            a = qa_match.group(2).strip()
            dataset.append({
                "instruction": q,
                "input": "",
                "output": a
            })
            continue

        # If we are inside a known section and it's a bullet point, add to buffer
        if current_section and line.startswith("*"):
            section_buffer.append(line)

    # Flush last section
    if current_section and section_buffer:
        full_text = "\n".join(section_buffer)
        dataset.append({
            "instruction": section_map.get(current_section, f"تحدث عن {current_section}"),
            "input": "",
            "output": full_text
        })

    return dataset

def main():
    print(f"🔍 Reading {INPUT_FILE}...")
    try:
        data = parse_markdown_map(INPUT_FILE)
    except FileNotFoundError:
        print(f"❌ Error: File {INPUT_FILE} not found. Make sure you are in the project root.")
        return

    print(f"🧩 Extracted {len(data)} records from Cognitive Map.")
    
    if len(data) == 0:
        print("⚠️ Warning: No records extracted. Check the file format.")
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        for entry in data:
            json.dump(entry, f, ensure_ascii=False)
            f.write('\n')
            
    print(f"✅ Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
