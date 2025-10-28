import os

api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    # Show first 10 and last 4 characters for verification
    masked_key = f"{api_key[:10]}...{api_key[-4:]}"
    print(f"Your API key: {masked_key}")
    print(f"Full length: {len(api_key)} characters")
    
    # Check if it starts with expected prefix
    if api_key.startswith("AIza"):
        print("✓ Key format looks correct (starts with 'AIza')")
    else:
        print(f"⚠ Key starts with '{api_key[:4]}' - expected 'AIza'")
else:
    print("✗ No API key found")