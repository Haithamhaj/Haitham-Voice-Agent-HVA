# Training Run Bundle: hs-20251213-v2.5-colab-l4-bulletproof (AUDIT READY)

This bundle contains the code and data instructions for reproducing the fine-tuning run `hs-20251213-v2.5`.

## Contents

- `code/`: Contains the Jupyter notebook `haithm_style_qwen3b_qlora_colab.ipynb` patched with:
    - **Clean Data Loading**: Configured to load cleaned datasets (free of `filecite`, `turn0file`, `[STATE:]`).
    - **Audit Export**: Automatically exports `train_used.jsonl` and `val_used.jsonl` before training starts.
- `data/raw/`: Original raw datasets (for reference).
- `manifest/`: Hashes of raw files.

## How to Run in Google Colab

1.  **Prepare Data**:
    - Locate the **Cleaned Datasets** (e.g., from `Data training V3/clean_remove_state/`).
    - Upload these 5 JSONL files to the root of your Colab runtime.
      - `dataset_haithm_style_natural_v2.jsonl`
      - `dataset_haithm_style_prompts.jsonl`
      - `dataset_haithm_style_persona_v2.jsonl`
      - `dataset_haithm_style_cognitive_v2.jsonl`
      - `dataset_haithm_v3_cognitive_map.jsonl`

2.  **Run Notebook**:
    - Upload `code/haithm_style_qwen3b_qlora_colab.ipynb`.
    - Run all cells.

## Audit Output

The notebook will create a folder `/content/run_audit/hs-20251213-v2.5/` containing:
- `train_used.jsonl`: The exact training data seen by the model.
- `val_used.jsonl`: The exact validation data.
- `manifest_used.json`: Cryptographic hashes of inputs and outputs.

You should download this folder to verify that no artifacts (like `filecite` or `[STATE:]`) leaked into the training set.
