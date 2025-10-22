"""
API Client for fetching data from Member C (with testing mode)
"""
import requests
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
import sys

# Add parent directory to path for config import
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from scripts.config import MEMBER_C_API_URL, API_TIMEOUT, RAW_DATA_DIR, PROCESSED_DATA_DIR


class MemberCAPIClient:
    """Client for interacting with Member C API"""
    
    def __init__(self, api_url: str = None, test_mode: bool = False):  # FIXED: Was _init
        """
        Initialize API Client
        
        Args:
            api_url: API endpoint URL (can be None in test mode)
            test_mode: If True, loads from local file instead of API
        """
        self.api_url = api_url or MEMBER_C_API_URL
        self.test_mode = test_mode
        self.timeout = API_TIMEOUT
        
        # Define paths
        self.raw_data_dir = RAW_DATA_DIR
        self.processed_data_dir = PROCESSED_DATA_DIR
        
        # Create directories if they don't exist
        os.makedirs(self.raw_data_dir, exist_ok=True)
        os.makedirs(self.processed_data_dir, exist_ok=True)
    
    def get_verification_report(self) -> Dict[str, Any]:
        """
        Get verification report from Member C API
        
        Returns:
            Dictionary containing the verification report
        """
        if self.test_mode:
            test_file = os.path.join(self.raw_data_dir, "verification_report.json")
            return self._load_test_data(test_file)
        else:
            return self._fetch_from_api()
    
    def fetch_analysis(self, params: Optional[Dict[str, Any]] = None, 
                      test_file: str = None) -> Dict[str, Any]:
        """
        Fetch analysis data from Member C API or local test file
        
        Args:
            params: Optional parameters for the API request
            test_file: Path to test file when in test mode
            
        Returns:
            Dictionary containing the analysis results
        """
        if self.test_mode:
            if test_file is None:
                test_file = os.path.join(self.raw_data_dir, "verification_report.json")
            return self._load_test_data(test_file)
        else:
            return self._fetch_from_api(params)
    
    def _load_test_data(self, test_file: str) -> Dict[str, Any]:
        """Load data from local test file"""
        try:
            if not os.path.exists(test_file):
                raise FileNotFoundError(f"Test file not found: {test_file}")
            
            print(f"📂 Loading test data from: {test_file}")
            
            with open(test_file, 'r') as f:
                data = json.load(f)
            
            # Validate structure
            self._validate_data_structure(data)
            
            # Save as "latest" for consistency
            self._save_raw_data(data, prefix="test")
            
            print(f"✅ Test data loaded successfully!")
            print(f"   - Total transactions: {data['meta']['total']}")
            print(f"   - Denied: {data['meta']['deny']}")
            print(f"   - Flagged: {data['meta']['flag']}")
            print(f"   - Passed: {data['meta']['pass']}")
            
            return data
            
        except FileNotFoundError as e:
            raise Exception(f"Test file not found: {test_file}")
        except json.JSONDecodeError:
            raise Exception(f"Invalid JSON in test file: {test_file}")
        except Exception as e:
            raise Exception(f"Error loading test data: {str(e)}")
    
    def _fetch_from_api(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Fetch data from actual API"""
        if not self.api_url:
            raise Exception("API URL not configured. Set api_url or use test_mode=True")
        
        try:
            print(f"📡 Fetching data from API: {self.api_url}")
            
            # Construct full endpoint URL using base URL from config
            endpoint = f"{self.api_url}/get-verification-report"
            
            response = requests.get(
                endpoint,
                params=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            data = response.json()
            
            # Validate structure
            self._validate_data_structure(data)
            
            # Save raw data
            self._save_raw_data(data, prefix="api")
            
            print(f"✅ Data fetched successfully from API!")
            print(f"   - Total transactions: {data['meta']['total']}")
            
            return data
            
        except requests.exceptions.ConnectionError:
            raise Exception(f"Could not connect to Member C API at {self.api_url}")
        except requests.exceptions.Timeout:
            raise Exception(f"Request to Member C API timed out after {self.timeout} seconds")
        except requests.exceptions.HTTPError as e:
            raise Exception(f"HTTP Error from Member C API: {str(e)}")
        except Exception as e:
            raise Exception(f"Error fetching data from Member C: {str(e)}")
    
    def _validate_data_structure(self, data: Dict[str, Any]) -> None:
        """Validate that data matches expected structure"""
        required_keys = ['meta', 'llm_summary', 'llm_explanations', 'data']
        
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key in data: {key}")
        
        # Validate meta
        meta_keys = ['total', 'deny', 'flag', 'pass', 'llm_enabled']
        for key in meta_keys:
            if key not in data['meta']:
                raise ValueError(f"Missing required key in meta: {key}")
        
        # Validate transactions
        if not isinstance(data['data'], list):
            raise ValueError("'data' must be a list of transactions")
        
        if len(data['data']) == 0:
            raise ValueError("No transactions found in data")
        
        # Validate transaction structure
        txn_keys = ['idx', 'status', 'ml_score', 'ring_score', 'combined_score', 'explanation']
        for txn in data['data'][:5]:  # Check first 5
            for key in txn_keys:
                if key not in txn:
                    raise ValueError(f"Transaction missing required key: {key}")
    
    def _save_raw_data(self, data: Dict[str, Any], prefix: str = "api") -> None:
        """Save raw data to file with timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save timestamped version
        filename = f"verification_report_{prefix}_{timestamp}.json"
        filepath = os.path.join(self.raw_data_dir, filename)
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        # Also save canonical file names in data/ (as requested)
        latest_filepath = os.path.join(self.raw_data_dir, "verification_report_latest.json")
        root_filepath = os.path.join(self.raw_data_dir, "verification_report.json")
        with open(latest_filepath, 'w') as f:
            json.dump(data, f, indent=2)
        with open(root_filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved to: {filepath}")
    
    def load_latest_data(self) -> Optional[Dict[str, Any]]:
        """Load the latest saved data from disk"""
        latest_filepath = os.path.join(self.raw_data_dir, "verification_report_latest.json")
        
        if os.path.exists(latest_filepath):
            with open(latest_filepath, 'r') as f:
                return json.load(f)
        return None
    
    def list_available_test_files(self) -> list:
        """List all available test files in data directory"""
        if not os.path.exists(self.raw_data_dir):
            return []
        
        test_files = [
            f for f in os.listdir(self.raw_data_dir) 
            if f.endswith('.json') and 'verification_report' in f
        ]
        return sorted(test_files)


def create_sample_data() -> Dict[str, Any]:
    """Create sample data for testing"""
    return {
        "meta": {
            "total": 100,
            "deny": 15,
            "flag": 25,
            "pass": 60,
            "llm_enabled": True
        },
        "llm_summary": "Analysis of 100 transactions revealed 15 denials and 25 flags. High-risk patterns detected in late-night transactions and unusual geographic locations.",
        "llm_explanations": [
            {"idx": 1, "explanation": "Suspicious transaction pattern detected"},
            {"idx": 2, "explanation": "High risk score due to unusual activity"}
        ],
        "data": [
            {
                "idx": i,
                "status": "deny" if i % 10 == 0 else ("flag" if i % 5 == 0 else "pass"),
                "ml_score": 0.85 if i % 10 == 0 else (0.65 if i % 5 == 0 else 0.25),
                "ring_score": 0.90 if i % 10 == 0 else (0.70 if i % 5 == 0 else 0.30),
                "combined_score": 0.875 if i % 10 == 0 else (0.675 if i % 5 == 0 else 0.275),
                "explanation": f"Transaction {i} analysis"
            }
            for i in range(1, 101)
        ]
    }


# Testing functions
def test_with_sample_data():
    """Test the client with sample data"""
    print("=" * 60)
    print("Testing API Client with Sample Data")
    print("=" * 60)
    
    # Create client in test mode
    client = MemberCAPIClient(test_mode=True)
    
    # List available test files
    print("\n📋 Available test files:")
    test_files = client.list_available_test_files()
    for i, file in enumerate(test_files, 1):
        print(f"   {i}. {file}")
    
    # Try to load test data
    try:
        data = client.fetch_analysis()
        
        print("\n📊 Data Summary:")
        print(f"   Total: {data['meta']['total']}")
        print(f"   Denied: {data['meta']['deny']}")
        print(f"   Flagged: {data['meta']['flag']}")
        print(f"   Passed: {data['meta']['pass']}")
        print(f"   LLM Enabled: {data['meta']['llm_enabled']}")
        
        print("\n📝 LLM Summary (first 200 chars):")
        print(f"   {data['llm_summary'][:200]}...")
        
        print("\n✅ Test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        return False


if __name__ == "__main__":  # FIXED: Was _name and main
    test_with_sample_data()