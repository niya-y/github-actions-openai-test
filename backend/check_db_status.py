import sys
import os

# 현재 디렉토리를 sys.path에 추가하여 app 모듈을 찾을 수 있게 함
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.models.user import User, UserTypeEnum
from app.models.profile import Guardian, Patient, Caregiver
from app.models.matching import MatchingRequest, MatchingResult

def check_status():
    db = SessionLocal()
    
    print("\n=== User Status ===")
    users = db.query(User).all()
    for user in users:
        print(f"ID: {user.user_id}, Name: {user.name}, Email: {user.email}, Type: {user.user_type}")

    print("\n=== Guardian Status ===")
    guardians = db.query(Guardian).all()
    for g in guardians:
        print(f"G_ID: {g.guardian_id}, User_ID: {g.user_id}, Name: {g.user.name}")

    print("\n=== Patient Status ===")
    patients = db.query(Patient).all()
    for p in patients:
        print(f"P_ID: {p.patient_id}, G_ID: {p.guardian_id}, Name: {p.name}")

    print("\n=== Matching Requests & Results ===")
    requests = db.query(MatchingRequest).all()
    print(f"Total Requests: {len(requests)}")
    for req in requests:
        print(f"Request ID: {req.request_id}, Patient ID: {req.patient_id}, Is Active: {req.is_active}, Created: {req.created_at}")
        
        results = db.query(MatchingResult).filter(MatchingResult.request_id == req.request_id).all()
        if results:
            for res in results:
                print(f"  -> Result ID: {res.matching_id}, Caregiver ID: {res.caregiver_id}, Status: {res.status}")
        else:
            print("  -> No Results found (Not saved or failed)")

    db.close()

if __name__ == "__main__":
    check_status()
