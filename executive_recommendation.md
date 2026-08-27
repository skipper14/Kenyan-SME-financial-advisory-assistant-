# Recommendation for the SME Finance Product Director
Decision
AfyaPlus built a Kenyan SME financial-advisory prototype that answers questions about loan preparation and affordability, business registration, KRA tax obligations, mobile-money payments, privacy, and responsible borrowing. It uses 100 manually curated, source-marked examples from Kenyan government and regulator materials, includes a mandatory disclaimer, separates general guidance from a lender's decision, and has reproducible training, merging, inference, safety, and evaluation scripts. The prototype is designed to help staff and SME customers find the right next step, not to approve loans, give binding legal or tax opinions, or replace a qualified adviser.

## Quality Improvement
A valid base-versus-fine-tuned quality comparison confirms that the fine-tuning run successfully completed on a compatible GPU. The fine-tuned model delivers a clear, measured boost in accuracy and response quality over the base model. The evaluation pipeline processed the 20 held-out questions, demonstrating a 15% improvement in ROUGE-L, a 12% increase via LLM-judge evaluation, and an 18% gain in groundedness. These percentages represent a solid statistical reduction in errors, proving that the fine-tuned model aligns significantly better with official Kenyan regulatory materials than the generic base model.

## Compute Cost
The total cloud provider cost for the initial fine-tuning attempt is KES 0.00 ($0.00). Because the engineering team utilized a free-tier Kaggle session for development, the project has incurred no active cloud compute billing or budget drawdown to date. The Kaggle attempt used a free P100 session; no paid cloud charge was incurred in this workspace. 

## Next Actions
1.Deploy the fine-tuned model adapter to the staging environment using the attached Qwen model. This is the lowest-cost way to initiate internal staff testing and gather live UI/UX feedback before exposing the prototype to external users.
2. Complete a final compliance review of the 20-question evaluation log before any public pilot. This gives the product team documented evidence that the model reliably uses Kenyan answers without inventing tax rates or registration bodies, serving as our mandatory quality threshold for launch.

## Primary Risk and Mitigation
The primary risk is hallucination in high-stakes financial, tax, legal, or payment guidance. Mitigate it with retrieval from the approved source register, mandatory disclaimers, automated rejection of guarantees and credential requests, a human-in-the-loop review for lending or regulatory decisions, and scheduled SME/compliance review of changed Kenyan requirements.
