# waf_service.py
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import uvicorn
import torch
import os
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from config import *

logging.basicConfig(filename=ERROR_LOG_FILE, level=logging.ERROR,
                    format="%(asctime)s - %(levelname)s - %(message)s", encoding="utf-8")

app = FastAPI()
LLM_MODEL = None
LLM_TOKENIZER = None
LABEL_MAPPING = {0: "CLEAN", 1: "SUSPICIOUS"}

def load_llm_model():
    global LLM_MODEL, LLM_TOKENIZER
    if not os.path.exists(LLM_MODEL_DIR):
        logging.error(f"Model directory not found: {LLM_MODEL_DIR}")
        return False
    try:
        print(f"Loading model from: {LLM_MODEL_DIR}")
        LLM_TOKENIZER = AutoTokenizer.from_pretrained(LLM_MODEL_DIR)
        LLM_MODEL = AutoModelForSequenceClassification.from_pretrained(LLM_MODEL_DIR)
        LLM_MODEL.eval()
        if torch.cuda.is_available():
            LLM_MODEL.to("cuda")
        return True
    except Exception as e:
        logging.error(f"Failed to load model: {e}")
        LLM_MODEL = None
        LLM_TOKENIZER = None
        return False

@app.on_event("startup")
async def startup_event():
    load_llm_model()

@app.get("/health")
async def health_check():
    if LLM_MODEL is None or LLM_TOKENIZER is None:
        return JSONResponse({"status": "unhealthy", "reason": "Model not loaded"}, status_code=503)
    return JSONResponse({"status": "healthy"})

@app.post("/analyze")
async def analyze_request(request: Request):
    if LLM_MODEL is None or LLM_TOKENIZER is None:
        logging.error("Model not loaded for inference")
        return {"decision": "CLEAN", "reason": "Model Load Failure"}

    try:
        data = await request.json()
        text = f"URI: {data.get('uri','')} Body: {data.get('body','')}"
        inputs = LLM_TOKENIZER(text, return_tensors="pt", truncation=True, padding=True, max_length=1024)
        if torch.cuda.is_available():
            inputs = {k: v.to("cuda") for k, v in inputs.items()}
        with torch.no_grad():
            outputs = LLM_MODEL(**inputs)
        logits = outputs.logits
        predicted = torch.argmax(logits, dim=-1).item()
        decision = LABEL_MAPPING.get(predicted, "CLEAN")
        return {"decision": decision, "reason": f"Class ID: {predicted}"}
    except Exception as e:
        logging.error(f"Inference error: {e}")
        return {"decision": "CLEAN", "reason": f"Inference Runtime Error: {e}"}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=WAF_PORT)
