"""
Unit tests for Smart EHR Summarizer
Tests entity extraction, summarization, and API responses
"""

import json
import pytest
from services.openai_service import generate_health_summary, _simple_entity_extract


class TestEntityExtraction:
    """Test entity extraction functions"""

    def test_medication_extraction_basic(self):
        """Test basic medication extraction"""
        text = "Patient on metformin 500mg BID, lisinopril 10mg daily, atorvastatin 20mg."
        result = _simple_entity_extract(text)
        assert "metformin" in result["medications"]
        assert "lisinopril" in result["medications"]
        assert "atorvastatin" in result["medications"]

    def test_medication_extraction_expanded(self):
        """Test expanded medication list including antibiotics and anticoagulants"""
        text = "Prescribed amoxicillin 500mg, warfarin 5mg, metoprolol 50mg BID."
        result = _simple_entity_extract(text)
        assert "amoxicillin" in result["medications"]
        assert "warfarin" in result["medications"]
        assert "metoprolol" in result["medications"]

    def test_allergy_extraction_simple(self):
        """Test allergy extraction with 'allergy to' pattern"""
        text = "Allergies to penicillin and sulfa drugs."
        result = _simple_entity_extract(text)
        assert "penicillin" in result["allergies"]
        assert "sulfa" in result["allergies"] or "sulfa drugs" in result["allergies"]

    def test_allergy_extraction_with_reaction(self):
        """Test allergy extraction with parenthetical reactions"""
        text = "Allergies: penicillin (anaphylaxis), ibuprofen (GI upset), latex."
        result = _simple_entity_extract(text)
        assert "penicillin" in result["allergies"]
        assert "ibuprofen" in result["allergies"]
        assert "latex" in result["allergies"]

    def test_allergy_extraction_colon_format(self):
        """Test allergy extraction with colon format"""
        text = "Allergies: codeine, NSAIDs (rash), ace inhibitors."
        result = _simple_entity_extract(text)
        assert "codeine" in result["allergies"]
        assert len(result["allergies"]) >= 2

    def test_risk_extraction_cardiac(self):
        """Test cardiac risk detection"""
        text = "PMH: CAD s/p MI 2018, hypertension, atrial fibrillation."
        result = _simple_entity_extract(text)
        assert "CAD" in result["risks"]
        assert "heart attack" in result["risks"] or "MI" in str(result)
        assert "hypertension" in result["risks"]

    def test_risk_extraction_diabetes_smoking(self):
        """Test diabetes and smoking risk detection"""
        text = "Patient has type 2 diabetes, smoking history 20 pack-years, quit 5 years ago."
        result = _simple_entity_extract(text)
        assert "diabetes" in result["risks"]
        assert "smoking" in result["risks"]

    def test_risk_extraction_comprehensive(self):
        """Test comprehensive risk detection"""
        text = "PMH: diabetes type 2, hypertension, stroke (2015), asthma, COPD, obesity."
        result = _simple_entity_extract(text)
        assert "diabetes" in result["risks"]
        assert "hypertension" in result["risks"]
        assert "stroke" in result["risks"]
        assert "asthma" in result["risks"]
        assert "COPD" in result["risks"]
        assert "obesity" in result["risks"]

    def test_no_false_positives(self):
        """Test that normal medical text doesn't trigger false positives"""
        text = "Patient reports normal appetite and sleep. No chest pain or dyspnea."
        result = _simple_entity_extract(text)
        assert len(result["medications"]) == 0
        assert len(result["risks"]) == 0


