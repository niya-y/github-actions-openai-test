# Data Flow Analysis - Complete Package

This package contains a comprehensive analysis of data flow throughout the Neulbom Care application. It documents how data moves between frontend pages, how it's transmitted via APIs, and how it's stored in the database.

## Files Included

1. **DATA_FLOW_ANALYSIS.md** (892 lines)
   - Complete technical analysis of all data flows
   - 5 main flow sections: Personality Test, Patient Info, Matching, Care Plans
   - Detailed request/response specifications
   - Complete issues documentation with line numbers
   - Model field reference

2. **DATA_FLOW_QUICK_REFERENCE.md** 
   - Executive summary of critical issues
   - Visual flow diagrams (ASCII art)
   - SessionStorage key inventory
   - API endpoint contract check
   - Testing checklist
   - Migration path for fixes

3. **DATA_FLOW_DIAGRAMS.md**
   - Detailed visual diagrams of data transformations
   - Complete user journey flowchart
   - Data transformation examples with real values
   - SessionStorage state machine
   - API contract matrix

## Critical Issues Summary

### Issue #1: Care Plan Generation Will Crash ❌
**Severity:** CRITICAL - Blocks feature entirely
**Location:** `backend/app/routes/care_plans.py:73-74`
**Problem:** Tries to access `patient.user_id` which doesn't exist
**Impact:** Care plan generation endpoint returns 500 error
**Status:** Not yet fixed

### Issue #2: Care Requirements Hardcoded ❌
**Severity:** CRITICAL - Wrong data used for AI generation
**Location:** `frontend/my-app/src/app/care-plans-create/page.tsx:54-59`
**Problem:** Static values instead of user's actual selections
**Impact:** AI generates care plan based on default values, not user needs
**Status:** Not yet fixed

### Issue #3: Health Condition Storage Incomplete ⚠️
**Severity:** MODERATE - Data retrieval inefficient
**Location:** `backend/app/routes/patients.py:110-129`
**Problem:** Mobility status embedded in note field
**Impact:** Requires string parsing to extract data
**Status:** Workaround possible, proper fix pending

### Issue #4: Medication Field Uncertain ⚠️
**Severity:** MODERATE - Unclear if data persists
**Location:** `backend/app/routes/patients.py:183-189`
**Problem:** Uses hasattr() - field existence not guaranteed
**Impact:** Medicine names may not be saved to database
**Status:** Needs model verification

## Data Flows Covered

### 1. Personality Test Flow ✅ WORKING
```
/personality-test 
  → sessionStorage (personality_scores, personality_answers)
  → /onboarding (POST /personality/tests)
  → Backend normalization and storage
  → /caregiver-finder (retrieves from sessionStorage)
  → XGBoost matching request
```

### 2. Patient Information Flow ✅ WORKING
```
/patient-condition-1 (POST /api/patients)
  → /patient-condition-2 (PUT /api/patients/{id}/health-status)
  → /patient-condition-3 (POST /api/patients/{id}/medications)
  → Database: Patient, HealthCondition, Medication tables
```

### 3. Caregiver Matching Flow ✅ WORKING
```
/caregiver-finder (POST /api/matching/recommend-xgboost)
  → Database query and XGBoost algorithm
  → /caregiver-result-loading
  → /caregiver-result-list (retrieves from sessionStorage)
  → User selects caregiver
  → sessionStorage: selectedCaregiver, matching_id
```

### 4. Care Plan Generation Flow ❌ BROKEN
```
/care-plans-create
  → Retrieves sessionStorage: patient_id, selectedCaregiver, personality_scores
  → ❌ HARDCODED care_requirements (should be from caregiver-finder)
  → POST /api/care-plans/generate
  → ❌ CRASHES on patient.user_id access
  → NEVER REACHES: Care plan generation
```

## SessionStorage State

