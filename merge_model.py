"""Merge a completed PEFT LoRA adapter into its base model."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--adapter-dir", required=True)
    parser.add_argument("--output-dir", default="merged_model")
    args = parser.parse_args()
    adapter_dir = Path(args.adapter_dir)
    if not (adapter_dir / "adapter_config.json").exists():
        raise FileNotFoundError(f"Completed PEFT adapter not found: {adapter_dir / 'adapter_config.json'}")

    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    base = AutoModelForCausalLM.from_pretrained(args.base_model, torch_dtype="auto", device_map="auto")
    adapter = PeftModel.from_pretrained(base, adapter_dir)
    merged = adapter.merge_and_unload()
    output_dir = Path(args.output_dir)
    merged.save_pretrained(output_dir, safe_serialization=True)
    AutoTokenizer.from_pretrained(args.base_model).save_pretrained(output_dir)
    print(f"Merged model saved to {output_dir}")


if __name__ == "__main__":
    main()
