"""Create a loss plot and evidence-based run diagnosis from trainer_state.json."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_dir", nargs="?", default="run")
    args = parser.parse_args()
    run_dir = Path(args.run_dir)
    state_path = run_dir / "trainer_state.json"
    if not state_path.exists():
        raise FileNotFoundError(f"Completed run required: {state_path}")
    state = json.loads(state_path.read_text())
    history = state.get("log_history", [])
    train = [(row["step"], row["loss"]) for row in history if "loss" in row]
    evaluation = [(row["step"], row["eval_loss"]) for row in history if "eval_loss" in row]
    if not train or not evaluation:
        raise ValueError("trainer_state.json must contain both training loss and eval_loss entries")

    import matplotlib.pyplot as plt

    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(*zip(*train), label="training loss", marker="o", linewidth=1.5)
    axis.plot(*zip(*evaluation), label="validation loss", marker="o", linewidth=2)
    axis.set_title("Kenyan SME advisory QLoRA loss progression")
    axis.set_xlabel("Update step")
    axis.set_ylabel("Loss")
    axis.grid(alpha=0.25)
    axis.legend()
    figure.tight_layout()
    figure.savefig(run_dir / "loss_curve.png", dpi=160)
    plt.close(figure)

    first_eval = evaluation[0][1]
    best_eval = min(value for _, value in evaluation)
    final_eval = evaluation[-1][1]
    final_train = train[-1][1]
    gap = final_eval - final_train
    if final_eval > first_eval * 1.10 and final_train < first_eval:
        diagnosis = "overfit"
        rationale = "Training loss improved while validation loss increased materially from its first evaluation."
    elif final_train > min(value for _, value in train) * 1.10 and final_eval > best_eval * 1.10:
        diagnosis = "underfit"
        rationale = "Both training and validation losses remain elevated or worsen, suggesting insufficient adaptation."
    else:
        diagnosis = "healthy"
        rationale = "Validation loss is stable or improving without a material divergence from training loss."
    report = f"""# Loss Curve Analysis

- Diagnosis: **{diagnosis}**
- Rationale: {rationale}
- First validation loss: `{first_eval:.4f}`
- Best validation loss: `{best_eval:.4f}`
- Final validation loss: `{final_eval:.4f}`
- Final training loss: `{final_train:.4f}`
- Final validation minus training loss: `{gap:.4f}`
- Plot: `loss_curve.png`

This diagnosis is based only on the recorded loss progression. It is not a substitute for the held-out test evaluation, safety tests, source-grounding tests, or human SME/compliance review. With only 10 validation examples, small changes should be interpreted cautiously.
"""
    (run_dir / "loss_curve_analysis.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
