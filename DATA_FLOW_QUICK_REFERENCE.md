˘¯
]\[;# Quick Reference: Data Flow Issues

## Critical Issues Summary

### Issue #1: Care Plan Generation Will Crash
**File:** `backend/app/routes/care_plans.py:73-74`
**Problem:** Tries to access `patient.user_id` but Patient model has no user_id field
**Impact:** 🔴 BLOCKS care plan generation
**Fix:** Use Guardian relationship instead
```python
# WRONG:
patient_user = db.query(User).filter(User.user_id == patient.user_id).first()

# CORRECT:
guardian = db.query(Guardian).filter(Guardian.guardian_id == patient.guardian_id).first()
patient_user = db.query(User).filter(User.user_id == guardian.user_id).first() if guardian else None
```

---

### Issue #2: Care Requirements Are Hardcoded
**File:** `frontend/my-app/src/app/care-plans-create/page.tsx:54-59`
**Problem:** Static values used instead of actual user selections
**Impact:** 🟡 Care plan AI not using actual requirements
```typescript
// WRONG (hardcoded):
care_requirements: {
    care_type: 'nursing-aide',
    time_slots: ['morning', 'afternoon'],
    gender: 'any',
    skills: []
}

// CORRECT (use sessionStorage):
const careRequirements = sessionStorage.getItem('care_requirements')
// Store during caregiver-finder submission
sessionStorage.setItem('care_requirements', JSON.stringify(requirements))
```

---

### Issue #3: Health Conditions Stored Incompletely
**File:** `backend/app/routes/patients.py:110-129`
**Problem:** Mobility status embedded in note field, not dedicated column
**Impact:** 🟡 Data retrieval inefficient
**Fix:** Add column and update storage
```python
# Current (bad):
health_condition = HealthCondition(
    patient_id=patient_id,
    disease_name=disease_name,
    note=f"Mobility: {request.mobility_status}"
)

# Correct:
# 1. Add column to HealthCondition model:
#    mobility_status: str
# 2. Store separately:
health_condition = HealthCondition(
    patient_id=patient_id,
    disease_name=disease_name,
    mobility_status=request.mobility_status
)
```

---

### Issue #4: Medication Field Existence Uncertain
**File:** `backend/app/routes/patients.py:183-189`
**Problem:** Uses hasattr() check - field may not exist or persist
**Impact:** 🟡 Unclear if medicine_names saved to database
**Fix:** Ensure field exists in model
```python
# Ensure Medication model has:
class Medication(Base):
    med_id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.patient_id'))
    medicine_names = Column(ARRAY(String))  # EXPLICIT FIELD
    # Remove old fields if not needed
```

---

## Data Flow Path Summary

```
PERSONALITY TEST FLOW:
personality-test (sessionStorage)
  ↓ [saves: personality_scores, personality_answers]
onboarding (POST /personality/tests)
  ↓ [sends answers from sessionStorage]
Backend: create_personality_test()
  ↓ [normalizes scores: 0-100]
  ↓ [saves to PatientPersonality table]
caregiver-finder
  ↓ [retrieves personality_scores from sessionStorage]
  ↓ [POST /api/matching/recommend-xgboost]

PATIENT INFO FLOW:
patient-condition-1 (form)
  ↓ [POST /api/patients]
  ↓ [saves patient_id to sessionStorage]
patient-condition-2
  ↓ [PUT /api/patients/{id}/health-status]
  ↓ [saves to HealthCondition table]
patient-condition-3
  ↓ [POST /api/patients/{id}/medications]
  ↓ [saves to Medication table]
caregiver-finder
  ↓ [retrieves patient_id from sessionStorage]

MATCHING FLOW:
caregiver-finder
  ↓ [collects requirements from form]
  ✅ [SHOULD: save care_requirements to sessionStorage]
  ✅ [POST /api/matching/recommend-xgboost]
  ↓ [saves matching_results to sessionStorage]
caregiver-result-list
  ↓ [retrieves from sessionStorage or API]
  ↓ [user selects caregiver]
  ↓ [saves selectedCaregiver + matching_id to sessionStorage]

CARE PLAN FLOW:
care-plans-create
  ❌ [WRONG: hardcoded care_requirements]
  ❌ [BROKEN: tries to access patient.user_id]
  ↓ [POST /api/care-plans/generate]
Backend: generate_care_plan()
  ❌ [CRASHES: patient.user_id doesn't exist]
  ↓ [calls CarePlanGenerationService]
  ↓ [returns generated care plan]
```

---

## SessionStorage Keys - What's Where

| Key | Location | Value | Status |
|-----|----------|-------|--------|
| `patient_id` | patient-condition-1 | `"123"` (string int) | ✅ OK |
| `personality_scores` | personality-test | `{empathy_score: 75, ...}` | ✅ OK |
| `personality_answers` | personality-test | `{q1: "{...}", q2: "{...}"}` | ⚠️ Inefficient |
| `matching_results` | caregiver-finder | `{matches: [...], total_count: 5}` | ✅ OK |
| `selectedCaregiver` | caregiver-result-list | `{caregiver_id: 1, ...}` | ✅ OK |
| `matching_id` | caregiver-result-list | `"456"` (string int) | ✅ OK |
| `care_requirements` | ❌ MISSING | Should be: `{care_type, time_slots, ...}` | ❌ NOT STORED |

---

## API Endpoint Contract Check

```
✅ POST /api/patients
   Request:  {name, age, gender, relationship}
   Response: {patient_id, name, birth_date, age, gender, guardian_id, created_at}
   Status:   WORKS (relationship not used by backend but accepted)

✅ PUT /api/patients/{id}/health-status
   Request:  {selectedDiseases[], mobility_status}
   Response: {patient_id, selected_diseases, mobility_status, updated_at}
   Status:   WORKS (but incomplete storage)

✅ POST /api/patients/{id}/medications
   Request:  {medicine_names[]}
   Response: {patient_id, med_id, medicine_names}
   Status:   WORKS (if field exists)

✅ POST /personality/tests
   Request:  {user_type, answers{q1: "{...}", ...}}
   Response: {empathy_score, activity_score, patience_score, independence_score, ...}
   Status:   WORKS (inefficient format)

✅ POST /api/matching/recommend-xgboost
   Request:  {patient_id, patient_personality, preferred_days[], preferred_time_slots[], requirements, care_start_date, care_end_date, top_k}
   Response: {patient_id, total_matches, matches[], algorithm_version, timestamp}
   Status:   WORKS

❌ POST /api/care-plans/generate
   Request:  {patient_id, caregiver_id, patient_personality, care_requirements}
   Response: {success, data, message}
   Status:   BROKEN (patient.user_id doesn't exist)
```

---

## Field Name Consistency Check

### Gender Format Inconsistency
```
Frontend UI Input:    'Male' | 'Female'
Frontend API Request: 'male' | 'female' (toLowerCase())
Backend Validator:    Converts back to 'Male' | 'Female'
Database Storage:     Enum(Male/Female)
Retrieval:            .value to get string 'Male'/'Female'
```
✅ Actually works but has unnecessary conversions

### Age vs Birth Date Issue
```
Frontend sends:       age (integer)
Backend converts:     birth_date = date(currentYear - age, 1, 1)
Database stores:      birth_date (DATE)
Retrieval loses:      Exact month/day (assumes Jan 1)
```
⚠️ Should send full birth_date instead

---

## Testing Checklist

- [ ] **Test personality flow:** personality-test → onboarding → caregiver-finder
  - [ ] Verify sessionStorage has correct format
  - [ ] Verify backend /personality/tests receives and stores correctly
  
- [ ] **Test patient info flow:** patient-condition-1 → -2 → -3
  - [ ] Verify patient_id saved correctly
  - [ ] Verify health conditions retrieved properly
  - [ ] Verify medications persisted
  
- [ ] **Test matching flow:** caregiver-finder → result-list
  - [ ] Verify matching_results matches API response
  - [ ] Verify selectedCaregiver stores complete object
  
- [ ] **Test care plan (WILL FAIL):** care-plans-create
  - [ ] Expected: AttributeError on patient.user_id
  - [ ] After fix: Verify complete care plan generated
  
- [ ] **Verify all sessionStorage keys:**
  - [ ] Are set correctly
  - [ ] Don't persist after logout
  - [ ] Have correct types (string, JSON)

---

## Migration Path

1. **Week 1: Fix Critical Issues**
   - [ ] Add logic to handle patient → user relationship correctly
   - [ ] Fix care plan generation user lookup
   - [ ] Test and verify care plan generates without errors

2. **Week 2: Store Missing Data**
   - [ ] Store care_requirements in sessionStorage
   - [ ] Update care-plans-create to use stored requirements
   - [ ] Add mobility_status column to HealthCondition

3. **Week 3: Optimize & Cleanup**
   - [ ] Remove hasattr() checks for medicine_names
   - [ ] Simplify personality answers format
   - [ ] Add comprehensive error handling

---

## Debug Tips

### Check SessionStorage in Browser Console
```javascript
// View all keys
Object.keys(sessionStorage)

// Get specific value
JSON.parse(sessionStorage.getItem('personality_scores'))

// Clear all
sessionStorage.clear()

// Watch network
// Open DevTools → Network → Filter by XHR
```

### Check Backend Request/Response
```python
# In route handler
import json
print(f"Request: {request.model_dump()}")

# After API call
print(f"Response status: {response.status_code}")
print(f"Response body: {response.json()}")
```

### Database Inspection
```sql
-- Check what was actually saved
SELECT * FROM patient_personalities WHERE patient_id = 1;
SELECT * FROM health_conditions WHERE patient_id = 1;
SELECT * FROM medications WHERE patient_id = 1;

-- Check Patient model
SELECT * FROM patients WHERE patient_id = 1;
```

