import ollama
import json
import time
import yaml
import pandas as pd
from pydantic import BaseModel, ValidationError

class RoutingDecision(BaseModel):
    intent: str
    priority: str
    sentiment: str
    urgency_score: int
    recommended_action: str
    route_to: str
    estimated_resolution: str
    summary: str

def load_prompt():
    with open("prompts/classify_prompt.yaml") as f:
        return yaml.safe_load(f)

def route_complaint(complaint: str, model: str = "llama3.2") -> dict:
    routing_prompt = f"""You are a senior support routing AI for Lenovo after-sales service.
Analyze this customer complaint and respond with valid JSON only.
No explanation, no markdown, just raw JSON.

Classify into exactly one intent: warranty, repair, refund, shipping, or technical

Your response must use these exact keys:
- intent: warranty, repair, refund, shipping, or technical
- priority: high, medium, or low
- sentiment: angry, neutral, or satisfied
- urgency_score: integer from 1 to 10
- recommended_action: one sentence on what to do
- route_to: one of — warranty_team, repair_center, billing_team, logistics_team, tech_support
- estimated_resolution: example — "24 hours", "3-5 business days", "immediate"
- summary: one sentence summarizing the complaint

Customer complaint: {complaint}"""

    start = time.time()

    for attempt in range(2):
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": routing_prompt}],
            options={"temperature": 0.0}
        )
        latency = round(time.time() - start, 3)
        raw = response["message"]["content"].strip()

        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        raw = raw.strip()

        try:
            parsed = json.loads(raw)
            validated = RoutingDecision(**parsed)
            return {
                "status": "success",
                "attempt": attempt + 1,
                "latency": latency,
                "data": validated.model_dump()
            }
        except (json.JSONDecodeError, ValidationError) as e:
            if attempt == 0:
                print(f"  Attempt 1 failed — retrying...")
                continue
            return {
                "status": "failed",
                "attempt": 2,
                "latency": latency,
                "error": str(e),
                "raw": raw
            }

def run_routing(complaints_path="data/complaints.json"):
    with open(complaints_path) as f:
        complaints = json.load(f)

    results = []

    for item in complaints:
        print(f"[{item['id']}/30] {item['complaint'][:60]}...")
        result = route_complaint(item["complaint"])

        if result["status"] == "success":
            d = result["data"]
            row = {
                "id": item["id"],
                "actual_category": item["category"],
                "intent": d["intent"],
                "priority": d["priority"],
                "sentiment": d["sentiment"],
                "urgency_score": d["urgency_score"],
                "recommended_action": d["recommended_action"],
                "route_to": d["route_to"],
                "estimated_resolution": d["estimated_resolution"],
                "summary": d["summary"],
                "latency": result["latency"],
                "correct": item["category"] == d["intent"]
            }
            print(f"  Route: {d['route_to']} | Priority: {d['priority']} | Urgency: {d['urgency_score']}/10 | ETA: {d['estimated_resolution']}")
        else:
            row = {
                "id": item["id"],
                "actual_category": item["category"],
                "intent": "failed",
                "priority": "none",
                "sentiment": "none",
                "urgency_score": 0,
                "recommended_action": "manual review required",
                "route_to": "general_support",
                "estimated_resolution": "unknown",
                "summary": "classification failed",
                "latency": result["latency"],
                "correct": False
            }
            print(f"  Failed — routing to general support")

        results.append(row)

    df = pd.DataFrame(results)
    df.to_csv("data/routing_results.csv", index=False)

    accuracy = df["correct"].sum() / len(df) * 100
    avg_urgency = df["urgency_score"].mean()

    print(f"\n{'='*55}")
    print(f"ROUTING REPORT")
    print(f"{'='*55}")
    print(f"Total complaints:     {len(df)}")
    print(f"Accuracy:             {accuracy:.1f}%")
    print(f"Avg urgency score:    {avg_urgency:.1f}/10")
    print(f"\n-- Route Distribution --")
    print(df["route_to"].value_counts().to_string())
    print(f"\n-- Priority Distribution --")
    print(df["priority"].value_counts().to_string())
    print(f"\n-- Sentiment Distribution --")
    print(df["sentiment"].value_counts().to_string())
    print(f"{'='*55}")
    print(f"Saved to data/routing_results.csv")
    return df

if __name__ == "__main__":
    run_routing()