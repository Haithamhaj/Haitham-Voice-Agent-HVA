# Haithm Style Finetuning Runs

This guide explains how to run the fine-tuning workflow to train Qwen 3B on Haithm's writing style.

## 1. Quick Data Check
Before any run, verify the dataset status:
```bash
python scripts/analyze_haithm_style_dataset.py
```

## 2. Start a Local Training Run
Ensure you have a GPU available (MPS on Mac is supported by PyTorch but QLoRA/bitsandbytes support varies. CUDA is recommended).

**Command:**
```bash
python finetune/haithm_style/train_haithm_style_qwen3b.py \
  --config finetune/haithm_style/config_style.yaml \
  --run-id hs-$(date +%Y%m%d-%H%M)
```
*Note: Replace `$(date ...)` with a manual ID like `hs-20251211-1200` if on Windows.*

## 3. Training on Google Colab
If you don't have a strong local GPU, use the provided notebook:

1. Open [Google Colab](https://colab.research.google.com/).
2. Upload `finetune/haithm_style/haithm_style_qwen3b_qlora_colab.ipynb`.
3. In the Files sidebar, upload your datasets:
   - `data/dataset_haithm_style_natural.jsonl`
   - `data/dataset_haithm_style_prompts.jsonl`
4. Run all cells.
5. Download the resulting `qwen-3b-haithm-style-lora.zip`.

## 4. Run Registry
All local runs are automatically logged to:
- `finetune/haithm_style/runs.json`

## Future Integration Ideas
Once a model is trained (`adapter_model.bin` + `config.json`):
1. **Ollama Integration**: Create a Modelfile that layers this adapter over `qwen2.5:3b`.
3. **Inference: Base vs Haithm-V1**
   To qualitatively test the model:
   ```bash
   python finetune/haithm_style/infer_haithm_style_qwen3b.py \
     --prompt "Write a short paragraph about why I use AI in my projects."
   ```

4. **UI Integration**
   The fine-tuned model is now integrated into the **Finetune Lab**.
   - **Endpoint**: `POST /finetune/style-compare`
   - **Function**: Compares Base vs Fine-Tuned (Haithm V1) side-by-side.
   - **Status**: The UI will show "Haithm-V1 (LoRA)" as available if the adapter exists on disk.

## 5. Experiment Log

### Run hs-20251211-v1-text-only – V1 Text-Only Natural Style (Sanity Check)

- **Date**: 2025-12-11
- **Status**: COMPLETED
- **Dataset**: Natural style only (~6170 samples)
- **Base Model**: Qwen/Qwen2.5-3B-Instruct
- **Output Dir**: `models/hva_haithm_style_lora_hs-20251211-v1-text-only`

#### Configuration
- **Max Steps**: 30 (Sanity Check)
- **Batch Size**: 2
- **Learning Rate**: 2e-4
- **Max Length**: 1024
- **Hardware**: macOS (MPS) - Full FP16 (no quantization)

#### Results
- **Final Loss**: ~2.16
- **Training Time**: ~5.5 mins
- **Notes**: 
  - Ran as a short sanity check to verify pipeline.
  - Used `adamw_torch` optimizer and disabled `bitsandbytes` due to macOS limitations.
  - `trl` v0.26 compatibility fixes applied (`SFTConfig`, `processing_class`).
