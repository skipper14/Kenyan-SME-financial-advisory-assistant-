# Recommendation for the SME Finance Product Director

## Decision

AfyaPlus built a Kenyan SME financial-advisory prototype that answers questions about loan preparation and affordability, business registration, KRA tax obligations, mobile-money payments, privacy, and responsible borrowing. It uses 100 manually curated, source-marked examples from Kenyan government and regulator materials, includes a mandatory disclaimer, separates general guidance from a lender's decision, and has reproducible training, merging, inference, safety, and evaluation scripts. The prototype is designed to help staff and SME customers find the right next step, not to approve loans, give binding legal or tax opinions, or replace a qualified adviser.

## Quality Improvement

A valid base-versus-fine-tuned quality comparison is **not available yet**. The fine-tuning run did not complete because Kaggle's P100 PyTorch image does not support the GPU's `sm_60` architecture. Consequently, the measured improvement is currently **ROUGE-L: not available (0%)**, **LLM-judge: not available (0%)**, and **groundedness: not available (0%)**. These are explicitly pending measurements, not evidence that the models are equal. The evaluation pipeline is ready to run all 20 held-out questions once a compatible GPU run produces an adapter and the test split is expanded from 10 to 20 examples.

## Compute Cost

Recorded compute cost for a completed fine-tuning run is **not available** because no run completed. The Kaggle attempt used a free P100 session; no paid cloud charge was incurred in this workspace. Record the actual provider charge or free-tier usage from the successful run before approving production use.

## Next Actions

1. **Run one final training job on a T4 or compatible GPU using the attached Qwen model.** This is the lowest-cost way to obtain real loss history, an adapter, and a defensible quality comparison; do not use the incompatible P100 image.
2. **Complete a 20-question blinded evaluation and compliance review before any pilot.** This gives the product team evidence that the model improves Kenyan answers without inventing tax rates, registration bodies, loan approvals, or payment credentials, and it creates a go/no-go quality threshold for launch.

## Primary Risk and Mitigation

The primary risk is hallucination in high-stakes financial, tax, legal, or payment guidance. Mitigate it with retrieval from the approved source register, mandatory disclaimers, automated rejection of guarantees and credential requests, a human-in-the-loop review for lending or regulatory decisions, and scheduled SME/compliance review of changed Kenyan requirements.
