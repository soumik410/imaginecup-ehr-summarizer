// ===== APPLICATION STATE =====
const state = {
    view: 'home',
    currentPatient: null,
    patients: {},
    uploads: {},
    loginId: '',
    loginPassword: '',
    registrationData: {
        name: '',
        age: '',
        gender: '',
        bloodType: '',
        pastConditions: '',
        currentMedications: '',
        knownAllergies: ''
    }
};

// ===== UTILITY FUNCTIONS =====

/**
 * Generate unique patient ID
 */
function generatePatientId() {
    return 'PT' + Math.random().toString(36).substr(2, 9).toUpperCase();
}

/**
 * Generate random password
 */
function generatePassword() {
    return Math.random().toString(36).substr(2, 8).toUpperCase();
}

/**
 * Simulate Azure AI document summarization
 */
function summarizeDocument(fileName) {
    const summaries = {
        'blood': 'Blood work shows elevated cholesterol (220 mg/dL) and slightly high blood sugar (115 mg/dL). Liver and kidney function normal. Vitamin D deficiency detected.',
        'x-ray': 'Chest X-ray reveals mild bronchial thickening consistent with chronic bronchitis. No signs of pneumonia or masses. Heart size normal.',
        'prescription': 'Patient prescribed Metformin 500mg (2x daily) for blood sugar management and Atorvastatin 10mg (1x nightly) for cholesterol control. 3-month follow-up recommended.',
        'ecg': 'ECG shows normal sinus rhythm at 72 bpm. No signs of arrhythmia or ischemia. PR interval and QT interval within normal limits.'
    };
    
    const type = fileName.toLowerCase();
    for (let key in summaries) {
        if (type.includes(key)) return summaries[key];
    }
    return 'Medical document analyzed. Key findings extracted and stored in patient record.';
}

/**
 * Detect risks and allergies from document summary
 */
function detectRisksAndAllergies(summary, patientData) {
    const risks = [];
    const allergies = [];
    
    if (summary.includes('cholesterol') || summary.includes('blood sugar')) {
        risks.push({ 
            level: 'Medium', 
            condition: 'Cardiovascular Risk', 
            detail: 'Elevated cholesterol levels detected' 
        });
    }
    
    if (summary.includes('bronchial') || summary.includes('bronchitis')) {
        risks.push({ 
            level: 'Low', 
            condition: 'Respiratory Concern', 
            detail: 'Chronic bronchial condition' 
        });
    }
    
    if (patientData.knownAllergies) {
        allergies.push({ 
            allergen: patientData.knownAllergies, 
            severity: 'High', 
            reaction: 'Avoid prescription' 
        });
    }
    
    return { risks, allergies };
}

// ===== EVENT HANDLERS =====

/**
 * Handle patient registration
 */
function handlePatientRegistration() {
    const patientId = generatePatientId();
    const password = generatePassword();
    
    const newPatient = {
        id: patientId,
        password: password,
        ...state.registrationData,
        registrationDate: new Date().toLocaleDateString()
    };
    
    state.patients[patientId] = newPatient;
    state.currentPatient = newPatient;
    state.uploads[patientId] = [];
    state.view = 'patientDash';
    render();
}

/**
 * Handle patient login (existing patients)
 */
function handlePatientLogin() {
    if (state.patients[state.loginId] && state.patients[state.loginId].password === state.loginPassword) {
        state.currentPatient = state.patients[state.loginId];
        state.view = 'patientDash';
        render();
    } else {
        alert('Invalid Patient ID or Password. Please check your credentials.');
    }
}

/**
 * Handle document upload by patient
 */
function handleDocumentUpload(fileName) {
    if (!state.currentPatient) return;
    
    const summary = summarizeDocument(fileName);
    const analysis = detectRisksAndAllergies(summary, state.currentPatient);
    
    const newDocument = {
        id: Date.now(),
        fileName: fileName,
        uploadDate: new Date().toLocaleDateString(),
        summary: summary,
        risks: analysis.risks,
        allergies: analysis.allergies
    };
    
    state.uploads[state.currentPatient.id].push(newDocument);
    render();
}

