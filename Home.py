"""
Main Streamlit Application - Home Page
Member D Fraud Detection Dashboard
"""
import streamlit as st
import json
import os
from scripts.api_client import MemberCAPIClient
from scripts.data_processor import DataProcessor
from scripts.config import PROCESSED_DATA_DIR

# Page configuration
st.set_page_config(
    page_title="Fraud Detection Dashboard",
    page_icon="🛡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1F2937;
        text-align: center;
        padding: 1rem 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #6B7280;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #F9FAFB;
        padding: 1.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #3B82F6;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'member_c_data' not in st.session_state:
    st.session_state.member_c_data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None


def load_data_from_api():
    """Load data from Member C API"""
    try:
        with st.spinner("Fetching data from Member C API..."):
            # Create client (uses configured base URL)
            client = MemberCAPIClient(test_mode=False)
            data = client.get_verification_report()
            
            st.session_state.member_c_data = data
            
            # Process the data
            processor = DataProcessor(data)
            processor.process_all()
            
            st.session_state.processed_data = processor
            st.session_state.data_loaded = True
            st.success("✅ Data loaded successfully from API!")
            return True
    except Exception as e:
        st.error(f"❌ Error loading data from API: {str(e)}")
        with st.expander("Show Error Details"):
            st.exception(e)
        return False

def ensure_data_loaded():
    """Ensure data is fetched and processed automatically"""
    if not st.session_state.get('data_loaded'):
        load_data_from_api()


def load_existing_data():
    """Load existing processed data"""
    try:
        dashboard_file = os.path.join(PROCESSED_DATA_DIR, "dashboard_data.json")
        
        if os.path.exists(dashboard_file):
            with open(dashboard_file, 'r') as f:
                dashboard_data = json.load(f)
            
            # Try to load from latest raw data
            client = MemberCAPIClient(test_mode=True)
            raw_data = client.load_latest_data()
            
            if raw_data:
                st.session_state.member_c_data = raw_data
                processor = DataProcessor(raw_data)
                st.session_state.processed_data = processor
                st.session_state.data_loaded = True
                st.success("✅ Loaded existing data!")
                return True
        
        st.warning("⚠ No existing data found. Please load new data.")
        return False
    except Exception as e:
        st.error(f"❌ Error loading existing data: {str(e)}")
        with st.expander("Show Error Details"):
            st.exception(e)
        return False


# Main content
st.markdown('<div class="main-header">🛡 Fraud Detection Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Member D - Transaction Analysis & Risk Management</div>', unsafe_allow_html=True)

""" Sidebar """
with st.sidebar:
    st.image("https://via.placeholder.com/150x50/3B82F6/FFFFFF?text=IRWA+FRAUD", use_container_width=True)
    st.markdown("---")

# Main page content
ensure_data_loaded()

if not st.session_state.data_loaded:
    st.error("❌ Failed to load data from Member C API.")
    st.stop()
    
    # Feature overview
    st.markdown("## 🎯 Features")
    
    feat_col1, feat_col2 = st.columns(2)
    
    with feat_col1:
        st.markdown("### 📊 Comprehensive Dashboard")
        st.write("""
        - Real-time transaction monitoring
        - Risk distribution analysis
        - Interactive visualizations
        - Exportable reports (PDF/CSV)
        """)
        
        st.markdown("### 🔍 Transaction Search")
        st.write("""
        - Search transactions by ID
        - Filter by risk category
        - View detailed analysis
        - LLM-powered explanations
        """)
    
    with feat_col2:
        st.markdown("### ⚙ Admin Feedback")
        st.write("""
        - Manual transaction review
        - Feedback categorization
        - Historical feedback tracking
        - Model improvement insights
        """)
        
        st.markdown("### 📈 Analytics")
        st.write("""
        - ML vs Ring score correlation
        - Threshold-based categorization
        - High-risk user identification
        - Trend analysis
        """)

else:
    st.success("✅ Data loaded successfully! Navigate to the dashboard to view analysis.")
    
    # Quick stats
    st.markdown("## 📊 Quick Statistics")
    
    meta = st.session_state.member_c_data.get('meta', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Transactions",
            meta.get('total', 0),
            delta=None
        )
    
    with col2:
        deny_count = meta.get('deny', 0)
        total = meta.get('total', 1)
        deny_rate = (deny_count / total * 100) if total > 0 else 0
        st.metric(
            "Denied",
            deny_count,
            delta=f"{deny_rate:.1f}%",
            delta_color="inverse"
        )
    
    with col3:
        flag_count = meta.get('flag', 0)
        flag_rate = (flag_count / total * 100) if total > 0 else 0
        st.metric(
            "Flagged",
            flag_count,
            delta=f"{flag_rate:.1f}%",
            delta_color="off"
        )
    
    with col4:
        pass_count = meta.get('pass', 0)
        pass_rate = (pass_count / total * 100) if total > 0 else 0
        st.metric(
            "Passed",
            pass_count,
            delta=f"{pass_rate:.1f}%",
            delta_color="normal"
        )
    
    # LLM Summary if available
    if st.session_state.member_c_data.get('llm_summary'):
        st.markdown("## 🤖 AI Analysis Summary")
        st.info(st.session_state.member_c_data['llm_summary'])
    
    st.markdown("---")
    st.markdown("### 🚀 Next Steps")
    st.write("Navigate to different sections using the sidebar or the links below:")
    
    nav_col1, nav_col2, nav_col3 = st.columns(3)
    
    with nav_col1:
        st.page_link("pages/1_📊_Dashboard.py", label="📊 View Dashboard", icon="📊")
    
    with nav_col2:
        st.page_link("pages/2_🔍_Transaction_Search.py", label="🔍 Search Transactions", icon="🔍")
    
    with nav_col3:
        st.page_link("pages/3_⚙️_Admin_Feedback.py", label="⚙ Admin Feedback", icon="⚙")