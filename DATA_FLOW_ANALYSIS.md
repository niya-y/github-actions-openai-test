# Complete Data Flow Analysis: Neulbom Care Application

## Executive Summary

This document traces the complete data flow through the Neulbom Care application, identifying how data is stored, transmitted, and transformed across frontend and backend systems. The analysis reveals several critical data consistency issues between sessionStorage keys, API request/response formats, and database field names.

---

## 1. PERSONALITY TEST FLOW

### 1.1 Frontend: /personality-test Page

**SessionStorage Operations:**
```typescript
// Line 282-283: personality-test/page.tsx
sessionStorage.setItem("personality_scores", JSON.stringify(normalizedScores))
sessionStorage.setItem("personality_answers", JSON.stringify(answers))
```

**Data Format Stored:**
```javascript
{
  empathy_score: number (0-100),
  activity_score: number (0-100),
  patience_score: number (0-100),
  independence_score: number (0-100)
}
```

**Answers Format:**
```javascript
{
  q1: "{\"empathy\": 5, \"activity\": 1, \"patience\": 4, \"independence\": 2}",
  q2: "{...}",
  // ... q3-q6
}
```

⚠️ **ISSUE #1: Answers stored as JSON strings, not parsed objects**
- Each answer value is a stringified JSON object
- Backend expects dict[str, str] to parse these strings

### 1.2 Frontend: /onboarding Page

**API Call Made:**
```typescript
// Line 44-47: onboarding/page.tsx
const response = await apiPost<any>('/personality/tests', {
    user_type: 'guardian',
    answers: personalityAnswers  // personalityAnswers = sessionStorage.getItem('personality_answers')
})
```

**Issue with Answers Structure:**
- Frontend sends `personalityAnswers` directly from sessionStorage
- This contains the stringified JSON format: `{q1: "{...}", q2: "{...}"}`
- Backend personality.py expects this exact format (lines 80-95)

### 1.3 Backend: POST /personality/tests

**Route Handler:**
```python
# Lines 24-29: backend/app/routes/personality.py
@router.post("/tests", status_code=status.HTTP_201_CREATED)
async def create_personality_test(
    request: PersonalityTestRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
)
```

**Request Schema:**
```python
# Lines 18-22: backend/app/schemas/personality.py
class PersonalityTestRequest(BaseModel):
    user_type: str = Field(..., pattern="^(guardian|caregiver)$")
    answers: dict = Field(..., description="12개 질문의 답변")
```

**Processing (Lines 80-95):**
```python
for question_id, score_json in request.answers.items():
    if isinstance(score_json, str):
        scores = json.loads(score_json)
    else:
        scores = score_json
    combined_scores["empathy"] += scores.get("empathy", 0)
    # ... accumulate other dimensions
```

**Score Normalization:**
```python
# Lines 98-112
max_score = question_count * 5  # 6 questions * 5 = 30
normalized_scores = {
    "empathy_score": min(100, (combined_scores["empathy"] / max_score) * 100),
    "activity_score": min(100, (combined_scores["activity"] / max_score) * 100),
    "patience_score": min(100, (combined_scores["patience"] / max_score) * 100),
    "independence_score": min(100, (combined_scores["independence"] / max_score) * 100)
}
```

**Database Storage:**
```python
# Lines 183-200
personality_record = PatientPersonality(
    patient_id=entity_id,
    empathy_score=result['empathy_score'],
    activity_score=result['activity_score'],
    patience_score=result['patience_score'],
    independence_score=result['independence_score']
)
db.add(personality_record)
db.commit()
```

✅ **Correct: Normalized scores (0-100) stored in database**

### 1.4 Frontend: /caregiver-finder Page

**SessionStorage Retrieval:**
```typescript
// Lines 72-86: caregiver-finder/page.tsx
const personalityScoresStr = sessionStorage.getItem('personality_scores')
let personalityScores = {
    empathy_score: 50,
    activity_score: 50,
    patience_score: 50,
    independence_score: 50
}

if (personalityScoresStr) {
    personalityScores = JSON.parse(personalityScoresStr)
}
```

