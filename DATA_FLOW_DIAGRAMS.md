# Data Flow Diagrams & Mappings

## 1. Complete User Journey & Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           COMPLETE USER FLOW                                 │
└─────────────────────────────────────────────────────────────────────────────┘

   STEP 1: PERSONALITY TEST
   ══════════════════════════
   
   /personality-test Page
   ├─ 6 situational questions
   ├─ 4 dimensions: empathy, activity, patience, independence
   └─ Each answer: 3 options with weighted scores
      └─ Calculate normalized scores (0-100)
      └─ Store to sessionStorage
         ├─ personality_scores: {empathy_score: 75, ...}
         ├─ personality_answers: {q1: "{...}", q2: "{...}"}
      └─ Navigate to /login
   
   ↓
   
   STEP 2: AUTHENTICATION
   ══════════════════════
   
   /login → /onboarding
   ├─ User logs in
   ├─ Fetch user info: GET /auth/me
   ├─ POST /personality/tests
   │  └─ Request: {user_type: "guardian", answers: {...}}
   │  └─ Backend normalizes and saves
   │  └─ Response: {empathy_score, activity_score, ...}
   └─ Navigate to /home
   
   ↓
   
   STEP 3: PATIENT INFORMATION
   ════════════════════════════
   
   /patient-condition-1
   ├─ Form: name, birthDate, gender, relationship
   ├─ Calculate age = currentYear - birthYear
   ├─ POST /api/patients
   │  └─ Request: {name, age, gender, relationship}
   │  └─ Backend creates Patient record
   │  └─ Response: {patient_id, name, gender, ...}
   ├─ Store to sessionStorage: patient_id = "123"
   └─ Navigate to /patient-condition-2
   
   ↓
   
   /patient-condition-2
   ├─ Form: select diseases (multi), select mobility status
   ├─ PUT /api/patients/{patient_id}/health-status
   │  └─ Request: {selectedDiseases: [{id, name}], mobility_status}
   │  └─ Backend saves to HealthCondition table
   │  └─ Response: {patient_id, selected_diseases, mobility_status}
   └─ Navigate to /patient-condition-3
   
   ↓
   
   /patient-condition-3
   ├─ Form: enter medication names (array)
   ├─ POST /api/patients/{patient_id}/medications
   │  └─ Request: {medicine_names: ["aspirin", "metformin"]}
   │  └─ Backend saves to Medication table
   │  └─ Response: {patient_id, med_id, medicine_names}
   └─ Navigate to /caregiver-finder
   
   ↓
   
   STEP 4: CAREGIVER MATCHING
   ════════════════════════════
   
   /caregiver-finder
   ├─ Form inputs:
   │  ├─ Care type: nursing-aide / nursing-assistant / nurse
   │  ├─ Preferred time slots: morning, afternoon, evening, night
   │  ├─ Preferred days: Monday, Tuesday, ... Sunday
   │  ├─ Gender preference: any, Male, Female
   │  ├─ Experience level: <1yr, 1-3yr, 3-5yr, 5+yr
   │  ├─ Skills: dementia, diabetes, bedsore, suction
   │  ├─ Care period: start_date, end_date
   │  └─ Budget: (optional)
   │
   ├─ Retrieve from sessionStorage:
   │  └─ personality_scores
   │  └─ patient_id
   │
   ├─ POST /api/matching/recommend-xgboost
   │  ├─ Request: {
   │  │    patient_id: 123,
   │  │    patient_personality: {empathy_score, activity_score, ...},
   │  │    requirements: {care_type, time_slots, gender, ...},
   │  │    preferred_days: [...],
   │  │    preferred_time_slots: [...],
   │  │    care_start_date: "2025-01-15",
   │  │    care_end_date: "2025-06-15",
   │  │    top_k: 5
   │  │  }
   │  │
   │  ├─ Backend:
   │  │  ├─ Query Caregiver table by care_type
   │  │  ├─ Fetch personality scores for each caregiver
   │  │  ├─ Run XGBoost matching algorithm
   │  │  ├─ Format results with scores
   │  │  └─ Save MatchingRequest to database
   │  │
   │  └─ Response: {
   │     patient_id, 
   │     total_matches: 5,
   │     matches: [{caregiver_id, name, grade, match_score, ...}]
   │  }
   │
   ├─ Store to sessionStorage: matching_results
   └─ Navigate to /caregiver-result-loading → /caregiver-result-list
   
   ↓
   
   /caregiver-result-list
   ├─ Retrieve from sessionStorage: matching_results
   ├─ Display matched caregivers with scores
   ├─ User selects one caregiver
   ├─ Store to sessionStorage:
   │  ├─ selectedCaregiver: {caregiver_id, name, ...}
   │  └─ matching_id: "456"
   └─ Navigate to /care-plans-create
   
   ↓
   
   STEP 5: CARE PLAN GENERATION
   ═════════════════════════════
   
   /care-plans-create
   ├─ Retrieve from sessionStorage:
   │  ├─ patient_id
   │  ├─ matching_id (optional)
   │  ├─ selectedCaregiver (extract caregiver_id)
   │  └─ personality_scores
   │
   ├─ ❌ ISSUE: care_requirements hardcoded instead of from sessionStorage
   │
   ├─ POST /api/care-plans/generate
   │  ├─ Request: {
   │  │    patient_id: 123,
   │  │    caregiver_id: 456,
   │  │    patient_personality: {...},
   │  │    care_requirements: {...}  ← HARDCODED
   │  │  }
   │  │
   │  ├─ ❌ Backend tries: patient.user_id (doesn't exist)
   │  │
   │  └─ Response: {success, data: {weekly_schedule, ...}}
   │
   └─ Store: care_plan in state/sessionStorage
```

---

## 2. Personality Test Data Transformation

```
┌─────────────────────────────────────────────────────────────────┐
│  PERSONALITY TEST: Data Format Changes                          │
└─────────────────────────────────────────────────────────────────┘

STEP 1: Frontend Question Selection
───────────────────────────────────
Question: "환자분이 우울해 보일 때, 당신은 주로 어떻게 하나요?"

User selects option:
"먼저 어떤 기분인지 물어보고 이야기를 들어주기"
  ↓
  Scores: {
    empathy: 5,
    activity: 1,
    patience: 4,
    independence: 2
  }


STEP 2: Accumulate All Answers
──────────────────────────────
Q1 Scores: empathy: 5, activity: 1, patience: 4, independence: 2
Q2 Scores: empathy: 3, activity: 4, patience: 2, independence: 1
Q3 Scores: empathy: 4, activity: 1, patience: 5, independence: 3
Q4 Scores: empathy: 3, activity: 4, patience: 5, independence: 4
Q5 Scores: empathy: 5, activity: 1, patience: 4, independence: 2
Q6 Scores: empathy: 5, activity: 5, patience: 3, independence: 5
────────────────────────────────────────────────────────
TOTAL:    empathy: 25, activity: 16, patience: 23, independence: 17


STEP 3: Store to SessionStorage
────────────────────────────────
sessionStorage.setItem("personality_answers", JSON.stringify({
  q1: "{\"empathy\": 5, \"activity\": 1, \"patience\": 4, \"independence\": 2}",
  q2: "{\"empathy\": 3, \"activity\": 4, \"patience\": 2, \"independence\": 1}",
  q3: "{\"empathy\": 4, \"activity\": 1, \"patience\": 5, \"independence\": 3}",
  q4: "{\"empathy\": 3, \"activity\": 4, \"patience\": 5, \"independence\": 4}",
  q5: "{\"empathy\": 5, \"activity\": 1, \"patience\": 4, \"independence\": 2}",
  q6: "{\"empathy\": 5, \"activity\": 5, \"patience\": 3, \"independence\": 5}"
}))

sessionStorage.setItem("personality_scores", JSON.stringify({
  empathy_score: 83.3,
  activity_score: 53.3,
  patience_score: 76.7,
  independence_score: 56.7
}))


STEP 4: Send to Backend
───────────────────────
POST /personality/tests
{
  user_type: "guardian",
  answers: {
    q1: "{\"empathy\": 5, \"activity\": 1, \"patience\": 4, \"independence\": 2}",
    q2: "{\"empathy\": 3, \"activity\": 4, \"patience\": 2, \"independence\": 1}",
    q3: "{\"empathy\": 4, \"activity\": 1, \"patience\": 5, \"independence\": 3}",
    q4: "{\"empathy\": 3, \"activity\": 4, \"patience\": 5, \"independence\": 4}",
    q5: "{\"empathy\": 5, \"activity\": 1, \"patience\": 4, \"independence\": 2}",
    q6: "{\"empathy\": 5, \"activity\": 5, \"patience\": 3, \"independence\": 5}"
  }
}


STEP 5: Backend Processing
──────────────────────────
for question_id, score_json in request.answers.items():
    scores = json.loads(score_json)  # Parse: "{...}" → {...}
    combined_scores["empathy"] += scores["empathy"]
    # ... accumulate others

max_score = 6 * 5 = 30
empathy_score = (25 / 30) * 100 = 83.3
activity_score = (16 / 30) * 100 = 53.3
patience_score = (23 / 30) * 100 = 76.7
independence_score = (17 / 30) * 100 = 56.7


STEP 6: Save to Database
────────────────────────
INSERT INTO patient_personalities (
  patient_id, 
  empathy_score, 
  activity_score, 
  patience_score, 
  independence_score
) VALUES (
  123, 
  83.3, 
  53.3, 
  76.7, 
  56.7
)


STEP 7: Retrieve for Matching
─────────────────────────────
GET from sessionStorage: personality_scores
{
  empathy_score: 83.3,
  activity_score: 53.3,
  patience_score: 76.7,
  independence_score: 56.7
}
  ↓
POST /api/matching/recommend-xgboost
{
  patient_personality: {
    empathy_score: 83.3,
    activity_score: 53.3,
    patience_score: 76.7,
    independence_score: 56.7
  },
  ...
}
```

---

## 3. Patient Information Data Structure

```
┌────────────────────────────────────────────────────┐
│  PATIENT INFO: Complete Data Storage Flow          │
└────────────────────────────────────────────────────┘

PATIENT-CONDITION-1
───────────────────
Form Input:
├─ Name: "김영희"
├─ Birth Date: "1950-03-15"
├─ Gender: "Female"
└─ Relationship: "어머니"

Frontend Processing:
├─ Calc age = 2025 - 1950 = 75
├─ API sends:
│  ├─ name: "김영희"
│  ├─ age: 75
│  ├─ gender: "female"  ← lowercase
│  └─ relationship: "어머니"
└─ sessionStorage.setItem("patient_id", "123")

Backend Processing (patients.py:50-61):
├─ Validate gender (female → Female via validator)
├─ Reconstruct birth_date = date(1950, 1, 1)  ← LOSES EXACT DATE!
├─ Create Patient:
│  ├─ patient_id: 123
│  ├─ guardian_id: 456 (from current user)
│  ├─ name: "김영희"
│  ├─ birth_date: 1950-01-01  (NOT 1950-03-15!)
│  ├─ gender: Female (Enum)
│  ├─ care_address: (from guardian)
│  └─ region_code: "TBD"
└─ Ignore relationship field

Database (patients table):
├─ patient_id: 123
├─ guardian_id: 456
├─ name: "김영희"
├─ birth_date: 1950-01-01
├─ gender: 'Female'
├─ care_address: "Seoul, Korea"
└─ region_code: "TBD"


PATIENT-CONDITION-2
───────────────────
Form Input:
├─ Selected Diseases:
│  ├─ {id: "diabetes", name: "당뇨병"}
│  ├─ {id: "hypertension", name: "고혈압"}
│  └─ {id: "arthritis", name: "관절염"}
└─ Mobility: "assistive-device"

API Request:
{
  selectedDiseases: [
    {id: "diabetes", name: "당뇨병"},
    {id: "hypertension", name: "고혈압"},
    {id: "arthritis", name: "관절염"}
  ],
  mobility_status: "assistive-device"
}

Backend Processing (patients.py:110-129):
├─ For each disease:
│  ├─ Extract name: "당뇨병", "고혈압", "관절염"
│  ├─ Create HealthCondition:
│  │  ├─ patient_id: 123
│  │  ├─ disease_name: "당뇨병"
│  │  └─ note: "Mobility: assistive-device"
│  ├─ Create HealthCondition:
│  │  ├─ patient_id: 123
│  │  ├─ disease_name: "고혈압"
│  │  └─ note: "Mobility: assistive-device"
│  └─ Create HealthCondition:
│     ├─ patient_id: 123
│     ├─ disease_name: "관절염"
│     └─ note: "Mobility: assistive-device"
└─ db.commit()

⚠️ ISSUE: Mobility status duplicated in each record!

Database (health_conditions table):
├─ Row 1: condition_id=1, patient_id=123, disease_name="당뇨병", note="Mobility: assistive-device"
├─ Row 2: condition_id=2, patient_id=123, disease_name="고혈압", note="Mobility: assistive-device"
└─ Row 3: condition_id=3, patient_id=123, disease_name="관절염", note="Mobility: assistive-device"


PATIENT-CONDITION-3
───────────────────
Form Input:
├─ Medicine 1: "아스피린"
├─ Medicine 2: "메트포민"
└─ Medicine 3: "리시노프릴"

API Request:
{
  medicine_names: ["아스피린", "메트포민", "리시노프릴"]
}

Backend Processing (patients.py:173-189):
├─ Find or create Medication record for patient_id=123
├─ If hasattr(medication, 'medicine_names'):  ← UNCERTAIN!
│  └─ medication.medicine_names = ["아스피린", "메트포민", "리시노프릴"]
└─ db.commit()

Database (medications table):
├─ med_id: 456
├─ patient_id: 123
├─ name: NULL
├─ dosage: NULL
├─ frequency: NULL
├─ intake_method: NULL
└─ medicine_names: ["아스피린", "메트포민", "리시노프릴"]  ← If field exists!
```

---

## 4. Matching Algorithm Data Flow

```
┌──────────────────────────────────────────────────┐
│  CAREGIVER MATCHING: Complete Request/Response   │
└──────────────────────────────────────────────────┘

FRONTEND REQUEST CONSTRUCTION
─────────────────────────────

Patient Personality (from sessionStorage):
{
  empathy_score: 83.3,
  activity_score: 53.3,
  patience_score: 76.7,
  independence_score: 56.7
}

Care Requirements (from form):
{
  care_type: "nursing-aide",
  time_slots: ["morning", "afternoon"],
  gender: "Female",
  experience: "5plus",
  skills: ["dementia", "diabetes"]
}

User Preferences:
{
  preferred_days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
  preferred_time_slots: ["morning", "afternoon"],
  care_start_date: "2025-01-15",
  care_end_date: "2025-06-15"
}

Complete Request Body:
{
  patient_id: 123,
  patient_personality: {
    empathy_score: 83.3,
    activity_score: 53.3,
    patience_score: 76.7,
    independence_score: 56.7
  },
  requirements: {
    care_type: "nursing-aide",
    time_slots: ["morning", "afternoon"],
    gender: "Female",
    experience: "5plus",
    skills: ["dementia", "diabetes"]
  },
  preferred_days: ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
  preferred_time_slots: ["morning", "afternoon"],
  care_start_date: "2025-01-15",
  care_end_date: "2025-06-15",
  top_k: 5
}


BACKEND PROCESSING
──────────────────

1. Extract care_type mapping:
   "nursing-aide" → search for "요양보호사"

2. Query caregivers:
   SELECT * FROM caregivers
   WHERE certifications LIKE '%요양보호사%'
   LIMIT 5

3. For each caregiver, fetch personality:
   SELECT empathy_score, activity_score, ...
   FROM caregiver_personalities
   WHERE caregiver_id = ?

4. Build candidate list:
   Caregiver #1:
   ├─ caregiver_id: 1001
   ├─ caregiver_name: "이미숙"
   ├─ job_title: "요양보호사 1급"
   ├─ experience_years: 8
   ├─ empathy_score: 78.5
   ├─ activity_score: 62.3
   ├─ patience_score: 81.2
   ├─ independence_score: 59.4
   ├─ hourly_rate: 25000
   ├─ avg_rating: 4.8
   └─ profile_image_url: "..."

5. Run XGBoost matching:
   EnhancedMatchingService.recommend_caregivers_xgboost(
     patient_id=123,
     patient_personality={83.3, 53.3, 76.7, 56.7},
     caregivers_with_personality=[{...}, {...}, ...],
     limit=5
   )

6. Score each caregiver:
   match_score = weighted_similarity(
     patient_personality,
     caregiver_personality
   )

7. Save MatchingRequest:
   INSERT INTO matching_requests (
     patient_id,
     required_qualification,
     preferred_regions,
     preferred_days,
     preferred_time_slots,
     care_start_date,
     care_end_date,
     additional_request,
     is_active
   ) VALUES (
     123,
     "nursing-aide",
     NULL,
     "['Monday', 'Tuesday', ...]",
     "['morning', 'afternoon']",
     "2025-01-15",
     "2025-06-15",
     NULL,
     true
   )


BACKEND RESPONSE
────────────────

{
  patient_id: 123,
  total_matches: 5,
  matches: [
    {
      caregiver_id: 1001,
      caregiver_name: "이미숙",
      job_title: "요양보호사 1급",
      grade: "A",
      match_score: 92,
      experience_years: 8,
      hourly_rate: 25000,
      avg_rating: 4.8,
      profile_image_url: "...",
      personality_analysis: "공감 능력이 뛰어나고 인내심이 있는...",
      specialties: ["dementia", "hypertension"],
      availability: ["weekday_morning", "weekday_afternoon"]
    },
    {... match #2 ...},
    {... match #3 ...},
    {... match #4 ...},
    {... match #5 ...}
  ],
  algorithm_version: "XGBoost_v3",
  timestamp: "2025-01-10T15:30:45Z"
}


FRONTEND STORAGE & DISPLAY
──────────────────────────

sessionStorage.setItem(
  "matching_results",
  JSON.stringify(response)
)

Display in /caregiver-result-list:
├─ Show "5명의 전문가를 찾았습니다"
├─ For each match:
│  ├─ Name: "이미숙"
│  ├─ Grade: ⭐⭐⭐
│  ├─ Match Score: 92%
│  ├─ Experience: 8년
│  ├─ Specialties: [치매, 고혈압]
│  ├─ Rate: 25,000원/시간
│  ├─ Rating: 4.8/5
│  └─ Buttons: [프로필 보기] [선택]

User clicks "선택":
├─ sessionStorage.setItem("selectedCaregiver", JSON.stringify(match))
├─ sessionStorage.setItem("matching_id", "456")
└─ Navigate to /care-plans-create
```

---

## 5. Care Plan Generation (Broken)

```
┌────────────────────────────────────────────────┐
│  CARE PLAN: Broken Data Flow                   │
└────────────────────────────────────────────────┘

FRONTEND: /care-plans-create
──────────────────────────────

useEffect() on mount:
├─ const patientId = sessionStorage.getItem("patient_id")  → "123"
├─ const selectedCaregiverStr = sessionStorage.getItem("selectedCaregiver")
│  └─ {caregiver_id: 1001, caregiver_name: "이미숙", ...}
├─ const personalityScoresStr = sessionStorage.getItem("personality_scores")
│  └─ {empathy_score: 83.3, ...}
│
├─ ❌ HARDCODED care_requirements (ISSUE #2):
│  {
│    care_type: "nursing-aide",
│    time_slots: ["morning", "afternoon"],
│    gender: "any",
│    skills: []
│  }
│
└─ POST /api/care-plans/generate
   {
     patient_id: 123,
     caregiver_id: 1001,
     patient_personality: {
       empathy_score: 83.3,
       activity_score: 53.3,
       patience_score: 76.7,
       independence_score: 56.7
     },
     care_requirements: {
       care_type: "nursing-aide",
       time_slots: ["morning", "afternoon"],
       gender: "any",
       skills: []
     }
   }


BACKEND: POST /api/care-plans/generate
─────────────────────────────────────────

# Step 1: Get Patient
patient = db.query(Patient).filter(
  Patient.patient_id == 123
).first()
# ✅ Works: Patient exists

# Step 2: ❌ CRASH HERE (ISSUE #1)
patient_user = db.query(User).filter(
  User.user_id == patient.user_id  ← patient.user_id doesn't exist!
).first()

# AttributeError: 'Patient' object has no attribute 'user_id'

# Expected to work but will crash before getting to:
# Step 3: Get Caregiver
# Step 4: Call CarePlanGenerationService.generate_care_plan()
# Step 5: Return generated care plan


CORRECT APPROACH (if Patient model was fixed):
──────────────────────────────────────────────

# Step 1: Get Patient
patient = db.query(Patient).filter(Patient.patient_id == 123).first()

# Step 2: Get Guardian → Get User
guardian = db.query(Guardian).filter(
  Guardian.guardian_id == patient.guardian_id
).first()
patient_user = db.query(User).filter(
  User.user_id == guardian.user_id
).first()

# Step 3: Build patient_info
patient_info = {
  "id": 123,
  "name": "김영희",
  "age": 75,
  "condition": "일반",
  "special_conditions": "당뇨병, 고혈압, 관절염"
}

# Step 4: Get Caregiver
caregiver = db.query(Caregiver).filter(
  Caregiver.caregiver_id == 1001
).first()
caregiver_user = db.query(User).filter(
  User.user_id == caregiver.user_id
).first()

# Step 5: Build caregiver_info
caregiver_info = {
  "id": 1001,
  "name": "이미숙",
  "experience_years": 8,
  "specialties": ["dementia", "hypertension"],
  "hourly_rate": 25000
}

# Step 6: Generate care plan
service = CarePlanGenerationService()
care_plan = service.generate_care_plan(
  patient_info=patient_info,
  caregiver_info=caregiver_info,
  patient_personality={83.3, 53.3, 76.7, 56.7},
  care_requirements={...}  ← HARDCODED, should be from sessionStorage!
)

# Step 7: Return response
{
  "success": true,
  "data": {
    "weekly_schedule": [
      {
        "day": "Monday",
        "activities": [
          {
            "time": "09:00-12:00",
            "activity": "아침 간호 (위생, 투약)",
            "notes": "당뇨약 투약 후 혈당 측정"
          },
          ...
        ]
      },
      ...
    ],
    "meal_plan": [...],
    "medication_schedule": [...],
    "caregiver_notes": "..."
  },
  "message": "케어 플랜이 생성되었습니다."
}
```

---

## 6. SessionStorage State Machine

```
┌──────────────────────────────────────────────────────┐
│  SESSION STATE PROGRESSION                           │
└──────────────────────────────────────────────────────┘

INITIAL STATE (Before personality-test)
───────────────────────────────────────
sessionStorage = {}

AFTER /personality-test
──────────────────────
sessionStorage = {
  personality_scores: "{empathy_score: 75, ...}",
  personality_answers: "{q1: \"...\", q2: \"...\", ...}"
}

AFTER /patient-condition-1
─────────────────────────
sessionStorage = {
  personality_scores: "{...}",
  personality_answers: "{...}",
  patient_id: "123"
}

AFTER /patient-condition-2 & /patient-condition-3
──────────────────────────────────────────────────
sessionStorage = {
  personality_scores: "{...}",
  personality_answers: "{...}",
  patient_id: "123"
  (health conditions only in database)
  (medications only in database)
}

AFTER /caregiver-finder (matching request)
───────────────────────────────────────────
sessionStorage = {
  personality_scores: "{...}",
  personality_answers: "{...}",
  patient_id: "123",
  matching_results: "{matches: [...], total_count: 5}",
  ❌ care_requirements: MISSING!  ← Should be stored here
}

AFTER /caregiver-result-list (caregiver selection)
──────────────────────────────────────────────────
sessionStorage = {
  personality_scores: "{...}",
  personality_answers: "{...}",
  patient_id: "123",
  matching_results: "{...}",
  selectedCaregiver: "{caregiver_id: 1001, name: \"이미숙\", ...}",
  matching_id: "456"
}

DURING /care-plans-create
─────────────────────────
sessionStorage = {
  personality_scores: "{...}",
  personality_answers: "{...}",
  patient_id: "123",
  matching_results: "{...}",
  selectedCaregiver: "{...}",
  matching_id: "456"
  (care_plan generated in component state, not sessionStorage)
}

AFTER LOGOUT
────────────
localStorage.removeItem('access_token')
localStorage.removeItem('onboarded')
sessionStorage.clear()  ← Should clear everything

Next login cycles through again
```

---

## 7. API Contract Summary Matrix

```
┌─────────────────────────────────────────────────────────────────────┐
│ API ENDPOINT | REQUEST FORMAT | RESPONSE FORMAT | STATUS            │
├─────────────────────────────────────────────────────────────────────┤
│ POST /auth/login              │ {email, password}           │ {access_token, token_type} │ ✅ OK      │
│ GET /auth/me                  │ (none)                      │ {user_id, email, name}     │ ✅ OK      │
│ POST /api/patients            │ {name, age, gender}         │ {patient_id, ...}          │ ✅ OK      │
│ PUT /api/patients/{id}/health │ {selectedDiseases[], mob}   │ {patient_id, ...}          │ ⚠️ OK *    │
│ POST /api/patients/{id}/meds  │ {medicine_names[]}          │ {patient_id, med_id}       │ ⚠️ OK *    │
│ POST /personality/tests       │ {user_type, answers{...}}   │ {empathy_score, ...}       │ ✅ OK      │
│ POST /api/matching/xgboost    │ {patient_id, personality...}│ {matches[], total_count}   │ ✅ OK      │
│ POST /api/care-plans/generate │ {patient_id, caregiver_id..}│ {success, data}            │ ❌ BROKEN  │
└─────────────────────────────────────────────────────────────────────┘

* = Works but has data mapping issues
```

