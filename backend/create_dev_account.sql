-- ========================================
-- Dev 계정 생성 SQL 스크립트
-- ========================================
-- 주의: 아래 쿼리를 DBeaver에서 한 번에 실행하세요
-- 각 쿼리는 ;로 구분되어 있습니다

-- Step 1: User 계정 생성
INSERT INTO public.users (email, password_hash, name, phone_number, user_type, profile_image_url, is_active, created_at, updated_at)
VALUES (
  'dev@test.com',
  '$2b$12$M0a4LVrZzyt8N0UCWfq1FeASpT4ObxLNU0LVA8U997DxtrQh526hC',
  'Dev User',
  '010-0000-0001',
  'guardian',
  NULL,
  true,
  NOW(),
  NOW()
);

-- Step 2: Guardian 프로필 생성 (user_id = 가장 최근 생성된 user의 id)
INSERT INTO public.guardians (user_id, address, relationship_to_patient, emergency_contact, created_at, updated_at)
SELECT user_id, '서울시 강남구 테헤란로', '자녀', '010-1234-5678', NOW(), NOW()
FROM public.users
WHERE email = 'dev@test.com'
LIMIT 1;

-- Step 3: Patient 프로필 생성 (guardian_id = 방금 생성된 guardian의 id)
INSERT INTO public.patients (guardian_id, name, birth_date, gender, height, weight, care_address, region_code, care_level, profile_image_url, created_at, updated_at)
SELECT guardian_id, 'Test Patient', '1950-01-01'::DATE, 'Male', 170, 70, '서울시 강남구 테헤란로', 'SEOUL_GANGNAM', NULL, NULL, NOW(), NOW()
FROM public.guardians
WHERE user_id = (
  SELECT user_id FROM public.users WHERE email = 'dev@test.com' LIMIT 1
)
LIMIT 1;