**API Request Payload:**
```typescript
// Lines 89-104
const payload = {
    patient_id: parseInt(patientId),
    patient_personality: personalityScores,  // ✅ Correct format
    preferred_days: preferredDays,
    preferred_time_slots: timeSlots,
    care_start_date: careStartDate || null,
    care_end_date: careEndDate || null,
    requirements: {
        care_type: careType,
        time_slots: timeSlots,
        gender: gender,
        experience: experience,
        skills: skills
    },
    top_k: 5
}
```

---

## 2. PATIENT INFORMATION FLOW

### 2.1 Frontend: /patient-condition-1 Page

**Form Collection:**
```typescript
// Lines 12-18
const formData = {
    name: '',
    birthDate: '',
    gender: 'Female',  // Frontend uses 'Male'/'Female'
    relationship: '',
    isDirectInput: false
}
```

**API Call:**
```typescript
// Lines 39-47: patient-condition-1/page.tsx
const response = await apiPost<PatientResponse>(
    '/api/patients',
    {
        name: formData.name,
        age: age,  // Calculated from birthDate
        gender: formData.gender.toLowerCase(),  // ✅ Converts to 'male'/'female'
        relationship: formData.relationship
    }
)
```

⚠️ **ISSUE #2: Relationship field in request but not used in backend**
- Frontend sends `relationship` field
- Backend doesn't use it (line 40-76 in patients.py)
- Database schema expects it elsewhere (Guardian model)

**SessionStorage:**
```typescript
// Line 52
sessionStorage.setItem('patient_id', response.patient_id.toString())
```

### 2.2 Backend: POST /api/patients

**Request Schema:**
```python
# Lines 77-89: backend/app/schemas/patient.py
class PatientCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    age: int = Field(..., ge=0, le=150)
    gender: str = Field(..., pattern=r'^(male|female)$')
    relationship: str = Field(...)
```

**Gender Validator:**
```python
# Lines 84-89
@field_validator('gender')
@classmethod
def convert_gender(cls, v: str) -> str:
    mapping = {'female': 'Female', 'male': 'Male'}
    return mapping.get(v, v)
```

**Processing:**
```python
# Lines 50-61: patients.py
current_year = date.today().year
birth_date = date(current_year - request.age, 1, 1)

patient = Patient(
    guardian_id=guardian.guardian_id,
    name=request.name,
    birth_date=birth_date,  # ✅ Reconstructed from age
    gender=request.gender,  # 'Male' or 'Female'
    care_address=guardian.address,  # Uses guardian's address
    region_code="TBD"
)
```

**Response:**
```python
# Lines 68-76
return PatientInfoResponse(
    patient_id=patient.patient_id,
    name=patient.name,
    birth_date=patient.birth_date.isoformat(),
    age=request.age,
    gender=patient.gender.value,  # Enum.value
    guardian_id=guardian.guardian_id,
    created_at=patient.created_at.isoformat()
)
```

### 2.3 Frontend: /patient-condition-2 Page

**Health Data Collection:**
```typescript
// Lines 28-32
const [selectedDiseases, setSelectedDiseases] = useState<DiseaseItem[]>([])
const [selectedMobility, setSelectedMobility] = useState<string>('')
const [otherDisease, setOtherDisease] = useState('')
```

**Data Structure:**
```typescript
// DiseaseItem = { id: string, name: string }
```

**API Call:**
```typescript
// Lines 65-70
const payload: HealthStatusUpdateRequest = {
    selectedDiseases: selectedDiseases,  // DiseaseItem[]
    mobility_status: selectedMobility    // string like 'independent', 'wheelchair'
}

await apiPut<HealthConditionResponse>(
    `/api/patients/${patientId}/health-status`,
    payload
)
```

### 2.4 Backend: PUT /api/patients/{patient_id}/health-status

**Request Schema:**
```python
# Lines 103-106: backend/app/schemas/patient.py
class HealthStatusUpdateRequest(BaseModel):
    selectedDiseases: List[DiseaseItem]
    mobility_status: str
```

