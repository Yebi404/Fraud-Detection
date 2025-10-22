"""
Dashboard Page - Main Analytics and Visualizations
"""
import streamlit as st
import json
import os
from scripts.api_client import MemberCAPIClient
import pandas as pd
from datetime import datetime
from scripts.config import PROCESSED_DATA_DIR, RISK_CATEGORIES, STATUS_CONFIG
from utils.visualization import (
    create_risk_distribution_chart,
    create_status_pie_chart,
    create_score_histogram,
    create_score_scatter,
    create_timeline_chart
)
from utils.export_utils import export_to_csv

st.set_page_config(
    page_title="Dashboard - Fraud Detection",
    page_icon="📊",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .risk-badge-critical {
        background-color: #DC2626;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .risk-badge-high {
        background-color: #EA580C;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .risk-badge-medium {
        background-color: #F59E0B;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .risk-badge-low {
        background-color: #10B981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Fraud Detection Dashboard")

# Check if data is loaded
if not st.session_state.get('data_loaded', False):
    with st.spinner("Fetching data from Member C API..."):
        try:
            client = MemberCAPIClient(test_mode=False)
            data = client.get_verification_report()
            from scripts.data_processor import DataProcessor
            processor = DataProcessor(data)
            processor.process_all()
            st.session_state.member_c_data = data
            st.session_state.processed_data = processor
            st.session_state.data_loaded = True
            st.rerun()
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.stop()

# Load dashboard data
try:
    dashboard_file = os.path.join(PROCESSED_DATA_DIR, "dashboard_data.json")
    with open(dashboard_file, 'r') as f:
        dashboard_data = json.load(f)
    
    alert_file = os.path.join(PROCESSED_DATA_DIR, "alert_report.json")
    with open(alert_file, 'r') as f:
        alert_data = json.load(f)
    
    transactions = st.session_state.member_c_data.get('data', [])
    
except Exception as e:
    st.error(f"Error loading dashboard data: {str(e)}")
    st.stop()

# Sidebar filters
st.sidebar.markdown("## 🔍 Filters")

status_filter = st.sidebar.multiselect(
    "Status",
    options=["deny", "flag", "pass"],
    default=["deny", "flag", "pass"]
)

score_range = st.sidebar.slider(
    "Combined Score Range",
    min_value=0.0,
    max_value=1.0,
    value=(0.0, 1.0),
    step=0.05
)

risk_filter = st.sidebar.multiselect(
    "Risk Category",
    options=list(RISK_CATEGORIES.keys()),
    default=list(RISK_CATEGORIES.keys())
)

st.sidebar.markdown("---")
st.sidebar.markdown("## 📥 Export Options")

col_pdf, col_csv = st.sidebar.columns(2)
with col_csv:
    if st.button("📊 Export CSV", use_container_width=True):
        try:
            with st.spinner("Generating CSV..."):
                csv_path = export_to_csv(transactions)
                st.success(f"✅ CSV saved!")
                with open(csv_path, 'rb') as f:
                    st.download_button(
                        "⬇️ Download CSV",
                        f,
                        file_name=os.path.basename(csv_path),
                        mime="text/csv",
                        use_container_width=True
                    )
        except Exception as e:
            st.error(f"Error generating CSV: {str(e)}")

# Main dashboard content
stats = dashboard_data['statistics']

# Top metrics
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        "Total Transactions",
        f"{stats['total_transactions']:,}",
        delta=None
    )

with col2:
    st.metric(
        "Denied",
        f"{stats['denied']:,}",
        delta=f"-{stats['denial_rate']:.1f}%",
        delta_color="inverse"
    )

with col3:
    st.metric(
        "Flagged",
        f"{stats['flagged']:,}",
        delta=f"{stats['flag_rate']:.1f}%",
        delta_color="off"
    )

with col4:
    st.metric(
        "Avg Score",
        f"{stats['avg_score']:.3f}",
        delta=None
    )

with col5:
    st.metric(
        "Max Score",
        f"{stats['max_score']:.3f}",
        delta=None
    )

st.markdown("---")

# Alert Summary
st.markdown("## 🚨 Alert Summary")
alert_summary = alert_data['summary']

alert_col1, alert_col2, alert_col3, alert_col4 = st.columns(4)

with alert_col1:
    st.metric("Total Alerts", alert_summary['total_alerts'])

with alert_col2:
    st.metric("Critical Alerts", alert_summary['critical_alerts'])

with alert_col3:
    st.metric("High Risk Alerts", alert_summary['high_risk_alerts'])

with alert_col4:
    requires_action = sum(1 for a in alert_data['alerts'] if a.get('requires_action', False))
    st.metric("Requires Action", requires_action)

# LLM Summary
if dashboard_data.get('llm_summary'):
    st.markdown("## 🤖 AI Analysis")
    st.info(dashboard_data['llm_summary'])

st.markdown("---")

# Visualizations
st.markdown("## 📈 Visualizations")

# First row - Risk distribution and Status
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.plotly_chart(
        create_risk_distribution_chart(dashboard_data['risk_distribution']),
        use_container_width=True
    )

with chart_col2:
    st.plotly_chart(
        create_status_pie_chart(dashboard_data['status_distribution']),
        use_container_width=True
    )

# Second row - Score histogram and scatter
chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    selected_status = st.selectbox(
        "Filter by status",
        options=[None, "deny", "flag", "pass"],
        format_func=lambda x: "All" if x is None else STATUS_CONFIG[x]['label']
    )
    st.plotly_chart(
        create_score_histogram(transactions, selected_status),
        use_container_width=True
    )

with chart_col4:
    st.plotly_chart(
        create_score_scatter(transactions),
        use_container_width=True
    )

# Third row - Timeline
st.plotly_chart(
    create_timeline_chart(transactions),
    use_container_width=True
)

st.markdown("---")

# Transaction breakdown by risk category
st.markdown("## 📋 Transaction Breakdown by Risk Category")

# Filter transactions based on sidebar selections
filtered_txns = [
    txn for txn in transactions
    if txn['status'] in status_filter
    and score_range[0] <= txn['combined_score'] <= score_range[1]
]

# Add risk category to each transaction
from scripts.data_processor import DataProcessor
processor = DataProcessor(st.session_state.member_c_data)

for txn in filtered_txns:
    txn['risk_category'] = processor.categorize_risk(txn['combined_score'])

filtered_txns = [txn for txn in filtered_txns if txn['risk_category'] in risk_filter]

# Display counts
risk_counts = {}
for category in RISK_CATEGORIES.keys():
    risk_counts[category] = sum(1 for t in filtered_txns if t['risk_category'] == category)

count_cols = st.columns(len(RISK_CATEGORIES))
for idx, (category, config) in enumerate(RISK_CATEGORIES.items()):
    with count_cols[idx]:
        st.markdown(
            f"""
            <div style="background-color: {config['color']}; padding: 1rem; border-radius: 0.5rem; text-align: center; color: white;">
                <h3 style="margin: 0; color: white;">{risk_counts[category]}</h3>
                <p style="margin: 0; color: white;">{config['label']}</p>
            </div>
            """,
            unsafe_allow_html=True
        )

st.markdown("---")

# Detailed transaction table
st.markdown("## 📄 Transaction Details")

# Pagination
items_per_page = st.selectbox("Items per page", [10, 25, 50, 100], index=1)

if filtered_txns:
    # Sort options
    sort_by = st.selectbox(
        "Sort by",
        ["combined_score", "ml_score", "ring_score", "idx"],
        format_func=lambda x: x.replace("_", " ").title()
    )
    
    sort_order = st.radio("Order", ["Descending", "Ascending"], horizontal=True)
    reverse = sort_order == "Descending"
    
    sorted_txns = sorted(filtered_txns, key=lambda x: x[sort_by], reverse=reverse)
    
    # Pagination
    total_pages = (len(sorted_txns) - 1) // items_per_page + 1
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_txns = sorted_txns[start_idx:end_idx]
    
    # Display transactions
    for txn in page_txns:
        risk_cat = txn['risk_category']
        config = RISK_CATEGORIES[risk_cat]
        status_config = STATUS_CONFIG[txn['status']]
        
        with st.expander(
            f"{status_config['icon']} Transaction {txn['idx']} - "
            f"{config['label']} (Score: {txn['combined_score']:.3f})"
        ):
            detail_col1, detail_col2, detail_col3 = st.columns(3)
            
            with detail_col1:
                st.markdown("**Transaction Info**")
                st.write(f"ID: {txn['idx']}")
                st.write(f"Status: {txn['status'].upper()}")
                st.markdown(
                    f"<span class='risk-badge-{risk_cat}'>{config['label']}</span>",
                    unsafe_allow_html=True
                )
            
            with detail_col2:
                st.markdown("**Scores**")
                st.write(f"Combined: {txn['combined_score']:.3f}")
                st.write(f"ML Score: {txn['ml_score']:.3f}")
                st.write(f"Ring Score: {txn['ring_score']:.3f}")
            
            with detail_col3:
                st.markdown("**Risk Level**")
                st.progress(txn['combined_score'])
                
                if txn['combined_score'] >= 0.85:
                    st.error("🔴 Critical Risk")
                elif txn['combined_score'] >= 0.70:
                    st.warning("🟠 High Risk")
                elif txn['combined_score'] >= 0.50:
                    st.info("🟡 Medium Risk")
                else:
                    st.success("🟢 Low Risk")
            
            st.markdown("**Explanation**")
            st.write(txn['explanation'])
            
            # LLM explanation if available
            llm_exp = processor.llm_explanations.get(txn['idx'])
            if llm_exp:
                st.markdown("**AI Analysis**")
                st.info(llm_exp)
    
    st.caption(f"Showing {start_idx + 1}-{min(end_idx, len(sorted_txns))} of {len(sorted_txns)} filtered transactions")

else:
    st.info("No transactions match the current filters.")

# High-risk users summary
st.markdown("---")
st.markdown("## ⚠️ High Risk Users")

try:
    high_risk_file = os.path.join(PROCESSED_DATA_DIR, "high_risk_users.csv")
    if os.path.exists(high_risk_file):
        high_risk_df = pd.read_csv(high_risk_file)
        
        if not high_risk_df.empty:
            st.dataframe(
                high_risk_df.head(10),
                use_container_width=True,
                hide_index=True
            )
            
            if st.button("📥 Download High Risk Users CSV"):
                csv = high_risk_df.to_csv(index=False)
                st.download_button(
                    "⬇️ Download",
                    csv,
                    f"high_risk_users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )
        else:
            st.info("No high-risk users identified.")
    else:
        st.info("High-risk users report not generated yet.")
except Exception as e:
    st.error(f"Error loading high-risk users: {str(e)}")