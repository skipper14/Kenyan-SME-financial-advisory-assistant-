# Kenyan SME Financial Advisory Corpus

This directory contains 100 source-grounded LLaMA chat-format instruction-tuning examples for a microfinance institution serving Kenyan SMEs.

## Files

- `sme_financial_advisory.jsonl`: master corpus, 100 records
- `sme_financial_advisory_train.jsonl`: 80 records
- `sme_financial_advisory_validation.jsonl`: 10 records
- `sme_financial_advisory_test.jsonl`: 10 records
- `source_register.json`: official source URLs
- `validation_report.json`: generated quality and token-estimate report
- `curation_note.md`: sourcing, quality, safety, and coverage notes
- `build_dataset.py`: reproducible builder and validator
- `fine_tune.py`: documented QLoRA training entry point
- `analyze_run.py`: loss plot and healthy/overfit/underfit diagnosis
- `requirements-finetune.txt`: CUDA/Kaggle training dependencies

Each JSONL record uses `messages` with `system`, `user`, and `assistant` roles, plus a numbered metadata ID. Assistant answers include a source key that resolves through `source_register.json`.

Regenerate the corpus and report from this directory with:

```bash
python build_dataset.py
```

The token report uses a portable regex estimate over user and assistant content because this repository does not pin a tokenizer. Re-run validation with the exact tokenizer for the selected LLaMA base model before training.

## QLoRA Run

Run this in Kaggle or another CUDA-enabled environment. The base model must be permitted for your use and available through Hugging Face credentials or the platform's model storage.

```bash
pip install -r requirements-finetune.txt
python fine_tune.py --model-name meta-llama/Llama-3.2-3B-Instruct --output-dir run
python analyze_run.py run
```

The completed run should produce `run/trainer_state.json`, `run/hyperparameters.json`, `run/loss_curve.png`, and `run/loss_curve_analysis.md`. The analyzer fails when `trainer_state.json` is absent; no loss curve or diagnosis should be fabricated. The held-out test split is intentionally not used during training.