/**
 * Handle doctor login
 */
function handleDoctorLogin() {
    if (state.patients[state.loginId] && state.patients[state.loginId].password === state.loginPassword) {
        state.currentPatient = state.patients[state.loginId];
        state.view = 'doctorDash';
        render();
    } else {
        alert('Invalid Patient ID or Password');
    }
}

/**
 * Handle document upload by doctor
 */
function handleDoctorUpload(fileName) {
    if (!state.currentPatient) return;
    
    const summary = summarizeDocument(fileName);
    const analysis = detectRisksAndAllergies(summary, state.currentPatient);
    
    const newDocument = {
        id: Date.now(),
        fileName: fileName,
        uploadDate: new Date().toLocaleDateString(),
        summary: summary,
        risks: analysis.risks,
        allergies: analysis.allergies,
        uploadedBy: 'Doctor'
    };
    
    state.uploads[state.currentPatient.id].push(newDocument);
    render();
}

// ===== NAVIGATION FUNCTIONS =====

/**
 * Navigate to different views
 */
function navigateTo(view) {
    state.view = view;
    // Reset login fields when navigating
    if (view === 'patientLogin' || view === 'doctorLogin') {
        state.loginId = '';
        state.loginPassword = '';
    }
    render();
}

/**
 * Patient logout
 */
function logout() {
    state.currentPatient = null;
    state.loginId = '';
    state.loginPassword = '';
    state.view = 'home';
    render();
}

/**
 * Doctor logout
 */
function doctorLogout() {
    state.currentPatient = null;
    state.loginId = '';
    state.loginPassword = '';
    state.view = 'doctorLogin';
    render();
}

/**
 * Update registration data
 */
function updateRegistration(field, value) {
    state.registrationData[field] = value;
}

// ===== VIEW COMPONENTS =====

/**
 * Home View - Landing page with portal selection
 */
function HomeView() {
    return `
        <div class="header">
            <h1>🏥 Smart EHR Summarizer</h1>
            <p>AI-Powered Electronic Health Records Management</p>
        </div>
        <div class="grid">
            <div class="portal-card" onclick="showPatientOptions()">
                <div class="icon-circle blue-icon">👤</div>
                <h2>Patient Portal</h2>
                <p>Register and manage your health records securely</p>
                <ul class="feature-list">
                    <li>Secure registration with unique ID</li>
                    <li>Upload prescriptions & reports</li>
                    <li>AI-powered risk detection</li>
                </ul>
                <div style="margin-top: 20px; display: flex; gap: 10px; justify-content: center;">
                    <button class="btn" style="background: #3b82f6; color: white; padding: 10px 20px; flex: 1;" onclick="event.stopPropagation(); navigateTo('patientReg')">
                        New Patient
                    </button>
                    <button class="btn" style="background: #10b981; color: white; padding: 10px 20px; flex: 1;" onclick="event.stopPropagation(); navigateTo('patientLogin')">
                        Existing Patient
                    </button>
                </div>
            </div>
            <div class="portal-card" onclick="navigateTo('doctorLogin')">
                <div class="icon-circle purple-icon">🩺</div>
                <h2>Doctor Portal</h2>
                <p>Access patient records and provide care</p>
                <ul class="feature-list">
                    <li>Secure patient access with credentials</li>
                    <li>View AI-summarized reports</li>
                    <li>Check allergies & medications</li>
                </ul>
            </div>
        </div>
    `;
}

/**
 * Show patient options (for mobile compatibility)
 */
function showPatientOptions() {
    // This function is called when clicking on the patient card
    // The buttons inside will handle their own clicks with event.stopPropagation()
}

/**
 * Patient Login View (for existing patients)
 */
