"""QLoRA fine-tuning entry point for the Kenyan SME advisory corpus.

Recommended environment: a Kaggle GPU notebook with a permitted Hugging Face
base model and an access token configured as an environment secret. This file
never embeds credentials and refuses to train if the corpus is malformed.

Hyperparameters are explicit so an experiment is reproducible:
- MODEL_NAME: small instruct model chosen for a first feasibility run; pass a
  permitted model at the command line because license/access choices vary.
- MAX_LENGTH=512: enough for the current examples while bounding GPU memory.
- NUM_TRAIN_EPOCHS=3: a conservative first pass for only 80 training records.
- PER_DEVICE_TRAIN_BATCH_SIZE=2: fits a modest Kaggle GPU under 4-bit loading.
- GRADIENT_ACCUMULATION_STEPS=8: effective batch size 16 for stable updates.
- LEARNING_RATE=2e-4: common LoRA adapter learning rate; lower it if validation
  loss rises early or generations become repetitive.
- WARMUP_RATIO=0.10: gradual first 10 percent of updates for a tiny corpus.
- WEIGHT_DECAY=0.01: mild regularisation without suppressing adaptation.
- LORA_R=16, LORA_ALPHA=32, LORA_DROPOUT=0.05: moderate adapter capacity and
  regularisation for domain style without changing all base-model weights.
- 4-bit NF4, double quantisation, bfloat16 compute: reduces memory; the script
  falls back to float16 when the GPU does not support bfloat16.
- EVAL and save every epoch: only three checkpoints, with best model selected
  by validation loss so the held-out test split remains untouched.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

from datasets import load_dataset
from peft import LoraConfig, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

ROOT = Path(__file__).parent
SYSTEM = (
    "You are a Kenyan SME financial advisory assistant for a microfinance institution. "
    "Give practical, source-grounded general information, distinguish guidance from a credit decision, "
    "and tell the user to confirm current requirements with the relevant authority or lender. "
    "This is not legal, tax, or financial advice; do not diagnose, make binding legal judgments, "
    "promise approval or returns, or make a credit decision. Escalate high-stakes or uncertain matters "
    "to a qualified professional, the lender, or the relevant Kenyan authority."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-name", default=os.getenv("MODEL_NAME", "meta-llama/Llama-3.2-3B-Instruct"))
    parser.add_argument("--output-dir", default=str(ROOT / "run"))
    parser.add_argument("--epochs", type=float, default=3.0)
    parser.add_argument("--max-length", type=int, default=512)
    return parser.parse_args()


def assert_corpus(path: Path) -> None:
    records = [json.loads(line) for line in path.read_text().splitlines()]
    if len(records) != 80:
        raise ValueError(f"Training split must contain 80 records, found {len(records)}")
    for number, record in enumerate(records, start=1):
        roles = [message.get("role") for message in record.get("messages", [])]
        if roles != ["system", "user", "assistant"]:
            raise ValueError(f"Record {number} has invalid roles: {roles}")
        if record["messages"][0]["content"] != SYSTEM:
            raise ValueError(f"Record {number} has an unexpected system prompt")


def render_messages(messages: list[dict], tokenizer) -> str:
    return tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=False)


def main() -> None:
    args = parse_args()
    train_file = ROOT / "sme_financial_advisory_train.jsonl"
    validation_file = ROOT / "sme_financial_advisory_validation.jsonl"
    assert_corpus(train_file)
    if not validation_file.exists():
        raise FileNotFoundError(validation_file)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    tokenizer = AutoTokenizer.from_pretrained(args.model_name, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    raw = load_dataset("json", data_files={"train": str(train_file), "validation": str(validation_file)})

    def render(record: dict) -> dict:
        return {"text": render_messages(record["messages"], tokenizer)}

    rendered = raw.map(render, remove_columns=raw["train"].column_names)

    def tokenize(batch: dict) -> dict:
        return tokenizer(batch["text"], truncation=True, max_length=args.max_length)

    tokenized = rendered.map(tokenize, batched=True, remove_columns=["text"])
    use_bf16 = bool(getattr(__import__("torch"), "cuda", None) and __import__("torch").cuda.is_bf16_supported())
    compute_dtype = __import__("torch").bfloat16 if use_bf16 else __import__("torch").float16
    quantization = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
        bnb_4bit_compute_dtype=compute_dtype,
    )
    model = AutoModelForCausalLM.from_pretrained(args.model_name, quantization_config=quantization, device_map="auto")
    model.config.use_cache = False
    model = prepare_model_for_kbit_training(model)
    model.add_adapter(LoraConfig(
        r=16,
        lora_alpha=32,
        lora_dropout=0.05,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    ))

    training_args = TrainingArguments(
        output_dir=str(output_dir),
        num_train_epochs=args.epochs,
        per_device_train_batch_size=2,
        per_device_eval_batch_size=2,
        gradient_accumulation_steps=8,
        learning_rate=2e-4,
        warmup_ratio=0.10,
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        logging_strategy="steps",
        logging_steps=1,
        eval_strategy="epoch",
        save_strategy="epoch",
        save_total_limit=2,
        load_best_model_at_end=True,
        metric_for_best_model="eval_loss",
        greater_is_better=False,
        gradient_checkpointing=True,
        fp16=not use_bf16,
        bf16=use_bf16,
        report_to="none",
        seed=42,
        data_seed=42,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=tokenized["train"],
        eval_dataset=tokenized["validation"],
        data_collator=DataCollatorForLanguageModeling(tokenizer=tokenizer, mlm=False),
    )
    trainer.train()
    trainer.save_model(output_dir)
    tokenizer.save_pretrained(output_dir)
    trainer.save_state()
    (output_dir / "hyperparameters.json").write_text(json.dumps({
        "model_name": args.model_name,
        "max_length": args.max_length,
        "epochs": args.epochs,
        "per_device_train_batch_size": 2,
        "per_device_eval_batch_size": 2,
        "gradient_accumulation_steps": 8,
        "effective_batch_size": 16,
        "learning_rate": 2e-4,
        "warmup_ratio": 0.10,
        "weight_decay": 0.01,
        "lr_scheduler_type": "cosine",
        "lora_r": 16,
        "lora_alpha": 32,
        "lora_dropout": 0.05,
        "quantization": "4-bit NF4 with double quantisation",
        "seed": 42,
    }, indent=2) + "\n")


if __name__ == "__main__":
    main()
