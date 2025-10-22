"""
Configuration file for Member D Fraud Detection Dashboard
"""
import os

# API Configuration
MEMBER_C_API_URL = "http://172.27.87.131:8002"  # Base URL; endpoint path is appended by client
API_TIMEOUT = 30  # seconds

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
# Save fetched verification report directly under data/ (no raw/ subfolder)
RAW_DATA_DIR = DATA_DIR
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, "processed")
FEEDBACK_DATA_DIR = os.path.join(DATA_DIR, "feedback")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
PDF_REPORTS_DIR = os.path.join(REPORTS_DIR, "pdf")
CSV_REPORTS_DIR = os.path.join(REPORTS_DIR, "csv")

# Score Thresholds
THRESHOLDS = {
    "critical": 0.85,
    "high": 0.70,
    "medium": 0.50,
    "low": 0.30
}

# Risk Categories and Colors
RISK_CATEGORIES = {
    "critical": {"label": "Critical Risk", "color": "#DC2626", "range": (0.85, 1.0)},
    "high": {"label": "High Risk", "color": "#EA580C", "range": (0.70, 0.85)},
    "medium": {"label": "Medium Risk", "color": "#F59E0B", "range": (0.50, 0.70)},
    "low": {"label": "Low Risk", "color": "#10B981", "range": (0.30, 0.50)},
    "minimal": {"label": "Minimal Risk", "color": "#3B82F6", "range": (0.0, 0.30)}
}

# Status Configuration
STATUS_CONFIG = {
    "deny": {"label": "Denied", "color": "#DC2626", "icon": "🚫"},
    "flag": {"label": "Flagged", "color": "#F59E0B", "icon": "⚠"},
    "pass": {"label": "Passed", "color": "#10B981", "icon": "✅"}
}

# Dashboard Settings
DASHBOARD_REFRESH_INTERVAL = 300
TRANSACTIONS_PER_PAGE = 50
MAX_CHART_POINTS = 1000

# Export Settings
PDF_EXPORT_CONFIG = {
    "page_size": "A4",
    "margin": 1,
    "font_family": "Helvetica"
}

CSV_EXPORT_CONFIG = {
    "encoding": "utf-8",
    "index": False
}

# Alert Rules
ALERT_RULES = {
    "high_score_deny": {
        "condition": "status == 'deny' and combined_score > 0.85",
        "severity": "critical",
        "message": "Transaction auto-denied due to critical risk score"
    },
    "repeated_flags": {
        "condition": "status == 'flag'",
        "severity": "high",
        "message": "Transaction flagged for manual review"
    },
    "score_threshold": {
        "condition": "combined_score > 0.70",
        "severity": "medium",
        "message": "Transaction score exceeds high-risk threshold"
    }
}

# Feedback Categories
FEEDBACK_CATEGORIES = [
    "True Positive - Correctly Flagged",
    "False Positive - Legitimate Transaction",
    "True Negative - Correctly Passed",
    "False Negative - Should Have Flagged",
    "Needs Investigation",
    "Other"
]

# Create directories if they don't exist
for directory in [RAW_DATA_DIR, PROCESSED_DATA_DIR, FEEDBACK_DATA_DIR, 
                  PDF_REPORTS_DIR, CSV_REPORTS_DIR]:
    os.makedirs(directory, exist_ok=True)