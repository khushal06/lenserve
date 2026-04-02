# LenServe — Customer Complaint Classifier

I built a full-stack AI tool that reads a customer complaint, figures out what the customer wants, and tells a support agent exactly what to do , all running locally on my laptop with no internet and no API costs.

## The Problem

Big companies handle millions of customer support tickets every year. Every single one gets manually read by a human agent who then has to figure out — is this a warranty issue? A refund? A shipping problem? A technical bug? That takes time, costs money, and does not scale.

Most companies just throw more agents at the problem. I wanted to see if AI could do the triage automatically.

## Why I Built This

Customer support is one of the most expensive operations any product company runs. Most of the tickets are repetitive — same 5 categories over and over. A human reading each one just to decide where to send it is a waste of time and money.

I wanted to build something that solves that problem with a local AI model — no API, no data leaving the building, fully auditable.

## What It Does

You type in a customer complaint. The system tells you:

- What the customer actually wants (warranty, repair, refund, shipping, or technical help)
- How urgent it is (1-10 score)
- How angry the customer is
- Which team to route the ticket to
- What action to take
- How long it should take to resolve

All of this happens in under 10 seconds, running completely offline on a MacBook.

## How I Built It

### Phase 1 — Data + Prompt Setup
I wrote 30 real customer complaints across 5 categories — warranty, repair, refund, shipping, and technical. I stored them in a JSON file and wrote a versioned prompt config in YAML so the prompt is treated like code, not an afterthought.

### Phase 2 — Intent Classifier
I built a Python classifier that sends each complaint to llama3.2 running locally via Ollama. The model has to respond in strict JSON format. I used Pydantic to validate every response and built an automatic retry — if the output is invalid JSON it tries once more before failing gracefully. Ran all 30 complaints and hit 86.7% accuracy on the first run.

### Phase 3 — Routing Engine
I upgraded the classifier to also return priority scores, sentiment detection, urgency scores from 1-10, team routing (warranty team, billing team, tech support, logistics, repair center), and an estimated resolution time. Ran all 30 again and got 83.3% routing accuracy with an average urgency score of 7.6/10.

### Phase 4 — FastAPI Backend
I wrapped everything in a FastAPI backend with 3 endpoints. POST a complaint to /classify and get back the intent. POST to /route and get the full routing decision. POST to /analyze and get both combined in one call. The API has auto-generated documentation at /docs.

### Phase 5 — React TypeScript Frontend
I built a full frontend in React and TypeScript. You can type any complaint or pick from 5 sample complaints. Hit Analyze and see the full structured result rendered in the UI — intent, route, priority badge, sentiment badge, urgency score, recommended action, resolution time, and summary. The whole thing calls the FastAPI backend which calls llama3.2 locally.

## Results

Across 30 complaints:
- Classification accuracy: 86.7%
- Routing accuracy: 83.3%
- Average urgency score: 7.6/10
- Average latency: under 10 seconds per complaint
- Failed classifications: 2 out of 30 (both were genuinely ambiguous edge cases)

## What I Learned

The retry logic matters more than I expected. 2 complaints consistently failed JSON validation on the first try. Without the retry mechanism those would be silent failures in production. Building the retry in from the start is the right call.

Pydantic is not optional for production AI systems. Without schema validation you have no idea if the model is returning what you think it is. llama3.2 is fast and reliable but it will occasionally return malformed JSON especially on edge case inputs.

Temperature 0 is non-negotiable for classification tasks. At 0.7 the model gets creative with the JSON structure and breaks validation. At 0.0 it follows the schema almost every time.

## What This Could Be Used For

- Any company with a high volume of customer support tickets
- E-commerce returns and refund processing
- Insurance claim intake
- IT helpdesk ticket routing
- Any situation where you need to classify and route unstructured text at scale without sending data to an external API

## Project Structure
```
lenserve/
├── src/
│   ├── classifier.py      # reads complaint, calls llama3.2, validates JSON, retries on failure
│   ├── router.py          # adds priority, urgency score, sentiment, team routing, ETA
│   ├── api.py             # fastapi backend with /classify, /route, /analyze endpoints
│   └── __init__.py
├── frontend/
│   └── src/
│       └── App.tsx        # react typescript UI — form, sample complaints, result display
├── data/
│   ├── complaints.json    # 30 sample complaints across 5 categories
│   ├── results.csv        # classification results from all 30 complaints
│   └── routing_results.csv # routing results from all 30 complaints
├── prompts/
│   └── classify_prompt.yaml  # versioned prompt config
├── main.py                # starts the fastapi server
└── README.md
```

## How To Run It

### 1. Get Ollama and pull the model
Download from https://ollama.com then:
```bash
ollama pull llama3.2
```

### 2. Clone and set up backend
```bash
git clone https://github.com/khushal06/lenserve.git
cd lenserve
python -m venv .venv
source .venv/bin/activate
pip install ollama pydantic fastapi uvicorn pandas pyyaml jinja2 python-multipart
```

### 3. Start the backend
```bash
python main.py
```
API runs at http://localhost:8000 and docs at http://localhost:8000/docs.

### 4. Start the frontend
Open a new terminal tab:
```bash
cd frontend
npm install
npm start
```
UI runs at http://localhost:3000 or http://localhost:3001.

### 5. Test it
Type any customer complaint and hit Analyze. Or pick one of the 5 sample complaints to see it work immediately.

## Tech Stack

| Component | Tool |
|---|---|
| LLM | llama3.2 via Ollama — runs 100% locally |
| Validation | Pydantic v2 |
| Backend | FastAPI + uvicorn |
| Frontend | React + TypeScript |
| HTTP client | axios |
| Data storage | pandas + CSV |
| Prompt config | YAML |
| Language | Python 3.11 + TypeScript |