**Processing:**
```python
# Lines 110-129: patients.py
for disease in request.selectedDiseases:
    if hasattr(disease, 'model_dump'):
        disease_dict = disease.model_dump()
    else:
        disease_dict = disease.dict() if hasattr(disease, 'dict') else dict(disease)

    disease_name = disease_dict.get('name', disease_dict.get('id', 'Unknown'))

    health_condition = HealthCondition(
        patient_id=patient_id,
        disease_name=disease_name,
        note=f"Mobility: {request.mobility_status}"
    )
    db.add(health_condition)
```

**Issues:**
- Disease objects are converted to dict
- Only disease name stored, not full structure
- Mobility status added to `note` field, not dedicated column

### 2.5 Frontend: /patient-condition-3 Page

**Medication Collection:**
```typescript
// Lines 13-14
const [currentMed, setCurrentMed] = useState('')
const [medicine_names, setMedicineNames] = useState<string[]>([])
```

**API Call:**
```typescript
// Lines 44-52
const payload: MedicationsCreateRequest = {
    medicine_names: medicine_names  // string[]
}

const response = await apiPost<MedicationResponse>(
    `/api/patients/${patientId}/medications`,
    payload
)
```

### 2.6 Backend: POST /api/patients/{patient_id}/medications

**Processing:**
```python
# Lines 173-188: patients.py
medication = Medication(
    patient_id=patient_id,
    name=None,
    dosage=None,
    frequency=None,
    intake_method=None
)

if hasattr(medication, 'medicine_names'):
    medication.medicine_names = request.medicine_names
```

⚠️ **ISSUE #3: Field existence checked with hasattr()**
- Code assumes `medicine_names` field might not exist
- Creates record with NULL values for standard fields
- Medication model may lack medicine_names column

---

## 3. CAREGIVER MATCHING FLOW

### 3.1 Frontend: /caregiver-finder → /caregiver-result-loading

**Data from SessionStorage:**
```typescript
// Line 42
const patientId = sessionStorage.getItem('patient_id')
```

**Matching Request:**
```typescript
// Lines 89-104
const payload = {
    patient_id: parseInt(patientId),
    patient_personality: {
        empathy_score: 50-100,
        activity_score: 50-100,
        patience_score: 50-100,
        independence_score: 50-100
    },
    preferred_days: ['Monday', 'Tuesday', ...],
    preferred_time_slots: ['morning', 'afternoon', ...],
    care_start_date: string | null,
    care_end_date: string | null,
    requirements: {
        care_type: 'nursing-aide' | 'nursing-assistant' | 'nurse',
        time_slots: string[],
        gender: 'Male' | 'Female' | 'any',
        experience: string,
        skills: string[]
    },
    top_k: 5
}

// Line 109
await apiPost<any>('/api/matching/recommend-xgboost', payload)
```

### 3.2 Backend: POST /api/matching/recommend-xgboost

**Request Schema:**
```python
# Lines 77-94: backend/app/routes/xgboost_matching.py
class XGBoostMatchingRequest(BaseModel):
    patient_id: int
    patient_personality: PersonalityScores  # empathy_score, activity_score, etc.
    requirements: Optional[MatchingRequirements]
    preferred_days: List[str]
    preferred_time_slots: List[str]
    care_start_date: Optional[date]
    care_end_date: Optional[date]
    top_k: int
```