class TestHealthSummarization:
    """Test health record summarization"""

    def test_summarization_returns_dict(self):
        """Test that summarization returns a dictionary with required keys"""
        text = "Patient is 65 years old with diabetes and hypertension on metformin and lisinopril."
        result = generate_health_summary(text)
        assert isinstance(result, dict)
        assert "summary" in result
        assert "medications" in result
        assert "allergies" in result
        assert "risks" in result

    def test_summarization_with_complex_ehr(self):
        """Test summarization with complex EHR data"""
        text = """Chief complaint: chest pain x2 hours. PMH: CAD s/p MI 2018, diabetes, hypertension, smoking.
        Medications: aspirin 81mg, atorvastatin 40mg, lisinopril 10mg, metoprolol 50mg BID.
        Allergies: latex (anaphylaxis), ibuprofen (GI upset).
        Vitals: BP 145/90, HR 92, RR 18, O2 98% RA."""
        result = generate_health_summary(text)
        assert len(result["summary"]) > 0
        assert "aspirin" in result["medications"]
        assert "latex" in result["allergies"]
        assert "CAD" in result["risks"]

    def test_empty_text_raises_error(self):
        """Test that empty text raises ValueError"""
        with pytest.raises(ValueError):
            generate_health_summary("")

    def test_mock_summary_formatting(self):
        """Test that mock summaries are properly formatted"""
        text = "Patient has type 2 diabetes, on metformin, allergy to penicillin."
        result = generate_health_summary(text)
        assert "MOCK SUMMARY" in result["summary"] or len(result["summary"]) > 0
        assert "diabetes" in result["risks"]
        assert "metformin" in result["medications"]
        assert "penicillin" in result["allergies"]

    def test_summary_text_truncation(self):
        """Test that very long summaries are truncated"""
        long_text = "Patient history: " + "A" * 500  # Create very long text
        result = generate_health_summary(long_text)
        summary = result["summary"]
        # Summary should be reasonable length (not extremely long)
        assert len(summary) < 500  # Should be truncated


class TestSamplePatients:
    """Test with realistic sample patient data"""

    def setup_method(self):
        """Load sample patient data"""
        with open("data/sample_ehr_records.json", "r") as f:
            self.patients = json.load(f)

    def test_patient_001_extraction(self):
        """Test extraction on patient 1 (routine follow-up)"""
        text = self.patients[0]["text"]
        result = generate_health_summary(text)
        assert "metformin" in result["medications"]
        assert "lisinopril" in result["medications"]
        assert "atorvastatin" in result["medications"]
        assert "penicillin" in result["allergies"]
        assert "sulfa" in result["allergies"] or "sulfa drugs" in result["allergies"]
        assert "diabetes" in result["risks"]
        assert "hypertension" in result["risks"]

    def test_patient_002_extraction(self):
        """Test extraction on patient 2 (acute cardiac event)"""
        text = self.patients[1]["text"]
        result = generate_health_summary(text)
        assert "aspirin" in result["medications"]
        assert "atorvastatin" in result["medications"]
        assert "metoprolol" in result["medications"]
        assert "latex" in result["allergies"]
        assert "CAD" in result["risks"]
        assert "heart attack" in result["risks"] or "smoking" in result["risks"]

    def test_patient_005_extraction(self):
        """Test extraction on patient 5 (acute infection, allergy history)"""
        text = self.patients[4]["text"]
        result = generate_health_summary(text)
        assert "amoxicillin" in result["allergies"]
        assert "azithromycin" in result["allergies"]
        assert "asthma" in result["risks"]

    def test_all_patients_valid_response(self):
        """Test that all sample patients produce valid responses"""
        for patient in self.patients:
            result = generate_health_summary(patient["text"])
            assert isinstance(result, dict)
            assert "summary" in result and len(result["summary"]) > 0
            assert "medications" in result and isinstance(result["medications"], list)
            assert "allergies" in result and isinstance(result["allergies"], list)
            assert "risks" in result and isinstance(result["risks"], list)


class TestDataValidation:
    """Test data integrity and validation"""

    def test_json_sample_data_valid(self):
        """Test that sample JSON data is valid"""
        with open("data/sample_ehr_records.json", "r") as f:
            data = json.load(f)
            assert isinstance(data, list)
            assert len(data) >= 5
            for patient in data:
                assert "id" in patient
                assert "age" in patient
                assert "gender" in patient
                assert "text" in patient

    def test_no_duplicate_patient_ids(self):
        """Test that all patient IDs are unique"""
        with open("data/sample_ehr_records.json", "r") as f:
            data = json.load(f)
            ids = [p["id"] for p in data]
            assert len(ids) == len(set(ids)), "Duplicate patient IDs found"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
