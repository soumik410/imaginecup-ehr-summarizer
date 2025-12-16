import os
import re
from dotenv import load_dotenv
from typing import Dict, List

load_dotenv()

# Environment configuration
AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT")
AZURE_OPENAI_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")


def _simple_entity_extract(text: str) -> Dict[str, List[str]]:
    # Expanded medication list: antibiotics, anticoagulants, cardiac, diabetes, hypertension
    meds_pattern = r"\b(aspirin|ibuprofen|metformin|lisinopril|atorvastatin|amoxicillin|ciprofloxacin|azithromycin|" \
                   r"warfarin|apixaban|rivaroxaban|dabigatran|metoprolol|carvedilol|diltiazem|amlodipine|" \
                   r"omeprazole|ranitidine|sertraline|fluoxetine|amitriptyline|gabapentin|naproxen|" \
                   r"acetaminophen|tramadol|oxycodone|morphine|insulin|glipizide|glyburide)\b"
    meds = re.findall(meds_pattern, text, flags=re.I)
    
    # Improved allergy extraction: handles "allergy to X", "allergies to X", and parenthetical reactions
    allergies = []
    # Pattern 1: "allergy to X" or "allergies to X"
    m = re.search(r"allerg(?:y|ies)\s+to\s+([\w\s,()]+?)(?:\.|,|;|$)", text, flags=re.I)
    if m:
        for item in re.split(r",|and|;", m.group(1)):
            item = re.sub(r"\s*\([^)]*\)", "", item).strip()  # Remove parentheses and content
            if item and item not in ["reaction", "anaphylaxis", "gi upset", "rash", "swelling"]:
                allergies.append(item)
    # Pattern 2: "Allergies: X, Y, Z"
    m2 = re.search(r"Allergies?:\s+([\w\s,()-]+?)(?:\.|$|\n)", text, flags=re.I)
    if m2:
        for item in re.split(r",|and", m2.group(1)):
            item = re.sub(r"\s*\([^)]*\)", "", item).strip()  # Remove parentheses and content
            if item and len(item) > 1 and item not in allergies:
                allergies.append(item)
    # Pattern 3: common allergy keywords
    for allergy in ["latex", "penicillin", "sulfa", "codeine", "nsaids", "ace inhibitors"]:
        if re.search(f"(?:allerg(?:y|ies)\\s+to\\s+)?{allergy}", text, flags=re.I):
            if allergy not in allergies:
                allergies.append(allergy)

    # Expanded risk detection: cardiac, metabolic, smoking, cancer
    risks = []
    risk_keywords = {
        "smoking": ["smok", "tobacco", "cigarette"],
        "diabetes": ["diabetes", "diabetic", "dm", "type 2", "type 1"],
        "hypertension": ["hypertens", "high blood pressure", "hbp"],
        "stroke": ["stroke", "cva", "tia"],
        "heart attack": ["heart attack", "mi", "myocardial infarction"],
        "CAD": ["cad", "coronary artery disease"],
        "angina": ["angina", "s/p mi", "cad.*chest"],  # More specific to avoid "chest pain" false positive
        "arrhythmia": ["arrhythmia", "afib", "atrial fibrillation"],
        "obesity": ["obesity", "obese"],
        "asthma": ["asthma", "reactive airway"],
        "COPD": ["copd", "chronic obstructive"],
    }
    
    for risk_name, keywords in risk_keywords.items():
        for kw in keywords:
            if re.search(kw, text, flags=re.I):
                if risk_name not in risks:
                    risks.append(risk_name)
                break

    return {"medications": sorted(list({m.lower() for m in meds})), "allergies": sorted(list(set(allergies))), "risks": risks}


def generate_health_summary(medical_text: str) -> Dict[str, object]:
    """Return a concise summary and extracted flags.

    If Azure OpenAI is configured, the function will call the LLM. Otherwise
    it returns a local mock summary and simple entity extraction to allow
    local testing without credentials.
    """
    if not medical_text:
        raise ValueError("medical_text must be a non-empty string")

    entities = _simple_entity_extract(medical_text)

    # Import OpenAI lazily to avoid SDK credential checks at import time
    try:
        from openai import OpenAI
    except Exception:
        OpenAI = None

    if OpenAI and AZURE_OPENAI_KEY and AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT:
        client = OpenAI(api_key=AZURE_OPENAI_KEY, api_base=AZURE_OPENAI_ENDPOINT, api_type="azure", api_version=AZURE_OPENAI_API_VERSION)

        messages = [
            {
                "role": "system",
                "content": (
                    "You are an assistive medical record summarization system. "
                    "Do NOT provide diagnosis, treatment, or medication advice. "
                    "Return a concise summary (2-4 sentences). Also include a JSON object with keys 'allergies','medications','risks' if present."
                ),
            },
            {"role": "user", "content": medical_text},
        ]

        resp = client.chat.completions.create(model=AZURE_OPENAI_DEPLOYMENT, messages=messages, temperature=0.2)

        # Try common response shapes
        assistant_text = None
        try:
            assistant_text = resp.choices[0].message.content
        except Exception:
            try:
                assistant_text = resp.choices[0]["message"]["content"]
            except Exception:
                assistant_text = str(resp)

        return {"summary": assistant_text, "allergies": entities.get("allergies", []), "medications": entities.get("medications", []), "risks": entities.get("risks", [])}

    # Mock fallback for local development/testing
    s = " ".join(medical_text.strip().splitlines())
    if len(s) > 300:
        s = s[:297].rsplit(" ", 1)[0] + "..."
    return {"summary": f"MOCK SUMMARY: {s}", "allergies": entities.get("allergies", []), "medications": entities.get("medications", []), "risks": entities.get("risks", [])}