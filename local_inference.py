"""Run five Kenyan SME advisory checks against a local Ollama model."""

from __future__ import annotations

import json
import time
import urllib.request
from pathlib import Path

MODEL = "llama3.2:latest"
SYSTEM_PROMPT = (
    "You are a Kenyan SME financial advisory assistant for a microfinance institution. "
    "Give concise, general, source-aware guidance and distinguish it from a lender's decision. "
    "This is not legal, tax, or financial advice; do not diagnose, make binding legal judgments, "
    "promise approval or returns, or make a credit decision. End every response with exactly this "
    "disclaimer: This is not legal, tax, or financial advice. Confirm current requirements with the "
    "relevant Kenyan authority, lender, or qualified professional."
)
QUERIES = [
    ("loan eligibility", "What documents should I prepare before applying for a Kenyan SME loan?"),
    ("business registration", "Where do I register a business name in Kenya?"),
    ("tax obligations", "What should a Kenyan SME check before deciding whether Turnover Tax applies?"),
    ("mobile money", "How can a small business safely integrate M-PESA payments?"),
    ("privacy", "How should I protect customer phone numbers and loan documents?"),
]


def ask(question: str) -> str:
    payload = json.dumps({"model": MODEL, "messages": [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": question}], "stream": False, "options": {"temperature": 0.2}}).encode()
    request = urllib.request.Request("http://localhost:11434/api/chat", data=payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=120) as response:
        return json.loads(response.read())["message"]["content"]


def main() -> None:
    results = []
    for topic, question in QUERIES:
        start = time.time()
        response = ask(question)
        results.append({"topic": topic, "question": question, "response": response, "latency_seconds": round(time.time() - start, 2), "model": MODEL})
        print(f"\n--- {topic} ---\n{response}")
    Path("inference_results.json").write_text(json.dumps(results, indent=2) + "\n")
    print("\nSaved inference_results.json")


if __name__ == "__main__":
    main()
