"""
Data processing logic for Member D
Processes Member C output and generates required outputs
"""
import json
import os
import pandas as pd
from datetime import datetime
from typing import Dict, Any, List
from scripts.config import (
    PROCESSED_DATA_DIR, THRESHOLDS, RISK_CATEGORIES, 
    STATUS_CONFIG, ALERT_RULES
)


class DataProcessor:
    """Process Member C output and generate reports"""
    
    def __init__(self, member_c_data: Dict[str, Any]):
        self.raw_data = member_c_data
        self.meta = member_c_data.get("meta", {})
        self.llm_summary = member_c_data.get("llm_summary")
        self.llm_explanations = {
            item["idx"]: item["explanation"] 
            for item in member_c_data.get("llm_explanations", [])
        }
        self.transactions = member_c_data.get("data", [])
    
    def process_all(self) -> None:
        """Process all data and generate all output files"""
        self.generate_alert_report()
        self.generate_high_risk_users()
        self.generate_dashboard_data()
    
    def categorize_risk(self, score: float) -> str:
        """Categorize transaction based on combined score"""
        for category, config in RISK_CATEGORIES.items():
            min_score, max_score = config["range"]
            if min_score <= score < max_score:
                return category
        return "minimal"
    
    def generate_alert_report(self) -> str:
        """Generate alert_report.json"""
        alerts = []
        
        for txn in self.transactions:
            idx = txn["idx"]
            status = txn["status"]
            score = txn["combined_score"]
            
            # Check alert rules
            triggered_alerts = []
            for rule_name, rule_config in ALERT_RULES.items():
                condition = rule_config["condition"]
                # Simple condition evaluation
                if self._check_condition(txn, condition):
                    triggered_alerts.append({
                        "rule": rule_name,
                        "severity": rule_config["severity"],
                        "message": rule_config["message"]
                    })
            
            if triggered_alerts or status in ["deny", "flag"]:
                alert = {
                    "transaction_id": idx,
                    "timestamp": datetime.now().isoformat(),
                    "status": status,
                    "combined_score": score,
                    "ml_score": txn["ml_score"],
                    "ring_score": txn["ring_score"],
                    "risk_category": self.categorize_risk(score),
                    "explanation": txn["explanation"],
                    "llm_explanation": self.llm_explanations.get(idx),
                    "alerts": triggered_alerts,
                    "requires_action": status == "deny" or score > THRESHOLDS["high"]
                }
                alerts.append(alert)
        
        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_alerts": len(alerts),
                "critical_alerts": sum(1 for a in alerts if a["risk_category"] == "critical"),
                "high_risk_alerts": sum(1 for a in alerts if a["risk_category"] == "high"),
                "denied_transactions": self.meta.get("deny", 0),
                "flagged_transactions": self.meta.get("flag", 0)
            },
            "llm_summary": self.llm_summary,
            "alerts": alerts
        }
        
        filepath = os.path.join(PROCESSED_DATA_DIR, "alert_report.json")
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2)
        
        return filepath
    
    def generate_high_risk_users(self) -> str:
        """Generate high_risk_users.csv"""
        high_risk_txns = [
            txn for txn in self.transactions 
            if txn["combined_score"] >= THRESHOLDS["high"]
        ]
        
        # Group by user (assuming idx represents user or transaction)
        user_risks = {}
        for txn in high_risk_txns:
            idx = txn["idx"]
            score = txn["combined_score"]
            status = txn["status"]
            
            if idx not in user_risks:
                user_risks[idx] = {
                    "user_id": idx,
                    "transaction_count": 0,
                    "max_score": 0,
                    "avg_score": 0,
                    "scores": [],
                    "denied_count": 0,
                    "flagged_count": 0,
                    "risk_category": "",
                    "explanations": []
                }
            
            user_risks[idx]["transaction_count"] += 1
            user_risks[idx]["scores"].append(score)
            user_risks[idx]["max_score"] = max(user_risks[idx]["max_score"], score)
            user_risks[idx]["explanations"].append(txn["explanation"])
            
            if status == "deny":
                user_risks[idx]["denied_count"] += 1
            elif status == "flag":
                user_risks[idx]["flagged_count"] += 1
        
        # Calculate averages and finalize
        high_risk_list = []
        for user_id, data in user_risks.items():
            data["avg_score"] = sum(data["scores"]) / len(data["scores"])
            data["risk_category"] = self.categorize_risk(data["max_score"])
            data["primary_explanation"] = data["explanations"][0]
            del data["scores"]
            del data["explanations"]
            high_risk_list.append(data)
        
        # Sort by max score descending
        high_risk_list.sort(key=lambda x: x["max_score"], reverse=True)
        
        df = pd.DataFrame(high_risk_list)
        filepath = os.path.join(PROCESSED_DATA_DIR, "high_risk_users.csv")
        df.to_csv(filepath, index=False)
        
        return filepath
    
    def generate_dashboard_data(self) -> str:
        """Generate dashboard_data.json"""
        # Calculate statistics
        risk_distribution = {category: 0 for category in RISK_CATEGORIES.keys()}
        status_distribution = {status: 0 for status in STATUS_CONFIG.keys()}
        score_ranges = []
        
        for txn in self.transactions:
            score = txn["combined_score"]
            status = txn["status"]
            
            risk_category = self.categorize_risk(score)
            risk_distribution[risk_category] += 1
            status_distribution[status] += 1
            
            score_ranges.append({
                "idx": txn["idx"],
                "score": score,
                "status": status,
                "risk_category": risk_category
            })
        
        # Calculate score statistics
        all_scores = [txn["combined_score"] for txn in self.transactions]
        
        dashboard_data = {
            "generated_at": datetime.now().isoformat(),
            "meta": self.meta,
            "statistics": {
                "total_transactions": self.meta.get("total", 0),
                "denied": self.meta.get("deny", 0),
                "flagged": self.meta.get("flag", 0),
                "passed": self.meta.get("pass", 0),
                "denial_rate": self.meta.get("deny", 0) / max(self.meta.get("total", 1), 1) * 100,
                "flag_rate": self.meta.get("flag", 0) / max(self.meta.get("total", 1), 1) * 100,
                "avg_score": sum(all_scores) / len(all_scores) if all_scores else 0,
                "max_score": max(all_scores) if all_scores else 0,
                "min_score": min(all_scores) if all_scores else 0
            },
            "risk_distribution": risk_distribution,
            "status_distribution": status_distribution,
            "score_ranges": score_ranges,
            "thresholds": THRESHOLDS,
            "llm_enabled": self.meta.get("llm_enabled", False),
            "llm_summary": self.llm_summary
        }
        
        filepath = os.path.join(PROCESSED_DATA_DIR, "dashboard_data.json")
        with open(filepath, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        return filepath
    
    def _check_condition(self, txn: Dict[str, Any], condition: str) -> bool:
        """Evaluate a simple condition string"""
        try:
            # Create safe evaluation context
            status = txn["status"]
            combined_score = txn["combined_score"]
            
            # Simple evaluation (in production, use a proper expression parser)
            return eval(condition, {}, {
                "status": status,
                "combined_score": combined_score
            })
        except:
            return False
    
    def get_transaction_by_id(self, idx: int) -> Dict[str, Any]:
        """Get a specific transaction by ID"""
        for txn in self.transactions:
            if txn["idx"] == idx:
                return {
                    **txn,
                    "llm_explanation": self.llm_explanations.get(idx),
                    "risk_category": self.categorize_risk(txn["combined_score"])
                }
        return None


if __name__ == "__main__":  # FIXED: Was _name and main
    # Test the data processor
    from scripts.api_client import MemberCAPIClient, create_sample_data
    
    sample_data = create_sample_data()
    processor = DataProcessor(sample_data)
    processor.process_all()
    print("Data processing complete!")