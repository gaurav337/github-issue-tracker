CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* GLOBAL RESET */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    color: #E2E8F0;
}

/* BACKGROUND */
.stApp {
    background-color: #0F172A; /* Slate 900 */
    background-image: 
        radial-gradient(at 0% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
        radial-gradient(at 100% 0%, rgba(6, 182, 212, 0.15) 0px, transparent 50%);
}

/* HEADERS */
h1 {
    color: white !important;
    font-weight: 800 !important;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 10px rgba(0,0,0,0.2);
}
p, .stCaption {
    color: #94A3B8 !important; /* Slate 400 */
}

/* METRIC CARDS */
.metric-box {
    background: rgba(30, 41, 59, 0.7); /* Slate 800 transparent */
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    padding: 24px;
    border-radius: 16px;
    text-align: center;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}
.metric-box:hover {
    transform: translateY(-4px);
    background: rgba(30, 41, 59, 0.9);
    border-color: rgba(139, 92, 246, 0.5); /* Violet glow */
    box-shadow: 0 10px 40px -10px rgba(139, 92, 246, 0.3);
}
.metric-value {
    font-size: 36px;
    font-weight: 800;
    background: linear-gradient(to right, #fff, #cbd5e1);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 8px;
}
.metric-label {
    font-size: 13px;
    font-weight: 600;
    color: #94A3B8;
    text-transform: uppercase;
    letter-spacing: 1px;
}
.new-count {
    margin-top: 12px;
    display: inline-block;
    background: rgba(6, 182, 212, 0.15); /* Cyan tint */
    color: #22D3EE; /* Cyan 400 */
    padding: 4px 12px;
    border-radius: 99px;
    font-size: 12px;
    font-weight: 700;
    border: 1px solid rgba(6, 182, 212, 0.3);
}

/* ISSUE CARD */
.issue-card {
    background: rgba(30, 41, 59, 0.4);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
    padding: 24px;
    margin-bottom: 16px;
    transition: all 0.2s ease;
}
.issue-card:hover {
    background: rgba(30, 41, 59, 0.8);
    border-color: rgba(255, 255, 255, 0.1);
    box-shadow: 0 4px 20px rgba(0,0,0,0.2);
}

.card-top {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 12px;
}

.issue-title {
    font-size: 18px;
    font-weight: 600;
    color: #F1F5F9; /* Slate 100 */
    text-decoration: none;
    line-height: 1.5;
}
.issue-title:hover {
    color: #8B5CF6; /* Violet 500 */
}

/* BADGES */
.badge-new {
    background: linear-gradient(135deg, #6366F1, #A855F7);
    color: white;
    padding: 4px 8px;
    border-radius: 6px;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    box-shadow: 0 4px 10px rgba(139, 92, 246, 0.4);
    margin-top: 5px;
}

/* META INFO */
.card-meta {
    display: flex;
    gap: 20px;
    font-size: 13px;
    color: #94A3B8;
    margin-bottom: 16px;
    align-items: center;
}
.repo-name {
    color: #CBD5E1;
    font-weight: 500;
    display: flex;
    align-items: center;
    gap: 6px;
}

/* LABELS */
.label-container {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
    margin-bottom: 20px;
}
.label-tag {
    background: rgba(255,255,255,0.05);
    color: #CBD5E1;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 12px;
    border: 1px solid rgba(255,255,255,0.1);
}
.label-good-first-issue {
    background: rgba(16, 185, 129, 0.15);
    color: #34D399; /* Emerald 400 */
    border-color: rgba(16, 185, 129, 0.3);
}
.label-help-wanted {
    background: rgba(245, 158, 11, 0.15);
    color: #FBBF24; /* Amber 400 */
    border-color: rgba(245, 158, 11, 0.3);
}

/* FOOTER */
.card-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-top: 16px;
    border-top: 1px solid rgba(255,255,255,0.05);
    color: #64748B;
    font-size: 12px;
}

.open-btn {
    background: rgba(255,255,255,0.05);
    color: #E2E8F0;
    padding: 8px 16px;
    border-radius: 8px;
    font-weight: 500;
    text-decoration: none;
    transition: all 0.2s;
}
.open-btn:hover {
    background: #8B5CF6;
    color: white;
}

/* OVERRIDE STREAMLIT DEFAULTS FOR DARK MODE */
div[data-testid="stSelectbox"] > div > div {
    background-color: #1E293B !important;
    color: white !important;
    border-color: #334155 !important;
}
div[data-testid="stTextInput"] > div > div > input {
    background-color: #1E293B !important;
    color: white !important;
    border-color: #334155 !important;
}
</style>
"""
