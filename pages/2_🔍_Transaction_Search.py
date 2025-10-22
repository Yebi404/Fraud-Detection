"""
Transaction Search Page - Search and view individual transactions
"""
import streamlit as st
from scripts.data_processor import DataProcessor
from scripts.config import RISK_CATEGORIES, STATUS_CONFIG
from scripts.api_client import MemberCAPIClient

st.set_page_config(
    page_title="Transaction Search",
    page_icon="🔍",
    layout="wide"
)

st.title("🔍 Transaction Search")

# Check if data is loaded
if not st.session_state.get('data_loaded', False):
    with st.spinner("Fetching data from Member C API..."):
        try:
            client = MemberCAPIClient(test_mode=False)
            data = client.get_verification_report()
            processor = DataProcessor(data)
            processor.process_all()
            st.session_state.member_c_data = data
            st.session_state.processed_data = processor
            st.session_state.data_loaded = True
            st.rerun()
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            st.stop()

# Get processor
processor = DataProcessor(st.session_state.member_c_data)
transactions = st.session_state.member_c_data.get('data', [])

# Search interface
st.markdown("## 🔎 Search by Transaction ID")

search_col1, search_col2 = st.columns([3, 1])

with search_col1:
    search_id = st.number_input(
        "Enter Transaction ID",
        min_value=0,
        value=0,
        step=1,
        help="Enter the transaction ID to search"
    )

with search_col2:
    st.markdown("<br>", unsafe_allow_html=True)
    search_button = st.button("🔍 Search", use_container_width=True, type="primary")

# Search results
if search_button or search_id > 0:
    txn = processor.get_transaction_by_id(search_id)
    
    if txn:
        st.success(f"✅ Transaction {search_id} found!")
        
        # Transaction details card
        risk_config = RISK_CATEGORIES[txn['risk_category']]
        status_config = STATUS_CONFIG[txn['status']]
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, {risk_config['color']}22 0%, {risk_config['color']}44 100%); 
                        padding: 2rem; border-radius: 1rem; border-left: 5px solid {risk_config['color']};">
                <h2 style="margin: 0;">{status_config['icon']} Transaction {txn['idx']}</h2>
                <p style="margin: 0.5rem 0 0 0; color: #6B7280;">Status: {txn['status'].upper()} | 
                Risk: {risk_config['label']}</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Metrics row
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("Combined Score", f"{txn['combined_score']:.3f}")
        
        with metric_col2:
            st.metric("ML Score", f"{txn['ml_score']:.3f}")
        
        with metric_col3:
            st.metric("Ring Score", f"{txn['ring_score']:.3f}")
        
        with metric_col4:
            st.metric("Status", txn['status'].upper())
        
        # Progress bars
        st.markdown("### 📊 Score Breakdown")
        
        progress_col1, progress_col2, progress_col3 = st.columns(3)
        
        with progress_col1:
            st.markdown("**Combined Score**")
            st.progress(txn['combined_score'])
            
            if txn['combined_score'] >= 0.85:
                st.error("🔴 Critical Risk")
            elif txn['combined_score'] >= 0.70:
                st.warning("🟠 High Risk")
            elif txn['combined_score'] >= 0.50:
                st.info("🟡 Medium Risk")
            else:
                st.success("🟢 Low Risk")
        
        with progress_col2:
            st.markdown("**ML Anomaly Score**")
            st.progress(txn['ml_score'])
            st.caption(f"{txn['ml_score']:.1%}")
        
        with progress_col3:
            st.markdown("**Risk Ring Score**")
            st.progress(txn['ring_score'])
            st.caption(f"{txn['ring_score']:.1%}")
        
        st.markdown("---")
        
        # Detailed analysis
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("### 📝 System Explanation")
            st.info(txn['explanation'])
            
            if txn.get('llm_explanation'):
                st.markdown("### 🤖 AI Analysis")
                st.success(txn['llm_explanation'])
        
        with col2:
            st.markdown("### ⚙️ Transaction Properties")
            
            st.markdown(f"""
            - **Transaction ID:** {txn['idx']}
            - **Status:** {txn['status'].upper()}
            - **Risk Category:** {risk_config['label']}
            - **Combined Score:** {txn['combined_score']:.4f}
            - **ML Score:** {txn['ml_score']:.4f}
            - **Ring Score:** {txn['ring_score']:.4f}
            """)
            
            st.markdown("### 🚦 Risk Thresholds")
            st.markdown("""
            - 🔴 **Critical:** ≥ 0.85
            - 🟠 **High:** 0.70 - 0.84
            - 🟡 **Medium:** 0.50 - 0.69
            - 🟢 **Low:** 0.30 - 0.49
            - 🔵 **Minimal:** < 0.30
            """)
        
        # Recommendations
        st.markdown("---")
        st.markdown("### 💡 Recommendations")
        
        if txn['status'] == 'deny':
            st.error("""
            **🚫 DENIED TRANSACTION**
            
            This transaction has been automatically denied due to high-risk indicators:
            - Review user account for suspicious activity
            - Contact user for verification if legitimate
            - Document decision for compliance
            - Consider account restrictions if pattern continues
            """)
        
        elif txn['status'] == 'flag':
            st.warning("""
            **⚠️ FLAGGED FOR REVIEW**
            
            This transaction requires manual review:
            - Verify transaction details with user
            - Check recent account activity
            - Review similar past transactions
            - Make manual approval/denial decision
            """)
        
        else:
            st.success("""
            **✅ APPROVED TRANSACTION**
            
            This transaction passed all checks:
            - Low risk scores across all metrics
            - Normal transaction patterns
            - No action required
            - Continue monitoring
            """)
        
        # Quick actions
        st.markdown("---")
        st.markdown("### ⚡ Quick Actions")
        
        action_col1, action_col2, action_col3 = st.columns(3)
        
        with action_col1:
            if st.button("📋 Copy Transaction ID", use_container_width=True):
                st.write(f"Transaction ID: {txn['idx']}")
                st.success("Copy the ID above")
        
        with action_col2:
            if st.button("⚙️ Provide Feedback", use_container_width=True):
                st.session_state['feedback_txn_id'] = txn['idx']
                st.switch_page("pages/3_⚙️_Admin_Feedback.py")
        
        with action_col3:
            if st.button("🔄 Search Another", use_container_width=True):
                st.rerun()
    
    else:
        st.error(f"❌ Transaction {search_id} not found in the dataset.")
        st.info("💡 Tip: Check the transaction ID and try again.")

