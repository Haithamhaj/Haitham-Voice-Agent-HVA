# 🚀 V3 Implementation Plan: The Synthetic Shift
**Objective:** Train Qwen 2.5 3B to be a *Reliable Agent* (Haitham Identity + Strict JSON), not just a *Chatbot*.

## 1. The Core Lesson from V2.5 Failure
**"Volume implies Importance."**
In V2.5, we had ~6000 lines of "Natural Chat" vs ~20 lines of "Persona Instructions". The model learned the chat style but ignored the instructions because they were statistically insignificant.

**The Fix:** We must artificially amplify the "Instruction" signal using **Synthetic Data**.

---

## 2. The V3 Strategy: "Synthetic Dominance"

We will build a new dataset (`dataset_v3_synthetic.jsonl`) containing **1,000+ generated examples** covering 3 critical pillars:

### Pillar A: Identity Reinforcement (300 Samples)
**Goal:** Kill the "Assistant" persona.
*   **Technique:** "Who are you?" questions with varied phrasing.
*   **Target Output:** "أنا هيثم" / "أنا نسختك الرقمية". Never "Assistant".
*   **Format:**
    *   User: "عرف عن نفسك."
    *   Assistant: "أنا نسختك الرقمية، موجود عشان أساعدك تشتغل بذكاء."

### Pillar B: JSON Iron-Fist (400 Samples)
**Goal:** Zero Hallucination.
*   **Technique:** Valid Command -> Valid JSON.
*   **Target Output:** Strict JSON only.
*   **Edge Cases:**
    *   "سكر الجهاز" -> `{"action": "system_shutdown", "target": "device"}`
    *   "افتح ملف مدري وينه" -> `{"action": "search_file", "target": "unknown", "query": "مدري وينه"}`
*   **Negative Samples:** examples where the user asks for JSON and the model *refuses* to give text explanations.

### Pillar C: Anti-Fluff & Style (300 Samples)
**Goal:** Truth-First, No Emojis, No Repetition.
*   **Technique:** Direct questions -> Direct answers.
*   **Correction Pairs:**
    *   User: "ليش الشركة خسرت؟"
    *   Bad Response (Fluff): "سؤال رائع! الشركات تخسر لأسباب..."
    *   Good Response (V3): "لأنها ركزت على المنتج ونسيت العميل."

---

## 3. Data Generation Pipeline (Automated)

We will not write 1000 examples by hand. We will use a script (`scripts/generate_v3_data.py`) that uses **GPT-4o / Gemini** to generate them:

1.  **Define Templates:** Create 20-30 scenario templates.
2.  **Generate Variations:** Use LLM to generate 50 variations for each template.
3.  **Validate:** Auto-check JSON syntax of generated data.

---

## 4. Training Configuration (Refined)

*   **Base Model:** Qwen 2.5 3B Instruct.
*   **Method:** QLoRA (Rank 64 - Higher capacity for new logic).
*   **Mix Ratio:**
    *   Synthetic Data (High Quality): **50%**
    *   Natural Chat (V2 - Filtered): **30%** (To keep the "Human" touch).
    *   Cognitive Map (V3): **20%**.

---

## 5. Execution Roadmap

### Phase 1: Data Fabrication (2 Days)
- [ ] Create `scripts/generate_v3_data.py`.
- [ ] Generate 1000 synthetic samples.
- [ ] Validate and clean dataset.

### Phase 2: Mixing & Training (1 Day)
- [ ] Merge Synthetic + Natural (Filtered).
- [ ] Run Training on Colab L4 (Batch 1, Accum 32).

### Phase 3: The "Deep Diagnostic" Check (1 Day)
- [ ] Run `evaluate_v2_5_deep.py` (renamed to V3) *before* celebrating.
- [ ] Expect 0% JSON errors.

---

## 6. Immediate Action
**Shall we generate the first batch of Synthetic Data now?**
