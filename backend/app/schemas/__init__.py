"""
Pydantic Schemas - 모든 스키마를 여기서 import
"""

# User & Authentication
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    SocialAccountBase,
    SocialAccountCreate,
    SocialAccountResponse,
    PersonalityTestBase,
    PersonalityTestCreate,
    PersonalityTestResponse,
    TokenResponse,
    KakaoLoginRequest,
    KakaoLoginResponse,
)

# Profile
from app.schemas.guardian import (
    GuardianBase,
    GuardianCreate,
    GuardianUpdate,
    GuardianResponse,
)

from app.schemas.patient import (
    PatientBase,
    PatientCreate,
    PatientUpdate,
    PatientResponse,
    PatientDetailResponse,
)

from app.schemas.caregiver import (
    CaregiverBase,
    CaregiverCreate,
    CaregiverUpdate,
    CaregiverResponse,
    CaregiverDetailResponse,
)

# Personality
from app.schemas.personality import (
    PersonalityScoreBase,
    PatientPersonalityCreate,
    PatientPersonalityUpdate,
    PatientPersonalityResponse,
    CaregiverPersonalityCreate,
    CaregiverPersonalityUpdate,
    CaregiverPersonalityResponse,
)

# Health
from app.schemas.health import (
    HealthConditionBase,
    HealthConditionCreate,
    HealthConditionUpdate,
    HealthConditionResponse,
    MedicationBase,
    MedicationCreate,
    MedicationUpdate,
    MedicationResponse,
    DietaryPreferenceBase,
    DietaryPreferenceCreate,
    DietaryPreferenceUpdate,
    DietaryPreferenceResponse,
)

# Matching
from app.schemas.matching import (
    CaregiverAvailabilityBase,
    CaregiverAvailabilityCreate,
    CaregiverAvailabilityUpdate,
    CaregiverAvailabilityResponse,
    MatchingRequestBase,
    MatchingRequestCreate,
    MatchingRequestUpdate,
    MatchingRequestResponse,
    MatchingResultBase,
    MatchingResultCreate,
    MatchingResultUpdate,
    MatchingResultResponse,
    MatchingResultDetailResponse,
)

# Care Execution
from app.schemas.schedule import (
    ScheduleBase,
    ScheduleCreate,
    ScheduleUpdate,
    ScheduleResponse,
    ScheduleDetailResponse,
)

from app.schemas.care_log import (
    CareLogBase,
    CareLogCreate,
    CareLogUpdate,
    CareLogResponse,
)

from app.schemas.meal_plan import (
    MealPlanBase,
    MealPlanCreate,
    MealPlanUpdate,
    MealPlanResponse,
)

from app.schemas.report import (
    CareReportBase,
    CareReportCreate,
    CareReportUpdate,
    CareReportResponse,
)

# Review
from app.schemas.review import (
    ReviewBase,
    ReviewCreate,
    ReviewUpdate,
    ReviewResponse,
)

__all__ = [
    # User & Authentication
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserResponse",
    "SocialAccountBase",
    "SocialAccountCreate",
    "SocialAccountResponse",
    "PersonalityTestBase",
    "PersonalityTestCreate",
    "PersonalityTestResponse",
    "TokenResponse",
    "KakaoLoginRequest",
    "KakaoLoginResponse",
    # Profile
    "GuardianBase",
    "GuardianCreate",
    "GuardianUpdate",
    "GuardianResponse",
    "PatientBase",
    "PatientCreate",
    "PatientUpdate",
    "PatientResponse",
    "PatientDetailResponse",
    "CaregiverBase",
    "CaregiverCreate",
    "CaregiverUpdate",
    "CaregiverResponse",
    "CaregiverDetailResponse",
    # Personality
    "PersonalityScoreBase",
    "PatientPersonalityCreate",
    "PatientPersonalityUpdate",
    "PatientPersonalityResponse",
    "CaregiverPersonalityCreate",
    "CaregiverPersonalityUpdate",
    "CaregiverPersonalityResponse",
    # Health
    "HealthConditionBase",
    "HealthConditionCreate",
    "HealthConditionUpdate",
    "HealthConditionResponse",
    "MedicationBase",
    "MedicationCreate",
    "MedicationUpdate",
    "MedicationResponse",
    "DietaryPreferenceBase",
    "DietaryPreferenceCreate",
    "DietaryPreferenceUpdate",
    "DietaryPreferenceResponse",
    # Matching
    "CaregiverAvailabilityBase",
    "CaregiverAvailabilityCreate",
    "CaregiverAvailabilityUpdate",
    "CaregiverAvailabilityResponse",
    "MatchingRequestBase",
    "MatchingRequestCreate",
    "MatchingRequestUpdate",
    "MatchingRequestResponse",
    "MatchingResultBase",
    "MatchingResultCreate",
    "MatchingResultUpdate",
    "MatchingResultResponse",
    "MatchingResultDetailResponse",
    # Care Execution
    "ScheduleBase",
    "ScheduleCreate",
    "ScheduleUpdate",
    "ScheduleResponse",
    "ScheduleDetailResponse",
    "CareLogBase",
    "CareLogCreate",
    "CareLogUpdate",
    "CareLogResponse",
    "MealPlanBase",
    "MealPlanCreate",
    "MealPlanUpdate",
    "MealPlanResponse",
    "CareReportBase",
    "CareReportCreate",
    "CareReportUpdate",
    "CareReportResponse",
    # Review
    "ReviewBase",
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
]
