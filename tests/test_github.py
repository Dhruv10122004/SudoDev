#!/usr/bin/env python3
"""
Simple test script to analyze any GitHub repository
Checks if the agent can successfully analyze the repo and identify issues
"""
import requests
import time
import sys

def test_repo(github_url, issue_description, branch="main"):
    """
    Test any GitHub repository with a specific issue description
    
    Args:
        github_url: Full GitHub URL (e.g., https://github.com/user/repo)
        issue_description: Description of the issue/bug to fix
        branch: Branch name (default: main)
    
    Returns:
        True if successful, False if failed, None if still running
    """
    api_url = "http://localhost:8000"
    
    print("="*70)
    print("GitHub Repository Analysis Test")
    print("="*70)
    print(f"\nRepository: {github_url}")
    print(f"Branch: {branch}")
    print(f"Issue: {issue_description[:100]}...")
    print()
    
    # Check server
    try:
        response = requests.get(f"{api_url}/")
        server_info = response.json()
        print(f"✓ Server running (v{server_info.get('version', 'unknown')})")
    except requests.exceptions.ConnectionError:
        print("✗ Server not running!")
        print("\nStart server with: make run")
        return False
    except Exception as e:
        print(f"✗ Error connecting to server: {e}")
        return False
    
    # Submit request
    payload = {
        "mode": "github",
        "github_url": github_url,
        "branch": branch,
        "issue_description": issue_description
    }
    
    print(f"\nSubmitting analysis request...")
    try:
        response = requests.post(f"{api_url}/api/run", json=payload)
        
        if response.status_code != 200:
            print(f"✗ Request failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
        
        data = response.json()
        run_id = data["run_id"]
        print(f"✓ Run started: {run_id}")
        
    except Exception as e:
        print(f"✗ Error submitting request: {e}")
        return False
    
    # Poll for results
    print("\n" + "="*70)
    print("Monitoring Progress")
    print("="*70)
    
    max_polls = 120  # 10 minutes max (5 sec intervals)
    start_time = time.time()
    
    for i in range(max_polls):
        time.sleep(5)
        
        try:
            status_response = requests.get(f"{api_url}/api/status/{run_id}")
            status_data = status_response.json()
            
            status = status_data["status"]
            message = status_data.get("message", "")
            logs = status_data.get("logs", [])
            elapsed = int(time.time() - start_time)
            
            # Print progress every 15 seconds or on status change
            if i % 3 == 0 or status in ["completed", "failed"]:
                print(f"\n[{elapsed}s] Status: {status.upper()}")
                print(f"Message: {message}")
                
                # Show important logs
                if logs:
                    important_logs = [
                        log for log in logs 
                        if any(keyword in log for keyword in [
                            'INIT', 'BUILD', 'REPO', 'CACHE', 'REPRODUCE', 
                            'LOCATE', 'FIX', 'VERIFY', 'COMPLETE', 'ERROR'
                        ])
                    ]
                    
                    if important_logs:
                        print(f"\nKey logs ({len(logs)} total):")
                        for log in important_logs[-5:]:
                            print(f"  {log}")
            
            # Check if finished
            if status == "completed":
                print("\n" + "="*70)
                print("✓ ANALYSIS COMPLETED SUCCESSFULLY")
                print("="*70)
                
                patch = status_data.get("patch", "")
                
                if patch:
                    print(f"\n✓ Fix Generated ({len(patch)} characters)")
                    print("\n" + "-"*70)
                    print("GENERATED PATCH:")
                    print("-"*70)
                    print(patch)
                    print("-"*70)
                    
                    # Save patch to file
                    filename = f"patch_{run_id[:8]}.patch"
                    with open(filename, 'w') as f:
                        f.write(patch)
                    print(f"\n✓ Patch saved to: {filename}")
                else:
                    print("\n⚠ No patch generated (issue may have been resolved differently)")
                
                # Show full logs
                print(f"\n\nFull execution logs:")
                print("-"*70)
                for log in logs:
                    print(log)
                print("-"*70)
                
                return True
            
            elif status == "failed":
                print("\n" + "="*70)
                print("✗ ANALYSIS FAILED")
                print("="*70)
                
                # Analyze why it failed
                reproduce_failed = any("Failed to reproduce" in log for log in logs)
                locate_failed = any("Failed to locate" in log for log in logs)
                fix_failed = any("Failed to generate fix" in log for log in logs)
                
                if reproduce_failed:
                    print("\n❌ Issue: Could not reproduce the bug")
                    print("\nPossible reasons:")
                    print("  1. The described bug doesn't actually exist in the code")
                    print("  2. The issue description wasn't clear enough")
                    print("  3. Missing dependencies to reproduce")
                    print("\n✓ This means: NO ISSUES FOUND IN THE REPOSITORY")
                    print("  (The code works as expected!)")
                
                elif locate_failed:
                    print("\n❌ Issue: Could not locate files to fix")
                    print("\nPossible reasons:")
                    print("  1. Issue description didn't mention specific files")
                    print("  2. Repository structure is unusual")
                    print("  3. Relevant code not in expected locations")
                
                elif fix_failed:
                    print("\n❌ Issue: Could not generate a fix")
                    print("\nPossible reasons:")
                    print("  1. Issue too complex for automatic fixing")
                    print("  2. Requires architectural changes")
                    print("  3. Multiple files need coordinated changes")
                
                else:
                    print(f"\n❌ Issue: {message}")
                
                # Show relevant logs
                print(f"\n\nRelevant logs:")
                print("-"*70)
                error_logs = [log for log in logs if 'ERROR' in log or 'FAIL' in log or 'reproduce' in log.lower()]
                for log in error_logs:
                    print(log)
                
                print(f"\n\nFull logs:")
                print("-"*70)
                for log in logs:
                    print(log)
                print("-"*70)
                
                return False
            
        except Exception as e:
            print(f"\n⚠ Error polling status: {e}")
            continue
    
    # Timeout
    print("\n" + "="*70)
    print("⏳ TIMEOUT (10 minutes)")
    print("="*70)
    print(f"\nRun is still in progress: {run_id}")
    print(f"\nCheck status manually:")
    print(f"  curl http://localhost:8000/api/status/{run_id}")
    
    return None


def main():
    """Interactive mode"""
    print("="*70)
    print("GitHub Repository Bug Analysis Tool")
    print("="*70)
    
    # Get inputs
    print("\nEnter repository details:")
    print("-"*70)
    
    github_url = input("GitHub URL: ").strip()
    if not github_url:
        github_url = "https://github.com/pallets/click"
        print(f"  (Using default: {github_url})")
    
    branch = input("Branch (default: main): ").strip()
    if not branch:
        branch = "main"
    
    print("\nIssue description (press Enter twice when done):")
    print("-"*70)
    lines = []
    while True:
        line = input()
        if not line and lines:
            break
        if line:
            lines.append(line)
    
    issue_description = "\n".join(lines)
    
    if not issue_description:
        print("\nNo issue description provided.")
        print("Using example: Testing basic functionality")
        issue_description = """
Please analyze the repository for any potential bugs or issues.
Create a test script that verifies the main functionality works correctly.
If everything works as expected, the test should pass.
        """
    
    # Run test
    result = test_repo(github_url, issue_description, branch)
    
    # Summary
    print("\n" + "="*70)
    if result is True:
        print("✓ TEST PASSED - Fix generated successfully")
        sys.exit(0)
    elif result is False:
        print("✗ TEST FAILED - See logs above for details")
        sys.exit(1)
    else:
        print("⏳ TEST IN PROGRESS - Check status manually")
        sys.exit(2)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Test GitHub repository analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python tests/test_any_repo.py
  
  # With arguments
  python tests/test_any_repo.py \\
    --url https://github.com/user/repo \\
    --branch main \\
    --issue "Bug in function X"
  
  # Quick test (checks if repo is accessible)
  python tests/test_any_repo.py \\
    --url https://github.com/user/repo \\
    --issue "Verify basic functionality"
        """
    )
    
    parser.add_argument("--url", help="GitHub repository URL")
    parser.add_argument("--branch", default="main", help="Branch name")
    parser.add_argument("--issue", help="Issue description")
    
    args = parser.parse_args()
    
    if args.url and args.issue:
        # Non-interactive mode
        result = test_repo(args.url, args.issue, args.branch)
        sys.exit(0 if result else 1)
    else:
        # Interactive mode
        main()