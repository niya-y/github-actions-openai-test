// frontend/my-app/src/types/api.ts

// ==================== 보호자 ====================

export interface GuardianCreateRequest {
  name: string;
  phone: string;
  address: string;
  relationship: string;
}

export interface GuardianResponse {
  guardian_id: number;
  user_id: number;
  name: string;
  phone: string;
  address: string;
  relationship: string;
  created_at: string;
}

// ==================== 환자 ====================

// 질병 항목 타입 정의
export interface DiseaseItem {
  id: string;
  name: string;
  icon?: string;
}

export interface PatientCreateRequest {
  name: string;
  age?: number;
  birth_date?: string;
  gender: 'Male' | 'Female';
  relationship: string;
}

export interface PatientResponse {
  patient_id: number;
  name: string;
  birth_date: string;
  age: number;
  gender: 'Male' | 'Female';
  guardian_id: number;
  created_at: string;
}

export interface HealthStatusUpdateRequest {
  selectedDiseases: DiseaseItem[];
  mobility_status: string;
}

export interface HealthConditionResponse {
  condition_id: number;
  patient_id: number;
  selected_diseases: DiseaseItem[];
  mobility_status: string;
  created_at: string;
}

export interface MedicationsCreateRequest {
  medicine_names: string[];
}

export interface MedicationResponse {
  med_id: number;
  patient_id: number;
  medicine_names: string[];
  created_at: string;
}

// ==================== OCR 약봉지 인식 ====================

export interface MedicineDetail {
  item_name: string;        // 약 이름
  entp_name: string;        // 제조사
  item_seq: string;         // 품목기준코드
  efficacy: string;         // 효능
  usage: string;            // 사용법
  precaution: string;       // 주의사항
  side_effect: string;      // 부작용
  storage: string;          // 보관법
  interaction: string;      // 상호작용
  item_image: string;       // 약품 이미지 URL
}

export interface OCRResultResponse {
  success: boolean;
  medicines: MedicineDetail[];
  medicine_names: string[];
  confidence: number;
  unverified_names: string[];
  message: string;
}

// ==================== 성향 테스트 ====================

export interface PersonalityTestRequest {
  user_type: 'guardian' | 'caregiver';
  answers: {
    step1: string;
    step2: string;
    step3: string;
  };
}

export interface PersonalityTestResponse {
  test_id: number;
  user_id: number;
  scores: {
    empathy_score: number;
    activity_score: number;
    patience_score: number;
    independence_score: number;
  };
  ai_analysis: string;
  created_at: string;
}

// ==================== 매칭 ====================

export interface MatchingRequirements {
  care_type: string;
  time_slots: string[];
  gender: 'Male' | 'Female' | 'any';
  experience: string;
  skills: string[];
}

export interface MatchingRequest {
  patient_id: number;
  requirements: MatchingRequirements;
}

export interface CaregiverMatch {
  matching_id?: number;
  caregiver_id: number;
  caregiver_name: string;
  grade: string;
  match_score: number;
  experience_years: number;
  specialties?: string[];
  hourly_rate: number;
  avg_rating: number;
  profile_image_url: string;
  personality_analysis?: string;
  job_title?: string;
  availability?: string[];
}

export interface MatchingResponse {
  matches: CaregiverMatch[];
  total_count: number;
}

// ==================== 리뷰 ====================

export interface ReviewCreateRequest {
  rating: number;
  comment: string;
}

export interface ReviewResponse {
  review_id: number;
  matching_id: number;
  rating: number;
  comment: string;
  created_at: string;
}

// ==================== 케어 플랜 ====================

export interface Schedule {
  schedule_id: number;
  title: string;
  start_time: string;
  end_time: string;
  category: string;
  is_completed: boolean;
}

export interface MealPlan {
  meal_plan_id: number;
  meal_date: string;
  meal_type: string;
  menu_name: string;
  nutrition_info: {
    calories: number;
    protein: number;
    carbs: number;
    fat: number;
  };
}

export interface CarePlansResponse {
  type: 'weekly' | 'monthly';
  schedules: Schedule[];
  meal_plans: MealPlan[];
}

// ==================== 마이페이지 ====================

export interface DashboardResponse {
  user: {
    user_id: number;
    name: string;
    email: string;
    phone: string;
    user_type: string;
    gender?: 'Male' | 'Female';
  };
  guardian: {
    guardian_id: number;
    address: string;
    relationship: string;
  } | null;
  patients: Array<{
    patient_id: number;
    name: string;
    age: number;
    care_level: string;
  }>;
  active_matching: {
    caregiver_name: string;
    match_score: number;
    start_date: string;
  } | null;
}
