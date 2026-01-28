import sqlite3
import os
from datetime import datetime

# Database file path
DB_NAME = "tracker.db"

def get_connection():
    """Returns a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

def init_db():
    """Initializes the database with the required tables."""
    conn = get_connection()
    cursor = conn.cursor()

    # Enable foreign key support
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Table 1: Categories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Table 2: Repositories
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS repositories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        github_owner TEXT NOT NULL,
        github_repo TEXT NOT NULL,
        full_name TEXT NOT NULL,
        category_id INTEGER,
        is_active BOOLEAN DEFAULT 1,
        last_refreshed_at TIMESTAMP,
        total_open_issues INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (category_id) REFERENCES categories (id)
    );
    """)

    # Table 3: Issues
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS issues (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        repository_id INTEGER,
        github_issue_id INTEGER NOT NULL,
        github_issue_url TEXT,
        title TEXT,
        state TEXT,
        labels TEXT,  -- Stored as JSON or comma-separated string
        is_assigned BOOLEAN DEFAULT 0,
        assignee_login TEXT,
        comments_count INTEGER DEFAULT 0,
        created_at_github TIMESTAMP,
        first_seen_at TIMESTAMP,
        last_updated_at TIMESTAMP,
        body_preview TEXT,
        seen_at TIMESTAMP,
        FOREIGN KEY (repository_id) REFERENCES repositories (id)
    );
    """)

    # --- Migration: Add seen_at to existing DB if missing ---
    try:
        cursor.execute("SELECT seen_at FROM issues LIMIT 1")
    except sqlite3.OperationalError:
        print("Migrating: Adding 'seen_at' column to issues table...")
        cursor.execute("ALTER TABLE issues ADD COLUMN seen_at TIMESTAMP")

    conn.commit()
    conn.close()
    print(f"Database {DB_NAME} initialized/updated successfully.")

# ... [seed_data function remains unchanged] ...

# --- NEW: Repo Management ---

def add_repository(owner, repo, category_id):
    conn = get_connection()
    full_name = f"{owner}/{repo}"
    
    # Check duplicate
    exists = conn.execute("SELECT id FROM repositories WHERE full_name = ?", (full_name,)).fetchone()
    if exists:
        conn.close()
        return False, "Repository already exists."
        
    conn.execute("""
        INSERT INTO repositories (github_owner, github_repo, full_name, category_id)
        VALUES (?, ?, ?, ?)
    """, (owner, repo, full_name, category_id))
    conn.commit()
    conn.close()
    return True, "Repository added successfully."

def delete_repository(repo_id):
    conn = get_connection()
    # Cascade delete issues first
    conn.execute("DELETE FROM issues WHERE repository_id = ?", (repo_id,))
    conn.execute("DELETE FROM repositories WHERE id = ?", (repo_id,))
    conn.commit()
    conn.close()

# --- NEW: Notification History ---

def mark_issue_seen(issue_id):
    conn = get_connection()
    conn.execute("UPDATE issues SET seen_at = ? WHERE id = ?", (datetime.now(), issue_id))
    conn.commit()
    conn.close()

# --- NEW: Statistics ---

def get_issue_stats():
    conn = get_connection()
    stats = {}
    
    # 1. Issues per day (last 7 days based on first_seen_at)
    # Note: SQLite date manipulation is tricky, simplifying to getting all timestamps and processing in python for reliability across sqlite versions
    rows = conn.execute("SELECT first_seen_at FROM issues").fetchall()
    
    # 2. Issues by category
    by_cat = conn.execute("""
        SELECT c.name, COUNT(i.id) as count
        FROM issues i
        JOIN repositories r ON i.repository_id = r.id
        JOIN categories c ON r.category_id = c.id
        GROUP BY c.name
    """).fetchall()
    stats['by_category'] = {row['name']: row['count'] for row in by_cat}
    
    # 3. Top Repos
    top_repos = conn.execute("""
        SELECT r.full_name, COUNT(i.id) as count
        FROM issues i
        JOIN repositories r ON i.repository_id = r.id
        GROUP BY r.full_name
        ORDER BY count DESC
        LIMIT 10
    """).fetchall()
    stats['top_repos'] = {row['full_name']: row['count'] for row in top_repos}
    
    conn.close()
    
    # Process daily stats in Python
    from collections import Counter
    daily_counts = Counter()
    now = datetime.now()
    for r in rows:
        if r['first_seen_at']:
            try:
                dt = datetime.fromisoformat(str(r['first_seen_at']))
                # If within last 7 days
                if (now - dt).days <= 7:
                    day_str = dt.strftime("%Y-%m-%d")
                    daily_counts[day_str] += 1
            except:
                pass
                
    stats['daily_history'] = dict(sorted(daily_counts.items()))
    return stats


# --- Data Access Methods (Modified) ---
# ... [get_categories, get_repositories, get_repository, update_repo_timestamp, upsert_issue remain unchanged] ...

def get_issues(filters=None):
    """
    Fetch issues based on filters.
    filters: dict with keys: category_id, repo_id, search, only_new, only_good_first, unassigned_only, unseen_only
    """
    filters = filters or {}
    conn = get_connection()
    
    # Base query with Join to get repo name and category name helper
    query = """
        SELECT i.*, r.full_name as repo_name, c.name as category_name
        FROM issues i
        JOIN repositories r ON i.repository_id = r.id
        JOIN categories c ON r.category_id = c.id
        WHERE 1=1
    """
    params = []
    
    # Apply Filters
    if filters.get('unseen_only'):
        query += " AND i.seen_at IS NULL"
        
    if filters.get('category_id'):
# ... [rest can be kept via context or I need to include it if replace_file_content requires contiguous context blocks]
# Since I need to modify get_issues to add 'unseen_only', I will output the start of get_issues and let the tool replace just the start if possible, or I have to replace the whole block.
# replace_file_content requires contiguous replacement. Let's include the whole function to be safe and clean.
        query += " AND r.category_id = ?"
        params.append(filters['category_id'])
        
    if filters.get('repo_id'):
        query += " AND i.repository_id = ?"
        params.append(filters['repo_id'])
        
    if filters.get('only_good_first'):
        keywords = ['good first issue', 'good-first-issue', 'beginner', 'help wanted']
        query += " AND (" + " OR ".join(["i.labels LIKE ?" for _ in keywords]) + ")"
        for k in keywords:
            params.append(f"%{k}%")
            
    if filters.get('unassigned_only'):
        query += " AND i.is_assigned = 0"
        
    # 'only_new' logic is currently post-processed in app.py but we can look at timestamps here too if needed.
    # Leaving as is for consistency with previous step.
        
    if filters.get('search'):
        term = f"%{filters['search']}%"
        query += " AND (i.title LIKE ? OR i.body_preview LIKE ?)"
        params.extend([term, term])
        
    query += " ORDER BY i.created_at_github DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

    return [dict(row) for row in rows]

def add_category(name, description=""):
    conn = get_connection()
    exists = conn.execute("SELECT id FROM categories WHERE name = ?", (name,)).fetchone()
    if exists:
        conn.close()
        return False, "Category already exists."
    
    conn.execute("INSERT INTO categories (name, description) VALUES (?, ?)", (name, description))
    conn.commit()
    conn.close()
    return True, "Category added successfully."

def seed_data():
    """Populates the database with initial categories and repositories."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if categories exist
    cursor.execute("SELECT count(*) FROM categories")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    print("Seeding initial data...")
    # ... [Implementation of seeding logic as before]
    # Re-implementing simplified seeding for restoration
    categories = [
        ("Machine Learning", "ML frameworks and tools"),
        ("Computer Vision", "Image and video processing"),
        ("NLP", "Natural language processing"),
        ("LLM", "Large Language Models")
    ]
    cursor.executemany("INSERT INTO categories (name, description) VALUES (?, ?)", categories)
    
    cursor.execute("SELECT id, name FROM categories")
    cat_map = {row['name']: row['id'] for row in cursor.fetchall()}
    
    repos = [
        ("huggingface", "transformers", cat_map["Machine Learning"]),
        ("pytorch", "pytorch", cat_map["Machine Learning"]),
        ("scikit-learn", "scikit-learn", cat_map["Machine Learning"]),
        ("openai", "CLIP", cat_map["Computer Vision"]),
        ("ultralytics", "ultralytics", cat_map["Computer Vision"]),
        ("explosion", "spaCy", cat_map["NLP"]),
        ("langchain-ai", "langchain", cat_map["LLM"]),
    ]
    
    for owner, repo, cat_id in repos:
        full_name = f"{owner}/{repo}"
        cursor.execute("""
            INSERT INTO repositories (github_owner, github_repo, full_name, category_id)
            VALUES (?, ?, ?, ?)
        """, (owner, repo, full_name, cat_id))
        
    conn.commit()
    conn.close()
    print("Seeding complete.")
    
    # Check if categories exist
    cursor.execute("SELECT count(*) FROM categories")
    if cursor.fetchone()[0] > 0:
        conn.close()
        return

    print("Seeding initial data...")
    
    # Insert Categories
    categories = [
        ("Machine Learning", "ML frameworks and tools"),
        ("Computer Vision", "Image and video processing"),
        ("NLP", "Natural language processing"),
        ("LLM", "Large Language Models")
    ]
    cursor.executemany("INSERT INTO categories (name, description) VALUES (?, ?)", categories)
    
    # Get Category IDs
    cursor.execute("SELECT id, name FROM categories")
    cat_map = {row['name']: row['id'] for row in cursor.fetchall()}
    
    # Insert Repositories
    repos = [
        ("huggingface", "transformers", cat_map["Machine Learning"]),
        ("pytorch", "pytorch", cat_map["Machine Learning"]),
        ("scikit-learn", "scikit-learn", cat_map["Machine Learning"]),
        ("openai", "CLIP", cat_map["Computer Vision"]),
        ("ultralytics", "ultralytics", cat_map["Computer Vision"]),
        ("explosion", "spaCy", cat_map["NLP"]),
        ("langchain-ai", "langchain", cat_map["LLM"]),
    ]
    
    for owner, repo, cat_id in repos:
        full_name = f"{owner}/{repo}"
        cursor.execute("""
            INSERT INTO repositories (github_owner, github_repo, full_name, category_id)
            VALUES (?, ?, ?, ?)
        """, (owner, repo, full_name, cat_id))
        
    conn.commit()
    conn.close()
    print("Seeding complete.")

