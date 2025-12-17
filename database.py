"""
Database configuration and models for Smart EHR Summarizer
Supports both patients and doctors with role-based access control
"""

from sqlalchemy import create_engine, Column, String, DateTime, Integer, Boolean, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL - SQLite for simplicity, easily switchable to PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./ehr_summarizer.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# ============================================================================
# DATABASE MODELS
# ============================================================================

class User(Base):
    """Base user model for both doctors and patients"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    full_name = Column(String)
    password_hash = Column(String)  # Never store plain passwords!
    role = Column(String)  # "patient" or "doctor"
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    patient_records = relationship("PatientRecord", back_populates="owner", cascade="all, delete-orphan")
    doctor_patients = relationship("DoctorPatientAccess", back_populates="doctor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(email={self.email}, role={self.role})>"


class PatientRecord(Base):
    """Patient EHR data and uploaded prescriptions"""
    __tablename__ = "patient_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), index=True)
    file_name = Column(String)  # Original filename
    file_path = Column(String)  # Path to uploaded file
    prescription_text = Column(Text)  # Extracted text from prescription
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    owner = relationship("User", back_populates="patient_records")
    summary = relationship("HealthSummary", back_populates="record", uselist=False, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<PatientRecord(patient_id={self.patient_id}, file={self.file_name})>"


class HealthSummary(Base):
    """AI-generated health summary for a prescription/EHR"""
    __tablename__ = "health_summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("patient_records.id"), unique=True, index=True)
    summary = Column(Text)  # AI-generated summary
    medications = Column(Text)  # JSON string of medications
    allergies = Column(Text)  # JSON string of allergies
    risks = Column(Text)  # JSON string of risks
    generated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationship
    record = relationship("PatientRecord", back_populates="summary")
    
    def __repr__(self):
        return f"<HealthSummary(record_id={self.record_id})>"


class DoctorPatientAccess(Base):
    """Track which doctors can access which patient records"""
    __tablename__ = "doctor_patient_access"
    
    id = Column(Integer, primary_key=True, index=True)
    doctor_id = Column(Integer, ForeignKey("users.id"), index=True)
    patient_id = Column(Integer, ForeignKey("users.id"), index=True)
    granted_at = Column(DateTime, default=datetime.utcnow)
    access_level = Column(String, default="read")  # "read" or "write"
    
    # Relationship
    doctor = relationship("User", back_populates="doctor_patients", foreign_keys=[doctor_id])
    
    def __repr__(self):
        return f"<DoctorPatientAccess(doctor_id={self.doctor_id}, patient_id={self.patient_id})>"


# ============================================================================
# DATABASE INITIALIZATION
# ============================================================================

def init_db():
    """Create all tables in database"""
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized successfully")


def get_db():
    """Dependency for FastAPI to inject database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
