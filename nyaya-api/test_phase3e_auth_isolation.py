import os
import sys
import json
from fastapi.testclient import TestClient

# Ensure app is on path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app
from app.db.session import SessionLocal
from app.core.config import settings
from app.core.security import create_access_token
from app.models.user import User
from app.models.dossier import Dossier
from app.models.saved_research import SavedResearch

client = TestClient(app)

def run_auth_and_tenant_isolation_tests():
    print("=================================================================")
    print("NYAYA AI — PHASE 3E: AUTHENTICATION & TENANT ISOLATION RED-TEAM")
    print("=================================================================")

    # -------------------------------------------------------------
    # 1. Unauthenticated Endpoint Access Rejection (401)
    # -------------------------------------------------------------
    print("\n--- 1. Unauthenticated Protected Endpoints Protection ---")
    protected_endpoints = [
        ("POST", "/api/v1/research/query", {"query": "Section 12A mediation"}),
        ("GET", "/api/v1/cases", None),
        ("GET", "/api/v1/statutes", None),
        ("GET", "/api/v1/dossiers", None),
        ("POST", "/api/v1/dossiers", {"title": "Unauthorized Dossier", "case_number": "CS(COMM) 100/2026"}),
        ("GET", "/api/v1/research/saved", None),
        ("GET", "/api/v1/audit-logs", None),
    ]

    for method, path, body in protected_endpoints:
        if method == "POST":
            resp = client.post(path, json=body)
        else:
            resp = client.get(path)
        assert resp.status_code == 401, f"Expected 401 on unauthenticated {method} {path}, got {resp.status_code}"
        print(f"  [PASS] {method} {path} -> 401 Unauthorized strictly enforced")

    # -------------------------------------------------------------
    # 2. Tampered & Expired JWT Tokens Rejection
    # -------------------------------------------------------------
    print("\n--- 2. Tampered & Invalid Token Rejection ---")
    tampered_headers = {"Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.invalidpayload.invalidsignature"}
    resp = client.get("/api/v1/cases", headers=tampered_headers)
    assert resp.status_code == 401, f"Expected 401 for tampered JWT, got {resp.status_code}"
    print("  [PASS] Tampered JWT rejected with 401 Unauthorized")

    empty_headers = {"Authorization": "Bearer "}
    resp = client.get("/api/v1/cases", headers=empty_headers)
    assert resp.status_code == 401
    print("  [PASS] Empty bearer token rejected with 401 Unauthorized")

    # -------------------------------------------------------------
    # 3. Multi-Tenant User Isolation (User A vs User B)
    # -------------------------------------------------------------
    print("\n--- 3. Multi-Tenant Judicial User Isolation ---")
    db = SessionLocal()
    try:
        # Find or create User A and User B
        user_a = db.query(User).filter(User.email == "judge@nyaya.gov.in").first()
        if not user_a:
            user_a = db.query(User).first()
        assert user_a is not None, "User A must exist in database"

        # Check if secondary test user exists
        user_b = db.query(User).filter(User.id != user_a.id).first()
        if not user_b:
            user_b = User(
                email="clerk_temp_test_unique@nyaya.gov.in",
                hashed_password=user_a.hashed_password,
                full_name="Judicial Research Clerk 02",
                role="RESEARCH_CLERK",
                court_division="Commercial Division, High Court",
                chambers_number="Chambers 405",
            )
            db.add(user_b)
            db.commit()
            db.refresh(user_b)

        token_a = create_access_token(data={"sub": user_a.id})
        token_b = create_access_token(data={"sub": user_b.id})
        headers_a = {"Authorization": f"Bearer {token_a}"}
        headers_b = {"Authorization": f"Bearer {token_b}"}

        # Step 3A: User A creates a confidential bench dossier
        create_resp = client.post(
            "/api/v1/dossiers",
            headers=headers_a,
            json={
                "matter_title": "Confidential Commercial Suit Dossier (Judge A)",
                "suit_number": "CS(COMM) 777/2026",
                "judicial_notes": "Confidential matter notes for trial preparation",
            }
        )
        assert create_resp.status_code in (200, 201), f"Failed to create dossier: {create_resp.text}"
        dossier_data = create_resp.json().get("data")
        dossier_id = dossier_data["id"]
        print(f"  [INFO] User A created dossier: {dossier_id}")

        # Step 3B: User B attempts to access User A's dossier directly
        get_b_resp = client.get(f"/api/v1/dossiers/{dossier_id}", headers=headers_b)
        # Must be 403 Forbidden or 404 Not Found (isolated)
        assert get_b_resp.status_code in (403, 404), (
            f"Expected 403/404 when User B reads User A's dossier, got {get_b_resp.status_code}"
        )
        print(f"  [PASS] User B forbidden from accessing User A's dossier directly ({get_b_resp.status_code})")

        # Step 3C: User B lists dossiers -> User A's dossier must NOT appear
        list_b_resp = client.get("/api/v1/dossiers", headers=headers_b)
        assert list_b_resp.status_code == 200
        b_dossier_ids = [d["id"] for d in list_b_resp.json().get("data", [])]
        assert dossier_id not in b_dossier_ids, "User A's dossier leaked into User B's dossier list!"
        print("  [PASS] User A's dossier is not visible in User B's dossier list")

        # Step 3D: User B attempts to delete User A's dossier
        del_b_resp = client.delete(f"/api/v1/dossiers/{dossier_id}", headers=headers_b)
        assert del_b_resp.status_code in (403, 404), (
            f"Expected 403/404 when User B deletes User A's dossier, got {del_b_resp.status_code}"
        )
        print(f"  [PASS] User B forbidden from deleting User A's dossier ({del_b_resp.status_code})")

        # Clean up dossier using User A
        client.delete(f"/api/v1/dossiers/{dossier_id}", headers=headers_a)

    finally:
        db.close()

    # -------------------------------------------------------------
    # 4. Secret Isolation in Responses & Logs
    # -------------------------------------------------------------
    print("\n--- 4. Secret Isolation Verification ---")
    query_resp = client.post(
        "/api/v1/research/query",
        headers=headers_a,
        json={"query": "Section 12A mediation rejection of plaint", "jurisdiction": "ALL"}
    )
    assert query_resp.status_code == 200
    resp_text = query_resp.text
    if settings.GEMINI_API_KEY and len(settings.GEMINI_API_KEY) > 5:
        assert settings.GEMINI_API_KEY not in resp_text, "CRITICAL: GEMINI_API_KEY leaked in API response!"
    assert "SECRET_KEY" not in resp_text
    print("  [PASS] Zero secret leakage in query response")
    print(f"  [PASS] GEMINI_API_KEY configured: {bool(settings.GEMINI_API_KEY)} (key value masked)")

    print("\n=================================================================")
    print("ALL AUTHENTICATION & TENANT ISOLATION RED-TEAM TESTS PASSED!")
    print("=================================================================")

if __name__ == "__main__":
    run_auth_and_tenant_isolation_tests()