# --- Data Access Methods ---

def get_categories():
    conn = get_connection()
    cats = conn.execute("SELECT * FROM categories ORDER BY id").fetchall()
    conn.close()
    return [dict(c) for c in cats]

def get_repositories(category_id=None, active_only=True):
    conn = get_connection()
    query = "SELECT * FROM repositories WHERE 1=1"
    params = []
    
    if category_id:
        query += " AND category_id = ?"
        params.append(category_id)
        
    if active_only:
        query += " AND is_active = 1"
        
    repos = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(r) for r in repos]

def get_repository(repo_id):
    conn = get_connection()
    repo = conn.execute("SELECT * FROM repositories WHERE id = ?", (repo_id,)).fetchone()
    conn.close()
    return dict(repo) if repo else None

def update_repo_timestamp(repo_id, total_issues):
    conn = get_connection()
    conn.execute("""
        UPDATE repositories 
        SET last_refreshed_at = ?, total_open_issues = ? 
        WHERE id = ?
    """, (datetime.now(), total_issues, repo_id))
    conn.commit()
    conn.close()

def upsert_issue(repo_id, issue_data):
    """
    Inserts a new issue or updates an existing one.
    Returns: 'new' if inserted, 'updated' if updated.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    # Check if exists
    cursor.execute("""
        SELECT id, first_seen_at FROM issues 
        WHERE repository_id = ? AND github_issue_id = ?
    """, (repo_id, issue_data['github_issue_id']))
    
    existing = cursor.fetchone()
    current_time = datetime.now()
    
    if existing:
        # Update existing
        cursor.execute("""
            UPDATE issues SET
                title = ?, state = ?, labels = ?, is_assigned = ?, 
                assignee_login = ?, comments_count = ?, last_updated_at = ?, body_preview = ?
            WHERE id = ?
        """, (
            issue_data['title'], issue_data['state'], issue_data['labels'], 
            issue_data['is_assigned'], issue_data['assignee_login'], issue_data['comments_count'],
            current_time, issue_data['body_preview'], existing['id']
        ))
        result = 'updated'
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO issues (
                repository_id, github_issue_id, github_issue_url, title, state, labels,
                is_assigned, assignee_login, comments_count, created_at_github,
                first_seen_at, last_updated_at, body_preview
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            repo_id, issue_data['github_issue_id'], issue_data['github_issue_url'], 
            issue_data['title'], issue_data['state'], issue_data['labels'], 
            issue_data['is_assigned'], issue_data['assignee_login'], issue_data['comments_count'],
            issue_data['created_at_github'], current_time, current_time, issue_data['body_preview']
        ))
        result = 'new'
        
    conn.commit()
    conn.close()
    return result

def get_issues(filters=None):
    """
    Fetch issues based on filters.
    filters: dict with keys: category_id, repo_id, search, only_new, only_good_first, unassigned_only
    """
    filters = filters or {}
    conn = get_connection()
    
    # Base query with Join to get repo name and category name helper
    query = """
        SELECT i.*, r.full_name as repo_name, c.name as category_name
        FROM issues i
        JOIN repositories r ON i.repository_id = r.id
        JOIN categories c ON r.category_id = c.id
        WHERE 1=1
    """
    params = []
    
    # Apply Filters
    if filters.get('category_id'):
        query += " AND r.category_id = ?"
        params.append(filters['category_id'])
        
    if filters.get('repo_id'):
        query += " AND i.repository_id = ?"
        params.append(filters['repo_id'])
        
    if filters.get('only_good_first'):
        # Checking labels string for keywords
        # Note: In production a separate tags table is better, but this works for MVP
        keywords = ['good first issue', 'good-first-issue', 'beginner', 'help wanted']
        query += " AND (" + " OR ".join(["i.labels LIKE ?" for _ in keywords]) + ")"
        for k in keywords:
            params.append(f"%{k}%")
            
    if filters.get('unassigned_only'):
        query += " AND i.is_assigned = 0"
        
    if filters.get('only_new'):
        # SQLite uses string comparison for dates, assuming ISO format
        # first_seen_at > now - 24 hours
        yesterday = datetime.now() # Logic handled in python or sql?
        # Let's do a simple check: sort by first_seen_at desc in python or pass timestamp
        # Ideally, we pass the timestamp string for 24h ago
        pass # Handling in Python post-processing or precise SQL if needed
        
    if filters.get('search'):
        term = f"%{filters['search']}%"
        query += " AND (i.title LIKE ? OR i.body_preview LIKE ?)"
        params.extend([term, term])
        
    query += " ORDER BY i.created_at_github DESC"
    
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return [dict(row) for row in rows]

if __name__ == "__main__":
    init_db()
    seed_data()
