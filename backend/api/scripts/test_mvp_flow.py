import sys
import json
import requests
from datetime import datetime
from pathlib import Path

def test_mvp_flow(base_url: str, test_data_dir: str) -> bool:
    """
    Test the full MVP flow from trace upload to issue creation.
    
    Args:
        base_url: Base URL of the API
        test_data_dir: Directory containing test data
        
    Returns:
        bool indicating if test was successful
    """
    try:
        # Step 1: Register test user
        print("Step 1: Registering test user...")
        register_response = requests.post(
            f"{base_url}/api/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123"
            }
        )
        if register_response.status_code != 200:
            print(f"Registration failed: {register_response.text}")
            return False
        
        # Step 2: Login
        print("Step 2: Logging in...")
        login_response = requests.post(
            f"{base_url}/api/auth/login",
            data={
                "username": "test@example.com",
                "password": "testpassword123"
            }
        )
        if login_response.status_code != 200:
            print(f"Login failed: {login_response.text}")
            return False
        
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # Step 3: Upload test trace
        print("Step 3: Uploading test trace...")
        test_log_path = Path(test_data_dir) / "error_log.json"
        with open(test_log_path, "rb") as f:
            files = {"file": f}
            upload_response = requests.post(
                f"{base_url}/api/logs/upload",
                files=files,
                headers=headers
            )
        if upload_response.status_code != 200:
            print(f"Trace upload failed: {upload_response.text}")
            return False
        
        trace_id = upload_response.json()["trace_id"]
        
        # Step 4: Analyze trace
        print("Step 4: Analyzing trace...")
        analyze_response = requests.post(
            f"{base_url}/api/logs/analyze/{trace_id}",
            headers=headers
        )
        if analyze_response.status_code != 200:
            print(f"Trace analysis failed: {analyze_response.text}")
            return False
        
        # Step 5: Check for issues
        print("Step 5: Checking for issues...")
        issues_response = requests.get(
            f"{base_url}/api/issues",
            headers=headers
        )
        if issues_response.status_code != 200:
            print(f"Failed to get issues: {issues_response.text}")
            return False
        
        issues = issues_response.json()
        if not issues:
            print("No issues found after trace analysis")
            return False
        
        # Step 6: Update issue
        print("Step 6: Updating issue...")
        issue_id = issues[0]["id"]
        update_response = requests.put(
            f"{base_url}/api/issues/{issue_id}",
            json={
                "status": "assigned",
                "assigned_to_user_id": 1
            },
            headers=headers
        )
        if update_response.status_code != 200:
            print(f"Failed to update issue: {update_response.text}")
            return False
        
        # Step 7: Check audit logs
        print("Step 7: Checking audit logs...")
        audit_response = requests.get(
            f"{base_url}/api/audit",
            headers=headers
        )
        if audit_response.status_code != 200:
            print(f"Failed to get audit logs: {audit_response.text}")
            return False
        
        audit_logs = audit_response.json()
        if not audit_logs:
            print("No audit logs found")
            return False
        
        print("MVP flow test completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error during MVP flow test: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test_mvp_flow.py <base_url> <test_data_dir>")
        sys.exit(1)
    
    base_url = sys.argv[1]
    test_data_dir = sys.argv[2]
    
    if test_mvp_flow(base_url, test_data_dir):
        print("MVP flow test passed")
        sys.exit(0)
    else:
        print("MVP flow test failed")
        sys.exit(1) 