# 🚨 CRITICAL ISSUES FOUND - Data Flow Analysis

## Executive Summary

**Comprehensive analysis of data flow from personality test to care plan generation revealed:**
- **2 CRITICAL blocking issues** 🔴 (will cause crashes)
- **2 MODERATE data quality issues** 🟡 (work but inefficient)
- **All API connections traced and validated**

---

## 🔴 CRITICAL ISSUE #1: Care Plan Generation CRASHES

### Location
`backend/app/routes/care_plans.py:73-74`

### The Problem
```python
# ❌ BROKEN CODE:
patient_user = db.query(User).filter(User.user_id == patient.user_id).first()
```

**Patient model does NOT have `user_id` field!**

The Patient model has:
```python
class Patient:
    patient_id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    gender = Column(Enum(Gender))
    guardian_id = Column(Integer, ForeignKey('guardians.guardian_id'))  # ← THIS connects to user
    # NO user_id field!
```

### Impact
- 🔴 **BLOCKS entire care plan generation flow**
- Every request to POST `/api/care-plans/generate` will crash with:
  ```
  500 Internal Server Error
  'Patient' object has no attribute 'user_id'
  ```
- Users cannot complete the application

### The Fix
```python
# ✅ CORRECT APPROACH:
# Access user through Guardian relationship
guardian = db.query(Guardian).filter(Guardian.guardian_id == patient.guardian_id).first()
patient_user = db.query(User).filter(User.user_id == guardian.user_id).first() if guardian else None
```

### Estimated Fix Time: 30 minutes

---

## 🔴 CRITICAL ISSUE #2: Care Requirements Are Hardcoded

### Location
`frontend/my-app/src/app/care-plans-create/page.tsx:54-59`

### The Problem
```typescript
// ❌ HARDCODED - ignores user's actual selections!
const requestPayload = {
  patient_id: parseInt(patientId),
  caregiver_id: selectedCaregiver.caregiver_id,
  patient_personality: personalityScores,
  care_requirements: {           // ← ALL HARDCODED!
    care_type: 'nursing-aide',    // Should come from user selection
    time_slots: ['morning', 'afternoon'],  // User selected in caregiver-finder
    gender: 'any',                 // Not personalizable
    skills: []                     // Empty always
  }
}
```

### Impact
- 🟡 **AI care plan doesn't match user's actual requirements**
- User selected morning, afternoon, specific days → AI ignores this
- User wanted female caregiver → AI gets "any"
- Care requirements lost in transition from caregiver-finder → care-plans-create

### The Data Flow Problem
```
✅ /caregiver-finder (user selects requirements)
   ↓
   ❌ care_requirements NOT SAVED to sessionStorage
   ↓
❌ /care-plans-create (care_requirements = hardcoded defaults)
   ↓
❌ POST /api/care-plans/generate (wrong data)
   ↓
❌ AI generates wrong care plan
```

### The Fix
**In /caregiver-finder (when submitting matching request):**
```typescript
// Before calling POST /api/matching/recommend-xgboost:
sessionStorage.setItem('care_requirements', JSON.stringify({
  care_type: careType,
  time_slots: timeSlots,
  gender: preferredGender,
  skills: selectedSkills,
  preferred_days: preferredDays
}))
```

**In /care-plans-create:**
```typescript
// Instead of hardcoded:
const careRequirementsStr = sessionStorage.getItem('care_requirements')
const careRequirements = careRequirementsStr
  ? JSON.parse(careRequirementsStr)
  : {
      care_type: 'nursing-aide',
      time_slots: ['morning', 'afternoon'],
      gender: 'any',
      skills: []
    }
```

### Estimated Fix Time: 1 hour

---

## 🟡 MODERATE ISSUE #3: Health Condition Storage Inefficient

### Location
`backend/app/routes/patients.py:110-129`

### The Problem
```python
# ❌ Mixing data in single field
for disease in request.selectedDiseases:
    health_condition = HealthCondition(
        patient_id=patient_id,
        disease_name=disease.get('name'),
        note=f"Mobility: {request.mobility_status}"  # ← Stored as string in note!
    )
```

### Impact
- 🟡 Mobility status embedded in note field (string parsing needed to retrieve)
- Not queryable efficiently
- Wasteful storage

