"""
Visualization utilities for creating charts
"""
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, List, Any
from scripts.config import RISK_CATEGORIES, STATUS_CONFIG


def create_risk_distribution_chart(risk_distribution: Dict[str, int]) -> go.Figure:
    """Create a bar chart for risk distribution"""
    categories = []
    counts = []
    colors = []
    
    for category, count in risk_distribution.items():
        if count > 0:
            categories.append(RISK_CATEGORIES[category]['label'])
            counts.append(count)
            colors.append(RISK_CATEGORIES[category]['color'])
    
    fig = go.Figure(data=[
        go.Bar(
            x=categories,
            y=counts,
            marker_color=colors,
            text=counts,
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Count: %{y}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='Risk Distribution by Category',
        xaxis_title='Risk Category',
        yaxis_title='Number of Transactions',
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_status_pie_chart(status_distribution: Dict[str, int]) -> go.Figure:
    """Create a pie chart for transaction status"""
    labels = []
    values = []
    colors = []
    
    for status, count in status_distribution.items():
        if count > 0:
            labels.append(STATUS_CONFIG[status]['label'])
            values.append(count)
            colors.append(STATUS_CONFIG[status]['color'])
    
    fig = go.Figure(data=[
        go.Pie(
            labels=labels,
            values=values,
            marker=dict(colors=colors),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>',
            textinfo='label+percent'
        )
    ])
    
    fig.update_layout(
        title='Transaction Status Distribution',
        height=400,
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_score_histogram(transactions: List[Dict[str, Any]], 
                          status_filter: str = None) -> go.Figure:
    """Create histogram of combined scores"""
    filtered_txns = transactions
    if status_filter:
        filtered_txns = [t for t in transactions if t['status'] == status_filter]
    
    scores = [t['combined_score'] for t in filtered_txns]
    
    fig = go.Figure(data=[
        go.Histogram(
            x=scores,
            nbinsx=30,
            marker_color='#3B82F6',
            hovertemplate='Score Range: %{x}<br>Count: %{y}<extra></extra>'
        )
    ])
    
    # Add threshold lines
    fig.add_vline(x=0.85, line_dash="dash", line_color="red", 
                  annotation_text="Critical", annotation_position="top")
    fig.add_vline(x=0.70, line_dash="dash", line_color="orange",
                  annotation_text="High", annotation_position="top")
    fig.add_vline(x=0.50, line_dash="dash", line_color="yellow",
                  annotation_text="Medium", annotation_position="top")
    
    fig.update_layout(
        title='Combined Score Distribution',
        xaxis_title='Combined Score',
        yaxis_title='Frequency',
        height=400,
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_score_scatter(transactions: List[Dict[str, Any]]) -> go.Figure:
    """Create scatter plot of ML vs Ring scores"""
    ml_scores = [t['ml_score'] for t in transactions]
    ring_scores = [t['ring_score'] for t in transactions]
    combined_scores = [t['combined_score'] for t in transactions]
    statuses = [t['status'] for t in transactions]
    
    colors_map = {'deny': '#DC2626', 'flag': '#F59E0B', 'pass': '#10B981'}
    colors_list = [colors_map[s] for s in statuses]
    
    fig = go.Figure(data=[
        go.Scatter(
            x=ml_scores,
            y=ring_scores,
            mode='markers',
            marker=dict(
                size=8,
                color=combined_scores,
                colorscale='Reds',
                showscale=True,
                colorbar=dict(title="Combined<br>Score"),
                line=dict(width=1, color='white')
            ),
            text=[f"ID: {t['idx']}<br>Status: {t['status']}" for t in transactions],
            hovertemplate='<b>%{text}</b><br>ML Score: %{x:.3f}<br>Ring Score: %{y:.3f}<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title='ML Score vs Ring Score',
        xaxis_title='ML Score',
        yaxis_title='Ring Score',
        height=500,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
    )
    
    return fig


def create_timeline_chart(transactions: List[Dict[str, Any]]) -> go.Figure:
    """Create timeline chart of transaction scores"""
    indices = [t['idx'] for t in transactions]
    scores = [t['combined_score'] for t in transactions]
    statuses = [t['status'] for t in transactions]
    
    colors_map = {'deny': '#DC2626', 'flag': '#F59E0B', 'pass': '#10B981'}
    
    fig = go.Figure()
    
    for status in ['deny', 'flag', 'pass']:
        status_txns = [(i, s) for i, s, st in zip(indices, scores, statuses) if st == status]
        if status_txns:
            idx_list, score_list = zip(*status_txns)
            fig.add_trace(go.Scatter(
                x=list(idx_list),
                y=list(score_list),
                mode='markers',
                name=STATUS_CONFIG[status]['label'],
                marker=dict(size=8, color=colors_map[status]),
                hovertemplate='<b>Transaction %{x}</b><br>Score: %{y:.3f}<extra></extra>'
            ))
    
    fig.update_layout(
        title='Transaction Scores Over Time',
        xaxis_title='Transaction ID',
        yaxis_title='Combined Score',
        height=400,
        showlegend=True,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='closest'
    )
    
    return fig