else:
    st.info("👆 Enter a transaction ID above to search")

# Browse all transactions
st.markdown("---")
st.markdown("## 📚 Browse All Transactions")

# Filters
browse_col1, browse_col2, browse_col3 = st.columns(3)

with browse_col1:
    status_filter = st.multiselect(
        "Filter by Status",
        options=["deny", "flag", "pass"],
        default=["deny", "flag", "pass"]
    )

with browse_col2:
    risk_filter = st.multiselect(
        "Filter by Risk",
        options=list(RISK_CATEGORIES.keys()),
        default=list(RISK_CATEGORIES.keys()),
        format_func=lambda x: RISK_CATEGORIES[x]['label']
    )

with browse_col3:
    score_threshold = st.slider(
        "Min Combined Score",
        min_value=0.0,
        max_value=1.0,
        value=0.0,
        step=0.05
    )

# Filter and display
filtered_txns = []
for txn in transactions:
    if txn['status'] in status_filter and txn['combined_score'] >= score_threshold:
        risk_cat = processor.categorize_risk(txn['combined_score'])
        if risk_cat in risk_filter:
            txn['risk_category'] = risk_cat
            filtered_txns.append(txn)

# Sort
sort_by = st.selectbox(
    "Sort by",
    ["combined_score", "ml_score", "ring_score", "idx"],
    format_func=lambda x: x.replace("_", " ").title()
)

filtered_txns.sort(key=lambda x: x[sort_by], reverse=True)

# Display
st.write(f"**Found {len(filtered_txns)} transactions**")

items_per_page = 20
total_pages = (len(filtered_txns) - 1) // items_per_page + 1 if filtered_txns else 0

if total_pages > 0:
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page
    page_txns = filtered_txns[start_idx:end_idx]
    
    # Display as cards
    for i in range(0, len(page_txns), 2):
        card_col1, card_col2 = st.columns(2)
        
        for j, card_col in enumerate([card_col1, card_col2]):
            if i + j < len(page_txns):
                txn = page_txns[i + j]
                risk_config = RISK_CATEGORIES[txn['risk_category']]
                status_config = STATUS_CONFIG[txn['status']]
                
                with card_col:
                    with st.container():
                        st.markdown(f"""
                        <div style="background-color: {risk_config['color']}22; padding: 1rem; 
                                    border-radius: 0.5rem; border-left: 4px solid {risk_config['color']};">
                            <h4 style="margin: 0;">{status_config['icon']} Transaction {txn['idx']}</h4>
                            <p style="margin: 0.5rem 0; color: #6B7280;">
                                {risk_config['label']} | Score: {txn['combined_score']:.3f}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"View Details", key=f"view_{txn['idx']}", use_container_width=True):
                            st.session_state['search_id'] = txn['idx']
                            st.rerun()
    
    st.caption(f"Showing {start_idx + 1}-{min(end_idx, len(filtered_txns))} of {len(filtered_txns)} transactions")

else:
    st.info("No transactions match the current filters.")