**Processing (Lines 156-204):**
```python
# 1. Extract care type
care_type = request.requirements.care_type
cert_keyword = CARE_TYPE_TO_CERTIFICATION.get(care_type, '요양보호사')

# 2. Query caregivers from database
caregivers = db.query(Caregiver).join(User).outerjoin(CaregiverPersonality).filter(
    Caregiver.certifications.ilike(f'%{cert_keyword}%')
).limit(request.top_k).all()

# 3. Build caregiver data with personality
for caregiver in caregivers:
    job_title = extract_matching_job_title(caregiver.certifications, cert_keyword)
    personality = caregiver.personality
    caregivers_with_personality.append({
        "caregiver_id": caregiver.caregiver_id,
        "caregiver_name": caregiver.user.name,
        "job_title": job_title,
        "experience_years": caregiver.experience_years,
        "empathy_score": personality.empathy_score if personality else 50,
        "activity_score": personality.activity_score if personality else 50,
        "patience_score": personality.patience_score if personality else 50,
        "independence_score": personality.independence_score if personality else 50,
        "hourly_rate": caregiver.hourly_rate or 25000,
        "avg_rating": caregiver.avg_rating or 4.5,
        "profile_image_url": caregiver.user.profile_image_url or ""
    })

# 4. Run XGBoost matching service
recommendations = EnhancedMatchingService.recommend_caregivers_xgboost(
    patient_id=request.patient_id,
    patient_personality={...},
    caregivers_with_personality=caregivers_with_personality,
    limit=request.top_k
)

# 5. Format and save matching request
matching_request = MatchingRequest(
    patient_id=request.patient_id,
    required_qualification=request.requirements.care_type,
    preferred_regions=None,
    preferred_days=request.preferred_days,
    preferred_time_slots=request.preferred_time_slots,
    care_start_date=request.care_start_date,
    care_end_date=request.care_end_date,
    additional_request=None,
    is_active=True
)
```

**Response:**
```python
# Lines 113-119
class XGBoostMatchingResponse(BaseModel):
    patient_id: int
    total_matches: int
    matches: List[CaregiverMatchResult]
    algorithm_version: str = "XGBoost_v3"
    timestamp: datetime
```

### 3.3 Frontend: /caregiver-result-loading → /caregiver-result-list

**SessionStorage:**
```typescript
// Line 116: caregiver-finder/page.tsx
sessionStorage.setItem('matching_results', JSON.stringify(response))
```

**Result Display (caregiver-result-list):**
```typescript
// Lines 20-29
const storedResults = sessionStorage.getItem('matching_results')
if (storedResults) {
    try {
        const parsed: MatchingResponse = JSON.parse(storedResults)
        if (parsed.matches && parsed.matches.length > 0) {
            setMatches(parsed.matches)
            setTotalCount(parsed.total_count)
            setLoading(false)
            return
        }
    } catch (e) {
        console.error('세션 스토리지 파싱 오류:', e)
    }
}
```

**Caregiver Selection:**
```typescript
// Lines 78-85
const handleSelectCaregiver = (caregiver: CaregiverMatch) => {
    sessionStorage.setItem('selectedCaregiver', JSON.stringify(caregiver))
    if (caregiver.matching_id) {
        sessionStorage.setItem('matching_id', caregiver.matching_id.toString())
    }
    router.push('/mypage-mycaregiver')
}
```

---

## 4. CARE PLAN GENERATION FLOW

### 4.1 Frontend: /care-plans-create Page

**Data Collection (useEffect on mount):**
```typescript
// Lines 25-35
const patientId = sessionStorage.getItem('patient_id')
const matchingId = sessionStorage.getItem('matching_id')
const selectedCaregiverStr = sessionStorage.getItem('selectedCaregiver')
const personalityScoresStr = sessionStorage.getItem('personality_scores')
```

**API Request:**
```typescript
// Lines 50-67
const requestPayload = {
    patient_id: parseInt(patientId),
    caregiver_id: selectedCaregiver.caregiver_id,
    patient_personality: personalityScores,
    care_requirements: {
        care_type: 'nursing-aide',
        time_slots: ['morning', 'afternoon'],
        gender: 'any',
        skills: []
    }
}

const response = await apiPost<any>(
    '/api/care-plans/generate',
    requestPayload
)
```

⚠️ **ISSUE #4: Care requirements hardcoded**
- Not using actual values from caregiver-finder page
- Static values don't reflect user's selections

### 4.2 Backend: POST /api/care-plans/generate

**Route Handler:**
```python
# Lines 29-133: backend/app/routes/care_plans.py
@router.post("/generate")
async def generate_care_plan(
    request: CarePlanGenerationRequest,
    db: Session = Depends(get_db)
)
```

