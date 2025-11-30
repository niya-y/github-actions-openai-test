# 🧪 Testing Guide - Post Fix Verification

## Summary of Fixes Applied

✅ **Issue #1 Fixed**: `patient.user_id` crash in care_plans.py
- File: `backend/app/routes/care_plans.py:73-81`
- Fixed: Now accesses user through Guardian relationship
- Impact: Care plan generation no longer crashes

✅ **Issue #2 Fixed**: Hardcoded care_requirements
- Files:
  - `frontend/my-app/src/app/caregiver-finder/page.tsx:118-131`
  - `frontend/my-app/src/app/care-plans-create/page.tsx:50-81`
- Fixed: care_requirements now saved to sessionStorage and used in AI prompts
- Impact: AI generates personalized care plans based on user selections

---

## 🧪 Testing Checklist

### **Test 1: Personality Test → Onboarding (5 min)**

```
Goal: Verify personality test data saves to DB

Steps:
1. Open browser: http://localhost:3000
2. Navigate to /welcome → /personality-test
3. Answer all 6 personality questions (any answers)
4. Click "간병인 찾기" button
5. Login with Kakao OAuth
6. Wait for /onboarding page

Expected Results:
✅ Should see: "[Onboarding] ✅ Personality test saved to DB successfully" in console
✅ No errors in browser console
✅ sessionStorage should have: personality_scores, personality_answers

Verify in Database:
```sql
SELECT * FROM patient_personality WHERE patient_id = [your_patient_id];
```
✅ Should have 4 score columns with values (not NULL)
```

---

### **Test 2: Patient Information (5 min)**

```
Goal: Verify all patient data saved correctly

From /onboarding, click "시작하기" → /patient-condition-1

Step 2.1: Basic Info
1. Fill: Name, Age, Gender, Region
2. Click "다음"
3. Check console: patient_id should be in sessionStorage

Expected:
✅ POST /api/patients success (200)
✅ sessionStorage has: patient_id
✅ Navigate to /patient-condition-2

Step 2.2: Health Status
1. Select 2+ diseases
2. Select mobility status
3. Click "다음"

Expected:
✅ PUT /api/patients/{id}/health-status success (200)
✅ Navigate to /patient-condition-3

Step 2.3: Medications
1. Add any medications
2. Click "다음"

Expected:
✅ POST /api/patients/{id}/medications success (200)
✅ Navigate to /caregiver-finder

Verify in Database:
```sql
SELECT * FROM health_conditions WHERE patient_id = [id];
SELECT * FROM medications WHERE patient_id = [id];
```
✅ Both tables should have records
```

---

### **Test 3: Caregiver Matching (5 min)**

```
Goal: Verify care_requirements saved to sessionStorage

At /caregiver-finder page:

1. Select:
   - Care Type: any option
   - Time Slots: morning AND afternoon (not just one)
   - Preferred Days: Mon-Fri (or your choice)
   - Care Start Date: 2025-01-15
   - Care End Date: 2025-03-15

2. Click "간병인 찾기"

Expected Console Output:
✅ "[Caregiver Finder] Submitting matching request:" with full payload
✅ POST /api/matching/recommend-xgboost 200 OK
✅ "XGBoost 매칭 요청 성공:" in console
✅ "[Caregiver Finder] ✅ care_requirements saved to sessionStorage:" in console

Check sessionStorage:
```javascript
// Open browser console (F12) and run:
sessionStorage.getItem('care_requirements')

// Should output something like:
{
  "care_type": "nursing-aide",
  "time_slots": ["morning", "afternoon"],
  "gender": "any",
  "experience": "5plus",
  "skills": ["dementia"],
  "preferred_days": ["Monday", "Tuesday", ...],
  "care_start_date": "2025-01-15",
  "care_end_date": "2025-03-15"
}
```

✅ care_requirements should have all fields populated
✅ Navigate to /caregiver-result-loading → /caregiver-result-list
```

---

### **Test 4: Select Caregiver (2 min)**

```
Goal: Verify caregiver selection saved

At /caregiver-result-list:

1. See list of matched caregivers
2. Click any caregiver
3. Wait for redirect to /care-plans-create

Expected:
✅ Caregiver clickable and selectable
✅ selectedCaregiver in sessionStorage
✅ Navigator to /care-plans-create
```

---

### **Test 5: Care Plan Generation (CRITICAL TEST)** ⭐

```
Goal: Verify care plan generates without crash

At /care-plans-create page (loading phase):

Watch Console CAREFULLY - Should see:

✅ "[Care Plan Create] Starting API call..." in console
✅ "patientId:", "matchingId:", "selectedCaregiver:", values logged
✅ "[Care Plan Create] Request payload:" with care_requirements ← KEY TEST!

🔴 TEST FAILED IF YOU SEE:
❌ 500 Internal Server Error
❌ "'Patient' object has no attribute 'user_id'"
✅ If you don't see these, Issue #1 is fixed!

Expected Payload Structure:
{
  "patient_id": 123,
  "caregiver_id": 456,
  "patient_personality": {
    "empathy_score": 75,
    "activity_score": 60,
    "patience_score": 80,
    "independence_score": 45
  },
  "care_requirements": {
    "care_type": "nursing-aide",      ← From sessionStorage, NOT hardcoded!
    "time_slots": ["morning", "afternoon"],
    "gender": "any",
    "skills": ["dementia"],
    "preferred_days": [...]           ← NEW: From sessionStorage
  }
}

Key Console Messages to Look For:

For Issue #1 Fix:
✅ "[Caregiver Finder] ✅ care_requirements saved to sessionStorage:"
   (shows that fix #2 is working)

For Issue #2 Fix:
✅ "[Care Plan Create] ✅ care_requirements loaded from sessionStorage:"
   (shows that care plan uses saved values, not hardcoded)

❌ FAILURE SIGNS:
❌ "[Care Plan Create] ⚠️ care_requirements not found in sessionStorage"
   (means care_requirements wasn't saved in caregiver-finder)

❌ "[Care Plan Create] Failed to parse care_requirements, using defaults"
   (means corrupted sessionStorage data)

After API Call:
✅ "[Care Plan Create] API Response received:" with data
✅ 7-day care plan displays (Monday through Sunday)
✅ See weekly schedule, activities, feedback
```

