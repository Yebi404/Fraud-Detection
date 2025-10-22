"""
Run Alert Agent - Fetch data and generate alerts
Supports both test mode (local files) and production mode (API)
"""
import os
import sys
import argparse
import json
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def main():
    """Main execution function"""
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run Alert Agent')
    parser.add_argument('--test', action='store_true', 
                       help='Run in test mode with local files')
    parser.add_argument('--file', type=str,
                       help='Test file path (used with --test)')
    parser.add_argument('--api-url', type=str,
                       help='Override API URL from config')
    parser.add_argument('--save-alerts', action='store_true', default=True,
                       help='Save alerts to file')
    parser.add_argument('--output-dir', type=str, default='reports',
                       help='Output directory for alerts')
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("🚀 ALERT AGENT - Fraud Detection System")
    print("=" * 70)
    print()
    
    # Determine mode
    if args.test:
        print("🧪 Running in TEST MODE (using local files)")
        if args.file:
            print(f"📂 Test file: {args.file}")
    else:
        print("🌐 Running in PRODUCTION MODE (fetching from API)")
        if args.api_url:
            print(f"📡 API URL: {args.api_url}")
    
    print()
    
    try:
        # Import required modules
        print("📦 Loading modules...")
        from agents.alert_agent import AlertAgent
        from api_client import MemberCAPIClient
        
        # Step 1: Fetch/Load Data
        print("\n" + "=" * 70)
        print("📥 STEP 1: Fetching Verification Report")
        print("=" * 70)
        
        # Create API client
        client = MemberCAPIClient(
            api_url=args.api_url,
            test_mode=args.test
        )
        
        if args.test:
            print(f"📂 Loading from local file...")
            data = client.fetch_analysis(test_file=args.file)
        else:
            print("📡 Fetching from Member C API...")
            data = client.fetch_analysis()
        
        print("✅ Data loaded successfully!")
        
        # Validate data structure
        print("\n🔍 Validating data structure...")
        required_keys = ['meta', 'llm_summary', 'llm_explanations', 'data']
        for key in required_keys:
            if key not in data:
                raise ValueError(f"Missing required key: {key}")
        print("✅ Data structure valid")
        
        # Display data summary
        print("\n📊 Data Summary:")
        print(f"   Total Transactions: {data['meta']['total']}")
        print(f"   Denied: {data['meta']['deny']} ({data['meta']['deny']/data['meta']['total']*100:.1f}%)")
        print(f"   Flagged: {data['meta']['flag']} ({data['meta']['flag']/data['meta']['total']*100:.1f}%)")
        print(f"   Passed: {data['meta']['pass']} ({data['meta']['pass']/data['meta']['total']*100:.1f}%)")
        print(f"   LLM Enabled: {'Yes' if data['meta']['llm_enabled'] else 'No'}")
        
        # Step 2: Run Alert Agent
        print("\n" + "=" * 70)
        print("🚨 STEP 2: Running Alert Agent")
        print("=" * 70)
        
        print("\n🔧 Initializing Alert Agent...")
        agent = AlertAgent()
        
        print("🔍 Analyzing transactions...")
        results = agent.analyze_batch(data['data'])
        
        print(f"✅ Analysis complete!")
        
        # Display alert summary
        print("\n📋 Alert Summary:")
        summary = results['summary']
        print(f"   Total Alerts: {summary['total_alerts']}")
        print(f"   Critical: {summary['by_severity']['critical']}")
        print(f"   High: {summary['by_severity']['high']}")
        print(f"   Medium: {summary['by_severity']['medium']}")
        print(f"   Low: {summary['by_severity']['low']}")
        print(f"   Requires Immediate Action: {summary['requires_immediate_action']}")
        
        print("\n📊 Alerts by Type:")
        for alert_type, count in summary['by_type'].items():
            print(f"   - {alert_type}: {count}")
        
        # Step 3: Save Results
        if args.save_alerts:
            print("\n" + "=" * 70)
            print("💾 STEP 3: Saving Results")
            print("=" * 70)
            
            # Create output directory
            os.makedirs(args.output_dir, exist_ok=True)
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            alert_file = os.path.join(args.output_dir, f"alerts_{timestamp}.json")
            
            print(f"\n📁 Saving alerts to: {alert_file}")
            agent.save_alerts(alert_file)
            print("✅ Alerts saved successfully!")
            
            # Also save a summary report
            summary_file = os.path.join(args.output_dir, f"summary_{timestamp}.json")
            summary_data = {
                "generated_at": datetime.now().isoformat(),
                "mode": "test" if args.test else "production",
                "source": args.file if args.test else args.api_url,
                "data_summary": data['meta'],
                "alert_summary": summary,
                "llm_summary": data['llm_summary']
            }
            
            with open(summary_file, 'w') as f:
                json.dump(summary_data, f, indent=2)
            print(f"📄 Summary saved to: {summary_file}")
        
        # Display high priority alerts
        print("\n" + "=" * 70)
        print("🚨 HIGH PRIORITY ALERTS")
        print("=" * 70)
        
        high_priority = [a for a in results['alerts'] if a['severity'] in ['critical', 'high']]
        
        if high_priority:
            print(f"\nFound {len(high_priority)} high priority alerts:\n")
            
            for i, alert in enumerate(high_priority[:10], 1):  # Show first 10
                print(f"{i}. [{alert['severity'].upper()}] {alert['type']}")
                print(f"   Transaction ID: {alert.get('transaction_id', 'N/A')}")
                print(f"   Message: {alert['message']}")
                print(f"   Timestamp: {alert['timestamp']}")
                print()
            
            if len(high_priority) > 10:
                print(f"   ... and {len(high_priority) - 10} more high priority alerts")
        else:
            print("\n✅ No high priority alerts detected")
        
        # Final summary
        print("\n" + "=" * 70)
        print("✅ ALERT AGENT EXECUTION COMPLETE")
        print("=" * 70)
        print(f"\n📊 Processed: {data['meta']['total']} transactions")
        print(f"🚨 Generated: {summary['total_alerts']} alerts")
        print(f"⚠  Action Required: {summary['requires_immediate_action']} alerts")
        
        if args.save_alerts:
            print(f"💾 Results saved to: {args.output_dir}/")
        
        print("\n🎉 Success!")
        
    except FileNotFoundError as e:
        print(f"\n❌ Error: File not found - {str(e)}")
        sys.exit(1)
        
    except ImportError as e:
        print(f"\n❌ Error: Missing module - {str(e)}")
        sys.exit(1)
        
    except ValueError as e:
        print(f"\n❌ Error: Invalid data - {str(e)}")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()