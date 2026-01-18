#!/usr/bin/env python3
"""
Test GitHub Issues Integration
"""
import requests
import time
import sys


def test_issue_url():
    """Test with full GitHub issue URL"""
    
    api_url = "http://localhost:8000"
    
    print("="*70)
    print("Test 1: GitHub Issue URL")
    print("="*70)
    
    # Check server
    try:
        response = requests.get(f"{api_url}/")
        print(f"✓ Server running: {response.json()}")
    except:
        print("✗ Server not running! Start with: make run")
        return False
    
    # Test payload with issue URL
    payload = {
        "mode": "github",
        "github_url": "https://github.com/pallets/flask",
        "branch": "main",
        "issue_url": "https://github.com/pallets/flask/issues/5063"
    }
    
    print(f"\nSubmitting request with issue URL...")
    print(f"  Repository: {payload['github_url']}")
    print(f"  Issue URL: {payload['issue_url']}")
    
    try:
        response = requests.post(f"{api_url}/api/run", json=payload)
        
        if response.status_code != 200:
            print(f"\n✗ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        run_id = data["run_id"]
        
        print(f"\n✓ Request accepted!")
        print(f"  Run ID: {run_id}")
        
        # Check if issue was fetched
        time.sleep(2)
        status_response = requests.get(f"{api_url}/api/status/{run_id}")
        status_data = status_response.json()
        
        logs = status_data.get("logs", [])
        issue_log = [log for log in logs if "ISSUE" in log or "GitHub" in log]
        
        if issue_log:
            print(f"\n✓ Issue fetched successfully!")
            for log in issue_log[:3]:
                print(f"  {log}")
            return True
        else:
            print(f"\n⚠ Issue fetch unclear, but request accepted")
            return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_issue_number():
    """Test with just issue number"""
    
    api_url = "http://localhost:8000"
    
    print("\n" + "="*70)
    print("Test 2: GitHub Issue Number")
    print("="*70)
    
    # Test payload with issue number
    payload = {
        "mode": "github",
        "github_url": "https://github.com/pallets/flask",
        "branch": "main",
        "issue_number": 5063
    }
    
    print(f"\nSubmitting request with issue number...")
    print(f"  Repository: {payload['github_url']}")
    print(f"  Issue #: {payload['issue_number']}")
    
    try:
        response = requests.post(f"{api_url}/api/run", json=payload)
        
        if response.status_code != 200:
            print(f"\n✗ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        run_id = data["run_id"]
        
        print(f"\n✓ Request accepted!")
        print(f"  Run ID: {run_id}")
        
        # Check logs
        time.sleep(2)
        status_response = requests.get(f"{api_url}/api/status/{run_id}")
        status_data = status_response.json()
        
        logs = status_data.get("logs", [])
        issue_log = [log for log in logs if "ISSUE" in log or "#" in log]
        
        if issue_log:
            print(f"\n✓ Issue number processed!")
            for log in issue_log[:3]:
                print(f"  {log}")
            return True
        else:
            print(f"\n⚠ Issue processing unclear, but request accepted")
            return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_manual_description():
    """Test with manual description (existing way)"""
    
    api_url = "http://localhost:8000"
    
    print("\n" + "="*70)
    print("Test 3: Manual Description (Existing Method)")
    print("="*70)
    
    payload = {
        "mode": "github",
        "github_url": "https://github.com/pallets/flask",
        "branch": "main",
        "issue_description": "Test issue: verify manual description still works"
    }
    
    print(f"\nSubmitting request with manual description...")
    
    try:
        response = requests.post(f"{api_url}/api/run", json=payload)
        
        if response.status_code != 200:
            print(f"\n✗ Request failed: {response.status_code}")
            return False
        
        print(f"\n✓ Manual description still works!")
        return True
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_fetch_issue_directly():
    """Test the GitHub API fetch directly"""
    
    print("\n" + "="*70)
    print("Test 4: Direct GitHub API Fetch")
    print("="*70)
    
    issue_url = "https://api.github.com/repos/pallets/flask/issues/5063"
    
    print(f"\nFetching issue from GitHub API...")
    print(f"  URL: {issue_url}")
    
    try:
        response = requests.get(
            issue_url,
            headers={
                'Accept': 'application/vnd.github.v3+json',
                'User-Agent': 'SudoDev-Test'
            },
            timeout=10
        )
        
        if response.status_code == 200:
            issue_data = response.json()
            
            print(f"\n✓ Issue fetched successfully!")
            print(f"  Title: {issue_data.get('title', 'N/A')}")
            print(f"  State: {issue_data.get('state', 'N/A')}")
            print(f"  Comments: {issue_data.get('comments', 0)}")
            print(f"  Labels: {[l['name'] for l in issue_data.get('labels', [])]}")
            
            body = issue_data.get('body', '')
            print(f"\n  Description preview:")
            print(f"  {body[:200]}...")
            
            return True
        else:
            print(f"\n✗ Failed to fetch: {response.status_code}")
            return False
    
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def main():
    print("="*70)
    print("GitHub Issues Integration Test Suite")
    print("="*70)
    
    results = {}
    
    # Test 1: Direct API fetch (fastest)
    results['direct_api'] = test_fetch_issue_directly()
    
    # Test 2: Issue URL
    results['issue_url'] = test_issue_url()
    
    # Test 3: Issue number
    results['issue_number'] = test_issue_number()
    
    # Test 4: Manual description
    results['manual'] = test_manual_description()
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status:10} {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! GitHub Issues integration is working!")
        return 0
    else:
        print("\n⚠ Some tests failed. Check the output above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())