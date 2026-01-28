import requests
import time
import os
from typing import List, Dict, Optional

# Constants
GITHUB_API_URL = "https://api.github.com/repos"
GOOD_FIRST_ISSUE_LABELS = {
    "good first issue",
    "good-first-issue",
    "beginner",
    "beginner friendly",
    "beginner-friendly",
    "easy",
    "help wanted",
    "help-wanted",
    "contributions welcome",
    "first-timers-only",
    "starter",
    "starter bug"
}

class GitHubAPIError(Exception):
    pass

class RateLimitExceededError(GitHubAPIError):
    pass

def is_good_first_issue(labels: List[Dict]) -> bool:
    """Checks if any label matches the 'good first issue' keywords."""
    for label in labels:
        if label['name'].lower() in GOOD_FIRST_ISSUE_LABELS:
            return True
    return False

def fetch_repo_issues(owner: str, repo: str, token: str) -> List[Dict]:
    """
    Fetches open issues from a GitHub repository.
    
    Args:
        owner: GitHub owner (e.g., 'huggingface')
        repo: Repository name (e.g., 'transformers')
        token: GitHub Personal Access Token
        
    Returns:
        List of dictionaries containing processed issue data.
    """
    url = f"{GITHUB_API_URL}/{owner}/{repo}/issues"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    params = {
        "state": "open",
        "per_page": 100,
        "sort": "created",
        "direction": "desc"
    }

    try:
        # Respectful delay
        time.sleep(1)
        
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 200:
            issues_data = response.json()
            processed_issues = []
            
            for item in issues_data:
                # Skip Pull Requests (GitHub API returns PRs as issues)
                if 'pull_request' in item:
                    continue
                    
                labels_list = [l['name'] for l in item.get('labels', [])]
                assignees = item.get('assignees', [])
                
                processed_issue = {
                    "github_issue_id": item['number'],
                    "github_issue_url": item['html_url'],
                    "title": item['title'],
                    "state": item['state'],
                    "labels": ",".join(labels_list),
                    "is_assigned": len(assignees) > 0,
                    "assignee_login": assignees[0]['login'] if assignees else None,
                    "comments_count": item['comments'],
                    "created_at_github": item['created_at'],
                    "body_preview": (item.get('body') or "")[:200],
                    "is_good_first_issue": is_good_first_issue(item.get('labels', []))
                }
                
                processed_issues.append(processed_issue)
                
            return processed_issues
            
        elif response.status_code == 403:
            # Check for specific rate limit message
            if "rate limit" in response.text.lower():
                raise RateLimitExceededError("GitHub API rate limit exceeded.")
            else:
                raise GitHubAPIError(f"Access Forbidden: {response.text}")
                
        elif response.status_code == 404:
            print(f"Warning: Repository {owner}/{repo} not found.")
            return []
            
        else:
            raise GitHubAPIError(f"Error fetching issues: {response.status_code} - {response.text}")

    except requests.exceptions.Timeout:
        print(f"Timeout fetching {owner}/{repo}. Retrying...")
        # Simple retry logic could go here, for now just failing gracefully
        return []
    except Exception as e:
        print(f"Unexpected error for {owner}/{repo}: {str(e)}")
        return []

if __name__ == "__main__":
    # Test block
    from dotenv import load_dotenv
    load_dotenv()
    
    token = os.getenv("GITHUB_TOKEN")
    if not token or token == "your_token_here":
        print("Please set GITHUB_TOKEN in .env file to test.")
    else:
        print("Testing fetch for 'streamlit/streamlit'...")
        issues = fetch_repo_issues("streamlit", "streamlit", token)
        print(f"Found {len(issues)} issues.")
        if issues:
            print("Sample Issue:", issues[0]['title'])
