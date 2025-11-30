"""
모델 통합 (schema.sql 기반)
"""

from app.models.user import User, SocialAccount, PersonalityTest, UserTypeEnum, SocialProviderEnum
from app.models.profile import Guardian, Patient, Caregiver, GenderEnum, CareLevelEnum
from app.models.care_details import (
    PatientPersonality,
    CaregiverPersonality,
    HealthCondition,
    Medication,
    DietaryPreference,
)
from app.models.matching import (
    MatchingRequest,
    MatchingResult,
    CaregiverAvailability,
    GradeEnum,
    MatchingStatusEnum,
)
from app.models.review import Review
from app.models.care_execution import (
    Schedule,
    CareLog,
    MealPlan,
    CareReport,
    MealTypeEnum,
    ReportTypeEnum,
    CareCategoryEnum,
)

__all__ = [
    # User models
    "User",
    "SocialAccount",
    "PersonalityTest",
    # Profile models
    "Guardian",
    "Patient",
    "Caregiver",
    # Care details
    "PatientPersonality",
    "CaregiverPersonality",
    "HealthCondition",
    "Medication",
    "DietaryPreference",
    # Matching
    "MatchingRequest",
    "MatchingResult",
    "CaregiverAvailability",
    # Review
    "Review",
    # Care execution
    "Schedule",
    "CareLog",
    "MealPlan",
    "CareReport",
    # Enums
    "UserTypeEnum",
    "SocialProviderEnum",
    "GenderEnum",
    "CareLevelEnum",
    "GradeEnum",
    "MatchingStatusEnum",
    "MealTypeEnum",
    "ReportTypeEnum",
    "CareCategoryEnum",
]