**Request Schema:**
```python
# Lines 21-26
class CarePlanGenerationRequest(BaseModel):
    patient_id: int
    caregiver_id: int
    patient_personality: dict
    care_requirements: dict
```

**Processing:**
```python
# Lines 64-88
patient = db.query(Patient).filter(Patient.patient_id == request.patient_id).first()
if not patient:
    raise HTTPException(status_code=404, detail="환자 정보를 찾을 수 없습니다")

patient_user = db.query(User).filter(User.user_id == patient.user_id).first()

caregiver = db.query(Caregiver).filter(
    Caregiver.caregiver_id == request.caregiver_id
).first()
if not caregiver:
    raise HTTPException(status_code=404, detail="간병인 정보를 찾을 수 없습니다")

caregiver_user = db.query(User).filter(User.user_id == caregiver.user_id).first()
```

⚠️ **ISSUE #5: No user_id in Patient model**
- Line 73-74 tries to query User where user_id == patient.user_id
- Patient model doesn't have user_id field
- This will fail with error

**Data Preparation:**
```python
# Lines 91-106
patient_info = {
    "id": patient.patient_id,
    "name": patient_user.name if patient_user else "환자",
    "age": patient.age,
    "condition": patient.care_level or "일반",
    "special_conditions": patient.medical_conditions or ""
}

caregiver_info = {
    "id": caregiver.caregiver_id,
    "name": caregiver_user.name if caregiver_user else "간병인",
    "experience_years": caregiver.experience_years or 0,
    "specialties": caregiver.specialties.split("|") if caregiver.specialties else [],
    "hourly_rate": caregiver.hourly_rate or 0
}
```

**AI Service Call:**
```python
# Lines 108-115
service = CarePlanGenerationService()
care_plan = service.generate_care_plan(
    patient_info=patient_info,
    caregiver_info=caregiver_info,
    patient_personality=request.patient_personality,
    care_requirements=request.care_requirements
)
```

---

## 5. DATA MAPPING SUMMARY TABLE

| Feature | Frontend Key | Frontend Type | API Field | API Type | Backend Model | DB Field | Status |
|---------|-------------|--------------|-----------|----------|---------------|----------|--------|
| **Personality Scores** | personality_scores | JSON string | patient_personality | PersonalityScores | PatientPersonality | empathy_score, activity_score, patience_score, independence_score | ✅ |
| **Patient ID** | patient_id | string | patient_id | int | Patient | patient_id | ✅ |
| **Patient Name** | (form) | string | name | string | Patient | name | ✅ |
| **Patient Gender** | gender (Male/Female) | string | gender (male/female) | string | Patient | gender (Enum) | ⚠️ Format mismatch |
| **Patient Age** | birthDate | date string | age | int | - | - | ⚠️ No age field in DB |
| **Patient Relationship** | relationship | string | relationship | string | Guardian | relationship | ✅ Correct model |
| **Diseases** | selectedDiseases | DiseaseItem[] | selectedDiseases | DiseaseItem[] | HealthCondition | disease_name + note | ⚠️ Incomplete storage |
| **Mobility Status** | selectedMobility | string | mobility_status | string | HealthCondition | note field | ⚠️ Embedded in note |
| **Medicines** | medicine_names | string[] | medicine_names | string[] | Medication | medicine_names | ⚠️ Field existence checked |
| **Matching ID** | matching_id | string | - | - | MatchingRequest | request_id | ✅ |
| **Selected Caregiver** | selectedCaregiver | JSON string | caregiver_id | int | - | - | ✅ |
| **Care Dates** | careStartDate/careEndDate | date strings | care_start_date/care_end_date | date | MatchingRequest | care_start_date/care_end_date | ✅ |
| **Time Slots** | preferred_time_slots | string[] | preferred_time_slots | string[] | MatchingRequest | preferred_time_slots | ✅ |
| **Preferred Days** | preferred_days | string[] | preferred_days | string[] | MatchingRequest | preferred_days | ✅ |

---

## 6. IDENTIFIED ISSUES & INCONSISTENCIES