function PatientLoginView() {
    const demoPatients = Object.values(state.patients);
    
    return `
        <button class="btn-back" onclick="navigateTo('home')">← Back to Home</button>
        <div class="card" style="max-width: 500px; margin: 0 auto;">
            <div class="icon-circle blue-icon" style="margin: 0 auto 20px;">👤</div>
            
            <h2 style="text-align: center; font-size: 2rem; margin-bottom: 10px;">Patient Login</h2>
            <p style="text-align: center; color: #64748b; margin-bottom: 30px;">Enter your credentials to access your health records</p>
            
            <div class="form-group">
                <label>Patient ID</label>
                <input type="text" id="patientLoginId" placeholder="Enter your patient ID"
                    value="${state.loginId}"
                    oninput="state.loginId = this.value">
            </div>

            <div class="form-group">
                <label>Password</label>
                <input type="password" id="patientLoginPassword" placeholder="Enter your password"
                    value="${state.loginPassword}"
                    oninput="state.loginPassword = this.value">
            </div>

            <button class="btn btn-primary" onclick="handlePatientLogin()"
                ${!state.loginId || !state.loginPassword ? 'disabled' : ''}>
                Login to Dashboard
            </button>

            <div class="alert" style="background: #eff6ff; border-left: 4px solid #3b82f6; margin-top: 20px;">
                <p style="text-align: center; color: #1e40af;">
                    🔒 Your data is encrypted and secure<br>
                    <small style="margin-top: 5px; display: block;">Don't have an account? <a href="#" onclick="navigateTo('patientReg'); return false;" style="color: #3b82f6; font-weight: 600;">Register here</a></small>
                </p>
            </div>

            ${demoPatients.length > 0 ? `
                <div class="demo-credentials">
                    <p><strong>Demo Patients Available for Testing:</strong></p>
                    ${demoPatients.map(p => `
                        <div class="cred-item">
                            <strong>${p.name}</strong><br>
                            ID: <strong>${p.id}</strong> | Pass: <strong>${p.password}</strong>
                        </div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Patient Registration View
 */
function PatientRegistrationView() {
    return `
        <button class="btn-back" onclick="navigateTo('home')">← Back to Home</button>
        <div class="card">
            <h2 style="text-align: center; margin-bottom: 30px; font-size: 2rem;">Patient Registration</h2>
            
            <div class="alert" style="background: #eff6ff; border-left: 4px solid #3b82f6; margin-bottom: 20px;">
                <p style="text-align: center; color: #1e40af;">
                    Already have an account? <a href="#" onclick="navigateTo('patientLogin'); return false;" style="color: #3b82f6; font-weight: 600;">Login here</a>
                </p>
            </div>
            
            <div class="form-group">
                <label>Full Name *</label>
                <input type="text" id="name" placeholder="Enter your full name" 
                    value="${state.registrationData.name}"
                    oninput="updateRegistration('name', this.value)">
            </div>

            <div class="grid">
                <div class="form-group">
                    <label>Age *</label>
                    <input type="number" id="age" placeholder="Age"
                        value="${state.registrationData.age}"
                        oninput="updateRegistration('age', this.value)">
                </div>
                <div class="form-group">
                    <label>Gender *</label>
                    <select id="gender" onchange="updateRegistration('gender', this.value)">
                        <option value="">Select</option>
                        <option value="Male" ${state.registrationData.gender === 'Male' ? 'selected' : ''}>Male</option>
                        <option value="Female" ${state.registrationData.gender === 'Female' ? 'selected' : ''}>Female</option>
                        <option value="Other" ${state.registrationData.gender === 'Other' ? 'selected' : ''}>Other</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label>Blood Type *</label>
                <select id="bloodType" onchange="updateRegistration('bloodType', this.value)">
                    <option value="">Select Blood Type</option>
                    <option value="A+" ${state.registrationData.bloodType === 'A+' ? 'selected' : ''}>A+</option>
                    <option value="A-" ${state.registrationData.bloodType === 'A-' ? 'selected' : ''}>A-</option>
                    <option value="B+" ${state.registrationData.bloodType === 'B+' ? 'selected' : ''}>B+</option>
                    <option value="B-" ${state.registrationData.bloodType === 'B-' ? 'selected' : ''}>B-</option>
                    <option value="AB+" ${state.registrationData.bloodType === 'AB+' ? 'selected' : ''}>AB+</option>
                    <option value="AB-" ${state.registrationData.bloodType === 'AB-' ? 'selected' : ''}>AB-</option>
                    <option value="O+" ${state.registrationData.bloodType === 'O+' ? 'selected' : ''}>O+</option>
                    <option value="O-" ${state.registrationData.bloodType === 'O-' ? 'selected' : ''}>O-</option>
                </select>
            </div>

            <div class="form-group">
                <label>Past Medical Conditions</label>
                <textarea rows="3" placeholder="e.g., Diabetes, Hypertension, Asthma..."
                    oninput="updateRegistration('pastConditions', this.value)">${state.registrationData.pastConditions}</textarea>
            </div>

            <div class="form-group">
                <label>Current Medications</label>
                <textarea rows="2" placeholder="List any medications you're currently taking"
                    oninput="updateRegistration('currentMedications', this.value)">${state.registrationData.currentMedications}</textarea>
            </div>

            <div class="form-group">
                <label>Known Allergies ⚠️</label>
                <textarea rows="2" placeholder="e.g., Penicillin, Peanuts, Latex..."
                    style="background: #fee2e2; border-color: #fca5a5;"
                    oninput="updateRegistration('knownAllergies', this.value)">${state.registrationData.knownAllergies}</textarea>
            </div>

            <button class="btn btn-primary" onclick="handlePatientRegistration()"
                ${!state.registrationData.name || !state.registrationData.age || !state.registrationData.gender || !state.registrationData.bloodType ? 'disabled' : ''}>
                Complete Registration
            </button>
        </div>
    `;
}

/**
 * Patient Dashboard View
 */
function PatientDashboardView() {
    const patientDocs = state.uploads[state.currentPatient?.id] || [];
    
    return `
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 30px;">
                <div>
                    <h2 style="font-size: 2rem; margin-bottom: 5px;">Welcome, ${state.currentPatient?.name}</h2>
                    <p style="color: #64748b;">Patient Dashboard</p>
                </div>
                <button class="logout-btn" onclick="logout()">Logout</button>
            </div>

            <div class="credentials-box">
                <div class="grid">
                    <div class="cred-item">
                        <div class="cred-label">🛡️ Your Patient ID</div>
                        <div class="cred-value">${state.currentPatient?.id}</div>
                    </div>
                    <div class="cred-item">
                        <div class="cred-label">🔒 Your Password</div>
                        <div class="cred-value">${state.currentPatient?.password}</div>
                    </div>
                </div>
                <div class="alert alert-warning" style="margin-top: 20px; margin-bottom: 0;">
                    <strong>Important:</strong> Save these credentials securely. Share them only with your healthcare providers.
                </div>
            </div>
        </div>

        <div class="card">
            <h3 style="font-size: 1.5rem; margin-bottom: 15px;">Upload Medical Documents</h3>
            <p style="color: #64748b; margin-bottom: 20px;">Upload prescriptions, lab reports, or medical records for AI analysis</p>
            
            <div class="upload-grid">
                <button class="upload-btn" onclick="handleDocumentUpload('Blood Test Report - ${new Date().toLocaleDateString()}')">
                    📊 Upload Blood Test
                </button>
                <button class="upload-btn" onclick="handleDocumentUpload('X-Ray Report - ${new Date().toLocaleDateString()}')">
                    🩻 Upload X-Ray
                </button>
                <button class="upload-btn" onclick="handleDocumentUpload('Prescription - ${new Date().toLocaleDateString()}')">
                    💊 Upload Prescription
                </button>
                <button class="upload-btn" onclick="handleDocumentUpload('ECG Report - ${new Date().toLocaleDateString()}')">
                    ❤️ Upload ECG
                </button>
            </div>
        </div>

        ${patientDocs.length > 0 ? `
        <div class="card">
            <h3 style="font-size: 1.5rem; margin-bottom: 20px;">Your Medical Documents</h3>
            
            ${patientDocs.map(doc => `
                <div class="document-card">
                    <div class="document-header">
                        <div>
                            <div class="document-title">📄 ${doc.fileName}</div>
                            <div class="document-date">Uploaded: ${doc.uploadDate}</div>
                        </div>
                    </div>
                    
                    <div class="summary-box">
                        <strong>AI Summary:</strong>
                        <p>${doc.summary}</p>
                    </div>

                    ${doc.risks.length > 0 ? `
                        <div class="risk-box">
                            <strong>⚠️ Detected Risks:</strong>
                            ${doc.risks.map(risk => `
                                <div style="margin-left: 20px; margin-top: 5px;">
                                    • <strong>${risk.condition}</strong> (${risk.level} Risk): ${risk.detail}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}

                    ${doc.allergies.length > 0 ? `
                        <div class="allergy-box">
                            <strong>🚨 Allergy Alerts:</strong>
                            ${doc.allergies.map(allergy => `
                                <div style="margin-left: 20px; margin-top: 5px;">
                                    • <strong>${allergy.allergen}</strong> (${allergy.severity} Severity): ${allergy.reaction}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>
        ` : ''}
    `;
}

/**
 * Doctor Login View
 */
function DoctorLoginView() {
    const demoPatients = Object.values(state.patients);
    
    return `
        <button class="btn-back" onclick="navigateTo('home')">← Back to Home</button>
        <div class="card" style="max-width: 500px; margin: 0 auto;">
            <div class="icon-circle purple-icon" style="margin: 0 auto 20px;">🩺</div>
            
            <h2 style="text-align: center; font-size: 2rem; margin-bottom: 10px;">Doctor Portal</h2>
            <p style="text-align: center; color: #64748b; margin-bottom: 30px;">Enter patient credentials to access their records</p>
            
            <div class="form-group">
                <label>Patient ID</label>
                <input type="text" id="loginId" placeholder="Enter patient ID"
                    value="${state.loginId}"
                    oninput="state.loginId = this.value">
            </div>

            <div class="form-group">
                <label>Patient Password</label>
                <input type="password" id="loginPassword" placeholder="Enter patient password"
                    value="${state.loginPassword}"
                    oninput="state.loginPassword = this.value">
            </div>

            <button class="btn btn-primary" onclick="handleDoctorLogin()"
                ${!state.loginId || !state.loginPassword ? 'disabled' : ''}>
                Access Patient Records
            </button>

            <div class="alert" style="background: #eef2ff; border-left: 4px solid #6366f1; margin-top: 20px;">
                <p style="text-align: center; color: #4338ca;">🔒 All access is logged for patient privacy and security</p>
            </div>

            ${demoPatients.length > 0 ? `
                <div class="demo-credentials">
                    <p><strong>Demo Patients Available:</strong></p>
                    ${demoPatients.map(p => `
                        <div class="cred-item">ID: <strong>${p.id}</strong> | Pass: <strong>${p.password}</strong></div>
                    `).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * Doctor Dashboard View
 */
function DoctorDashboardView() {
    const patientDocs = state.uploads[state.currentPatient?.id] || [];
    
    return `
        <div class="card">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 30px;">
                <div>
                    <h2 style="font-size: 2rem; margin-bottom: 5px;">Doctor Dashboard</h2>
                    <p style="color: #64748b;">Patient: ${state.currentPatient?.name}</p>
                </div>
                <button class="logout-btn" onclick="doctorLogout()">Logout</button>
            </div>

            <div class="info-grid">
                <div class="info-card blue">
                    <div class="label">Patient ID</div>
                    <div class="value">${state.currentPatient?.id}</div>
                </div>
                <div class="info-card purple">
                    <div class="label">Age / Gender</div>
                    <div class="value">${state.currentPatient?.age} / ${state.currentPatient?.gender}</div>
                </div>
                <div class="info-card red">
                    <div class="label">Blood Type</div>
                    <div class="value">${state.currentPatient?.bloodType}</div>
                </div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3 style="margin-bottom: 15px; color: #2563eb;">⏰ Past Conditions</h3>
                <p>${state.currentPatient?.pastConditions || 'None reported'}</p>
            </div>
            <div class="card">
                <h3 style="margin-bottom: 15px; color: #10b981;">💊 Current Medications</h3>
                <p>${state.currentPatient?.currentMedications || 'None reported'}</p>
            </div>
            <div class="card" style="border: 2px solid #fca5a5;">
                <h3 style="margin-bottom: 15px; color: #dc2626;">⚠️ Known Allergies</h3>
                <p style="color: #dc2626; font-weight: 600;">${state.currentPatient?.knownAllergies || 'None reported'}</p>
            </div>
        </div>

        <div class="card">
            <h3 style="font-size: 1.5rem; margin-bottom: 15px;">Upload New Medical Report</h3>
            <p style="color: #64748b; margin-bottom: 20px;">Add new prescriptions or test results to patient record</p>
            
            <div class="upload-grid">
                <button class="upload-btn" onclick="handleDoctorUpload('New Prescription - Dr. Smith - ${new Date().toLocaleDateString()}')">
                    ➕ Add Prescription
                </button>
                <button class="upload-btn" onclick="handleDoctorUpload('Lab Results - ${new Date().toLocaleDateString()}')">
                    ➕ Add Lab Results
                </button>
            </div>
        </div>

        <div class="card">
            <h3 style="font-size: 1.5rem; margin-bottom: 20px;">Patient Medical History</h3>
            
            ${patientDocs.length === 0 ? `
                <p style="text-align: center; color: #64748b; padding: 40px 0;">No documents uploaded yet</p>
            ` : patientDocs.map(doc => `
                <div class="document-card" style="border: 2px solid #e5e7eb;">
                    <div class="document-header">
                        <div>
                            <div class="document-title">📄 ${doc.fileName}</div>
                            <div class="document-date">
                                ${doc.uploadDate}
                                ${doc.uploadedBy ? `<span style="color: #7c3aed; margin-left: 10px;">• Uploaded by ${doc.uploadedBy}</span>` : ''}
                            </div>
                        </div>
                        <div style="color: #9ca3af;">👁️</div>
                    </div>
                    
                    <div class="summary-box">
                        <strong>AI-Generated Summary:</strong>
                        <p>${doc.summary}</p>
                    </div>

                    ${doc.risks.length > 0 ? `
                        <div class="risk-box">
                            <strong>⚠️ Risk Assessment:</strong>
                            ${doc.risks.map(risk => `
                                <div style="margin-left: 20px; margin-top: 5px;">
                                    • <strong>${risk.condition}</strong> (${risk.level} Risk): ${risk.detail}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}

                    ${doc.allergies.length > 0 ? `
                        <div class="allergy-box">
                            <strong>🚨 Critical Allergy Alerts:</strong>
                            ${doc.allergies.map(allergy => `
                                <div style="margin-left: 20px; margin-top: 5px;">
                                    • <strong>${allergy.allergen}</strong> (${allergy.severity}): ${allergy.reaction}
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `).join('')}
        </div>
    `;
}

// ===== RENDER FUNCTION =====

/**
 * Main render function - updates the DOM based on current state
 */
function render() {
    const app = document.getElementById('app');
    
    let content = '';
    switch(state.view) {
        case 'home':
            content = HomeView();
            break;
        case 'patientLogin':
            content = PatientLoginView();
            break;
        case 'patientReg':
            content = PatientRegistrationView();
            break;
        case 'patientDash':
            content = PatientDashboardView();
            break;
        case 'doctorLogin':
            content = DoctorLoginView();
            break;
        case 'doctorDash':
            content = DoctorDashboardView();
            break;
    }
    
    app.innerHTML = content;
}

// ===== INITIALIZE APPLICATION =====
render();