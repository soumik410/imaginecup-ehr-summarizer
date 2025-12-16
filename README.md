# Smart Electronic Health Record (EHR) Summarizer

A FastAPI-based AI system that summarizes patient medical records, extracts key medical flags (allergies, medications, risks), and helps doctors make faster, safer decisions.

## Problem & Solution

**Problem:** Doctors waste time reading long patient histories.  
**Solution:** AI summarizes key medical history and flags critical information.

---

## Features

✅ **Summarization** - Concise 2-4 sentence summaries of patient history  
✅ **Allergy Detection** - Automatically extracts and flags drug/food allergies  
✅ **Medication Extraction** - Identifies all medications and dosages  
✅ **Risk Flagging** - Highlights cardiac, diabetes, smoking, and other risks  
✅ **Azure Integration** - Connects to Azure OpenAI for LLM-powered summaries  
✅ **Local Testing** - Works without Azure keys (mock summaries) for development  

---

## Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

1. **Clone the repository:**
```bash
git clone https://github.com/YOUR-USERNAME/imaginecup-ehr-summarizer.git
cd imaginecup-ehr-summarizer
```

2. **Create a virtual environment:**
```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Run the server:**
```bash
uvicorn main:app --port 8001
```

Server will start at: `http://127.0.0.1:8001`

---

## API Endpoints

### **GET /health**
Check if the server is running.

**Request:**
```bash
curl http://127.0.0.1:8001/
```

**Response:**
```json
{"status": "OK"}
```

---

### **POST /summarize**
Submit patient EHR text and get summary + extracted flags.

**Request:**
```bash
curl -X POST http://127.0.0.1:8001/summarize \
  -H "Content-Type: application/json" \
  -d '{"text":"Patient is 65-year-old male with diabetes, hypertension, smoking history. Allergies to penicillin. On metformin, lisinopril, atorvastatin."}'
```

**Response:**
```json
{
  "summary": "MOCK SUMMARY: Patient is 65-year-old male with diabetes, hypertension, smoking history. Allergies to penicillin. On metformin, lisinopril, atorvastatin.",
  "allergies": ["penicillin"],
  "medications": ["atorvastatin", "lisinopril", "metformin"],
  "risks": ["smoking", "diabetes", "hypertension"]
}
```

---

## Configuration

### Local Testing (Default)
No configuration needed. The app uses mock summaries and local entity extraction.

### Azure OpenAI Integration (Optional)

1. Create an Azure OpenAI account: https://azure.microsoft.com/en-us/products/cognitive-services/openai-service/
2. Create a `.env` file in the project root:
```
AZURE_OPENAI_KEY=your-api-key-here
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_DEPLOYMENT=your-deployment-name
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

3. Restart the server—it will now use Azure OpenAI for real summaries.

---

## Project Structure

```
imaginecup_backend/
├── main.py                    # FastAPI app
├── services/
│   └── openai_service.py     # Summarization logic
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

---

## Sample EHR Inputs

**Example 1: Chronic Disease Management**
```
Chief complaint: routine follow-up. PMH: diabetes type 2, hypertension, obesity.
Medications: metformin 1000mg BID, lisinopril 20mg daily, atorvastatin 40mg daily.
Allergies: penicillin (anaphylaxis), sulfa drugs (rash).
Smoking: quit 5 years ago. Exercise: minimal.
```

**Example 2: Acute Presentation**
```
Chief complaint: chest pain x2 hours. PMH: CAD s/p MI 2018, diabetes, smoking.
Medications: aspirin 81mg, atorvastatin 40mg, lisinopril 10mg, metoprolol 50mg BID.
Allergies: latex, ibuprofen (GI upset).
Vitals: BP 145/90, HR 92, RR 18, O2 98% RA.
EKG: normal sinus rhythm, no acute changes.
```

---

## Testing

Run a quick test:
```bash
python -c "from services.openai_service import generate_health_summary; \
result = generate_health_summary('Patient has diabetes, hypertension. Allergies to penicillin. On metformin and lisinopril.'); \
import json; print(json.dumps(result, indent=2))"
```

---

## Next Steps

- [ ] Add Azure OpenAI credentials for real LLM summaries
- [ ] Enhance entity extraction patterns
- [ ] Add unit tests
- [ ] Deploy to Azure Container Apps
- [ ] Add PII redaction for HIPAA compliance
- [ ] Implement audit logging

---

## Team

Built for Microsoft Imagine Cup 2025

---

## License

MIT License

---

## Support

For issues or questions, create a GitHub issue or contact the team.