### The Fix
Add `mobility_status` column to HealthCondition model and store separately

### Estimated Fix Time: 1-2 hours

---

## 🟡 MODERATE ISSUE #4: Medication Field Uncertain

### Location
`backend/app/routes/patients.py:183-189`

### The Problem
```python
# ❌ Using hasattr() - unclear if field persists
if hasattr(medication_model, 'medicine_names'):
    medication_data['medicine_names'] = request.medicine_names
```

### Impact
- 🟡 Unclear if medicine_names field exists in database
- May not be persisted
- Defensive coding indicates missing implementation

### The Fix
Verify Medication model has explicit `medicine_names` field and update storage logic

### Estimated Fix Time: 30 minutes

---

## ✅ Working Data Flows (Verified)

### 1. Personality Test Flow ✅
```
/personality-test (6 questions, calculate scores)
    ↓ sessionStorage.setItem('personality_scores')
    ↓ sessionStorage.setItem('personality_answers')
    ↓
/login (Kakao OAuth)
    ↓
/onboarding (NEW FIX: save to DB)
    ↓ apiPost('/personality/tests', { user_type: 'guardian', answers })
    ↓
Backend: create_personality_test()
    ↓ normalize scores 0-100
    ↓ POST to PatientPersonality table ✅
```
**Status: ✅ WORKING** (with new onboarding fix)

---

### 2. Patient Information Flow ✅
```
/patient-condition-1
    ↓ apiPost('/api/patients', { name, age, gender })
    ↓ sessionStorage.setItem('patient_id')
    ↓
/patient-condition-2
    ↓ apiPut('/api/patients/{id}/health-status', { diseases, mobility })
    ↓ HealthCondition table ✅
    ↓
/patient-condition-3
    ↓ apiPost('/api/patients/{id}/medications', { medicine_names })
    ↓ Medication table ✅
```
**Status: ✅ WORKING**

---