---

### **Test 6: Complete Care Plan Review (3 min)**

```
Goal: Verify care plan loads with AI-generated content

At /care-plans-create page (steps 1-4):

Step 1 (Loading):
✅ Shows "케어 플랜 생성 중..." or similar
✅ Transitions to Step 2 after ~3 seconds

Step 2 (Weekly Schedule):
✅ Shows 7 days (Mon-Sun)
✅ Each day has activities
✅ Activities have times, titles, assignees
✅ Click Next button

Step 3 (Caregiver Feedback):
✅ Shows feedback on activities
✅ Has recommendations for adjustments
✅ Click Next button

Step 4 (Final Review):
✅ Shows complete summary
✅ Click "대시보드로" → /mypage-dashboard

Expected Database:
```sql
SELECT * FROM care_plans WHERE patient_id = [id];
SELECT * FROM care_plan_activities WHERE care_plan_id = [id];
```
✅ care_plans table has record
✅ care_plan_activities table has ~42 activities (7 days × ~6 activities)
```

---

### **Test 7: Verify AI Used Correct Requirements** ⭐

```
Goal: Confirm AI care plan matches user's selections (not hardcoded)

Method: Compare care plan content with what you selected

Example:

You Selected in /caregiver-finder:
- Time: morning AND afternoon
- Days: Monday, Tuesday, Wednesday, Thursday, Friday only
- Gender: Female (preferred)

AI Should Have Generated:
✅ Activities mainly scheduled for morning/afternoon
✅ Activities only M-Fri (no weekend activities)
✅ Female caregiver name in assignments (if available)

❌ If you see:
❌ Weekend activities (Sat-Sun)
❌ Evening activities (18:00+)
❌ Male caregiver exclusively
→ Then Issue #2 wasn't fully fixed

This proves the AI used sessionStorage care_requirements, not hardcoded defaults
```

---

## 🔧 If Tests Fail

### Failure: Test 5 shows 500 error with "user_id" message

**Cause**: Issue #1 not fully fixed

**Debug Steps**:
1. Check backend logs: Is error in care_plans.py:73-81?
2. Verify Guardian import: `from app.models.profile import Patient, Caregiver, Guardian`
3. Verify code uses: `Guardian.guardian_id == patient.guardian_id`
4. Restart backend: `python main.py`

---

### Failure: Test 5 shows wrong console message about care_requirements

**Cause**: Issue #2 not fully fixed

**Debug Steps**:

1. Check sessionStorage in browser (F12 → Application → SessionStorage):
   - Should have key: `care_requirements`
   - Should have JSON value with all fields

2. If missing from sessionStorage:
   - Check /caregiver-finder page.tsx lines 118-131
   - Verify `sessionStorage.setItem('care_requirements', ...)`
   - Restart frontend: `npm run dev`

3. If present in sessionStorage:
   - Check /care-plans-create page.tsx lines 50-81
   - Verify it's reading from sessionStorage
   - Verify it's using those values in requestPayload

---

### Failure: Backend health check fails

```bash
# Terminal: Check if backend is running
curl http://localhost:8000/health

# If not running:
cd /Users/sangwon/Project/Sesac_class/neulbom-merge/neulbomcare-test03/backend
source venv/bin/activate
python main.py
```

---

## ✅ All Tests Pass Checklist

```
PERSONALITY TEST PHASE:
☐ Test 1: personality_scores saved to DB
☐ Can login with test data

PATIENT INFO PHASE:
☐ Test 2.1: patient_id created in DB
☐ Test 2.2: health_conditions saved in DB
☐ Test 2.3: medications saved in DB

MATCHING PHASE:
☐ Test 3: care_requirements in sessionStorage
☐ Matching results display correctly
☐ Test 4: Caregiver selectable

CARE PLAN PHASE:
☐ Test 5: NO CRASH (Issue #1 fixed) ⭐
☐ care_plan_generation API success (200)
☐ Test 6: 7-day schedule displays
☐ Test 7: AI used correct requirements (Issue #2 fixed) ⭐

DATABASE:
☐ All patient data in DB
☐ All care plan activities in DB
☐ All relationships intact
```

---

## 🎉 Success!

If all tests pass:
- ✅ Issue #1 (patient.user_id crash) is FIXED
- ✅ Issue #2 (hardcoded care_requirements) is FIXED
- ✅ Full application flow works end-to-end
- ✅ Data properly persisted to database
- ✅ AI generates personalized care plans based on user selections

**The application is ready for production testing!** 🚀

---

## 📝 Notes for Team

- Keep browser console open (F12) during testing
- Watch for the specific console messages mentioned above
- If any console shows "❌" or errors, check the Debug section
- Database verification requires direct SQL access or DB client
- All times should be in HH:MM format (e.g., 07:00, 14:30)

**Estimated Total Testing Time: 25 minutes**