### CRITICAL ISSUES

#### Issue #1: Missing Patient.user_id Field
**Location:** care_plans.py:73-74
**Code:**
```python
patient_user = db.query(User).filter(User.user_id == patient.user_id).first()
```
**Problem:** Patient model doesn't have user_id field
**Impact:** Care plan generation will crash with AttributeError
**Solution:** Use guardian's user_id instead:
```python
patient_user = db.query(User).join(Guardian).filter(
    Guardian.guardian_id == patient.guardian_id
).first()
```

#### Issue #2: Care Requirements Hardcoded
**Location:** care-plans-create/page.tsx:54-59
**Code:**
```typescript
care_requirements: {
    care_type: 'nursing-aide',
    time_slots: ['morning', 'afternoon'],
    gender: 'any',
    skills: []
}
```
**Problem:** Static values don't reflect user's actual selections from caregiver-finder
**Impact:** AI-generated care plan not based on actual requirements
**Solution:** Store care_requirements in sessionStorage during matching request

#### Issue #3: Health Condition Storage Incomplete
**Location:** patients.py:110-129
**Code:**
```python
for disease in request.selectedDiseases:
    disease_name = disease_dict.get('name', disease_dict.get('id', 'Unknown'))
    health_condition = HealthCondition(
        patient_id=patient_id,
        disease_name=disease_name,
        note=f"Mobility: {request.mobility_status}"
    )
```
**Problem:**
- Only disease name stored, not full structure
- Mobility status mixed into note field
- No dedicated mobility_status column
**Impact:** Data retrieval requires parsing string notes
**Solution:** Add mobility_status column to HealthCondition model

#### Issue #4: Medication Field Uncertainty
**Location:** patients.py:183-189
**Code:**
```python
if hasattr(medication, 'medicine_names'):
    medication.medicine_names = request.medicine_names
```
**Problem:** Assumes medicine_names field might not exist
**Impact:** Unclear data model; field may not persist to database
**Solution:** Define field explicitly in Medication model

### MODERATE ISSUES

#### Issue #5: Gender Format Inconsistency
**Frontend:** 'Male' | 'Female'
**Backend Request:** 'male' | 'female'
**Backend Storage:** Enum (Male/Female)
**Problem:** Multiple transformations with potential loss points

#### Issue #6: Personality Answers Storage Format
**Frontend SessionStorage:** `{q1: "{...}", q2: "{...}"}`  (stringified JSON)
**Backend Processing:** Expects dict with JSON strings
**Problem:** Inefficient double-encoding; could be simplified

#### Issue #7: Age Calculation
**Frontend:** Sends calculated age from birthDate
**Backend:** Reconstructs birthDate from age (loses exact date)
**Problem:** Year-only precision; all patients born January 1st of reconstructed year

---

## 7. SESSIONSTORATE KEY INVENTORY

| Key | Set Location | Use Location | Format | Issues |
|-----|--------------|--------------|--------|--------|
| patient_id | patient-condition-1 | caregiver-finder, care-plans-create | string (int) | ✅ Consistent |
| personality_scores | personality-test | caregiver-finder, care-plans-create | JSON string | ✅ Consistent |
| personality_answers | personality-test | onboarding | JSON string | ✅ Internal use |
| matching_results | caregiver-finder | caregiver-result-list | JSON string | ✅ Consistent |
| selectedCaregiver | caregiver-result-list | care-plans-create, mypage-mycaregiver | JSON string | ✅ Consistent |
| matching_id | caregiver-result-list | care-plans-create-3 | string (int) | ✅ Consistent |
| onboarded | onboarding | (not used for routing) | string 'true' | ⚠️ localStorage, not sessionStorage |
| guardian_id | guardians | (not clearly used) | string (int) | ⚠️ Unused after initialization |

---

## 8. API ENDPOINT VALIDATION

### Request/Response Matching

#### ✅ POST /api/patients
- Frontend sends: PatientCreateRequest (name, age, gender, relationship)
- Backend expects: PatientCreateRequest
- Backend returns: PatientInfoResponse
- Frontend expects: PatientResponse (compatible)