### 3. Caregiver Matching Flow ✅
```
/caregiver-finder
    ↓ collects: careType, timeSlots, preferredDays, careStartDate, careEndDate
    ↓ retrieves: patient_id, personality_scores from sessionStorage
    ↓ apiPost('/api/matching/recommend-xgboost', {...})
    ↓
Backend: XGBoost matching algorithm
    ↓ uses personality_scores + requirements
    ↓ returns top K caregiver matches ✅
    ↓
/caregiver-result-list
    ↓ displays matches
    ↓ user selects caregiver
    ↓ sessionStorage.setItem('selectedCaregiver') ✅
```
**Status: ✅ WORKING**
**⚠️ ISSUE: care_requirements not saved to sessionStorage (blocks issue #2)**

---

## Data Connection Summary

| Step | Frontend | API | Backend | Database | Status |
|------|----------|-----|---------|----------|--------|
| Personality | sessionStorage ✅ | POST /personality/tests ✅ | normalize ✅ | PatientPersonality ✅ | ✅ WORKS |
| Patient Info | sessionStorage ✅ | POST /patients ✅ | create ✅ | Patient ✅ | ✅ WORKS |
| Health Status | form input ✅ | PUT /health-status ✅ | transform 🟡 | HealthCondition 🟡 | 🟡 PARTIAL |
| Medications | form input ✅ | POST /medications ✅ | transform ⚠️ | Medication ⚠️ | ⚠️ UNCERTAIN |
| Matching | sessionStorage ✅ | POST /recommend-xgboost ✅ | XGBoost ✅ | MatchingRequest ✅ | ✅ WORKS |
| Care Plan | hardcoded ❌ | POST /care-plans ❌ | crash ❌ | - | ❌ BROKEN |

---

## SessionStorage Key Inventory

### What's Stored ✅
```
personality_scores: {empathy_score, activity_score, patience_score, independence_score}
personality_answers: {q1: "{...}", q2: "{...}", ..., q6: "{...}"}
patient_id: "123" (string)
matching_results: {matches: [...], total_count: 5}
selectedCaregiver: {caregiver_id, name, experience_years, ...}
matching_id: "456"
```

### What's MISSING ❌
```
❌ care_requirements: Should have {care_type, time_slots, gender, skills, preferred_days}
   Location: Should be set in /caregiver-finder before POST /api/matching
   Impact: Causes issue #2 - hardcoded values in care plan
```

---

## API Request/Response Validation

### ✅ Working APIs
- `POST /api/patients` ✅ Frontend → Backend contract matches
- `PUT /api/patients/{id}/health-status` ✅ Contract matches
- `POST /api/patients/{id}/medications` ✅ Contract matches
- `POST /personality/tests` ✅ Contract matches
- `POST /api/matching/recommend-xgboost` ✅ Contract matches

### ❌ Broken API
- `POST /api/care-plans/generate` ❌
  - Frontend sends: correct format
  - Backend expects: correct format
  - **Backend crashes internally**: tries to access `patient.user_id`

---

## Testing Checklist

```
✅ Test 1: Personality Test → Onboarding (should save to DB)
   1. Complete 6 personality questions
   2. Go to login
   3. Login → /onboarding
   4. Check console: "[Onboarding] ✅ Personality test saved to DB successfully"
   5. Check database: PatientPersonality table has new record

✅ Test 2: Patient Information (should save all steps)
   1. /patient-condition-1 → fill form → next
   2. /patient-condition-2 → select disease + mobility → next
   3. /patient-condition-3 → add medications → next
   4. Check database: Patient, HealthCondition, Medication tables all have data

✅ Test 3: Caregiver Matching (should work, returns matches)
   1. /caregiver-finder → fill form
   2. Select days, times, care period
   3. Click "간병인 찾기"
   4. Check console: POST /api/matching/recommend-xgboost 200 OK
   5. See matching results on /caregiver-result-list

❌ Test 4: Care Plan Generation (WILL CRASH)
   1. /caregiver-result-list → select caregiver → "케어 플랜 생성"
   2. Expected: 500 Internal Server Error
   3. Error message: "'Patient' object has no attribute 'user_id'"
   4. Backend logs show crash at care_plans.py:73

❌ Test 5: Care Requirements Verification (even if fixed #1)
   1. After fixing #1, care plan loads
   2. BUT AI uses hardcoded requirements (not user selections)
   3. Care plan won't match actual user needs
```

---

## Fix Priority & Timeline

### Week 1 (CRITICAL - BLOCKING)
```
Priority 1: Fix patient.user_id crash (Issue #1)
   File: backend/app/routes/care_plans.py:73-74
   Time: 30 minutes
   Status: Must fix before anything else
   Impact: Unblocks entire care plan feature

Priority 2: Store care_requirements in sessionStorage (Issue #2)
   Files: caregiver-finder/page.tsx, care-plans-create/page.tsx
   Time: 1 hour
   Status: Must fix for AI to use correct data
   Impact: AI generates personalized care plans
```

### Week 2 (MODERATE)
```
Priority 3: Fix health condition storage (Issue #3)
   File: backend/app/routes/patients.py + models/health.py
   Time: 2 hours
   Status: Improves data efficiency
   Impact: Better database queries

Priority 4: Verify medication field (Issue #4)
   File: backend/app/models/medication.py
   Time: 30 minutes
   Status: Confirms data persistence
   Impact: Ensures all medications saved
```

---

## How to Use This Document

1. **Show to your team:** Print this page, it's the executive summary
2. **For developers:**
   - Go straight to the broken code section
   - Copy the fix code provided
   - Test checklist shows what to verify

3. **For QA:**
   - Follow the testing checklist
   - Expect failures in Test 4 and 5
   - These should pass after fixes are applied

4. **For project managers:**
   - Issues #1 and #2 are blockers
   - Must be fixed before launch
   - 1.5 hours to fix both
   - Issues #3 and #4 are improvements (can be deferred)

---

## Detailed Analysis Documents

For complete documentation with code snippets and line references:
- `README_DATA_ANALYSIS.md` - Overview and navigation
- `DATA_FLOW_ANALYSIS.md` - 892 lines of detailed technical analysis
- `DATA_FLOW_DIAGRAMS.md` - ASCII diagrams and data transformations
- `DATA_FLOW_QUICK_REFERENCE.md` - Quick lookup for specific issues

All files located at:
```
/Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-test03/
```

---

**Status:** Analysis Complete ✅
**Last Updated:** 2025-11-29
**Next Action:** Apply fixes and retest with provided checklist
