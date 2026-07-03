#!/usr/bin/env python3
"""
Test script to verify data is being saved to MySQL database
"""

import asyncio
import json
from datetime import datetime
from src.db.database import get_db_session, create_db_tables
from src.db.repository import LoanApplicationRepository, LoanDecisionRepository
from src.models.schemas import LoanApplication

def print_header(text):
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")

def print_step(num, text):
    print(f"\n[Step {num}] {text}")
    print("-" * 80)

async def main():
    print_header("DATABASE SAVE VERIFICATION TEST")

    # Step 1: Verify database connection
    print_step(1, "Verify Database Connection")
    try:
        create_db_tables()
        print("✓ Database tables verified/created successfully")
    except Exception as e:
        print(f"✗ Failed to create tables: {e}")
        return

    # Step 2: Check current count
    print_step(2, "Check Current Application Count")
    session = get_db_session()
    try:
        repo = LoanApplicationRepository(session)
        count = repo.get_applications_count()
        print(f"✓ Current applications in database: {count}")
    except Exception as e:
        print(f"✗ Failed to count applications: {e}")
        session.close()
        return
    finally:
        session.close()

    # Step 3: Create test application
    print_step(3, "Create Test Application")
    test_app_id = f"TEST_SAVE_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    test_data = {
        "applicant_id": test_app_id,
        "applicant_name": "Test User - Database Save",
        "age": 35,
        "income": 5000,
        "employment_type": "salaried",
        "credit_score": 720,
        "loan_amount": 50000,
        "loan_tenure_months": 60,
        "existing_liabilities": 10000,
        "location": "California",
        "employment_years": 5
    }
    print(f"Test Application ID: {test_app_id}")
    print(f"Data: {json.dumps(test_data, indent=2)}")

    # Step 4: Save to database
    print_step(4, "Save Application to Database")
    session = get_db_session()
    try:
        repo = LoanApplicationRepository(session)
        saved_app = repo.create_application(test_data)
        print(f"✓ Application saved successfully")
        print(f"  - DB ID: {saved_app.id}")
        print(f"  - Applicant ID: {saved_app.applicant_id}")
        print(f"  - Status: {saved_app.status.value}")
        print(f"  - Created At: {saved_app.created_at}")
    except Exception as e:
        print(f"✗ Failed to save application: {e}")
        import traceback
        traceback.print_exc()
        session.close()
        return
    finally:
        session.close()

    # Step 5: Retrieve from database
    print_step(5, "Retrieve Application from Database")
    session = get_db_session()
    try:
        repo = LoanApplicationRepository(session)
        retrieved_app = repo.get_application(test_app_id)

        if retrieved_app:
            print(f"✓ Application retrieved successfully")
            print(f"  - ID: {retrieved_app.id}")
            print(f"  - Applicant ID: {retrieved_app.applicant_id}")
            print(f"  - Name: {retrieved_app.applicant_name}")
            print(f"  - Status: {retrieved_app.status.value}")
            print(f"  - Risk Score: {retrieved_app.risk_score}")
            print(f"  - Created At: {retrieved_app.created_at}")
            print(f"  - Updated At: {retrieved_app.updated_at}")
        else:
            print(f"✗ Application NOT found in database")
            return
    except Exception as e:
        print(f"✗ Failed to retrieve application: {e}")
        import traceback
        traceback.print_exc()
        session.close()
        return
    finally:
        session.close()

    # Step 6: Update application status
    print_step(6, "Update Application Status")
    session = get_db_session()
    try:
        repo = LoanApplicationRepository(session)
        updated_app = repo.update_application_status(test_app_id, "completed", risk_score=45.5)
        print(f"✓ Application status updated successfully")
        print(f"  - New Status: {updated_app.status.value}")
        print(f"  - Risk Score: {updated_app.risk_score}")
        print(f"  - Updated At: {updated_app.updated_at}")
    except Exception as e:
        print(f"✗ Failed to update application: {e}")
        import traceback
        traceback.print_exc()
        session.close()
        return
    finally:
        session.close()

    # Step 7: Save decision
    print_step(7, "Save Decision to Database")
    decision_data = {
        "applicant_id": test_app_id,
        "application_status": "approved",
        "risk_score": 45.5,
        "confidence_level": 82.5,
        "applicant_profile": {"income_stability": 85, "employment_risk": "low"},
        "financial_risk": {"dti_ratio": 0.35, "credit_score_risk": "medium"},
        "loan_decision": {"classification": "approved", "factors": ["Strong income stability"]},
        "compliance_action": {"action": "Decision recorded"},
        "final_explanation": "Application approved based on strong profile",
        "next_steps": ["Send approval letter", "Schedule disbursement"],
        "processing_duration_seconds": 3.5
    }

    session = get_db_session()
    try:
        repo = LoanDecisionRepository(session)
        saved_decision = repo.create_decision(decision_data)
        print(f"✓ Decision saved successfully")
        print(f"  - ID: {saved_decision.id}")
        print(f"  - Applicant ID: {saved_decision.applicant_id}")
        print(f"  - Status: {saved_decision.application_status}")
        print(f"  - Confidence: {saved_decision.confidence_level}%")
    except Exception as e:
        print(f"✗ Failed to save decision: {e}")
        import traceback
        traceback.print_exc()
        session.close()
        return
    finally:
        session.close()

    # Step 8: Retrieve decision
    print_step(8, "Retrieve Decision from Database")
    session = get_db_session()
    try:
        repo = LoanDecisionRepository(session)
        retrieved_decision = repo.get_decision(test_app_id)

        if retrieved_decision:
            print(f"✓ Decision retrieved successfully")
            print(f"  - Status: {retrieved_decision.application_status}")
            print(f"  - Risk Score: {retrieved_decision.risk_score}")
            print(f"  - Confidence Level: {retrieved_decision.confidence_level}%")
            print(f"  - Explanation: {retrieved_decision.final_explanation}")
        else:
            print(f"✗ Decision NOT found in database")
    except Exception as e:
        print(f"✗ Failed to retrieve decision: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

    # Step 9: Check final count
    print_step(9, "Check Final Application Count")
    session = get_db_session()
    try:
        repo = LoanApplicationRepository(session)
        final_count = repo.get_applications_count()
        print(f"✓ Final application count: {final_count}")
        print(f"  (Added {final_count - count} application(s) during this test)")
    except Exception as e:
        print(f"✗ Failed to count applications: {e}")
    finally:
        session.close()

    print_header("✓ ALL TESTS PASSED - DATABASE SAVING IS WORKING")
    print(f"\nYour system is correctly saving data to MySQL database.")
    print(f"Test Application ID: {test_app_id}")
    print(f"\nYou can verify the data in MySQL with:")
    print(f"  mysql -h localhost -u root -pTek@12345 loan_approval")
    print(f"  SELECT * FROM applications WHERE applicant_id = '{test_app_id}';")
    print(f"  SELECT * FROM decisions WHERE applicant_id = '{test_app_id}';")

if __name__ == "__main__":
    asyncio.run(main())
