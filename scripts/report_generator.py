"""
Report generation utilities for PDF and CSV exports
"""
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from scripts.config import PDF_REPORTS_DIR, CSV_REPORTS_DIR, RISK_CATEGORIES, STATUS_CONFIG


class ReportGenerator:
    """Generate PDF and CSV reports"""
    
    def _init(self):  # FIXED: Was _init
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
    
    def _setup_custom_styles(self):
        """Setup custom paragraph styles"""
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1F2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))
        
        self.styles.add(ParagraphStyle(
            name='CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#374151'),
            spaceAfter=12,
            spaceBefore=12
        ))
    
    def generate_dashboard_pdf(self, dashboard_data: Dict[str, Any], 
                               transactions: List[Dict[str, Any]]) -> str:
        """Generate comprehensive dashboard PDF report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"dashboard_report_{timestamp}.pdf"
        filepath = os.path.join(PDF_REPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph("Fraud Detection Dashboard Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Report metadata
        metadata = [
            ["Report Generated:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Total Transactions:", str(dashboard_data['statistics']['total_transactions'])],
            ["Analysis Period:", "Current Session"]
        ]
        
        metadata_table = Table(metadata, colWidths=[2*inch, 3*inch])
        metadata_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#F3F4F6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1F2937')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB'))
        ]))
        story.append(metadata_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Executive Summary
        story.append(Paragraph("Executive Summary", self.styles['CustomHeading']))
        stats = dashboard_data['statistics']
        summary_data = [
            ["Metric", "Count", "Percentage"],
            ["Denied Transactions", str(stats['denied']), f"{stats['denial_rate']:.2f}%"],
            ["Flagged Transactions", str(stats['flagged']), f"{stats['flag_rate']:.2f}%"],
            ["Passed Transactions", str(stats['passed']), 
             f"{100 - stats['denial_rate'] - stats['flag_rate']:.2f}%"],
        ]
        
        summary_table = Table(summary_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3B82F6')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F9FAFB')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB'))
        ]))
        story.append(summary_table)
        story.append(Spacer(1, 0.3*inch))
        
        # Risk Distribution
        story.append(Paragraph("Risk Distribution", self.styles['CustomHeading']))
        risk_data = [["Risk Category", "Count", "Percentage"]]
        total = dashboard_data['statistics']['total_transactions']
        for category, count in dashboard_data['risk_distribution'].items():
            if count > 0:
                risk_data.append([
                    RISK_CATEGORIES[category]['label'],
                    str(count),
                    f"{(count/total*100):.1f}%"
                ])
        
        risk_table = Table(risk_data, colWidths=[2.5*inch, 1.5*inch, 1.5*inch])
        risk_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6366F1')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB'))
        ]))
        story.append(risk_table)
        story.append(Spacer(1, 0.3*inch))
        
        # LLM Summary if available
        if dashboard_data.get('llm_summary'):
            story.append(Paragraph("AI Analysis Summary", self.styles['CustomHeading']))
            llm_para = Paragraph(dashboard_data['llm_summary'], self.styles['BodyText'])
            story.append(llm_para)
            story.append(Spacer(1, 0.3*inch))
        
        # High Risk Transactions
        story.append(PageBreak())
        story.append(Paragraph("High Risk Transactions", self.styles['CustomHeading']))
        
        high_risk_txns = [txn for txn in transactions if txn['combined_score'] >= 0.70][:20]
        
        if high_risk_txns:
            txn_data = [["ID", "Status", "Score", "Category"]]
            for txn in high_risk_txns:
                from scripts.data_processor import DataProcessor
                processor = DataProcessor({'data': transactions, 'meta': {}, 'llm_explanations': {}})
                risk_cat = processor.categorize_risk(txn['combined_score'])
                txn_data.append([
                    str(txn['idx']),
                    txn['status'].upper(),
                    f"{txn['combined_score']:.3f}",
                    RISK_CATEGORIES[risk_cat]['label']
                ])
            
            txn_table = Table(txn_data, colWidths=[1*inch, 1.2*inch, 1.2*inch, 2*inch])
            txn_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB'))
            ]))
            story.append(txn_table)
        
        # Build PDF
        doc.build(story)
        return filepath
    
    def generate_transaction_csv(self, transactions: List[Dict[str, Any]], 
                                 filename: str = None) -> str:
        """Generate CSV export of transactions"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transactions_{timestamp}.csv"
        
        filepath = os.path.join(CSV_REPORTS_DIR, filename)
        
        df = pd.DataFrame(transactions)
        df.to_csv(filepath, index=False)
        return filepath
    
    def generate_alert_csv(self, alert_data: Dict[str, Any]) -> str:
        """Generate CSV export of alerts"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"alerts_{timestamp}.csv"
        filepath = os.path.join(CSV_REPORTS_DIR, filename)
        
        alerts = alert_data.get('alerts', [])
        
        # Flatten alert data
        flattened = []
        for alert in alerts:
            flat_alert = {
                'transaction_id': alert['transaction_id'],
                'timestamp': alert['timestamp'],
                'status': alert['status'],
                'combined_score': alert['combined_score'],
                'ml_score': alert['ml_score'],
                'ring_score': alert['ring_score'],
                'risk_category': alert['risk_category'],
                'explanation': alert['explanation'],
                'requires_action': alert['requires_action']
            }
            flattened.append(flat_alert)
        
        df = pd.DataFrame(flattened)
        df.to_csv(filepath, index=False)
        return filepath
    
    def generate_high_risk_pdf(self, high_risk_data: pd.DataFrame) -> str:
        """Generate PDF report for high-risk users"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"high_risk_users_{timestamp}.pdf"
        filepath = os.path.join(PDF_REPORTS_DIR, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Title
        title = Paragraph("High Risk Users Report", self.styles['CustomTitle'])
        story.append(title)
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        story.append(Paragraph(f"Total High Risk Users: {len(high_risk_data)}", 
                              self.styles['CustomHeading']))
        story.append(Spacer(1, 0.2*inch))
        
        # Table data
        table_data = [["User ID", "Max Score", "Avg Score", "Denied", "Flagged", "Risk Category"]]
        
        for _, row in high_risk_data.head(50).iterrows():
            table_data.append([
                str(row['user_id']),
                f"{row['max_score']:.3f}",
                f"{row['avg_score']:.3f}",
                str(row['denied_count']),
                str(row['flagged_count']),
                row['risk_category'].upper()
            ])
        
        table = Table(table_data, colWidths=[1*inch, 1*inch, 1*inch, 0.8*inch, 0.8*inch, 1.2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#DC2626')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#E5E7EB'))
        ]))
        story.append(table)
        
        doc.build(story)
        return filepath