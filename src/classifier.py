import ollama
import json
import time
import yaml
import pandas as pd
import os
from pydantic import BaseModel, ValidationError

class ComplaintClassification(BaseModel):
    intent: str
    confidence: str
    sentiment: str
    priority: str
    recommended_action: str
    summary: str

def load_prompt(path="prompts/classify_prompt.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

def classify(complaint: str, model: str = "llama3.2") -> dict:
    prompt_cfg = load_prompt()
    prompt = prompt_cfg["template"].format(complaint=complaint)

    start = time.time()
    response = ollama.chat(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.0}
    )
    latency = round(time.time() - start, 3)
    raw = response["message"]["content"].strip()

    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    for attempt in range(2):
        try:
            parsed = json.loads(raw)
            validated = ComplaintClassification(**parsed)
            return {
                "status": "success",
                "attempt": attempt + 1,
                "latency": latency,
                "data": validated.model_dump()
            }
        except (json.JSONDecodeError, ValidationError) as e:
            if attempt == 0:
                print(f"Attempt 1 failed — retrying...")
                response = ollama.chat(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    options={"temperature": 0.0}
                )
                raw = response["message"]["content"].strip()
                if raw.startswith("```"):
                    raw = raw.split("```")[1]
                    if raw.startswith("json"):
                        raw = raw[4:]
                raw = raw.strip()
                continue
            return {
                "status": "failed",
                "attempt": 2,
                "latency": latency,
                "error": str(e),
                "raw": raw
            }

def run_all(complaints_path="data/complaints.json"):
    with open(complaints_path) as f:
        complaints = json.load(f)

    results = []
    passed = 0
    failed = 0

    for item in complaints:
        print(f"[{item['id']}/30] {item['complaint'][:60]}...")
        result = classify(item["complaint"])

        if result["status"] == "success":
            passed += 1
            row = {
                "id": item["id"],
                "actual_category": item["category"],
                "predicted_intent": result["data"]["intent"],
                "confidence": result["data"]["confidence"],
                "sentiment": result["data"]["sentiment"],
                "priority": result["data"]["priority"],
                "recommended_action": result["data"]["recommended_action"],
                "summary": result["data"]["summary"],
                "latency": result["latency"],
                "attempts": result["attempt"],
                "correct": item["category"] == result["data"]["intent"]
            }
        else:
            failed += 1
            row = {
                "id": item["id"],
                "actual_category": item["category"],
                "predicted_intent": "failed",
                "confidence": "none",
                "sentiment": "none",
                "priority": "none",
                "recommended_action": "none",
                "summary": "none",
                "latency": result["latency"],
                "attempts": result["attempt"],
                "correct": False
            }
        results.append(row)
        print(f"  Intent: {row['predicted_intent']} | Priority: {row['priority']} | Sentiment: {row['sentiment']} | Correct: {row['correct']}")

    df = pd.DataFrame(results)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/results.csv", index=False)

    accuracy = df["correct"].sum() / len(df) * 100
    print(f"\n{'='*50}")
    print(f"Total: {len(complaints)} | Passed: {passed} | Failed: {failed}")
    print(f"Classification Accuracy: {accuracy:.1f}%")
    print(f"Results saved to data/results.csv")
    print(f"{'='*50}")
    return df

if __name__ == "__main__":
    run_all()