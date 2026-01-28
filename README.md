# 🔍 GitHub Issue Tracker

A beautiful, modern **Streamlit-based dashboard** for tracking and discovering "Good First Issues" across multiple GitHub repositories. Perfect for open-source contributors looking to find beginner-friendly issues to work on.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python) ![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red?logo=streamlit) ![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 🏠 Dashboard
- **Real-time Issue Tracking** - Automatically fetches open issues from tracked GitHub repositories
- **Category Organization** - Organize repositories into custom categories (Machine Learning, Computer Vision, NLP, LLM, etc.)
- **Issue Cards** - Beautiful, modern UI cards displaying issue details including:
  - Issue title with direct GitHub links
  - Repository name
  - Assignee status
  - Comment count
  - Labels with color-coded badges
  - First seen timestamp
  - NEW badge for issues discovered in the last 24 hours

### 🔎 Advanced Filtering
- **Category Filter** - Filter issues by repository category
- **Repository Filter** - Filter by specific repository
- **Issue Type Filter**:
  - All Issues
  - Good First Issue Only
  - Unassigned Only
- **Search** - Full-text search across issue titles and descriptions
- **New Issues Filter** - Show only issues discovered in the last 24 hours
- **Unseen Filter** - Show only issues you haven't marked as "seen"

### 👁️ Issue Management
- **Mark as Seen** - Track which issues you've already reviewed
- **Unseen Counter** - Quickly see how many new issues await your attention

### 📊 Statistics Tab
- **Issues by Category** - Bar chart showing issue distribution across categories
- **Top Active Repositories** - Bar chart of repos with most open issues
- **Daily History** - Area chart showing issues found over the last 7 days

### ⚙️ Settings Tab
- **Add New Category** - Create custom categories for organizing repos
- **Add New Repository** - Add any GitHub repository with automatic validation
- **Manage Repositories** - View, track, and delete existing repositories

### 🔄 Refresh System
- **Refresh All** - Update all tracked repositories at once with progress bar
- **Refresh Category** - Update all repositories in a specific category
- **Refresh Repository** - Update a single repository

### 🎨 Beautiful Dark Theme
- Modern glassmorphism design
- Gradient backgrounds with subtle animations
- Color-coded labels for different issue types
- Responsive hover effects
- Custom Google Fonts (Inter)

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | Streamlit |
| Database | SQLite |
| API | GitHub REST API v3 |
| Styling | Custom CSS with Glassmorphism |
| Charts | Streamlit native charts |

---

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- Git
- GitHub Personal Access Token

### Step 1: Clone the Repository

```bash
git clone https://github.com/yourusername/GitTracker.git
cd GitTracker
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Get a GitHub Personal Access Token

1. Go to [GitHub Settings → Developer Settings → Personal Access Tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it a descriptive name (e.g., "GitTracker")
4. Select scopes:
   - `public_repo` (for accessing public repositories)
5. Click **"Generate token"**
6. **Copy the token** (you won't see it again!)

### Step 5: Configure the Token

**Option A: Using `.env` file (Recommended for local development)**

Create or edit the `.env` file in the project root:

```env
GITHUB_TOKEN=your_github_token_here
```

**Option B: Using Streamlit Secrets (Recommended for deployment)**

Create `.streamlit/secrets.toml`:

```toml
GITHUB_TOKEN = "your_github_token_here"
```

### Step 6: Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

---

## 📁 Project Structure

```
GitTracker/
├── app.py              # Main Streamlit application
├── database.py         # SQLite database operations
├── github_client.py    # GitHub API integration
├── logic.py            # Business logic for refreshing repos
├── styles.py           # Custom CSS styling
├── requirements.txt    # Python dependencies
├── tracker.db          # SQLite database file (auto-created)
├── .env                # Environment variables (create this)
├── .gitignore          # Git ignore rules
├── .streamlit/
│   ├── config.toml     # Streamlit configuration
│   └── secrets.toml    # Streamlit secrets (create this)
└── README.md           # This file
```

---

## 📝 Dependencies

| Package | Purpose |
|---------|---------|
| `streamlit` | Web application framework |
| `requests` | HTTP requests to GitHub API |
| `pandas` | Data manipulation for charts |
| `python-dotenv` | Loading environment variables |

---

## 🚀 Usage Guide

### First Launch
1. On first launch, the app automatically initializes the database
2. Default categories are created: Machine Learning, Computer Vision, NLP, LLM
3. Sample repositories are added (huggingface/transformers, pytorch/pytorch, etc.)
4. Click **"🔄 Refresh All"** to fetch issues from all repositories

### Adding Repositories
1. Go to the **⚙️ Settings** tab
2. Enter the repository owner and name
3. Select a category
4. Click **"Add Repository"**
5. The repository is validated against GitHub before adding

### Tracking Issues
1. Use filters to find issues that interest you
2. Click on issue titles to open them on GitHub
3. Mark issues as "seen" using the **"👁️ Mark Seen"** button
4. Use the **"👀 Show Unseen Only"** checkbox to focus on new discoveries

### Creating Categories
1. Go to the **⚙️ Settings** tab
2. Enter a category name and optional description
3. Click **"Add Category"**

---

## 🔧 Configuration

### Streamlit Theme
The app uses a custom dark theme. You can modify `.streamlit/config.toml`:

```toml
[theme]
primaryColor = "#8B5CF6"
backgroundColor = "#0F172A"
secondaryBackgroundColor = "#1E293B"
textColor = "#E2E8F0"
```

### Good First Issue Labels
The app recognizes these labels as beginner-friendly:
- `good first issue`
- `good-first-issue`
- `beginner`
- `beginner friendly`
- `easy`
- `help wanted`
- `contributions welcome`
- `first-timers-only`
- `starter`

---

## 🤝 Contributing

Contributions are welcome! Feel free to:
1. Fork the repository
2. Create a feature branch
3. Submit a pull request

---

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

---

## 🙏 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Icons from GitHub Octicons
- Design inspired by modern glassmorphism trends

---

**Made with ❤️ for the Open Source Community**