#### ✅ PUT /api/patients/{id}/health-status
- Frontend sends: HealthStatusUpdateRequest (selectedDiseases[], mobility_status)
- Backend expects: HealthStatusUpdateRequest
- Backend returns: success response
- Status: ✅ Matches

#### ✅ POST /api/patients/{id}/medications
- Frontend sends: MedicationsCreateRequest (medicine_names[])
- Backend expects: MedicationsCreateRequest
- Backend returns: MedicationInfoResponse
- Status: ✅ Matches

#### ❌ POST /personality/tests
- Frontend sends: PersonalityTestRequest (user_type, answers)
- answers format: {q1: "{...}", q2: "{...}"}
- Backend expects: PersonalityTestRequest with same format
- Status: ✅ Matches (but inefficient format)

#### ⚠️ POST /api/matching/recommend-xgboost
- Frontend sends: XGBoostMatchingRequest
- Fields:
  - patient_personality: PersonalityScores ✅
  - preferred_days: string[] ✅
  - preferred_time_slots: string[] ✅
  - care_start_date: date | null ✅
  - care_end_date: date | null ✅
  - requirements: MatchingRequirements ✅
- Status: ✅ Matches

#### ❌ POST /api/care-plans/generate
- Frontend sends: CarePlanGenerationRequest
- Issues:
  - care_requirements: hardcoded static values
  - patient_personality: from sessionStorage
  - No matching_id passed (but saved separately)
- Backend expects:
  - patient_id ✅
  - caregiver_id ✅
  - patient_personality ✅
  - care_requirements (expects valid but receives static)
- Backend issue: patient.user_id doesn't exist
- Status: ❌ Broken data flow

---

## 9. RECOMMENDATIONS

### High Priority
1. **Fix Patient.user_id reference** - Add field or use Guardian relationship
2. **Pass actual care requirements** - Store during matching, retrieve for care plan
3. **Add mobility_status column** - Stop embedding in note field
4. **Ensure Medication.medicine_names field** - Remove hasattr check, define explicitly

### Medium Priority
5. **Simplify personality answers storage** - Remove JSON stringification
6. **Use consistent date formats** - Preserve full birth date, don't calculate age
7. **Add data validation endpoints** - Return detailed field validation errors
8. **Document sessionStorage lifecycle** - Clear on logout, validate on page load

### Low Priority
9. **Optimize personality score normalization** - Consider caching calculated values
10. **Add matching_id to response immediately** - Don't wait for result list

---

## 10. DATA PERSISTENCE CHECKLIST

- [ ] SessionStorage cleared on logout
- [ ] API calls include Authorization header
- [ ] Database constraints enforced
- [ ] Foreign key relationships validated
- [ ] Enum conversions tested
- [ ] JSON parsing error handling
- [ ] Age calculation precision tested
- [ ] Disease list retrieval and updates
- [ ] Medication data persistence verified
- [ ] Care plan generation with complete requirements

---

## APPENDIX: Model Field Reference

### Patient
- patient_id (PK)
- guardian_id (FK)
- name
- birth_date (DATE - not age)
- gender (Enum: Male/Female)
- care_address
- region_code
- care_level (optional)
- **Missing: user_id**

### HealthCondition
- condition_id (PK)
- patient_id (FK)
- disease_name (VARCHAR)
- note (TEXT - contains mobility info)
- **Missing: dedicated mobility_status field**

### Medication
- med_id (PK)
- patient_id (FK)
- name, dosage, frequency, intake_method (mostly NULL)
- **Unclear: medicine_names field**

### PatientPersonality
- personality_id (PK)
- patient_id (FK)
- empathy_score (0-100)
- activity_score (0-100)
- patience_score (0-100)
- independence_score (0-100)

### MatchingRequest
- request_id (PK)
- patient_id (FK)
- required_qualification
- preferred_regions
- preferred_days (TEXT[])
- preferred_time_slots (TEXT[])
- care_start_date (DATE)
- care_end_date (DATE)
- additional_request
- is_active

