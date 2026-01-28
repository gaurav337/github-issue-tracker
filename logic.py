import time
import os
from datetime import datetime, timedelta
import database
import github_client

def get_github_token():
    # Priority: 1. Streamlit Secrets, 2. Environment Variable
    import streamlit as st
    if hasattr(st, "secrets") and "GITHUB_TOKEN" in st.secrets:
        return st.secrets["GITHUB_TOKEN"]
        
    from dotenv import load_dotenv
    load_dotenv()
    return os.getenv("GITHUB_TOKEN")

def refresh_repository(repo_id: int):
    """
    Refreshes a single repository.
    Returns dict with stats: {new, updated, errors}
    """
    repo = database.get_repository(repo_id)
    if not repo:
        return {"error": "Repository not found"}
        
    token = get_github_token()
    if not token:
        return {"error": "GitHub Token not found"}
        
    print(f"Refreshing {repo['full_name']}...")
    
    # Fetch from GitHub
    try:
        issues = github_client.fetch_repo_issues(repo['github_owner'], repo['github_repo'], token)
    except Exception as e:
        return {"error": str(e)}
        
    new_count = 0
    updated_count = 0
    
    # Sync with DB
    for issue in issues:
        result = database.upsert_issue(repo_id, issue)
        if result == 'new':
            new_count += 1
        elif result == 'updated':
            updated_count += 1
            
    # Update repo timestamp
    database.update_repo_timestamp(repo_id, len(issues))
    
    return {
        "new": new_count,
        "updated": updated_count,
        "total": len(issues),
        "repo_name": repo['full_name']
    }

def refresh_category(category_id: int, progress_callback=None):
    """
    Refreshes all active repos in a category.
    progress_callback: function(current, total, status_text)
    """
    repos = database.get_repositories(category_id, active_only=True)
    stats = {
        "total_new": 0,
        "total_updated": 0,
        "repos_processed": 0,
        "repos_failed": 0,
        "details": []
    }
    
    for i, repo in enumerate(repos):
        if progress_callback:
            progress_callback(i, len(repos), f"Refreshing {repo['full_name']}...")
            
        result = refresh_repository(repo['id'])
        
        if "error" in result:
            stats["repos_failed"] += 1
            stats["details"].append(f"Failed {repo['full_name']}: {result['error']}")
        else:
            stats["repos_processed"] += 1
            stats["total_new"] += result["new"]
            stats["total_updated"] += result["updated"]
            
        # Small delay to be safe between repos if not handled in client
        time.sleep(0.5)
        
    return stats

def refresh_all(progress_callback=None):
    """
    Refreshes ALL active repositories.
    """
    repos = database.get_repositories(active_only=True)
    stats = {
        "total_new": 0,
        "total_updated": 0,
        "repos_processed": 0,
        "repos_failed": 0
    }
    
    for i, repo in enumerate(repos):
        if progress_callback:
            progress_callback(i, len(repos), f"Refreshing {repo['full_name']}...")
            
        result = refresh_repository(repo['id'])
        
        if "error" in result:
            stats["repos_failed"] += 1
        else:
            stats["repos_processed"] += 1
            stats["total_new"] += result["new"]
            stats["total_updated"] += result["updated"]
            
        time.sleep(0.5)
        
    return stats
