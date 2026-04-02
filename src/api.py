from fastapi import FastAPI
from pydantic import BaseModel
from src.classifier import classify
from src.router import route_complaint

app = FastAPI(
    title="LenServe — AI After-Sales Classifier",
    description="Classifies and routes Lenovo customer complaints using local LLM",
    version="1.0.0"
)

class ComplaintRequest(BaseModel):
    complaint: str
    model: str = "llama3.2"

class HealthResponse(BaseModel):
    status: str
    message: str

@app.get("/", response_model=HealthResponse)
def root():
    return {
        "status": "running",
        "message": "LenServe API is live. Go to /docs to test it."
    }

@app.get("/health", response_model=HealthResponse)
def health():
    return {
        "status": "healthy",
        "message": "All systems operational"
    }

@app.post("/classify")
def classify_complaint(request: ComplaintRequest):
    result = classify(request.complaint, request.model)
    if result["status"] == "success":
        return {
            "status": "success",
            "complaint": request.complaint,
            "classification": result["data"],
            "latency": result["latency"],
            "attempts": result["attempt"]
        }
    return {
        "status": "failed",
        "complaint": request.complaint,
        "error": result.get("error", "unknown error"),
        "latency": result["latency"]
    }

@app.post("/route")
def route_complaint_endpoint(request: ComplaintRequest):
    result = route_complaint(request.complaint, request.model)
    if result["status"] == "success":
        return {
            "status": "success",
            "complaint": request.complaint,
            "routing": result["data"],
            "latency": result["latency"],
            "attempts": result["attempt"]
        }
    return {
        "status": "failed",
        "complaint": request.complaint,
        "error": result.get("error", "unknown error"),
        "latency": result["latency"]
    }

@app.post("/analyze")
def full_analysis(request: ComplaintRequest):
    classify_result = classify(request.complaint, request.model)
    route_result = route_complaint(request.complaint, request.model)

    return {
        "status": "success",
        "complaint": request.complaint,
        "classification": classify_result.get("data"),
        "routing": route_result.get("data"),
        "total_latency": round(
            classify_result.get("latency", 0) + route_result.get("latency", 0), 3
        )
    }