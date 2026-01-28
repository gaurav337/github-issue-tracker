import streamlit as st
import pandas as pd
import time
import textwrap
from datetime import datetime
import logic
import database
from styles import CSS

# 1. Config and Setup
st.set_page_config(
    page_title="GitHub Issue Tracker",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize DB on first load
if 'db_initialized' not in st.session_state:
    database.init_db()
    database.seed_data()
    st.session_state['db_initialized'] = True

st.markdown(CSS, unsafe_allow_html=True)

# 2. Helper Functions
def format_time_ago(dt_obj):
    if not isinstance(dt_obj, datetime):
        # Handle string timestamps from SQLite
        try:
            dt_obj = datetime.fromisoformat(str(dt_obj))
        except:
            return "unknown time"
            
    now = datetime.now()
    diff = now - dt_obj
    
    if diff.days > 0:
        return f"{diff.days} days ago"
    hours = diff.seconds // 3600
    if hours > 0:
        return f"{hours} hours ago"
    minutes = diff.seconds // 60
    return f"{minutes} mins ago"

def get_label_class(label_name):
    lower = label_name.lower()
    if 'good first' in lower or 'good-first' in lower:
        return 'label-tag label-good-first-issue'
    if 'help wanted' in lower:
        return 'label-tag label-help-wanted'
    return 'label-tag'

# 3. Session State Management
if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = None
    
def run_refresh_all():
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def update_progress(current, total, text):
        progress_bar.progress(current / total)
        status_text.text(text)
        
    stats = logic.refresh_all(progress_callback=update_progress)
    
    progress_bar.empty()
    status_text.success(f"Refresh Complete! Found {stats['total_new']} new issues.")
    time.sleep(2)
    status_text.empty()
    st.session_state['last_refresh'] = datetime.now()
    st.rerun()

def run_refresh_category(cat_id):
    with st.spinner("Refreshing category..."):
        stats = logic.refresh_category(cat_id)
    if stats['repos_failed'] > 0:
        st.error(f"Complete with errors. {stats['repos_failed']} repositories failed.")
    else:
        st.success(f"Updated! Found {stats['total_new']} new issues.")
    time.sleep(1.5)
    st.rerun()

# 4. Main App Layout

# HEADERS
c1, c2 = st.columns([3, 1])
with c1:
    st.title("🔍 GitHub Issue Tracker")
    last_update = st.session_state.get('last_refresh', "Never")
    if isinstance(last_update, datetime):
        last_update = format_time_ago(last_update)
    st.caption(f"Last updated: {last_update}")

with c2:
    if st.button("🔄 Refresh All", type="primary", use_container_width=True):
        run_refresh_all()
        
st.markdown("---")

# CATEGORIES SECTION
st.subheader("Categories")
categories = database.get_categories()
cat_cols = st.columns(len(categories))

selected_cat_id_from_card = None

for idx, cat in enumerate(categories):
    # Get stats for this category
    repos = database.get_repositories(cat['id'])
    repo_ids = [r['id'] for r in repos]
    
    # Calculate stats (simple query equivalent)
    # Ideally should be a proper SQL aggregation, doing generic fetch for MVP
    # This might be slow if thousands of issues, but okay for MVP (<500 issues)
    issues = database.get_issues({'category_id': cat['id']})
    total_issues = len(issues)
    
    # New calculation (Naive for now without exact 24h logic in DB)
    # logic is: first_seen_at < 24h ago. 
    # Let's count in python for now
    now = datetime.now()
    new_issues = sum(1 for i in issues if (
        isinstance(i['first_seen_at'], str) and 
        (now - datetime.fromisoformat(i['first_seen_at'])).total_seconds() < 86400
    ))
    
    with cat_cols[idx]:
        st.markdown(f"""
        <div class="metric-box">
            <div class="metric-value">{total_issues}</div>
            <div class="metric-label">{cat['name']}</div>
            <div class="new-count">+{new_issues} New</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button(f"🔄 Refresh", key=f"btn_cat_{cat['id']}", use_container_width=True):
            run_refresh_category(cat['id'])


# FILTER SECTION
st.markdown("### Filters")
with st.container():
    f_col1, f_col2, f_col3, f_col4 = st.columns(4)
    
    with f_col1:
        # Category Filter
        cat_options = {"All": None}
        for c in categories:
            cat_options[c['name']] = c['id']
        sel_cat_name = st.selectbox("Category", list(cat_options.keys()))
        selected_cat_id = cat_options[sel_cat_name]
        
    with f_col2:
        # Repo Filter
        repo_options = {"All": None}
        # Filter repos list by selected category if any
        if selected_cat_id:
             cat_repos = database.get_repositories(selected_cat_id)
        else:
             cat_repos = database.get_repositories()
             
        for r in cat_repos:
            repo_options[r['full_name']] = r['id']
        sel_repo_name = st.selectbox("Repository", list(repo_options.keys()))
        selected_repo_id = repo_options[sel_repo_name]

    with f_col3:
        filter_type = st.selectbox("Show", ["All Issues", "Good First Issue Only", "Unassigned Only"])
        
    with f_col4:
        search_query = st.text_input("Search", placeholder="Search titles...")
        
    only_new = st.checkbox("🆕 Show New Only ( < 24h )")

# RESULTS SECTION
filters = {
    'category_id': selected_cat_id,
    'repo_id': selected_repo_id,
    'search': search_query,
    'only_good_first': filter_type == "Good First Issue Only",
    'unassigned_only': filter_type == "Unassigned Only",
    'only_new': only_new
}

filtered_issues = database.get_issues(filters)

# Post-processing for "New" filter if DB didn't handle it strictly
if only_new:
    final_issues = []
    for i in filtered_issues:
        fs = i['first_seen_at']
        if isinstance(fs, str):
            fs_dt = datetime.fromisoformat(fs)
            if (datetime.now() - fs_dt).total_seconds() < 86400:
                final_issues.append(i)
    filtered_issues = final_issues

st.caption(f"Showing {len(filtered_issues)} issues")

# 5. RENDER ISSUE LIST
if not filtered_issues:
    st.info("No issues found matching your filters. Try hitting Refresh!")
else:
    for issue in filtered_issues:
        # Prepare Data
        is_new = False
        fs = issue['first_seen_at']
        if isinstance(fs, str):
            fs_dt = datetime.fromisoformat(fs)
            if (datetime.now() - fs_dt).total_seconds() < 86400:
                is_new = True
                
        new_badge_html = '<span class="badge-new">NEW</span>' if is_new else ''
        
        # Labels
        labels_html = ""
        if issue['labels']:
            for l in issue['labels'].split(','):
                l = l.strip()
                if not l: continue
                c_class = get_label_class(l)
                labels_html += f'<span class="{c_class}">{l}</span>'
                
        assignee_html = f"👤 {issue['assignee_login']}" if issue['is_assigned'] else "👤 Unassigned"
        
        card_html = f"""
<div class="issue-card">
    <div class="card-top">
        {new_badge_html}
        <a class="issue-title" href="{issue['github_issue_url']}" target="_blank">{issue['title']}</a>
    </div>
    <div class="card-meta">
        <span class="repo-name">
            <svg aria-hidden="true" height="16" viewBox="0 0 16 16" width="16" style="fill: currentColor;">
                <path d="M2 2.5A2.5 2.5 0 0 1 4.5 0h8.75a.75.75 0 0 1 .75.75v12.5a.75.75 0 0 1-.75.75h-2.5a.75.75 0 0 1 0-1.5h1.75v-2h-8a1 1 0 0 0-.714 1.7.75.75 0 1 1-1.072 1.05A2.495 2.495 0 0 1 2 11.5Zm10.5-1h-8a1 1 0 0 0-1 1v6.708A2.486 2.486 0 0 1 4.5 9h8ZM5 12.25a.25.25 0 0 1 .25-.25h3.5a.25.25 0 0 1 .25.25v3.25a.25.25 0 0 1-.4.2l-1.45-1.087a.25.25 0 0 0-.3 0L5.4 15.45a.25.25 0 0 1-.4-.2Z"></path>
            </svg>
            &nbsp;{issue['repo_name']}
        </span>
        <span>{assignee_html}</span>
        <span class="comments-count">
            <svg aria-hidden="true" height="16" viewBox="0 0 16 16" width="16" style="fill: currentColor;">
                <path d="M1 2.75C1 1.784 1.784 1 2.75 1h10.5c.966 0 1.75.784 1.75 1.75v7.5A1.75 1.75 0 0 1 13.25 12H9.06l-2.573 2.573A1.457 1.457 0 0 1 4 13.543V12H2.75A1.75 1.75 0 0 1 1 10.25Zm1.75-.25a.25.25 0 0 0-.25.25v7.5c0 .138.112.25.25.25h2a.75.75 0 0 1 .75.75v2.19l2.72-2.72a.75.75 0 0 1 .53-.22h4.5a.25.25 0 0 0 .25-.25v-7.5a.25.25 0 0 0-.25-.25Z"></path>
            </svg>
            &nbsp;{issue['comments_count']}
        </span>
    </div>
    <div class="label-container">
        {labels_html}
    </div>
    <div class="card-footer">
        <span>First seen: {format_time_ago(issue['first_seen_at'])}</span>
        <a class="open-btn" href="{issue['github_issue_url']}" target="_blank">Open on GitHub ↗</a>
    </div>
</div>
"""
        st.markdown(card_html, unsafe_allow_html=True)
