"""
Export utilities for CSV and PDF generation
"""
import pandas as pd
from typing import List, Dict, Any
from scripts.report_generator import ReportGenerator


def export_to_csv(data: List[Dict[str, Any]], filename: str = None) -> str:
    """
    Export data to CSV
    
    Args:
        data: List of dictionaries to export
        filename: Optional custom filename
        
    Returns:
        Path to generated CSV file
    """
    generator = ReportGenerator()
    return generator.generate_transaction_csv(data, filename)


def export_to_pdf(dashboard_data: Dict[str, Any], 
                  transactions: List[Dict[str, Any]]) -> str:
    """
    Export dashboard data to PDF
    
    Args:
        dashboard_data: Dashboard statistics and metadata
        transactions: List of transaction dictionaries
        
    Returns:
        Path to generated PDF file
    """
    generator = ReportGenerator()
    return generator.generate_dashboard_pdf(dashboard_data, transactions)


def export_high_risk_csv(high_risk_df: pd.DataFrame, filename: str = None) -> str:
    """Export high-risk users to CSV"""
    from datetime import datetime
    from scripts.config import CSV_REPORTS_DIR
    import os
    
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"high_risk_users_{timestamp}.csv"
    
    filepath = os.path.join(CSV_REPORTS_DIR, filename)
    high_risk_df.to_csv(filepath, index=False)
    return filepath


def export_high_risk_pdf(high_risk_df: pd.DataFrame) -> str:
    """Export high-risk users to PDF"""
    generator = ReportGenerator()
    return generator.generate_high_risk_pdf(high_risk_df)