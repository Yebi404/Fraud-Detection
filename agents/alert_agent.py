"""
Alert Agent - Real-time monitoring and alert generation
Monitors transactions and triggers alerts based on configurable rules
this is in agents folder
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from enum import Enum


class AlertSeverity(Enum):
    """Alert severity levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class AlertType(Enum):
    """Types of alerts"""
    HIGH_RISK_TRANSACTION = "high_risk_transaction"
    VELOCITY_SPIKE = "velocity_spike"
    UNUSUAL_PATTERN = "unusual_pattern"
    THRESHOLD_BREACH = "threshold_breach"
    REPEATED_DENIALS = "repeated_denials"
    SUSPICIOUS_BEHAVIOR = "suspicious_behavior"


class AlertAgent:
    """
    Alert Agent for monitoring and generating alerts
    """
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize Alert Agent
        
        Args:
            config: Configuration dictionary with thresholds and rules
        """
        self.config = config or self._default_config()
        self.alerts = []
        self.alert_history = []
        
    def _default_config(self) -> Dict[str, Any]:
        """Default configuration for alert rules"""
        return {
            "thresholds": {
                "critical_score": 0.85,
                "high_score": 0.70,
                "medium_score": 0.50,
                "velocity_count": 5,
                "velocity_window": 300  # 5 minutes in seconds
            },
            "rules": {
                "auto_alert_critical": True,
                "auto_alert_high": True,
                "alert_on_velocity": True,
                "alert_on_pattern": True,
                "alert_on_repeated_denials": True
            },
            "notification_channels": {
                "email": False,
                "sms": False,
                "webhook": False,
                "dashboard": True
            }
        }
    
    def analyze_transaction(self, transaction: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Analyze a single transaction and generate alerts if needed
        
        Args:
            transaction: Transaction data dictionary
            
        Returns:
            List of generated alerts
        """
        generated_alerts = []
        
        # Rule 1: Critical Score Alert
        if transaction['combined_score'] >= self.config['thresholds']['critical_score']:
            alert = self._create_alert(
                transaction_id=transaction['idx'],
                alert_type=AlertType.THRESHOLD_BREACH,
                severity=AlertSeverity.CRITICAL,
                message=f"Critical risk score detected: {transaction['combined_score']:.3f}",
                details={
                    "score": transaction['combined_score'],
                    "ml_score": transaction['ml_score'],
                    "ring_score": transaction['ring_score'],
                    "status": transaction['status']
                }
            )
            generated_alerts.append(alert)
        
        # Rule 2: High Score Alert
        elif transaction['combined_score'] >= self.config['thresholds']['high_score']:
            alert = self._create_alert(
                transaction_id=transaction['idx'],
                alert_type=AlertType.HIGH_RISK_TRANSACTION,
                severity=AlertSeverity.HIGH,
                message=f"High risk transaction detected: {transaction['combined_score']:.3f}",
                details={
                    "score": transaction['combined_score'],
                    "status": transaction['status']
                }
            )
            generated_alerts.append(alert)
        
        # Rule 3: Denied Transaction Alert
        if transaction['status'] == 'deny':
            alert = self._create_alert(
                transaction_id=transaction['idx'],
                alert_type=AlertType.HIGH_RISK_TRANSACTION,
                severity=AlertSeverity.HIGH,
                message=f"Transaction automatically denied",
                details={
                    "score": transaction['combined_score'],
                    "reason": transaction.get('explanation', 'N/A')
                }
            )
            generated_alerts.append(alert)
        
        # Rule 4: Unusual Pattern Alert (score mismatch)
        ml_ring_diff = abs(transaction['ml_score'] - transaction['ring_score'])
        if ml_ring_diff > 0.3:
            alert = self._create_alert(
                transaction_id=transaction['idx'],
                alert_type=AlertType.UNUSUAL_PATTERN,
                severity=AlertSeverity.MEDIUM,
                message=f"Unusual pattern: Large difference between ML and Ring scores",
                details={
                    "ml_score": transaction['ml_score'],
                    "ring_score": transaction['ring_score'],
                    "difference": ml_ring_diff
                }
            )
            generated_alerts.append(alert)
        
        # Store alerts
        self.alerts.extend(generated_alerts)
        self.alert_history.extend(generated_alerts)
        
        return generated_alerts
    
    def analyze_batch(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze batch of transactions and generate comprehensive alerts
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Dictionary with batch analysis results
        """
        batch_alerts = []
        
        # Analyze individual transactions
        for txn in transactions:
            txn_alerts = self.analyze_transaction(txn)
            batch_alerts.extend(txn_alerts)
        
        # Batch-level analysis
        
        # Rule 5: Velocity Check - Multiple high-risk transactions
        high_risk_txns = [t for t in transactions if t['combined_score'] >= 0.70]
        if len(high_risk_txns) >= self.config['thresholds']['velocity_count']:
            alert = self._create_alert(
                transaction_id=None,
                alert_type=AlertType.VELOCITY_SPIKE,
                severity=AlertSeverity.CRITICAL,
                message=f"Velocity spike detected: {len(high_risk_txns)} high-risk transactions",
                details={
                    "count": len(high_risk_txns),
                    "transaction_ids": [t['idx'] for t in high_risk_txns]
                }
            )
            batch_alerts.append(alert)
        
        # Rule 6: Multiple Denials
        denied_txns = [t for t in transactions if t['status'] == 'deny']
        if len(denied_txns) >= 3:
            alert = self._create_alert(
                transaction_id=None,
                alert_type=AlertType.REPEATED_DENIALS,
                severity=AlertSeverity.HIGH,
                message=f"Multiple transactions denied: {len(denied_txns)} denials detected",
                details={
                    "count": len(denied_txns),
                    "transaction_ids": [t['idx'] for t in denied_txns]
                }
            )
            batch_alerts.append(alert)
        
        return {
            "total_alerts": len(batch_alerts),
            "alerts": batch_alerts,
            "summary": self._generate_summary(batch_alerts)
        }
    
    def _create_alert(
        self,
        transaction_id: Optional[int],
        alert_type: AlertType,
        severity: AlertSeverity,
        message: str,
        details: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Create an alert object"""
        return {
            "alert_id": f"ALT-{datetime.now().strftime('%Y%m%d%H%M%S')}-{len(self.alerts)}",
            "timestamp": datetime.now().isoformat(),
            "transaction_id": transaction_id,
            "type": alert_type.value,
            "severity": severity.value,
            "message": message,
            "details": details,
            "acknowledged": False,
            "resolved": False
        }
    
    def _generate_summary(self, alerts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate summary of alerts"""
        severity_counts = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "info": 0
        }
        
        type_counts = {}
        
        for alert in alerts:
            severity_counts[alert['severity']] += 1
            alert_type = alert['type']
            type_counts[alert_type] = type_counts.get(alert_type, 0) + 1
        
        return {
            "total_alerts": len(alerts),
            "by_severity": severity_counts,
            "by_type": type_counts,
            "requires_immediate_action": severity_counts['critical'] + severity_counts['high']
        }
    
    def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get active (unresolved) alerts"""
        active = [a for a in self.alerts if not a['resolved']]
        
        if severity:
            active = [a for a in active if a['severity'] == severity]
        
        return sorted(active, key=lambda x: x['timestamp'], reverse=True)
    
    def acknowledge_alert(self, alert_id: str, user: str = "system") -> bool:
        """Acknowledge an alert"""
        for alert in self.alerts:
            if alert['alert_id'] == alert_id:
                alert['acknowledged'] = True
                alert['acknowledged_by'] = user
                alert['acknowledged_at'] = datetime.now().isoformat()
                return True
        return False
    
    def resolve_alert(self, alert_id: str, user: str = "system", resolution_notes: str = "") -> bool:
        """Resolve an alert"""
        for alert in self.alerts:
            if alert['alert_id'] == alert_id:
                alert['resolved'] = True
                alert['resolved_by'] = user
                alert['resolved_at'] = datetime.now().isoformat()
                alert['resolution_notes'] = resolution_notes
                return True
        return False
    
    def save_alerts(self, filepath: str) -> None:
        """Save alerts to file"""
        alert_data = {
            "generated_at": datetime.now().isoformat(),
            "total_alerts": len(self.alerts),
            "active_alerts": len([a for a in self.alerts if not a['resolved']]),
            "summary": self._generate_summary(self.alerts),
            "alerts": self.alerts
        }
        
        with open(filepath, 'w') as f:
            json.dump(alert_data, f, indent=2)
    
    def load_alerts(self, filepath: str) -> None:
        """Load alerts from file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                self.alerts = data.get('alerts', [])
    
    def clear_resolved_alerts(self) -> int:
        """Clear resolved alerts and return count"""
        before_count = len(self.alerts)
        self.alerts = [a for a in self.alerts if not a['resolved']]
        return before_count - len(self.alerts)
    
    def get_alert_statistics(self) -> Dict[str, Any]:
        """Get comprehensive alert statistics"""
        total = len(self.alert_history)
        active = len([a for a in self.alerts if not a['resolved']])
        resolved = len([a for a in self.alert_history if a.get('resolved', False)])
        
        return {
            "total_generated": total,
            "active": active,
            "resolved": resolved,
            "acknowledged": len([a for a in self.alerts if a.get('acknowledged', False)]),
            "by_severity": self._generate_summary(self.alert_history)['by_severity'],
            "by_type": self._generate_summary(self.alert_history)['by_type']
        }


# Example usage
if __name__ == "__main__":
    # Create agent
    agent = AlertAgent()
    
    # Sample transaction
    sample_txn = {
        "idx": 1001,
        "status": "deny",
        "ml_score": 0.92,
        "ring_score": 0.88,
        "combined_score": 0.90,
        "explanation": "High risk detected"
    }
    
    # Analyze
    alerts = agent.analyze_transaction(sample_txn)
    print(f"Generated {len(alerts)} alerts")
    
    for alert in alerts:
        print(f"- {alert['severity'].upper()}: {alert['message']}")