from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv
from services.openai_service import generate_health_summary

load_dotenv()

app = FastAPI()

@app.get("/")
def health():
    return {"status": "OK"}


@app.post("/summarize")
def summarize(payload: dict):
    if "text" not in payload:
        raise HTTPException(status_code=400, detail="Missing medical text")
    return generate_health_summary(payload["text"])
