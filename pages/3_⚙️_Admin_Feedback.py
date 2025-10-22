"""
Admin Feedback Page - Manual review and feedback for transactions
"""
import streamlit as st
import json
import os
from datetime import datetime
from scripts.data_processor import DataProcessor
from scripts.config import FEEDBACK_DATA_DIR, FEEDBACK_CATEGORIES, RISK_CATEGORIES, STATUS_CONFIG

st.set_page_config(
    page_title="Admin Feedback",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Admin Feedback System")

# Check if data is loaded
if not st.session_state.get('data_loaded', False):
    st.warning("⚠️ No data loaded. Please load data from the Home page.")
    if st.button("Go to Home"):
        st.switch_page("Home.py")
    st.stop()

# Initialize feedback storage
feedback_file = os.path.join(FEEDBACK_DATA_DIR, "admin_feedback.json")

def load_feedbacks():
    """Load existing feedbacks"""
    if os.path.exists(feedback_file):
        with open(feedback_file, 'r') as f:
            return json.load(f)
    return []

def save_feedback(feedback):
    """Save a new feedback"""
    feedbacks = load_feedbacks()
    feedbacks.append(feedback)
    with open(feedback_file, 'w') as f:
        json.dump(feedbacks, f, indent=2)

# Get processor
processor = DataProcessor(st.session_state.member_c_data)
transactions = st.session_state.member_c_data.get('data', [])

# Tabs
tab1, tab2, tab3 = st.tabs(["📝 Submit Feedback", "📊 Feedback History", "📈 Analytics"])

# Tab 1: Submit Feedback
with tab1:
    st.markdown("## 📝 Transaction Review & Feedback")
    
    # Check if coming from search page
    prefilled_id = st.session_state.get('feedback_txn_id', 0)
    
    search_col1, search_col2 = st.columns([3, 1])
    
    with search_col1:
        txn_id = st.number_input(
            "Transaction ID",
            min_value=0,
            value=prefilled_id,
            step=1,
            help="Enter the transaction ID to review"
        )
    
    with search_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        load_txn = st.button("🔍 Load Transaction", use_container_width=True, type="primary")
    
    # Clear prefilled ID after use
    if 'feedback_txn_id' in st.session_state:
        del st.session_state['feedback_txn_id']
    
    if load_txn or txn_id > 0:
        txn = processor.get_transaction_by_id(txn_id)
        
        if txn:
            st.success(f"✅ Transaction {txn_id} loaded successfully!")
            
            # Display transaction details
            risk_config = RISK_CATEGORIES[txn['risk_category']]
            status_config = STATUS_CONFIG[txn['status']]
            
            st.markdown(f"""
                <div style="background: linear-gradient(135deg, {risk_config['color']}22 0%, {risk_config['color']}44 100%); 
                            padding: 1.5rem; border-radius: 1rem; border-left: 5px solid {risk_config['color']}; margin: 1rem 0;">
                    <h3 style="margin: 0;">{status_config['icon']} Transaction {txn['idx']}</h3>
                    <p style="margin: 0.5rem 0 0 0;">Status: {txn['status'].upper()} | 
                    Risk: {risk_config['label']} | Score: {txn['combined_score']:.3f}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Transaction metrics
            met_col1, met_col2, met_col3 = st.columns(3)
            
            with met_col1:
                st.metric("Combined Score", f"{txn['combined_score']:.3f}")
            
            with met_col2:
                st.metric("ML Score", f"{txn['ml_score']:.3f}")
            
            with met_col3:
                st.metric("Ring Score", f"{txn['ring_score']:.3f}")
            
            # Explanations
            with st.expander("📋 View Explanations", expanded=True):
                st.markdown("**System Explanation:**")
                st.info(txn['explanation'])
                
                if txn.get('llm_explanation'):
                    st.markdown("**AI Analysis:**")
                    st.success(txn['llm_explanation'])
            
            st.markdown("---")
            
            # Feedback form
            st.markdown("### 💬 Provide Your Feedback")
            
            with st.form("feedback_form"):
                feedback_col1, feedback_col2 = st.columns(2)
                
                with feedback_col1:
                    feedback_category = st.selectbox(
                        "Feedback Category",
                        options=FEEDBACK_CATEGORIES,
                        help="Categorize your assessment of this transaction"
                    )
                    
                    correct_decision = st.radio(
                        "Was the system's decision correct?",
                        options=["Yes", "No", "Partially"],
                        horizontal=True
                    )
                
                with feedback_col2:
                    should_be_status = st.selectbox(
                        "What should the status be?",
                        options=["deny", "flag", "pass"],
                        index=["deny", "flag", "pass"].index(txn['status']),
                        format_func=lambda x: STATUS_CONFIG[x]['label']
                    )
                    
                    severity = st.select_slider(
                        "Actual Risk Level",
                        options=["Very Low", "Low", "Medium", "High", "Critical"],
                        value="Medium"
                    )
                
                feedback_notes = st.text_area(
                    "Additional Notes",
                    placeholder="Provide any additional context, observations, or recommendations...",
                    height=150
                )
                
                reviewer_name = st.text_input(
                    "Reviewer Name (Optional)",
                    placeholder="Your name"
                )
                
                col1, col2, col3 = st.columns([1, 1, 2])
                
                with col1:
                    submit_feedback = st.form_submit_button("✅ Submit Feedback", use_container_width=True, type="primary")
                
                with col2:
                    clear_form = st.form_submit_button("🔄 Clear", use_container_width=True)
                
                if submit_feedback:
                    # Create feedback record
                    feedback_record = {
                        "transaction_id": txn['idx'],
                        "timestamp": datetime.now().isoformat(),
                        "reviewer": reviewer_name if reviewer_name else "Anonymous",
                        "original_status": txn['status'],
                        "original_score": txn['combined_score'],
                        "original_risk_category": txn['risk_category'],
                        "feedback_category": feedback_category,
                        "correct_decision": correct_decision,
                        "should_be_status": should_be_status,
                        "severity_assessment": severity,
                        "notes": feedback_notes,
                        "system_explanation": txn['explanation'],
                        "llm_explanation": txn.get('llm_explanation')
                    }
                    
                    save_feedback(feedback_record)
                    st.success("✅ Feedback submitted successfully!")
                
                if clear_form:
                    st.rerun()
        
        else:
            st.error(f"❌ Transaction {txn_id} not found.")
            st.info("💡 Please check the transaction ID and try again.")
    else:
        st.info("👆 Enter a transaction ID above to begin review")

# Tab 2: Feedback History
with tab2:
    st.markdown("## 📊 Feedback History")
    
    feedbacks = load_feedbacks()
    
    if feedbacks:
        st.write(f"**Total Feedbacks:** {len(feedbacks)}")
        
        # Filters
        hist_col1, hist_col2, hist_col3 = st.columns(3)
        
        with hist_col1:
            filter_category = st.multiselect(
                "Filter by Category",
                options=FEEDBACK_CATEGORIES,
                default=FEEDBACK_CATEGORIES
            )
        
        with hist_col2:
            filter_correct = st.multiselect(
                "Correct Decision?",
                options=["Yes", "No", "Partially"],
                default=["Yes", "No", "Partially"]
            )
        
        with hist_col3:
            filter_reviewer = st.text_input("Filter by Reviewer", "")
        
        # Filter feedbacks
        filtered_feedbacks = [
            fb for fb in feedbacks
            if fb['feedback_category'] in filter_category
            and fb['correct_decision'] in filter_correct
            and (not filter_reviewer or filter_reviewer.lower() in fb['reviewer'].lower())
        ]
        
        st.write(f"**Showing {len(filtered_feedbacks)} feedbacks**")
        
        # Sort options
        sort_by = st.selectbox(
            "Sort by",
            ["timestamp", "transaction_id", "reviewer"],
            format_func=lambda x: x.replace("_", " ").title()
        )
        
        filtered_feedbacks.sort(key=lambda x: x.get(sort_by, ""), reverse=True)
        
        # Display feedbacks
        for fb in filtered_feedbacks:
            timestamp = datetime.fromisoformat(fb['timestamp'])
            
            with st.expander(
                f"Transaction {fb['transaction_id']} - {fb['feedback_category']} "
                f"({timestamp.strftime('%Y-%m-%d %H:%M')})"
            ):
                detail_col1, detail_col2 = st.columns(2)
                
                with detail_col1:
                    st.markdown("**Transaction Details**")
                    st.write(f"ID: {fb['transaction_id']}")
                    st.write(f"Original Status: {fb['original_status'].upper()}")
                    st.write(f"Original Score: {fb['original_score']:.3f}")
                    st.write(f"Risk Category: {fb['original_risk_category'].title()}")
                
                with detail_col2:
                    st.markdown("**Feedback Details**")
                    st.write(f"Reviewer: {fb['reviewer']}")
                    st.write(f"Correct Decision: {fb['correct_decision']}")
                    st.write(f"Should Be: {fb['should_be_status'].upper()}")
                    st.write(f"Severity: {fb['severity_assessment']}")
                
                st.markdown("**Feedback Category:**")
                st.info(fb['feedback_category'])
                
                if fb.get('notes'):
                    st.markdown("**Additional Notes:**")
                    st.write(fb['notes'])
                
                st.caption(f"Submitted on {timestamp.strftime('%Y-%m-%d at %H:%M:%S')}")
        
        # Export feedbacks
        st.markdown("---")
        if st.button("📥 Export Feedbacks as CSV"):
            import pandas as pd
            from scripts.config import CSV_REPORTS_DIR
            
            df = pd.DataFrame(filtered_feedbacks)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(CSV_REPORTS_DIR, f"feedbacks_{timestamp}.csv")
            df.to_csv(csv_path, index=False)
            
            with open(csv_path, 'rb') as f:
                st.download_button(
                    "⬇️ Download CSV",
                    f,
                    file_name=f"feedbacks_{timestamp}.csv",
                    mime="text/csv"
                )
    
    else:
        st.info("No feedback records found. Submit your first feedback in the 'Submit Feedback' tab.")

# Tab 3: Analytics
with tab3:
    st.markdown("## 📈 Feedback Analytics")
    
    feedbacks = load_feedbacks()
    
    if feedbacks:
        import pandas as pd
        import plotly.express as px
        import plotly.graph_objects as go
        
        df = pd.DataFrame(feedbacks)
        
        # Summary metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            st.metric("Total Reviews", len(feedbacks))
        
        with metric_col2:
            correct_count = len([f for f in feedbacks if f['correct_decision'] == 'Yes'])
            accuracy = (correct_count / len(feedbacks) * 100) if feedbacks else 0
            st.metric("System Accuracy", f"{accuracy:.1f}%")
        
        with metric_col3:
            unique_reviewers = len(set(f['reviewer'] for f in feedbacks))
            st.metric("Unique Reviewers", unique_reviewers)
        
        with metric_col4:
            avg_score = sum(f['original_score'] for f in feedbacks) / len(feedbacks)
            st.metric("Avg Reviewed Score", f"{avg_score:.3f}")
        
        st.markdown("---")
        
        # Charts
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            # Feedback category distribution
            category_counts = df['feedback_category'].value_counts()
            fig1 = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title="Feedback Category Distribution"
            )
            st.plotly_chart(fig1, use_container_width=True)
        
        with chart_col2:
            # Correct decision distribution
            correct_counts = df['correct_decision'].value_counts()
            fig2 = px.bar(
                x=correct_counts.index,
                y=correct_counts.values,
                title="System Decision Accuracy",
                labels={'x': 'Assessment', 'y': 'Count'},
                color=correct_counts.values,
                color_continuous_scale=['red', 'yellow', 'green']
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        # Status comparison
        st.markdown("### 📊 Original vs Recommended Status")
        
        status_comparison = df.groupby(['original_status', 'should_be_status']).size().reset_index(name='count')
        
        fig3 = px.bar(
            status_comparison,
            x='original_status',
            y='count',
            color='should_be_status',
            title="Status Comparison",
            labels={'original_status': 'Original Status', 'count': 'Count', 'should_be_status': 'Recommended Status'},
            barmode='group'
        )
        st.plotly_chart(fig3, use_container_width=True)
        
        # Severity assessment
        st.markdown("### ⚠️ Risk Severity Assessment")
        
        severity_counts = df['severity_assessment'].value_counts()
        fig4 = go.Figure(data=[
            go.Bar(
                x=severity_counts.index,
                y=severity_counts.values,
                marker_color=['#3B82F6', '#10B981', '#F59E0B', '#EA580C', '#DC2626'][:len(severity_counts)]
            )
        ])
        fig4.update_layout(
            title="Severity Distribution",
            xaxis_title="Severity Level",
            yaxis_title="Count"
        )
        st.plotly_chart(fig4, use_container_width=True)
        
        # Reviewer activity
        st.markdown("### 👥 Reviewer Activity")
        
        reviewer_counts = df['reviewer'].value_counts().head(10)
        fig5 = px.bar(
            x=reviewer_counts.values,
            y=reviewer_counts.index,
            orientation='h',
            title="Top 10 Most Active Reviewers",
            labels={'x': 'Number of Reviews', 'y': 'Reviewer'}
        )
        st.plotly_chart(fig5, use_container_width=True)
        
        # Insights
        st.markdown("---")
        st.markdown("### 💡 Key Insights")
        
        insights_col1, insights_col2 = st.columns(2)
        
        with insights_col1:
            st.markdown("**Model Performance**")
            false_positives = len([f for f in feedbacks if f['feedback_category'] == 'False Positive - Legitimate Transaction'])
            false_negatives = len([f for f in feedbacks if f['feedback_category'] == 'False Negative - Should Have Flagged'])
            
            st.write(f"- False Positives: {false_positives} ({false_positives/len(feedbacks)*100:.1f}%)")
            st.write(f"- False Negatives: {false_negatives} ({false_negatives/len(feedbacks)*100:.1f}%)")
            st.write(f"- Needs Investigation: {len([f for f in feedbacks if f['feedback_category'] == 'Needs Investigation'])}")
        
        with insights_col2:
            st.markdown("**Recommendations**")
            
            if false_positives > len(feedbacks) * 0.2:
                st.warning("⚠️ High false positive rate - consider adjusting thresholds")
            
            if false_negatives > len(feedbacks) * 0.1:
                st.error("🚨 Concerning false negative rate - review detection rules")
            
            if accuracy > 80:
                st.success("✅ System performing well overall")
            else:
                st.info("ℹ️ Consider model retraining with feedback data")
    
    else:
        st.info("No feedback data available for analytics. Submit reviews to see insights here.")