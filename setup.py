"""
Setup script for Member D Fraud Detection Dashboard
Creates necessary directories and initializes the project
"""
import os
import sys

def create_directory_structure():
    """Create all necessary directories"""
    directories = [
        "agents",
        "data/raw",
        "data/processed",
        "data/feedback",
        "reports/pdf",
        "reports/csv",
        "scripts/__pycache__",
        "pages",
        "utils",
        ".streamlit"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        
        # Create .gitkeep files for empty directories
        if "raw" in directory or "processed" in directory or "feedback" in directory or "pdf" in directory or "csv" in directory:
            gitkeep_path = os.path.join(directory, ".gitkeep")
            if not os.path.exists(gitkeep_path):
                with open(gitkeep_path, 'w') as f:
                    f.write("")
    
    print("✅ Directory structure created successfully!")

def create_init_files():
    """Create __init__.py files for Python packages"""
    init_files = [
        "scripts/__init__.py",
        "utils/__init__.py",
        "pages/__init__.py"
    ]
    
    for init_file in init_files:
        if not os.path.exists(init_file):
            with open(init_file, 'w') as f:
                f.write('"""Package initialization"""')
    
    print("✅ Package initialization files created!")

def setup_sample_data():
    """Setup sample data for testing"""
    from scripts.api_client import MemberCAPIClient, create_sample_data
    
    try:
        client = MemberCAPIClient()
        sample = create_sample_data()
        client.upload_sample_data(sample)
        print("✅ Sample data created successfully!")
    except Exception as e:
        print(f"⚠️ Warning: Could not create sample data: {str(e)}")

def main():
    """Main setup function"""
    print("🚀 Setting up Member D Fraud Detection Dashboard...")
    print("=" * 60)
    
    # Create directories
    print("\n📁 Creating directory structure...")
    create_directory_structure()
    
    # Create init files
    print("\n📝 Creating package initialization files...")
    create_init_files()
    
    # Setup sample data
    print("\n📊 Setting up sample data...")
    setup_sample_data()
    
    print("\n" + "=" * 60)
    print("✅ Setup complete!")
    print("\n📖 Next steps:")
    print("   1. Activate your virtual environment: venv\\Scripts\\activate (Windows) or source venv/bin/activate (Linux/Mac)")
    print("   2. Install dependencies: pip install -r requirements.txt")
    print("   3. Run the application: streamlit run Home.py")
    print("\n🌐 The dashboard will open in your web browser automatically!")

if __name__ == "__main__":
    main()
