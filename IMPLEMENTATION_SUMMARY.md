# Care Period Implementation Summary

## Overview
Adding care period dates (start and end dates) to the matching system to capture when a patient needs care services.

---

## 1. DATABASE MIGRATION (Run in DBeaver)

**File:** `backend/migrations/001_add_care_period_to_matching_requests.sql`

**Step 1: Add columns to matching_requests table**
```sql
ALTER TABLE matching_requests
ADD COLUMN care_start_date DATE DEFAULT NULL,
ADD COLUMN care_end_date DATE DEFAULT NULL;
```

**Step 2: Add check constraint**
```sql
ALTER TABLE matching_requests
ADD CONSTRAINT check_care_dates CHECK (
    care_start_date IS NULL OR
    care_end_date IS NULL OR
    care_start_date < care_end_date
);
```

**Step 3: Create index for efficient querying**
```sql
CREATE INDEX idx_matching_requests_care_dates
ON matching_requests(care_start_date, care_end_date)
WHERE is_active = true;
```

**Verification query:**
```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_name = 'matching_requests'
ORDER BY ordinal_position;
```

Expected output should show:
- `care_start_date` (date, nullable)
- `care_end_date` (date, nullable)

---

## 2. BACKEND CODE CHANGES (Already Implemented)

### 2.1 SQLAlchemy Model Update
**File:** `app/models/matching.py`

Changes made:
- Added `care_start_date: Column(Date, nullable=True)`
- Added `care_end_date: Column(Date, nullable=True)`
- Added CHECK constraint validation
- Added index for date range queries

### 2.2 API Schema Update
**File:** `app/routes/xgboost_matching.py`

Changes made:
- Added `care_start_date` field to `XGBoostMatchingRequest`
- Added `care_end_date` field to `XGBoostMatchingRequest`
- Added `preferred_days` field (required)
- Added `preferred_time_slots` field (required)
- Added validator to ensure `care_start_date < care_end_date`
- Updated `/recommend-xgboost` endpoint to save `MatchingRequest` with care dates

### 2.3 Endpoint Updated
The `/api/matching/recommend-xgboost` endpoint now:
1. Accepts care period dates in the request
2. Validates the dates
3. Saves `MatchingRequest` to database with:
   - `patient_id`
   - `preferred_days` (from request)
   - `preferred_time_slots` (from request)
   - `care_start_date` (from request)
   - `care_end_date` (from request)
   - Returns matching results as before

---

## 3. API REQUEST EXAMPLE

```json
{
  "patient_id": 1,
  "patient_personality": {
    "empathy_score": 75,
    "activity_score": 55,
    "patience_score": 80,
    "independence_score": 45
  },
  "preferred_days": ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"],
  "preferred_time_slots": ["morning", "afternoon"],
  "care_start_date": "2025-12-15",
  "care_end_date": "2026-01-15",
  "requirements": {
    "care_type": "nursing-aide",
    "time_slots": ["morning", "afternoon"],
    "gender": "Female",
    "skills": []
  },
  "top_k": 5
}
```

---

## 4. FRONTEND CHANGES NEEDED

### 4.1 Update caregiver-finder page
Need to add date input fields for:
- Care start date (date picker)
- Care end date (date picker)
- Validation: start date < end date

### 4.2 Update API call
When submitting the form, include:
- `preferred_days` (from existing selection)
- `preferred_time_slots` (from existing selection)
- `care_start_date` (new - from date picker)
- `care_end_date` (new - from date picker)

---

## 5. DATABASE RELATIONSHIPS

### Before
```
MatchingRequest
├── patient_id
├── preferred_days (JSONB)
├── preferred_time_slots (JSONB)
└── additional_request
```

### After
```
MatchingRequest
├── patient_id
├── preferred_days (JSONB) ← existing
├── preferred_time_slots (JSONB) ← existing
├── care_start_date (NEW) ← DATE
├── care_end_date (NEW) ← DATE
└── additional_request
```

### Use in Matching
When selecting a caregiver (MatchingResult):
- Use `matching_requests.care_start_date/end_date` for the initial care period
- Can set `matching_results.contract_start_date/end_date` to negotiate actual contract dates

---

## 6. VALIDATION RULES

The system validates:
- ✅ `care_start_date < care_end_date` (at database and API level)
- ✅ `preferred_days` is a non-empty JSON array
- ✅ `preferred_time_slots` is a non-empty JSON array
- ✅ Both dates can be NULL (optional)

---

## 7. NEXT STEPS

1. **Run SQL migration** in DBeaver using the provided `.sql` file
2. **Restart backend** to apply model changes
3. **Add date input fields** to `/caregiver-finder` frontend page
4. **Update API call** to include `care_start_date` and `care_end_date`
5. **Test** the complete flow:
   - Select caregiver with date range
   - Verify dates are saved in database
   - Verify dates appear in matching request details

---

## 8. ROLLBACK (if needed)

If you need to revert the changes:

```sql
-- Drop the constraint
ALTER TABLE matching_requests DROP CONSTRAINT check_care_dates;

-- Drop the index
DROP INDEX idx_matching_requests_care_dates;

-- Drop the columns
ALTER TABLE matching_requests DROP COLUMN care_end_date;
ALTER TABLE matching_requests DROP COLUMN care_start_date;
```

---

## Files Modified

### Backend
- ✅ `app/models/matching.py` - Model updated with new columns
- ✅ `app/routes/xgboost_matching.py` - Schema and endpoint updated
- ✅ `migrations/001_add_care_period_to_matching_requests.sql` - SQL migration created

### Frontend
- ⏳ `pages/caregiver-finder/page.tsx` - **NEEDS DATE INPUT FIELDS**

---

## Implementation Checklist

- [x] Create SQL migration file
- [x] Update MatchingRequest model
- [x] Update XGBoostMatchingRequest schema
- [x] Add validation for care dates
- [x] Update endpoint to save care dates
- [ ] Add date inputs to frontend
- [ ] Test complete flow
- [ ] Deploy

---

## Questions?

Refer back to database schema:
- `matching_requests` now has `care_start_date` and `care_end_date`
- `matching_results` already has `contract_start_date` and `contract_end_date` for negotiated dates
- `caregiver_availability` has weekly recurring availability (day_of_week + time)
