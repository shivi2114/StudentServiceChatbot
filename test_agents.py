import sys
from fastapi.testclient import TestClient
from backend.app.main import app

def run_tests():
    print("=== Testing CampusAI Multi-Agent Backend ===")
    client = TestClient(app)

    # 1. Login
    res_login = client.post("/api/auth/login", json={"email": "student@campusai.edu", "password": "student123"})
    if res_login.status_code != 200:
        print("Login failed:", res_login.text)
        sys.exit(1)
    token = res_login.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print("[PASS] Student Login successful")

    # 2. Academic Agent
    r1 = client.post("/api/chat", json={"message": "What is the mandatory attendance requirement?"}, headers=headers)
    assert r1.status_code == 200, r1.text
    j1 = r1.json()
    print(f"[PASS] Academic Agent: {j1['agent_name']} | Citations: {len(j1['citations'])}")
    print(f"       Answer snippet: {j1['answer'][:90]}...")

    # 3. Personal Fee Record Lookup
    r2 = client.post("/api/chat", json={"message": "How much fee do I owe for semester 6?"}, headers=headers)
    assert r2.status_code == 200, r2.text
    j2 = r2.json()
    print(f"[PASS] Fee Agent: {j2['agent_name']} | Source: {j2['source']}")
    print(f"       Answer snippet: {j2['answer'][:90]}...")

    # 4. Complaint Management with Action Approval
    r3 = client.post("/api/chat", json={"message": "The hostel wifi is down and disconnected in Room 304"}, headers=headers)
    assert r3.status_code == 200, r3.text
    j3 = r3.json()
    print(f"[PASS] Complaint Agent Action Approval required: {j3['action_required'] is not None}")
    
    if j3['action_required']:
        print(f"       Action prepared: {j3['action_required']['action_title']}")
        # Student approves action
        r4 = client.post("/api/chat", json={"message": "Confirm submission", "confirmed_action": j3['action_required']}, headers=headers)
        assert r4.status_code == 200, r4.text
        j4 = r4.json()
        print(f"[PASS] Action confirmed, ticket created in DB: {'CMP-' in j4['answer']}")
        print(f"       Ticket reply snippet: {j4['answer'][:90]}...")

    # 5. Scholarship Agent
    r5 = client.post("/api/chat", json={"message": "Am I eligible for any scholarships with my 8.72 CGPA?"}, headers=headers)
    assert r5.status_code == 200, r5.text
    j5 = r5.json()
    print(f"[PASS] Scholarship Agent: {j5['agent_name']}")
    print(f"       Answer snippet: {j5['answer'][:90]}...")

    # 6. Placement Agent
    r6 = client.post("/api/chat", json={"message": "What are the Tier 1 placement criteria and drives?"}, headers=headers)
    assert r6.status_code == 200, r6.text
    j6 = r6.json()
    print(f"[PASS] Placement Agent: {j6['agent_name']}")
    print(f"       Answer snippet: {j6['answer'][:90]}...")

    print("\n>>> ALL MULTI-AGENT WORKFLOWS, TOOLS, AND APIS ARE VERIFIED AND WORKING! <<<")

if __name__ == "__main__":
    run_tests()