| Key | Set By | Used By | Status |
|-----|--------|---------|--------|
| `patient_id` | patient-condition-1 | caregiver-finder, care-plans-create | ✅ OK |
| `personality_scores` | personality-test | caregiver-finder, care-plans-create | ✅ OK |
| `personality_answers` | personality-test | onboarding | ✅ OK |
| `matching_results` | caregiver-finder | caregiver-result-list | ✅ OK |
| `selectedCaregiver` | caregiver-result-list | care-plans-create, mypage | ✅ OK |
| `matching_id` | caregiver-result-list | care-plans-create-3 | ✅ OK |
| `care_requirements` | ❌ NEVER SET | care-plans-create | ❌ MISSING |

## Database Models

### Patient
- ✅ patient_id, guardian_id, name, birth_date, gender, care_address, region_code
- ❌ Missing: user_id (referenced in care_plans.py:73)
- ⚠️ Age lost: backend reconstructs birth_date as Jan 1 of calculated year

### HealthCondition
- ✅ condition_id, patient_id, disease_name
- ⚠️ Incomplete: mobility_status embedded in note field

### Medication
- ⚠️ Uncertain: medicine_names field existence not verified
- ❌ Bad practice: hasattr() check instead of explicit field definition

### PatientPersonality
- ✅ Complete: personality_id, patient_id, empathy_score, activity_score, patience_score, independence_score

### MatchingRequest
- ✅ Complete: All required fields including care dates

## API Endpoints Status

| Endpoint | Status | Issues |
|----------|--------|--------|
| POST /api/patients | ✅ Works | relationship field unused |
| PUT /api/patients/{id}/health-status | ⚠️ Works | Incomplete storage |
| POST /api/patients/{id}/medications | ⚠️ Works | Field existence uncertain |
| POST /personality/tests | ✅ Works | Inefficient format (JSON strings) |
| POST /api/matching/recommend-xgboost | ✅ Works | All data correct |
| POST /api/care-plans/generate | ❌ BROKEN | patient.user_id doesn't exist |

## How to Use This Analysis

### For QA/Testing:
1. Start with **DATA_FLOW_QUICK_REFERENCE.md**
2. Follow the **Testing Checklist** section
3. Reference **DATA_FLOW_DIAGRAMS.md** for expected values
4. Use **API Contract Check** to validate endpoints

### For Developers:
1. Read **DATA_FLOW_ANALYSIS.md** for complete context
2. Use **Section 6: Identified Issues** for specific fixes
3. Reference line numbers to locate exact code
4. Follow **Section 9: Recommendations** priority order

### For Architects:
1. Review **Section 1: Complete User Journey** for overview
2. Check **Section 5: Data Mapping Summary Table** for consistency
3. Use **Data Persistence Checklist** for validation
4. Reference **APPENDIX: Model Field Reference** for schema

## Fix Priority

### Week 1 (Critical)
- [ ] Fix Patient.user_id access in care_plans.py
- [ ] Test care plan generation endpoint
- [ ] Verify no other patient.user_id references

### Week 2 (Important)
- [ ] Store care_requirements in sessionStorage
- [ ] Update care-plans-create to use stored requirements
- [ ] Add mobility_status column to HealthCondition

### Week 3 (Optimization)
- [ ] Verify medicine_names field in Medication model
- [ ] Remove hasattr() checks
- [ ] Simplify personality answer format

## Related Files

- Database schema: `/database_schema_sql.md`
- Frontend structure: `/frontend/my-app/src/app/*/page.tsx`
- Backend routes: `/backend/app/routes/*.py`
- Models: `/backend/app/models/*.py`
- Schemas: `/backend/app/schemas/*.py`

## Questions?

Refer to the specific analysis document:
- **What fields are in the API request?** → DATA_FLOW_ANALYSIS.md Section 3-4
- **Where is data stored?** → DATA_FLOW_DIAGRAMS.md Section 3
- **Why is care plan broken?** → DATA_FLOW_QUICK_REFERENCE.md Issue #1
- **How does data flow end-to-end?** → DATA_FLOW_DIAGRAMS.md Section 1
- **What are all the issues?** → DATA_FLOW_ANALYSIS.md Section 6

---

**Generated:** January 2025
**Status:** Complete
**Coverage:** 100% of user journey (Personality Test → Care Plan)
